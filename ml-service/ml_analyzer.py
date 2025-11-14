from flask import Flask, request, jsonify
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from collections import Counter
import numpy as np
import joblib
import logging
import time
from pathlib import Path

# Configure logging for production-ready request tracking
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Model version for API responses
MODEL_VERSION = "1.0.0"

# Directory for persisted models
MODELS_DIR = Path("models")
MODEL_PATH = MODELS_DIR / "isolation_forest_model.joblib"
SCALER_PATH = MODELS_DIR / "scaler.joblib"
VOCAB_PATH = MODELS_DIR / "vocabulary.joblib"

# Global vocabulary for rare word detection
word_frequency = Counter()

# --- Training with more realistic feature ranges and scaling ---
# Features we will use:
# 0) message length (20-400 typical)
# 1) service hash bucket (0-1000)
# 2) error keyword presence (0/1)
# 3) digit ratio in message (0-1)

def _update_vocabulary(message: str):
    """Update word frequency counter for rare word detection."""
    words = message.lower().split()
    word_frequency.update(words)

def _get_rare_word_score(message: str) -> float:
    """
    Calculate rare word score based on vocabulary frequency.
    Higher score = more rare/unusual words.
    
    Returns:
        float: Rare word score (0-10)
    """
    if not word_frequency:
        return 0.0
    
    words = message.lower().split()
    if not words:
        return 0.0
    
    # Calculate average rarity of words
    total_messages = sum(word_frequency.values()) / len(word_frequency) if word_frequency else 1
    rarities = []
    
    for word in words:
        freq = word_frequency.get(word, 0)
        if freq == 0:
            # Completely new word - very rare
            rarities.append(10.0)
        else:
            # Normalize frequency to 0-10 scale (inverse)
            # Common words (high freq) → low score
            # Rare words (low freq) → high score
            rarity = max(0, 10 - (freq / total_messages * 100))
            rarities.append(rarity)
    
    return np.mean(rarities) if rarities else 0.0

def _featurize(message: str, service: str) -> np.ndarray:
    """
    Extract features from log message and service name.
    
    Args:
        message: Log message text
        service: Service name
        
    Returns:
        numpy array of features: [length, service_hash, error_severity, digit_ratio, word_count, rare_word_score]
    """
    length = len(message)
    svc_hash = hash(service) % 1000
    lower = message.lower()
    
    # Comprehensive error severity scoring (0-10 scale)
    error_severity = 0
    
    # Critical (10)
    if any(k in lower for k in ["critical", "fatal", "panic", "crashed", "abort", "aborted", "killed", "segfault", "core dump"]):
        error_severity = 10
    # Severe (8)
    elif any(k in lower for k in ["error", "exception", "failed", "failure", "rejected", "denied", "invalid", "forbidden", "unauthorized"]):
        error_severity = 8
    # High (6)
    elif any(k in lower for k in ["timeout", "unavailable", "refused", "connection", "unreachable", "deadlock", "conflict", "corrupt"]):
        error_severity = 6
    # Medium (4)
    elif any(k in lower for k in ["warning", "warn", "retry", "retrying", "degraded", "throttle", "throttled"]):
        error_severity = 4
    # Low (2)
    elif any(k in lower for k in ["deprecated", "slow", "delay", "latency"]):
        error_severity = 2
    
    digits = sum(ch.isdigit() for ch in message)
    digit_ratio = (digits / max(1, length)) if length > 0 else 0.0
    word_count = len(message.split())
    
    # Rare word detection score
    rare_word_score = _get_rare_word_score(message)
    
    return np.array([length, svc_hash, error_severity, digit_ratio, word_count, rare_word_score], dtype=float)

def _train_model():
    """
    Train a new IsolationForest model with synthetic data.
    This is used when no persisted model is found.
    
    Returns:
        tuple: (model, scaler) trained IsolationForest and StandardScaler
    """
    logger.info("Training new model with synthetic data...")
    rng = np.random.default_rng(42)
    
    # Generate normal traffic patterns (80% of data)
    normal_size = 320
    normal_lengths = rng.integers(20, 200, size=normal_size)
    normal_svc = rng.integers(0, 1000, size=normal_size)
    normal_severity = rng.choice([0, 2, 4], size=normal_size, p=[0.7, 0.2, 0.1])  # Mostly no errors, some warnings
    normal_digit_ratio = rng.uniform(0.0, 0.15, size=normal_size)
    normal_word_count = rng.integers(3, 15, size=normal_size)
    normal_rare_score = rng.uniform(0.0, 3.0, size=normal_size)  # Low rarity for normal logs
    
    # Generate anomalous patterns (20% of data)
    anomaly_size = 80
    anomaly_lengths = rng.integers(50, 500, size=anomaly_size)  # Longer messages
    anomaly_svc = rng.integers(0, 1000, size=anomaly_size)
    anomaly_severity = rng.choice([6, 8, 10], size=anomaly_size, p=[0.3, 0.5, 0.2])  # High severity errors
    anomaly_digit_ratio = rng.uniform(0.0, 0.3, size=anomaly_size)
    anomaly_word_count = rng.integers(5, 30, size=anomaly_size)
    anomaly_rare_score = rng.uniform(5.0, 10.0, size=anomaly_size)  # High rarity for anomalies
    
    # Combine normal and anomalous data
    lengths = np.concatenate([normal_lengths, anomaly_lengths])
    svc = np.concatenate([normal_svc, anomaly_svc])
    severity = np.concatenate([normal_severity, anomaly_severity])
    digit_ratio = np.concatenate([normal_digit_ratio, anomaly_digit_ratio])
    word_count = np.concatenate([normal_word_count, anomaly_word_count])
    rare_score = np.concatenate([normal_rare_score, anomaly_rare_score])
    
    train = np.column_stack([lengths, svc, severity, digit_ratio, word_count, rare_score]).astype(float)
    
    scaler = StandardScaler()
    train_scaled = scaler.fit_transform(train)
    model = IsolationForest(contamination=0.2, random_state=42)  # Expect 20% anomalies
    model.fit(train_scaled)
    logger.info("Model training completed successfully")
    return model, scaler

def _load_model():
    """
    Load persisted model, scaler, and vocabulary from disk, or train new ones if not found.
    
    Returns:
        tuple: (model, scaler) IsolationForest and StandardScaler
    """
    global word_frequency
    
    # Ensure models directory exists
    MODELS_DIR.mkdir(exist_ok=True)
    
    # Try to load existing model, scaler, and vocabulary
    if MODEL_PATH.exists() and SCALER_PATH.exists():
        try:
            logger.info(f"Loading model from {MODEL_PATH}")
            model = joblib.load(MODEL_PATH)
            logger.info(f"Loading scaler from {SCALER_PATH}")
            scaler = joblib.load(SCALER_PATH)
            
            # Load vocabulary if exists
            if VOCAB_PATH.exists():
                logger.info(f"Loading vocabulary from {VOCAB_PATH}")
                word_frequency = joblib.load(VOCAB_PATH)
            
            logger.info("Model and scaler loaded successfully")
            return model, scaler
        except Exception as e:
            logger.warning(f"Failed to load persisted model: {e}. Training new model...")
    
    # Train new model if loading failed or files don't exist
    model, scaler = _train_model()
    
    # Save the newly trained model
    try:
        logger.info(f"Saving model to {MODEL_PATH}")
        joblib.dump(model, MODEL_PATH)
        logger.info(f"Saving scaler to {SCALER_PATH}")
        joblib.dump(scaler, SCALER_PATH)
        logger.info(f"Saving vocabulary to {VOCAB_PATH}")
        joblib.dump(word_frequency, VOCAB_PATH)
        logger.info("Model, scaler, and vocabulary saved successfully")
    except Exception as e:
        logger.error(f"Failed to save model: {e}")
    
    return model, scaler

# Load or train model on startup
logger.info("Initializing ML Analyzer...")
model, scaler = _load_model()
logger.info("ML Analyzer ready")

@app.route("/predict", methods=["POST"])
def predict():
    """
    Predict if a log entry is an anomaly.
    
    Expected JSON body:
    {
        "serviceName": "string",
        "message": "string"
    }
    
    Returns:
        JSON with isAnomaly (bool), score (float), and modelVersion (string)
    """
    start_time = time.time()
    
    try:
        # Input validation
        if not request.is_json:
            logger.warning("Request is not JSON")
            return jsonify({"error": "Content-Type must be application/json"}), 400
        
        data = request.get_json()
        if data is None:
            logger.warning("Request body is empty")
            return jsonify({"error": "Request body cannot be empty"}), 400
        
        message = data.get("message", "")
        service = data.get("serviceName", "")
        
        # Validate required fields
        if not message or not isinstance(message, str):
            logger.warning(f"Invalid message field: {message}")
            return jsonify({"error": "Field 'message' is required and must be a non-empty string"}), 400
        
        if not service or not isinstance(service, str):
            logger.warning(f"Invalid serviceName field: {service}")
            return jsonify({"error": "Field 'serviceName' is required and must be a non-empty string"}), 400
        
        logger.info(f"Processing prediction request for service: {service}, message length: {len(message)}")
        
        # Update vocabulary with this message for rare word detection
        _update_vocabulary(message)
        
        # Build features and scale
        features = _featurize(message, service).reshape(1, -1)
        features_scaled = scaler.transform(features)
        prediction = model.predict(features_scaled)[0]  # 1 = normal, -1 = anomaly
        score = float(model.decision_function(features_scaled)[0])  # higher => more normal
        
        is_anomaly = bool(prediction == -1)
        latency_ms = (time.time() - start_time) * 1000
        
        result = {
            "service": str(service),
            "message": str(message),
            "isAnomaly": is_anomaly,
            "score": score,
            "modelVersion": MODEL_VERSION
        }
        
        logger.info(f"Prediction completed: isAnomaly={is_anomaly}, score={score:.4f}, latency={latency_ms:.2f}ms")
        return jsonify(result), 200

    except Exception as e:
        latency_ms = (time.time() - start_time) * 1000
        logger.error(f"Error processing prediction request: {str(e)}, latency={latency_ms:.2f}ms", exc_info=True)
        return jsonify({"error": str(e), "modelVersion": MODEL_VERSION}), 500

@app.route("/", methods=["GET"])
def index():
    """Root endpoint - service information."""
    logger.info("Root endpoint accessed")
    return jsonify({
        "service": "ML Anomaly Detection Service",
        "status": "running",
        "version": MODEL_VERSION
    }), 200

@app.route("/health", methods=["GET"])
def health():
    """
    Health check endpoint.
    Verifies that the model and scaler are loaded and functional.
    """
    try:
        logger.debug("Health check requested")
        # Basic check that model exists and can score
        # Features: [length, service_hash, error_severity, digit_ratio, word_count, rare_word_score]
        test_features = [[100.0, 500.0, 0.0, 0.05, 5.0, 0.0]]
        _ = float(model.decision_function(scaler.transform(test_features))[0])
        logger.debug("Health check passed")
        return jsonify({
            "status": "up",
            "modelVersion": MODEL_VERSION,
            "modelLoaded": True
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}", exc_info=True)
        return jsonify({
            "status": "down",
            "error": str(e),
            "modelVersion": MODEL_VERSION
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)

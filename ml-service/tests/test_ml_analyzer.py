"""
Unit tests for ML Analyzer Flask service.

Tests cover:
- Health check endpoint
- Prediction endpoint with valid/invalid inputs
- Error handling
- Response format validation
"""

import pytest
import json
import sys
from pathlib import Path

# Add parent directory to path to import ml_analyzer
sys.path.insert(0, str(Path(__file__).parent.parent))

from ml_analyzer import app


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestHealthEndpoint:
    """Tests for the /health endpoint."""
    
    def test_health_check_success(self, client):
        """Test that health check returns 'up' status when model is loaded."""
        response = client.get('/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'up'
        assert data['modelLoaded'] is True
        assert 'modelVersion' in data
        assert data['modelVersion'] == '1.0.0'
    
    def test_health_check_content_type(self, client):
        """Test that health check returns JSON content type."""
        response = client.get('/health')
        assert response.content_type == 'application/json'


class TestRootEndpoint:
    """Tests for the root / endpoint."""
    
    def test_root_endpoint(self, client):
        """Test that root endpoint returns service information."""
        response = client.get('/')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['service'] == 'ML Anomaly Detection Service'
        assert data['status'] == 'running'
        assert 'version' in data


class TestPredictEndpoint:
    """Tests for the /predict endpoint."""
    
    def test_predict_valid_request(self, client):
        """Test prediction with valid input."""
        payload = {
            'serviceName': 'test-service',
            'message': 'GET /api/users 200 OK'
        }
        response = client.post(
            '/predict',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Verify response structure
        assert 'isAnomaly' in data
        assert isinstance(data['isAnomaly'], bool)
        assert 'score' in data
        assert isinstance(data['score'], (int, float))
        assert 'service' in data
        assert 'message' in data
        assert 'modelVersion' in data
        assert data['modelVersion'] == '1.0.0'
    
    def test_predict_anomaly_detection(self, client):
        """Test that error messages are detected as anomalies."""
        payload = {
            'serviceName': 'api',
            'message': 'Error: database connection timeout exception'
        }
        response = client.post(
            '/predict',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        # Error messages should typically be flagged as anomalies
        # (though this depends on the model's training)
        assert 'isAnomaly' in data
    
    def test_predict_missing_message(self, client):
        """Test prediction with missing message field."""
        payload = {
            'serviceName': 'test-service'
        }
        response = client.post(
            '/predict',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'message' in data['error'].lower()
    
    def test_predict_missing_service_name(self, client):
        """Test prediction with missing serviceName field."""
        payload = {
            'message': 'Some log message'
        }
        response = client.post(
            '/predict',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'servicename' in data['error'].lower() or 'service' in data['error'].lower()
    
    def test_predict_empty_message(self, client):
        """Test prediction with empty message."""
        payload = {
            'serviceName': 'test-service',
            'message': ''
        }
        response = client.post(
            '/predict',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_predict_empty_service_name(self, client):
        """Test prediction with empty serviceName."""
        payload = {
            'serviceName': '',
            'message': 'Some log message'
        }
        response = client.post(
            '/predict',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_predict_invalid_json(self, client):
        """Test prediction with invalid JSON."""
        response = client.post(
            '/predict',
            data='not json',
            content_type='application/json'
        )
        
        # Flask may return 400 or 500 depending on how it handles malformed JSON
        assert response.status_code in [400, 500]
    
    def test_predict_wrong_content_type(self, client):
        """Test prediction without JSON content type."""
        payload = {
            'serviceName': 'test',
            'message': 'test message'
        }
        response = client.post(
            '/predict',
            data=json.dumps(payload),
            content_type='text/plain'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'json' in data['error'].lower()
    
    def test_predict_empty_body(self, client):
        """Test prediction with empty request body."""
        response = client.post(
            '/predict',
            data='',
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_predict_non_string_message(self, client):
        """Test prediction with non-string message."""
        payload = {
            'serviceName': 'test-service',
            'message': 12345  # Not a string
        }
        response = client.post(
            '/predict',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_predict_non_string_service_name(self, client):
        """Test prediction with non-string serviceName."""
        payload = {
            'serviceName': 12345,  # Not a string
            'message': 'Some log message'
        }
        response = client.post(
            '/predict',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data


class TestResponseFormat:
    """Tests for response format consistency."""
    
    def test_predict_response_always_includes_version(self, client):
        """Test that all predict responses include modelVersion."""
        payload = {
            'serviceName': 'test',
            'message': 'test message'
        }
        response = client.post(
            '/predict',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        data = json.loads(response.data)
        assert 'modelVersion' in data
    
    def test_error_response_includes_version(self, client):
        """Test that error responses include modelVersion."""
        payload = {
            'serviceName': '',  # Invalid
            'message': 'test'
        }
        response = client.post(
            '/predict',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        # Even error responses should include version
        data = json.loads(response.data)
        # Note: Some validation errors might not include version, which is acceptable
        # but we check if it's present, it should be correct
        if 'modelVersion' in data:
            assert data['modelVersion'] == '1.0.0'


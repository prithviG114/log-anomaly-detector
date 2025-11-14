import { Link } from 'react-router-dom'
import './Header.css'

export default function Header() {
  return (
    <header>
      <div className="logo">Log Anomaly Detector</div>
      <nav>
        <Link to="/">About</Link>
        <Link to="/visualizations">Visualizations</Link>
      </nav>
    </header>
  )
}

import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Header from './components/Header'
import Footer from './components/Footer'
import About from './pages/About'
import Visualizations from './pages/Visualizations'

function App() {
  return (
    <Router>
      <Header />
      <Routes>
        <Route path="/" element={<About />} />
        <Route path="/visualizations" element={<Visualizations />} />
      </Routes>
      <Footer />
    </Router>
  )
}

export default App

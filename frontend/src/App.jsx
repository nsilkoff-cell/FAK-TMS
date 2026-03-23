import { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [apiStatus, setApiStatus] = useState('connecting...')

  useEffect(() => {
    // Test connection to backend
    fetch(import.meta.env.REACT_APP_API_URL || 'http://localhost:8000/health')
      .then(res => res.json())
      .then(() => setApiStatus('connected'))
      .catch(() => setApiStatus('disconnected'))
  }, [])

  return (
    <div className="App">
      <header>
        <h1>FAK-TMS Dashboard</h1>
        <p>Freight & Accounting Kit - Transportation Management System</p>
      </header>
      
      <main>
        <div className="status">
          <h2>Status</h2>
          <p>API Connection: <strong>{apiStatus}</strong></p>
        </div>

        <div className="placeholder">
          <h2>Welcome to FAK-TMS</h2>
          <p>Dashboard features coming soon:</p>
          <ul>
            <li>Load Management</li>
            <li>Carrier Sourcing</li>
            <li>Rate Optimization</li>
            <li>Invoice Tracking</li>
          </ul>
        </div>
      </main>
    </div>
  )
}

export default App
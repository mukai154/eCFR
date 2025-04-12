import { useEffect, useState } from 'react';
import { pingBackend, fetchMetrics } from './api/ecfrApi';
import HistoryView from './views/HistoryView'; // Import the new view
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'; // React Router setup

function MetricsView({ message, metrics }) {
  return (
    <>
      <h1>🔗 ECFR Frontend</h1>
      <p>
        Backend Status: <strong>{message || 'Loading...'}</strong>
      </p>
      <section style={{ marginTop: '2rem' }}>
        <h2>📊 Word Count by Agency</h2>
        {metrics ? (
          <ul>
            {Object.entries(metrics.agencies).map(([agency, count]) => (
              <li key={agency}>
                <strong>{agency}:</strong> {count.toLocaleString()} words
              </li>
            ))}
          </ul>
        ) : (
          <p>Loading metrics...</p>
        )}
      </section>
    </>
  );
}

function App() {
  const [message, setMessage] = useState(null);
  const [metrics, setMetrics] = useState(null);

  useEffect(() => {
    pingBackend()
      .then((data) => setMessage(data.message))
      .catch((err) => {
        console.error('Error connecting to backend:', err);
        setMessage('Error: Could not reach backend.');
      });

    fetchMetrics()
      .then(setMetrics)
      .catch((err) => {
        console.error('Error fetching metrics:', err);
      });
  }, []);

  return (
    <Router>
      <main style={{ padding: '2rem', fontFamily: 'sans-serif' }}>
        <nav style={{ marginBottom: '2rem' }}>
          <Link to="/" style={{ marginRight: '1rem' }}>Metrics</Link>
          <Link to="/history">History</Link>
        </nav>

        <Routes>
          <Route path="/" element={<MetricsView message={message} metrics={metrics} />} />
          <Route path="/history" element={<HistoryView />} />
        </Routes>
      </main>
    </Router>
  );
}

export default App;

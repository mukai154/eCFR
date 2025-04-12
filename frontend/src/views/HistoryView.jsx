import { useEffect, useState } from 'react';
import { fetchHistory } from '../api/ecfrApi'; // Import API function
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
} from 'recharts'; // Import Recharts components

export default function HistoryView() {
  const [data, setData] = useState([]);        // State to store response data
  const [loading, setLoading] = useState(false); // State to manage loading state

  const [title, setTitle] = useState('');       // Title number input (starts empty)
  const [dates, setDates] = useState(['2022-01-01', '2023-01-01', '2024-01-01']);
  const [formDates, setFormDates] = useState([...dates]);

  const [error, setError] = useState(null);     // Input validation error message

  const loadHistory = () => {
    if (!title || Number(title) <= 0) {
      setError('Please enter a valid title number greater than 0.');
      return;
    }
    setError(null);
    setLoading(true);
    fetchHistory(Number(title), formDates)
      .then(setData)
      .catch((err) => {
        console.error('Failed to fetch history:', err);
        setError('Failed to fetch history. Please check your input.');
      })
      .finally(() => setLoading(false));
  };

  // Load initial data on mount
  useEffect(() => {
    loadHistory();
  }, []);

  return (
    <div style={{ padding: '2rem' }}>
      <h2>📈 eCFR History</h2>

      {/* Input controls for title and dates */}
      <div style={{ marginBottom: '1.5rem' }}>
        <label>
          Title:&nbsp;
          <input
            type="text"
            value={title}
            onChange={(e) => {
              const value = e.target.value;
              // Allow only numeric characters using regex
              if (/^\d*$/.test(value)) {
                setTitle(value);
              }
            }}
            placeholder="1"
            style={{ marginRight: '1rem' }}
          />
        </label>
        {formDates.map((date, index) => (
          <label key={index} style={{ marginRight: '1rem' }}>
            Date {index + 1}:{' '}
            <input
              type="date"
              value={date}
              onChange={(e) => {
                const updated = [...formDates];
                updated[index] = e.target.value;
                setFormDates(updated);
              }}
            />
          </label>
        ))}
        <button onClick={loadHistory}>Fetch History</button>
      </div>

      {error && (
        <p style={{ color: 'red', marginBottom: '1rem' }}>{error}</p>
      )}

      {loading ? (
        <p>Loading history...</p>
      ) : (
        <>
          {/* Line chart visualization */}
          <div style={{ height: 300, marginBottom: '2rem' }}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="word_count" stroke="#8884d8" />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Textual list fallback */}
          <ul>
            {data.map((item) => (
              <li key={item.date}>
                <strong>{item.date}:</strong>{' '}
                {item.word_count ? `${item.word_count.toLocaleString()} words` : 'No data'}
              </li>
            ))}
          </ul>
        </>
      )}
    </div>
  );
}

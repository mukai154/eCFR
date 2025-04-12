// Base URL for your FastAPI backend
const BASE_URL = 'http://localhost:8000';

// Example function to check if the backend is responding
export async function pingBackend() {
  const res = await fetch(`${BASE_URL}/`);
  if (!res.ok) throw new Error('Backend not responding');
  return res.json();
}

// Fetch agency word count metrics from the backend
export async function fetchMetrics() {
  const res = await fetch(`${BASE_URL}/metrics`);
  if (!res.ok) throw new Error('Failed to fetch metrics');
  return res.json();
}

// Fetch word count history data from the backend
export async function fetchHistory(title = 10, dates = []) {
  // Build query string: ?title=10&dates=YYYY-MM-DD&dates=YYYY-MM-DD...
  const query = dates.map(date => `dates=${date}`).join('&');
  const res = await fetch(`${BASE_URL}/history?title=${title}&${query}`);
  if (!res.ok) throw new Error('Failed to fetch history');
  return res.json();
}

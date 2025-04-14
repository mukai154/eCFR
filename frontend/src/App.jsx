import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import HomeView from './views/HomeView';

const App = () => {
  return (
    <Router>
      <nav style={{ padding: '1rem', borderBottom: '1px solid #ccc', marginBottom: '2rem' }}>
        <Link to="/" style={{ marginRight: '1rem' }}>Home</Link>
        {/* You can add more links here */}
      </nav>

      <Routes>
        <Route path="/" element={<HomeView />} />
        <Route path="*" element={<div>404 Not Found</div>} />
      </Routes>
    </Router>
  );
};

export default App;

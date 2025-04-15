import React, { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom'; // NEW

const AgencySearch = ({ onSelect }) => {
  const [query, setQuery] = useState('');
  const [agencies, setAgencies] = useState([]);
  const [filtered, setFiltered] = useState([]);
  const [loading, setLoading] = useState(true);
  const inputRef = useRef(null); // added ref

  useEffect(() => {
    const fetchAgencies = async () => {
      try {
        const res = await fetch(`${import.meta.env.VITE_BACKEND_URL}/agencies`);
        const data = await res.json();
        setAgencies(data);
      } catch (err) {
        console.error('Error fetching agencies:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchAgencies();
  }, []);

  useEffect(() => {
    if (query.length < 1) {
      setFiltered([]);
      return;
    }

    const matches = agencies.filter(a =>
      a.agency.toLowerCase().includes(query.toLowerCase())
    );
    setFiltered(matches);
  }, [query, agencies]);

  const handleSelect = (agency) => {
    setQuery(agency.agency);
    inputRef.current?.blur();
    setTimeout(() => setFiltered([]), 100);
    onSelect && onSelect(agency);
  };

  return (
    <div>
      {loading ? (
        <p>🔎 Analyzing ECFR Agencies...</p>
      ) : (
        <>
          <input
            ref={inputRef}
            type="text"
            placeholder="Search for an agency..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            autoComplete="off"
            style={{ width: '25vw' }}
          />
          {filtered.length > 0 && (
            <ul style={{ border: '1px solid #ccc', marginTop: 0, padding: 10 }}>
              {filtered.map((agency) => (
                <li key={agency.agency} onClick={() => handleSelect(agency)} style={{ cursor: 'pointer' }}>
                  {agency.agency}
                </li>
              ))}
            </ul>
          )}
        </>
      )}
    </div>
  );
};

export default AgencySearch;

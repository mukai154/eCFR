import { useEffect, useState } from 'react';
import AgencySearch from '../components/AgencySearch';
import Chart from 'chart.js/auto';

function HomeView() {
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [selectedAgency, setSelectedAgency] = useState(null);
  const [correctionsData, setCorrectionsData] = useState([]);
  const [expandedIndices, setExpandedIndices] = useState({});
  const [analysisProgress, setAnalysisProgress] = useState({});
  const [analysisResults, setAnalysisResults] = useState({});
  const [analysisControllers, setAnalysisControllers] = useState({});

  useEffect(() => {
    const checkBackend = async () => {
      try {
        const res = await fetch('http://localhost:8000/');
        const data = await res.json();
        setMessage(data.message);
      } catch (err) {
        setMessage('Backend not reachable');
        console.error('Error fetching backend status:', err);
      } finally {
        setLoading(false);
      }
    };
    checkBackend();
  }, []);

  useEffect(() => {
    const fetchCorrections = async () => {
      if (!selectedAgency || !selectedAgency.titles) return;
      setLoading(true); // Start loading
      let allCorrections = [];

      for (const fullTitle of selectedAgency.titles) {
        const match = fullTitle.match(/Title\s(\d+)\sCFR\s(\w+)/i);
        const titleNumber = match ? parseInt(match[1]) : null;
        const chapter = match ? match[2] : null;

        if (!titleNumber) {
          console.warn("Skipping invalid title:", fullTitle);
          continue;
        }

        try {
          const res = await fetch(`http://localhost:8000/corrections?title=${titleNumber}`);
          const data = await res.json();

          allCorrections.push({
            title: titleNumber,
            chapter,
            total_corrections: data.corrections?.length || 0,
            corrections: data.corrections?.map(entry => ({
              date: entry.date,
              location: entry.location || 'Unknown',
            })) || [],
          });
        } catch (error) {
          console.error("Error fetching corrections:", error);
        }
      }

      setCorrectionsData(allCorrections);
      setExpandedIndices({});
      setLoading(false); // Finish loading
    };

    fetchCorrections();
  }, [selectedAgency]);

  const toggleExpanded = (index) => {
    setExpandedIndices((prev) => ({
      ...prev,
      [index]: !prev[index],
    }));
  };

  const analyzeRevisionHistory = async (index, titleData) => {
    if (!titleData.corrections?.length) return;

    const seen = new Set();
    const uniqueCorrections = titleData.corrections.filter(({ date, location }) => {
      const key = `${date}-${location}`;
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    });

    const total = uniqueCorrections.length;
    let results = [];

    const startTime = Date.now();
    const controller = new AbortController();
    setAnalysisControllers(prev => ({ ...prev, [index]: controller }));
    setAnalysisProgress(prev => ({ ...prev, [index]: { text: "Starting...", percent: 0 } }));

    try {
      for (let i = 0; i < total; i++) {
        const { date } = uniqueCorrections[i];
        const percent = Math.round(((i + 1) / total) * 100);
        const elapsed = (Date.now() - startTime) / 1000;
        const estimatedRemaining = Math.round((elapsed / (i + 1)) * (total - (i + 1)));

        setAnalysisProgress(prev => ({
          ...prev,
          [index]: {
            text: `Analyzing Revision ${i + 1}/${total} | Estimated ${estimatedRemaining}s remaining`,
            percent
          }
        }));

        const res = await fetch(`http://localhost:8000/wordcount?title=${titleData.title}&date=${date}`, {
          signal: controller.signal
        });
        const data = await res.json();
        results.push({ date, words: data.word_count || 0 });

        const partialResults = [...results];
        requestAnimationFrame(() => {
          const sortedResults = partialResults.sort((a, b) => new Date(a.date) - new Date(b.date));
          const canvas = document.getElementById(`chart-${index}`);
          if (!canvas) return;

          const existing = Chart.getChart(canvas);
          if (existing) existing.destroy();

          const labels = sortedResults.map(r => r.date);
          const dataPoints = sortedResults.map(r => r.words);
          new Chart(canvas, {
            type: 'line',
            data: {
              labels,
              datasets: [{
                label: 'Word Count',
                data: dataPoints,
                fill: true,
                borderColor: '#00FFFF',
                backgroundColor: 'rgba(0, 255, 255, 0.1)',
                pointBackgroundColor: '#00FFFF',
                tension: 0.3
              }]
            },
            options: {
              responsive: true,
              maintainAspectRatio: false,
              scales: {
                x: { display: true, title: { display: true, text: 'Revision Date' }},
                y: { display: true, title: { display: true, text: 'Word Count' }}
              },
              plugins: {
                title: {
                  display: true,
                  text: 'Word Count Over Time'
                }
              }
            }
          });
        });
      }

      setAnalysisResults(prev => ({ ...prev, [index]: results }));

    } catch (err) {
      if (err.name === "AbortError") {
        console.log("Download aborted for index", index);
      } else {
        console.error("Error during analysis:", err);
      }
    } finally {
      setAnalysisProgress(prev => ({ ...prev, [index]: false }));
      setAnalysisControllers(prev => {
        const { [index]: _, ...rest } = prev;
        return rest;
      });
    }
  };

  return (
    <>
      <h1>ECFR Analyzer Alpha Version 1.0.0</h1>
      <p>
        Backend Status:{' '}
        <strong>{loading ? 'Loading...' : message}</strong>
      </p>
      <section style={{ marginTop: '2rem' }}>
        <h2>🔍 Search for an Agency</h2>
        <AgencySearch onSelect={setSelectedAgency} selectedAgency={selectedAgency} />
      </section>

      {selectedAgency && !loading && (
        <section style={{ marginTop: '2rem' }}>
          <h3>Associated Regulations for {selectedAgency.agency}</h3>
          <h4>{selectedAgency.titles?.length || 0} Total Titles</h4>
          <h4>  {correctionsData.reduce((acc, c) => acc + c.total_corrections, 0)} Total Corrections</h4>
          {correctionsData.map((c, index) => (
            <div key={c.title + c.chapter}>
              <strong>Title {c.title} CFR {c.chapter || ''}</strong> – Total Revisions: {c.total_corrections}
              {c.total_corrections > 0 && (
                <>
                  <div>
                    <button onClick={() => toggleExpanded(index)} style={{ margin: '0.5rem 0' }}>
                      {expandedIndices[index] ? 'Hide revision history' : 'View revision history'}
                    </button>
                    {expandedIndices[index] && (
                      <ul>
                        {c.corrections?.map((entry, idx) => (
                          <li key={idx}>
                            {entry.date} – {entry.location} Revised
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                  <div style={{ margin: '0.5rem 0' }}>
                    <button onClick={() => analyzeRevisionHistory(index, c)} disabled={!!analysisProgress[index]}>
                      {analysisProgress[index]?.text || 'Analyze revision history'}
                    </button>
                    {analysisControllers[index] && (
                      <button onClick={() => {
                        analysisControllers[index].abort();
                      }} style={{ marginLeft: '1rem' }}>
                        Cancel
                      </button>
                    )}
                    {analysisProgress[index] && (
                      <div style={{ width: '100%', background: '#ccc', marginTop: '0.5rem' }}>
                        <div style={{
                          width: `${analysisProgress[index]?.percent || 0}%`,
                          background: '#4caf50',
                          height: '10px',
                          transition: 'width 0.3s ease'
                        }} />
                      </div>
                    )}
                    <div style={{ backgroundColor: '#1e1e1e', borderRadius: '16px', width: '100%', height: '300px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                      <canvas id={`chart-${index}`} style={{ width: '100%', height: '300px' }} />
                      {!analysisResults[index] && (
                        <span style={{ color: '#ccc', position: 'absolute' }}>Awaiting Analysis</span>
                      )}
                    </div>
                    {analysisResults[index] && (
                      <div style={{ marginTop: '0.5rem' }}>
                        <strong>Word Counts by Revision:</strong>
                        <ul>
                          {analysisResults[index].map((entry, i) => (
                            <li key={i}>{entry.date} – {entry.words} words</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </>
              )}
            </div>
          ))}
        </section>
      )}
    </>
  );
}

export default HomeView;

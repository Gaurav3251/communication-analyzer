import { useState } from 'react';
import axios from 'axios';
import './App.css';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function App() {
  const [transcript, setTranscript] = useState('');
  const [duration, setDuration] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [file, setFile] = useState(null);

  const analyzeTranscript = async () => {
    if (!transcript.trim()) {
      setError('Please enter a transcript');
      return;
    }
    setLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await axios.post(`${API_URL}/analyze`, {
        transcript: transcript,
        duration_seconds: duration ? parseInt(duration) : null
      });
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Analysis failed. Please check your input.');
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e) => {
    const selectedFile = e.target.files[0];
    if (!selectedFile) return;

    if (!selectedFile.name.endsWith('.txt')) {
      setError('Please upload a .txt file');
      return;
    }

    setFile(selectedFile);
    setError('');
    setResult(null);

    try {
      // Just read and display the file content, don't analyze yet
      const text = await selectedFile.text();
      setTranscript(text);
    } catch (err) {
      setError('Failed to read file. Please ensure it is a valid .txt file.');
      setFile(null);
    }
  };

  const clearAll = () => {
    setTranscript('');
    setDuration('');
    setResult(null);
    setError('');
    setFile(null);
  };

  const getScoreColor = (score, max) => {
    const pct = (score / max) * 100;
    if (pct >= 80) return '#10b981';
    if (pct >= 60) return '#f59e0b';
    if (pct >= 40) return '#f97316';
    return '#ef4444';
  };

  const getOverallGrade = (score) => {
    if (score >= 85) return { grade: 'A', label: 'Excellent' };
    if (score >= 70) return { grade: 'B', label: 'Good' };
    if (score >= 55) return { grade: 'C', label: 'Satisfactory' };
    if (score >= 40) return { grade: 'D', label: 'Needs Work' };
    return { grade: 'F', label: 'Poor' };
  };

  return (
    <div className="app">
      <header>
        <h1>Communication Skills Analyzer</h1>
        <p>AI-powered scoring for self-introduction transcripts</p>
      </header>

      <main>
        <section className="input-section">
          <div className="input-methods">
            <div className="method">
              <h3>Option 1: Paste Text</h3>
              <textarea
                value={transcript}
                onChange={(e) => setTranscript(e.target.value)}
                placeholder="Paste the transcript here..."
                rows={8}
              />
            </div>

            <div className="method">
              <h3>Option 2: Upload File</h3>
              <div className="file-upload">
                <input
                  type="file"
                  accept=".txt"
                  onChange={handleFileUpload}
                  id="file-input"
                />
                <label htmlFor="file-input" className="file-label">
                  {file ? file.name : 'Choose .txt file'}
                </label>
              </div>
            </div>
          </div>
          
          <div className="controls">
            <div className="duration-input">
              <label>Duration (seconds):</label>
              <input
                type="number"
                value={duration}
                onChange={(e) => setDuration(e.target.value)}
                placeholder="Optional"
              />
            </div>

            <div className="actions">
              <button 
                className="btn-primary" 
                onClick={analyzeTranscript}
                disabled={loading || !transcript.trim()}
              >
                {loading ? 'Analyzing...' : 'Analyze'}
              </button>
              <button className="btn-secondary" onClick={clearAll}>
                Clear
              </button>
            </div>
          </div>

          {error && <div className="error">{error}</div>}
        </section>

        {result && (
          <section className="results">
            <div className="overall">
              <div className="score-circle" style={{borderColor: getScoreColor(result.overall_score, 100)}}>
                <span className="score">{result.overall_score}</span>
                <span className="max">/100</span>
              </div>
              <div className="grade-info">
                <span className="grade" style={{color: getScoreColor(result.overall_score, 100)}}>
                  {getOverallGrade(result.overall_score).grade}
                </span>
                <span className="label">{getOverallGrade(result.overall_score).label}</span>
              </div>
              <div className="stats">
                <span>{result.word_count} words</span>
                <span>{result.sentence_count} sentences</span>
              </div>
            </div>

            <p className="summary">{result.summary}</p>

            <h3>Detailed Scores</h3>
            <div className="criteria">
              {result.criteria_scores.map((c, i) => (
                <div key={i} className="criterion">
                  <div className="criterion-header">
                    <span className="name">{c.metric}</span>
                    <span className="score" style={{color: getScoreColor(c.score, c.max_score)}}>
                      {c.score}/{c.max_score}
                    </span>
                  </div>
                  <div className="bar">
                    <div 
                      className="fill" 
                      style={{
                        width: `${(c.score / c.max_score) * 100}%`,
                        backgroundColor: getScoreColor(c.score, c.max_score)
                      }}
                    />
                  </div>
                  <p className="feedback">{c.feedback}</p>
                  <span className="tag">{c.criterion}</span>
                </div>
              ))}
            </div>
          </section>
        )}
      </main>
    </div>
  );
}

export default App;
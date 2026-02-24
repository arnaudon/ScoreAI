import React, { useState } from 'react';
import { api, Response, Score } from '../api';

interface AgentProps {
  onScoreSelect?: (scoreId: number) => void;
}

const Agent: React.FC<AgentProps> = ({ onScoreSelect }) => {
  const [question, setQuestion] = useState('');
  const [response, setResponse] = useState<Response | null>(null);
  const [messageHistory, setMessageHistory] = useState<any[]>([]);
  const [scores, setScores] = useState<Score[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleRunAgent = async () => {
    if (!question) return;

    setLoading(true);
    setError(null);
    try {
      // In Streamlit, session state holds message history. Here we use local state.
      const result = await api.runAgent(question, messageHistory);
      
      setResponse(result.response);
      setMessageHistory(prev => [...prev, ...result.message_history]);

      if (result.response.score_id) {
        // Fetch scores to display table
        const scoresData = await api.getScores();
        setScores(scoresData.scores);
      }
    } catch (err) {
      console.error(err);
      setError("Something went wrong, try again later");
    } finally {
      setLoading(false);
    }
  };

  const handleOpenPdf = (scoreId: number) => {
    if (onScoreSelect) {
      onScoreSelect(scoreId);
    } else {
        console.log("PDF open requested for score ID:", scoreId);
    }
  };

  const handleCleanHistory = () => {
    setMessageHistory([]);
    setResponse(null);
    setScores([]);
  };

  return (
    <div className="agent-container">
      <div className="input-group">
        <label htmlFor="question">Question</label>
        <input
          id="question"
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleRunAgent()}
          placeholder="Ask a question..."
        />
        <button onClick={handleRunAgent} disabled={loading}>
          {loading ? 'Running...' : 'Submit'}
        </button>
      </div>

      {error && <div className="error">{error}</div>}

      {response && (
        <div className="response-area">
          <p>{response.response}</p>
          
          {response.score_id && (
            <div className="scores-table">
              <h3>Scores</h3>
              <table>
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Title</th>
                    <th>Composer</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {scores
                    .filter(s => s.id === response.score_id) // Streamlit version selects the specific row
                    .map(score => (
                    <tr key={score.id} className={score.id === response.score_id ? 'selected' : ''}>
                      <td>{score.id}</td>
                      <td>{score.title}</td>
                      <td>{score.composer}</td>
                      <td>
                        <button onClick={() => handleOpenPdf(score.id!)}>
                            Open PDF
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      <div className="caption">
        <p>Here is how to use me:</p>
        <ul>
          <li>Ask me a question about a score or a composer</li>
          <li>I can give you a random score from a composer</li>
          <li>etc...</li>
        </ul>
      </div>

      <button onClick={handleCleanHistory} className="clean-history-btn">
        clean history
      </button>
    </div>
  );
};

export default Agent;

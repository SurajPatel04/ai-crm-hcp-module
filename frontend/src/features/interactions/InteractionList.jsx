import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { fetchInteractions } from './interactionSlice';
import { useNavigate } from 'react-router-dom';

const InteractionList = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { interactions, loading, error } = useSelector((state) => state.interactions);

  useEffect(() => {
    dispatch(fetchInteractions());
  }, [dispatch]);

  const getSentimentClass = (sentiment) => {
    switch(sentiment?.toLowerCase()) {
      case 'positive': return 'badge positive';
      case 'neutral': return 'badge neutral';
      case 'negative': return 'badge negative';
      default: return 'badge neutral';
    }
  };

  if (loading && interactions.length === 0) {
    return <div>Loading interactions...</div>;
  }

  if (error) {
    return <div style={{ color: 'var(--error)' }}>Error: {error}</div>;
  }

  return (
    <div className="card" style={{ padding: '2rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <h2>Interaction History</h2>
        <button className="btn-primary" onClick={() => navigate('/log-interaction')}>
          + New Interaction
        </button>
      </div>

      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>HCP Name</th>
              <th>Type</th>
              <th>Date</th>
              <th>Sentiment</th>
              <th>AI Summary</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {interactions.map((interaction) => (
              <tr key={interaction.id}>
                <td style={{ fontWeight: 500 }}>{interaction.hcp_name || 'Unknown HCP'}</td>
                <td>{interaction.interaction_type}</td>
                <td>{interaction.interaction_date}</td>
                <td>
                  <span className={getSentimentClass(interaction.sentiment)}>
                    {interaction.sentiment}
                  </span>
                </td>
                <td style={{ maxWidth: '300px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                  {interaction.ai_summary || interaction.topics_discussed || '-'}
                </td>
                <td>
                  <button 
                    onClick={() => navigate(`/interactions/${interaction.id}/edit`)}
                    style={{ color: 'var(--primary)', fontWeight: 500, padding: '0.25rem 0.5rem' }}
                  >
                    Edit
                  </button>
                </td>
              </tr>
            ))}
            {interactions.length === 0 && !loading && (
              <tr>
                <td colSpan="6" style={{ textAlign: 'center', color: 'var(--text-secondary)' }}>
                  No interactions found.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default InteractionList;

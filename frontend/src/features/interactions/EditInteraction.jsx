import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate, useParams } from 'react-router-dom';
import { fetchInteractionById, updateInteraction, clearCurrent } from './interactionSlice';
import api from '../../services/api';

const EditInteraction = () => {
  const { id } = useParams();
  const dispatch = useDispatch();
  const navigate = useNavigate();
  
  const { current, loading } = useSelector((state) => state.interactions);
  const [hcps, setHcps] = useState([]);
  
  const [formData, setFormData] = useState({
    hcp_id: '',
    interaction_type: '',
    interaction_date: '',
    interaction_time: '',
    topics_discussed: '',
    sentiment: '',
    outcomes: ''
  });

  useEffect(() => {
    // Fetch HCPS
    api.get('/hcp/').then(res => setHcps(res.data)).catch(console.error);
    // Fetch specific interaction
    dispatch(fetchInteractionById(id));
    
    return () => {
      dispatch(clearCurrent());
    };
  }, [dispatch, id]);

  useEffect(() => {
    if (current) {
      setFormData({
        hcp_id: current.hcp_id || '',
        interaction_type: current.interaction_type || 'Meeting',
        interaction_date: current.interaction_date || '',
        interaction_time: current.interaction_time ? current.interaction_time.substring(0,5) : '',
        topics_discussed: current.topics_discussed || '',
        sentiment: current.sentiment || 'Neutral',
        outcomes: current.outcomes || ''
      });
    }
  }, [current]);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const resultAction = await dispatch(updateInteraction({ id, data: formData }));
    if (updateInteraction.fulfilled.match(resultAction)) {
      navigate('/interactions');
    } else {
      alert("Failed to update interaction");
    }
  };

  if (loading && !current) {
    return <div>Loading...</div>;
  }

  return (
    <div className="card" style={{ maxWidth: '800px', margin: '0 auto', padding: '2rem' }}>
      <h2 style={{ marginBottom: '2rem' }}>Edit Interaction</h2>
      <form onSubmit={handleSubmit}>
        
        <div className="form-group">
          <label className="form-label">Healthcare Professional</label>
          <select name="hcp_id" value={formData.hcp_id} onChange={handleChange} required>
            <option value="">Select HCP...</option>
            {hcps.map(hcp => (
              <option key={hcp.id} value={hcp.id}>{hcp.full_name}</option>
            ))}
          </select>
        </div>

        <div style={{ display: 'flex', gap: '1rem' }}>
          <div className="form-group" style={{ flex: 1 }}>
            <label className="form-label">Interaction Type</label>
            <select name="interaction_type" value={formData.interaction_type} onChange={handleChange}>
              <option value="Meeting">Meeting</option>
              <option value="Call">Call</option>
              <option value="Email">Email</option>
              <option value="Conference">Conference</option>
              <option value="Virtual">Virtual</option>
            </select>
          </div>
          <div className="form-group" style={{ flex: 1 }}>
            <label className="form-label">Sentiment</label>
            <select name="sentiment" value={formData.sentiment} onChange={handleChange}>
              <option value="Positive">Positive</option>
              <option value="Neutral">Neutral</option>
              <option value="Negative">Negative</option>
            </select>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '1rem' }}>
          <div className="form-group" style={{ flex: 1 }}>
            <label className="form-label">Date</label>
            <input type="date" name="interaction_date" value={formData.interaction_date} onChange={handleChange} required />
          </div>
          <div className="form-group" style={{ flex: 1 }}>
            <label className="form-label">Time</label>
            <input type="time" name="interaction_time" value={formData.interaction_time} onChange={handleChange} />
          </div>
        </div>

        <div className="form-group">
          <label className="form-label">Topics Discussed</label>
          <textarea name="topics_discussed" value={formData.topics_discussed} onChange={handleChange} rows="4"></textarea>
        </div>

        <div className="form-group">
          <label className="form-label">Outcomes</label>
          <textarea name="outcomes" value={formData.outcomes} onChange={handleChange} rows="3"></textarea>
        </div>

        <div style={{ display: 'flex', gap: '1rem', marginTop: '2rem' }}>
          <button type="button" onClick={() => navigate('/interactions')} style={{ flex: 1, padding: '0.75rem', backgroundColor: 'var(--bg-color)', border: '1px solid var(--border-color)', borderRadius: '6px', fontWeight: 500 }}>
            Cancel
          </button>
          <button type="submit" className="btn-primary" disabled={loading} style={{ flex: 1 }}>
            {loading ? 'Saving...' : 'Update Interaction'}
          </button>
        </div>

      </form>
    </div>
  );
};

export default EditInteraction;

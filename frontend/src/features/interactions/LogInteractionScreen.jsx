import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { createInteraction } from './interactionSlice';
import ChatPanel from '../agent/ChatPanel';
import api from '../../services/api';

const LogInteractionScreen = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { loading, aiExtractedData } = useSelector((state) => state.interactions);
  
  const [hcps, setHcps] = useState([]);
  const [formData, setFormData] = useState({
    hcp_id: '',
    interaction_type: 'Meeting',
    interaction_date: new Date().toISOString().split('T')[0],
    interaction_time: '12:00',
    topics_discussed: '',
    sentiment: 'Neutral',
    outcomes: '',
    ai_summary: '',
    log_method: 'form'
  });

  // Fetch HCPs for dropdown
  useEffect(() => {
    const fetchHcps = async () => {
      try {
        const response = await api.get('/hcp/');
        setHcps(response.data);
      } catch (error) {
        console.error('Failed to fetch HCPs', error);
      }
    };
    fetchHcps();
  }, []);

  // Auto-fill form when AI extracts data
  useEffect(() => {
    if (aiExtractedData) {
      const sanitizedData = {};
      for (const [key, value] of Object.entries(aiExtractedData)) {
        sanitizedData[key] = value !== null ? value : '';
      }

      // If the AI returned an HCP that isn't in our local list (e.g. newly created), add it
      if (sanitizedData.hcp_id && sanitizedData.hcp_name) {
        setHcps(prev => {
          const exists = prev.find(h => h.id === sanitizedData.hcp_id);
          if (!exists) {
            return [...prev, { id: sanitizedData.hcp_id, full_name: sanitizedData.hcp_name }];
          }
          return prev;
        });
      }

      setFormData(prev => ({
        ...prev,
        ...sanitizedData,
        log_method: 'chat' // set log method to chat if AI filled it
      }));
    }
  }, [aiExtractedData]);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.hcp_id) {
      alert("Please select an HCP");
      return;
    }
    const resultAction = await dispatch(createInteraction(formData));
    if (createInteraction.fulfilled.match(resultAction)) {
      navigate('/interactions');
    } else {
      alert("Failed to log interaction: " + resultAction.payload);
    }
  };

  return (
    <div className="split-layout">
      {/* LEFT: FORM */}
      <div className="split-left card" style={{ padding: '2rem' }}>
        <h2 style={{ marginBottom: '2rem' }}>Log Interaction</h2>
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
            <textarea 
              name="topics_discussed" 
              value={formData.topics_discussed} 
              onChange={handleChange} 
              rows="3" 
              placeholder="What was discussed?"
            ></textarea>
          </div>

          <div className="form-group">
            <label className="form-label">Outcomes / Next Steps</label>
            <textarea 
              name="outcomes" 
              value={formData.outcomes} 
              onChange={handleChange} 
              rows="3" 
              placeholder="Any follow-ups or outcomes?"
            ></textarea>
          </div>

          <div className="form-group">
            <label className="form-label">Summary</label>
            <textarea 
              name="ai_summary" 
              value={formData.ai_summary} 
              onChange={handleChange} 
              rows="3" 
              placeholder="Interaction summary..."
            ></textarea>
          </div>

        </form>
      </div>

      {/* RIGHT: CHAT PANEL */}
      <div className="split-right card">
        <ChatPanel hcpId={formData.hcp_id} />
      </div>
    </div>
  );
};

export default LogInteractionScreen;

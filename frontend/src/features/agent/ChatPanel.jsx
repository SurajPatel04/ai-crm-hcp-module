import React, { useState, useEffect, useRef } from 'react';
import { useDispatch } from 'react-redux';
import api from '../../services/api';
import { setAiExtractedData } from '../interactions/interactionSlice';

const ChatPanel = ({ hcpId }) => {
  const [messages, setMessages] = useState([
    { role: 'ai', content: 'Hi! I can help you log an interaction. Just tell me what happened.' }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [threadId, setThreadId] = useState(null);
  const [currentInteractionId, setCurrentInteractionId] = useState(null);
  const messagesEndRef = useRef(null);
  const dispatch = useDispatch();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = input.trim();
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setInput('');
    setIsLoading(true);

    try {
      const payload = {
        message: userMessage,
        thread_id: threadId,  // null on first request, reused after that
        current_interaction_id: currentInteractionId,
      };

      const response = await api.post('/chat/', payload);

      const { response: aiReply, actions, thread_id } = response.data;

      if (thread_id) {
        setThreadId(thread_id);
      }

      setMessages(prev => [...prev, { role: 'ai', content: aiReply }]);

      if (actions && actions.length > 0) {
        const action = actions.find(a => a.action === 'log_interaction' || a.action === 'edit_interaction');
        if (action) {
          if (action.interaction_id) {
            setCurrentInteractionId(action.interaction_id);
          }
          if (action.form_data) {
            // Send extracted data to Redux so the form can auto-fill
            dispatch(setAiExtractedData(action.form_data));
          }
        }
      }

    } catch (error) {
      setMessages(prev => [...prev, { role: 'ai', content: 'Sorry, I encountered an error processing your request.' }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-messages">
        {messages.map((msg, idx) => (
          <div key={idx} className={`chat-bubble ${msg.role}`}>
            {msg.content}
          </div>
        ))}
        {isLoading && (
          <div className="chat-bubble ai" style={{ fontStyle: 'italic', opacity: 0.7 }}>
            Typing...
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <form className="chat-input-area" onSubmit={handleSend}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="e.g. Met Dr. Smith today, discussed Cardiolex..."
          disabled={isLoading}
        />
        <button type="submit" disabled={isLoading || !input.trim()}>
          Log
        </button>
      </form>
    </div>
  );
};

export default ChatPanel;

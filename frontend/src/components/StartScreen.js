import React, { useState } from 'react';
import './StartScreen.css';

function StartScreen({ onStartInterview }) {
  const [topic, setTopic] = useState('');
  const [numQuestions, setNumQuestions] = useState(4);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!topic.trim()) {
      setError('Please enter a topic for the interview');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      await onStartInterview(topic.trim(), numQuestions);
    } catch (err) {
      setError(err.message || 'Failed to start interview. Please try again.');
      setIsLoading(false);
    }
  };

  return (
    <div className="start-screen">
      <div className="start-screen-content">
        <h1>AI Interviewer</h1>
        <p className="subtitle">Practice answering questions on any topic</p>
        
        <form onSubmit={handleSubmit} className="start-form">
          <div className="form-group">
            <label htmlFor="topic">Interview Topic</label>
            <input
              type="text"
              id="topic"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="e.g., AI in the workplace, Your career goals, Python programming..."
              disabled={isLoading}
              autoFocus
            />
          </div>

          <div className="form-group">
            <label htmlFor="numQuestions">Number of Questions: {numQuestions}</label>
            <input
              type="range"
              id="numQuestions"
              min="3"
              max="5"
              value={numQuestions}
              onChange={(e) => setNumQuestions(parseInt(e.target.value))}
              disabled={isLoading}
            />
            <div className="range-labels">
              <span>3</span>
              <span>5</span>
            </div>
          </div>

          {error && <div className="error-message">{error}</div>}

          <button 
            type="submit" 
            className="start-button"
            disabled={isLoading}
          >
            {isLoading ? 'Starting Interview...' : 'Start Interview'}
          </button>
        </form>
      </div>
    </div>
  );
}

export default StartScreen;

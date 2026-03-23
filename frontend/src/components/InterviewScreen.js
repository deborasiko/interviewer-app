import React, { useState, useRef, useEffect } from 'react';
import './InterviewScreen.css';

function InterviewScreen({ 
  interviewId, 
  currentQuestion, 
  questionNumber, 
  totalQuestions, 
  topic,
  qaPairs,
  onSubmitAnswer, 
  onSkip, 
  onQuit 
}) {
  const [answer, setAnswer] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const textareaRef = useRef(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.focus();
    }
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!answer.trim()) {
      setError('Please provide an answer or skip this question');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      await onSubmitAnswer(answer.trim());
      setAnswer('');
      setIsLoading(false);
    } catch (err) {
      setError(err.message || 'Failed to submit answer. Please try again.');
      setIsLoading(false);
    }
  };

  const handleSkip = async () => {
    setIsLoading(true);
    setError('');
    
    try {
      await onSkip();
      setAnswer('');
      setIsLoading(false);
    } catch (err) {
      setError(err.message || 'Failed to skip. Please try again.');
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && e.ctrlKey) {
      handleSubmit(e);
    }
  };

  const progress = (questionNumber / totalQuestions) * 100;

  return (
    <div className="interview-screen">
      <div className="interview-header">
        <div className="topic-display">
          <span className="topic-label">Topic:</span>
          <span className="topic-value">{topic}</span>
        </div>
        <div className="question-counter">
          Question {questionNumber} of {totalQuestions}
        </div>
      </div>

      <div className="progress-bar">
        <div className="progress-fill" style={{ width: `${progress}%` }}></div>
      </div>

      {qaPairs.length > 0 && (
        <div className="qa-history">
          <h3>Previous Questions:</h3>
          <div className="qa-pairs">
            {qaPairs.map((pair, index) => (
              <div key={index} className="qa-pair">
                <div className="q-item">
                  <strong>Q{index + 1}:</strong> {pair.question}
                </div>
                <div className="a-item">
                  <strong>A{index + 1}:</strong> {pair.answer || '(skipped)'}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="question-card">
        <div className="question-number">Question {questionNumber}</div>
        <h2 className="question-text">{currentQuestion}</h2>
      </div>

      <form onSubmit={handleSubmit} className="answer-form">
        <div className="form-group">
          <label htmlFor="answer">Your Answer</label>
          <textarea
            ref={textareaRef}
            id="answer"
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type your answer here... (Press Ctrl+Enter to submit)"
            disabled={isLoading}
            rows={6}
          />
        </div>

        {error && <div className="error-message">{error}</div>}

        <div className="button-group">
          <button 
            type="button" 
            className="quit-button"
            onClick={onQuit}
            disabled={isLoading}
          >
            Quit Interview
          </button>
          <button 
            type="button" 
            className="skip-button"
            onClick={handleSkip}
            disabled={isLoading}
          >
            Skip Question
          </button>
          <button 
            type="submit" 
            className="submit-button"
            disabled={isLoading || !answer.trim()}
          >
            {isLoading ? 'Submitting...' : 'Submit Answer'}
          </button>
        </div>
      </form>
    </div>
  );
}

export default InterviewScreen;

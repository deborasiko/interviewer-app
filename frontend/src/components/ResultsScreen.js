import React, { useState } from 'react';
import './ResultsScreen.css';

function ResultsScreen({ 
  interviewId, 
  topic, 
  summary, 
  analysis, 
  qaPairs,
  savePath,
  onNewInterview 
}) {
  const [activeTab, setActiveTab] = useState('summary');

  const renderSentiment = () => {
    if (!analysis || !analysis.sentiment) {
      return <p className="no-data">No sentiment analysis available</p>;
    }

    const { compound, pos, neu, neg } = analysis.sentiment;
    
    return (
      <div className="sentiment-analysis">
        <div className="sentiment-score">
          <div className="score-label">Overall Score</div>
          <div className={`score-value ${compound >= 0 ? 'positive' : 'negative'}`}>
            {compound.toFixed(2)}
          </div>
          <div className="score-description">
            {compound >= 0.05 ? 'Positive' : compound <= -0.05 ? 'Negative' : 'Neutral'}
          </div>
        </div>
        <div className="sentiment-breakdown">
          <div className="breakdown-item">
            <span className="breakdown-label">Positive</span>
            <div className="breakdown-bar">
              <div className="breakdown-fill positive" style={{ width: `${pos * 100}%` }}></div>
            </div>
            <span className="breakdown-value">{(pos * 100).toFixed(1)}%</span>
          </div>
          <div className="breakdown-item">
            <span className="breakdown-label">Neutral</span>
            <div className="breakdown-bar">
              <div className="breakdown-fill neutral" style={{ width: `${neu * 100}%` }}></div>
            </div>
            <span className="breakdown-value">{(neu * 100).toFixed(1)}%</span>
          </div>
          <div className="breakdown-item">
            <span className="breakdown-label">Negative</span>
            <div className="breakdown-bar">
              <div className="breakdown-fill negative" style={{ width: `${neg * 100}%` }}></div>
            </div>
            <span className="breakdown-value">{(neg * 100).toFixed(1)}%</span>
          </div>
        </div>
      </div>
    );
  };

  const renderKeywords = () => {
    if (!analysis || !analysis.keywords) {
      return <p className="no-data">No keywords available</p>;
    }

    const { keywords, bigrams } = analysis.keywords;

    return (
      <div className="keywords-analysis">
        <div className="keywords-section">
          <h4>Top Keywords</h4>
          <div className="keyword-tags">
            {keywords.map((keyword, index) => (
              <span key={index} className="keyword-tag">
                {keyword}
              </span>
            ))}
          </div>
        </div>
        {bigrams && bigrams.length > 0 && (
          <div className="keywords-section">
            <h4>Key Phrases</h4>
            <div className="keyword-tags">
              {bigrams.map((bigram, index) => (
                <span key={index} className="keyword-tag phrase">
                  {bigram}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderTranscript = () => {
    return (
      <div className="transcript-view">
        {qaPairs.map((pair, index) => (
          <div key={index} className="transcript-item">
            <div className="transcript-q">
              <strong>Q{index + 1}:</strong> {pair.question}
            </div>
            <div className="transcript-a">
              <strong>A{index + 1}:</strong> {pair.answer || '(skipped)'}
            </div>
          </div>
        ))}
      </div>
    );
  };

  const renderSummary = () => {
    if (!summary) {
      return <p className="no-data">No summary available</p>;
    }

    return (
      <div className="summary-content">
        {Object.entries(summary).map(([key, value]) => (
          <div key={key} className="summary-item">
            <h4>{key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</h4>
            {typeof value === 'string' ? (
              <p>{value}</p>
            ) : Array.isArray(value) ? (
              <ul>
                {value.map((item, index) => (
                  <li key={index}>{item}</li>
                ))}
              </ul>
            ) : (
              <pre>{JSON.stringify(value, null, 2)}</pre>
            )}
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="results-screen">
      <div className="results-header">
        <h1>Interview Complete! 🎉</h1>
        <p className="topic-result">Topic: {topic}</p>
        {savePath && (
          <p className="save-path">Saved to: <code>{savePath}</code></p>
        )}
      </div>

      <div className="tabs">
        <button 
          className={`tab ${activeTab === 'summary' ? 'active' : ''}`}
          onClick={() => setActiveTab('summary')}
        >
          Summary
        </button>
        <button 
          className={`tab ${activeTab === 'analysis' ? 'active' : ''}`}
          onClick={() => setActiveTab('analysis')}
        >
          Analysis
        </button>
        <button 
          className={`tab ${activeTab === 'transcript' ? 'active' : ''}`}
          onClick={() => setActiveTab('transcript')}
        >
          Transcript
        </button>
      </div>

      <div className="tab-content">
        {activeTab === 'summary' && renderSummary()}
        {activeTab === 'analysis' && (
          <div className="analysis-content">
            <div className="analysis-section">
              <h3>Sentiment Analysis</h3>
              {renderSentiment()}
            </div>
            <div className="analysis-section">
              <h3>Keyword Extraction</h3>
              {renderKeywords()}
            </div>
          </div>
        )}
        {activeTab === 'transcript' && renderTranscript()}
      </div>

      <div className="results-footer">
        <button className="new-interview-button" onClick={onNewInterview}>
          Start New Interview
        </button>
      </div>
    </div>
  );
}

export default ResultsScreen;

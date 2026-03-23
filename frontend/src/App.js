import React, { useState } from 'react';
import StartScreen from './components/StartScreen';
import InterviewScreen from './components/InterviewScreen';
import ResultsScreen from './components/ResultsScreen';
import './App.css';

const API_BASE_URL = 'http://localhost:8000';

function App() {
  const [screen, setScreen] = useState('start'); // 'start', 'interview', 'results'
  const [interviewId, setInterviewId] = useState(null);
  const [currentQuestion, setCurrentQuestion] = useState('');
  const [questionNumber, setQuestionNumber] = useState(0);
  const [totalQuestions, setTotalQuestions] = useState(4);
  const [topic, setTopic] = useState('');
  const [qaPairs, setQaPairs] = useState([]);
  const [summary, setSummary] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [savePath, setSavePath] = useState(null);

  const startInterview = async (topic, numQuestions) => {
    try {
      const response = await fetch(`${API_BASE_URL}/interview/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          topic: topic,
          num_questions: numQuestions
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to start interview');
      }

      const data = await response.json();
      
      setInterviewId(data.interview_id);
      setCurrentQuestion(data.question);
      setQuestionNumber(1);
      setTotalQuestions(numQuestions);
      setTopic(topic);
      setQaPairs([]);
      setSummary(null);
      setAnalysis(null);
      setSavePath(null);
      setScreen('interview');

    } catch (error) {
      console.error('Error starting interview:', error);
      throw error;
    }
  };

  const submitAnswer = async (answer) => {
    try {
      const response = await fetch(`${API_BASE_URL}/interview/answer`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          interview_id: interviewId,
          question: currentQuestion,
          answer: answer
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to submit answer');
      }

      const data = await response.json();

      // Add current Q&A pair to history
      setQaPairs(prev => [...prev, { question: currentQuestion, answer: answer }]);

      if (data.completed) {
        // Interview is complete
        setSummary(data.summary);
        setAnalysis(data.analysis);
        setScreen('results');
        
        // Try to get the save path - don't fail if this doesn't work
        try {
          const interviewResponse = await fetch(`${API_BASE_URL}/interview/${interviewId}`);
          if (interviewResponse.ok) {
            const interviewData = await interviewResponse.json();
            // The save path would typically come from the backend
            setSavePath(interviewData.metadata?.file_path || `interviews/${interviewId}.json`);
          }
        } catch (e) {
          // Set a default save path if fetch fails
          setSavePath(`interviews/${interviewId}.json`);
          console.log('Could not fetch save path, using default');
        }
      } else {
        // Continue to next question
        setCurrentQuestion(data.next_question);
        setQuestionNumber(prev => prev + 1);
      }

    } catch (error) {
      console.error('Error submitting answer:', error);
      throw error;
    }
  };

  const skipQuestion = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/interview/answer`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          interview_id: interviewId,
          question: currentQuestion,
          answer: '' // Empty answer indicates skip
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to skip question');
      }

      const data = await response.json();

      // Add skipped Q&A pair to history
      setQaPairs(prev => [...prev, { question: currentQuestion, answer: '' }]);

      if (data.completed) {
        setSummary(data.summary);
        setAnalysis(data.analysis);
        setScreen('results');
      } else {
        setCurrentQuestion(data.next_question);
        setQuestionNumber(prev => prev + 1);
      }

    } catch (error) {
      console.error('Error skipping question:', error);
      throw error;
    }
  };

  const quitInterview = () => {
    if (window.confirm('Are you sure you want to quit the interview? Your progress will be lost.')) {
      setScreen('start');
      resetInterviewState();
    }
  };

  const resetInterviewState = () => {
    setInterviewId(null);
    setCurrentQuestion('');
    setQuestionNumber(0);
    setTotalQuestions(4);
    setTopic('');
    setQaPairs([]);
    setSummary(null);
    setAnalysis(null);
    setSavePath(null);
  };

  const startNewInterview = () => {
    setScreen('start');
    resetInterviewState();
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>AI Interviewer</h1>
      </header>
      
      <main className="App-main">
        {screen === 'start' && (
          <StartScreen onStartInterview={startInterview} />
        )}

        {screen === 'interview' && (
          <InterviewScreen
            interviewId={interviewId}
            currentQuestion={currentQuestion}
            questionNumber={questionNumber}
            totalQuestions={totalQuestions}
            topic={topic}
            qaPairs={qaPairs}
            onSubmitAnswer={submitAnswer}
            onSkip={skipQuestion}
            onQuit={quitInterview}
          />
        )}

        {screen === 'results' && (
          <ResultsScreen
            interviewId={interviewId}
            topic={topic}
            summary={summary}
            analysis={analysis}
            qaPairs={qaPairs}
            savePath={savePath}
            onNewInterview={startNewInterview}
          />
        )}
      </main>
    </div>
  );
}

export default App;

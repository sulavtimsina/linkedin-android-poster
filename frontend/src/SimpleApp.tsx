import React, { useState } from 'react';
import axios from 'axios';

function SimpleApp() {
  const [redditPost, setRedditPost] = useState<any>(null);
  const [summary, setSummary] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');

  const testReddit = async () => {
    setLoading(true);
    setError('');
    setRedditPost(null);
    setSummary('');
    
    try {
      const response = await axios.post('http://127.0.0.1:8000/api/test-reddit');
      setRedditPost(response.data);
    } catch (err: any) {
      setError(`Reddit Error: ${err.response?.data?.detail || err.message}`);
    }
    setLoading(false);
  };

  const testOpenAI = async () => {
    if (!redditPost) {
      setError('Please fetch a Reddit post first!');
      return;
    }
    
    setLoading(true);
    setError('');
    setSummary('');
    
    try {
      const response = await axios.post('http://127.0.0.1:8000/api/test-openai', {
        text: `Title: ${redditPost.title}\n\nContent: ${redditPost.content || 'No content'}\n\nURL: ${redditPost.url}`
      });
      setSummary(response.data.summary);
    } catch (err: any) {
      setError(`OpenAI Error: ${err.response?.data?.detail || err.message}`);
    }
    setLoading(false);
  };

  const testFullPipeline = async () => {
    await testReddit();
    // Wait a bit for state to update
    setTimeout(() => {
      if (redditPost) {
        testOpenAI();
      }
    }, 1000);
  };

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif', maxWidth: '1200px', margin: '0 auto' }}>
      <h1 style={{ color: '#333' }}>🚀 LinkedIn Android Poster - API Test Dashboard</h1>
      
      <div style={{ marginTop: '20px', padding: '20px', backgroundColor: '#f3f4f6', borderRadius: '10px' }}>
        <h2>Quick API Tests</h2>
        
        <div style={{ display: 'flex', gap: '10px', marginTop: '15px' }}>
          <button 
            style={{ 
              backgroundColor: '#FF5700', 
              color: 'white', 
              padding: '10px 20px', 
              border: 'none', 
              borderRadius: '5px',
              cursor: loading ? 'not-allowed' : 'pointer',
              opacity: loading ? 0.5 : 1
            }}
            onClick={testReddit}
            disabled={loading}
          >
            🔴 Test Reddit API
          </button>
          
          <button 
            style={{ 
              backgroundColor: '#10b981', 
              color: 'white', 
              padding: '10px 20px', 
              border: 'none', 
              borderRadius: '5px',
              cursor: loading || !redditPost ? 'not-allowed' : 'pointer',
              opacity: loading || !redditPost ? 0.5 : 1
            }}
            onClick={testOpenAI}
            disabled={loading || !redditPost}
          >
            🤖 Test OpenAI Summarize
          </button>
          
          <button 
            style={{ 
              backgroundColor: '#a855f7', 
              color: 'white', 
              padding: '10px 20px', 
              border: 'none', 
              borderRadius: '5px',
              cursor: loading ? 'not-allowed' : 'pointer',
              opacity: loading ? 0.5 : 1
            }}
            onClick={testFullPipeline}
            disabled={loading}
          >
            ⚡ Test Both (Full Pipeline)
          </button>
        </div>
        
        {loading && (
          <div style={{ marginTop: '20px', color: '#3b82f6' }}>
            Loading... Please wait...
          </div>
        )}
        
        {error && (
          <div style={{ marginTop: '20px', padding: '10px', backgroundColor: '#fee2e2', color: '#991b1b', borderRadius: '5px' }}>
            ❌ {error}
          </div>
        )}
      </div>

      {redditPost && (
        <div style={{ marginTop: '20px', padding: '20px', backgroundColor: '#fff', borderRadius: '10px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
          <h3 style={{ color: '#FF5700' }}>🔴 Reddit Post (from r/{redditPost.subreddit})</h3>
          <div style={{ marginTop: '10px' }}>
            <strong>Title:</strong> {redditPost.title}
          </div>
          <div style={{ marginTop: '10px' }}>
            <strong>Author:</strong> {redditPost.author}
          </div>
          <div style={{ marginTop: '10px' }}>
            <strong>Score:</strong> {redditPost.score} | <strong>Comments:</strong> {redditPost.comments}
          </div>
          {redditPost.content && (
            <div style={{ marginTop: '10px' }}>
              <strong>Content:</strong>
              <div style={{ marginTop: '5px', padding: '10px', backgroundColor: '#f9fafb', borderRadius: '5px' }}>
                {redditPost.content.substring(0, 500)}
                {redditPost.content.length > 500 && '...'}
              </div>
            </div>
          )}
          <div style={{ marginTop: '10px' }}>
            <a href={redditPost.url} target="_blank" rel="noopener noreferrer" style={{ color: '#3b82f6' }}>
              🔗 View on Reddit
            </a>
          </div>
        </div>
      )}

      {summary && (
        <div style={{ marginTop: '20px', padding: '20px', backgroundColor: '#fff', borderRadius: '10px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
          <h3 style={{ color: '#10b981' }}>🤖 OpenAI Summary</h3>
          <div style={{ marginTop: '10px', padding: '15px', backgroundColor: '#d1fae5', borderRadius: '5px' }}>
            {summary}
          </div>
        </div>
      )}

      <div style={{ marginTop: '30px', padding: '20px', backgroundColor: '#f9fafb', borderRadius: '10px' }}>
        <h3>📊 System Status</h3>
        <div style={{ marginTop: '10px' }}>
          <div>✅ Frontend: Running on http://localhost:5173</div>
          <div>✅ Backend: Running on http://127.0.0.1:8000</div>
          <div>📖 API Docs: <a href="http://127.0.0.1:8000/docs" target="_blank" style={{ color: '#3b82f6' }}>View Swagger UI</a></div>
        </div>
        
        <div style={{ marginTop: '15px' }}>
          <h4>How to use:</h4>
          <ol style={{ marginLeft: '20px' }}>
            <li>Click "Test Reddit API" to fetch a top post from Android subreddits</li>
            <li>Once fetched, click "Test OpenAI Summarize" to generate a summary</li>
            <li>Or click "Test Both" to run the full pipeline automatically</li>
          </ol>
        </div>
      </div>
    </div>
  );
}

export default SimpleApp;
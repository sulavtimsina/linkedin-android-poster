import React, { useState, useEffect } from 'react';
import { apiService } from './api';
import { Topic, LinkedInPost, AppStatus, AppSettings } from './types';
import { 
  Play, Pause, Download, Send, Settings, Eye, 
  Copy, Trash2, Edit3, RefreshCw, Plus,
  CheckCircle, Clock, AlertCircle, XCircle
} from 'lucide-react';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [status, setStatus] = useState<AppStatus | null>(null);
  const [settings, setSettings] = useState<AppSettings | null>(null);
  const [topics, setTopics] = useState<Topic[]>([]);
  const [posts, setPosts] = useState<LinkedInPost[]>([]);
  const [selectedTopics, setSelectedTopics] = useState<number[]>([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [statusData, settingsData, topicsData, postsData] = await Promise.all([
        apiService.getStatus(),
        apiService.getSettings(),
        apiService.getTopics(50),
        apiService.getPosts(20)
      ]);
      
      setStatus(statusData);
      setSettings(settingsData);
      setTopics(topicsData);
      setPosts(postsData);
    } catch (error) {
      console.error('Error loading data:', error);
      setMessage('Error loading data');
    }
  };

  const handleFetchNow = async () => {
    setLoading(true);
    try {
      await apiService.fetchNow();
      setMessage('Fetch started');
      setTimeout(loadData, 2000); // Reload data after 2 seconds
    } catch (error) {
      setMessage('Error starting fetch');
    }
    setLoading(false);
  };

  const handleGenerateNow = async () => {
    setLoading(true);
    try {
      await apiService.generateNow();
      setMessage('Generation started');
      setTimeout(loadData, 2000);
    } catch (error) {
      setMessage('Error starting generation');
    }
    setLoading(false);
  };

  const handleGeneratePost = async () => {
    if (selectedTopics.length === 0) {
      setMessage('Select topics first');
      return;
    }
    
    setLoading(true);
    try {
      await apiService.generatePost(selectedTopics);
      setMessage('Post generated');
      setSelectedTopics([]);
      loadData();
    } catch (error) {
      setMessage('Error generating post');
    }
    setLoading(false);
  };

  const handlePublishPost = async (postId: number) => {
    setLoading(true);
    try {
      await apiService.publishPost(postId);
      setMessage('Post published');
      loadData();
    } catch (error) {
      setMessage('Error publishing post');
    }
    setLoading(false);
  };

  const handleCopyPost = (content: string) => {
    navigator.clipboard.writeText(content);
    setMessage('Post copied to clipboard');
  };

  const handleDeletePost = async (postId: number) => {
    if (!confirm('Delete this post?')) return;
    
    try {
      await apiService.deletePost(postId);
      setMessage('Post deleted');
      loadData();
    } catch (error) {
      setMessage('Error deleting post');
    }
  };

  const toggleScheduler = async () => {
    try {
      if (status?.scheduler_running) {
        await apiService.pauseScheduler();
      } else {
        await apiService.resumeScheduler();
      }
      loadData();
    } catch (error) {
      setMessage('Error toggling scheduler');
    }
  };

  const formatInterval = (seconds: string): string => {
    const s = parseInt(seconds);
    if (s >= 3600) return `${Math.floor(s / 3600)}h`;
    if (s >= 60) return `${Math.floor(s / 60)}m`;
    return `${s}s`;
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'posted': return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'queued': return <Clock className="w-4 h-4 text-blue-500" />;
      case 'failed': return <XCircle className="w-4 h-4 text-red-500" />;
      default: return <AlertCircle className="w-4 h-4 text-yellow-500" />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <h1 className="text-3xl font-bold text-gray-900">LinkedIn Android Poster</h1>
            <div className="flex items-center space-x-4">
              {status && (
                <div className="flex items-center space-x-2">
                  <div className={`w-3 h-3 rounded-full ${status.scheduler_running ? 'bg-green-500' : 'bg-red-500'}`}></div>
                  <span className="text-sm text-gray-600">
                    {status.scheduler_running ? 'Running' : 'Paused'}
                  </span>
                </div>
              )}
              <button
                onClick={toggleScheduler}
                className="bg-blue-500 text-white px-4 py-2 rounded-lg flex items-center space-x-2"
              >
                {status?.scheduler_running ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                <span>{status?.scheduler_running ? 'Pause' : 'Resume'}</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      <nav className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            {['dashboard', 'topics', 'posts', 'settings'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`py-4 px-1 border-b-2 font-medium text-sm capitalize ${
                  activeTab === tab
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                {tab}
              </button>
            ))}
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {message && (
          <div className="mb-4 p-4 bg-blue-100 border border-blue-400 text-blue-700 rounded">
            {message}
            <button 
              onClick={() => setMessage('')}
              className="float-right text-blue-700 font-bold"
            >
              ×
            </button>
          </div>
        )}

        {activeTab === 'dashboard' && (
          <div className="space-y-6">
            {/* Status Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <CheckCircle className={`h-6 w-6 ${status?.linkedin_configured ? 'text-green-400' : 'text-gray-400'}`} />
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">LinkedIn</dt>
                        <dd className="text-lg font-medium text-gray-900">
                          {status?.linkedin_configured ? 'Connected' : 'Not Connected'}
                        </dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <CheckCircle className={`h-6 w-6 ${status?.reddit_configured ? 'text-green-400' : 'text-gray-400'}`} />
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">Reddit</dt>
                        <dd className="text-lg font-medium text-gray-900">
                          {status?.reddit_configured ? 'Connected' : 'Not Connected'}
                        </dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <CheckCircle className={`h-6 w-6 ${status?.x_configured ? 'text-green-400' : 'text-gray-400'}`} />
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">X (Twitter)</dt>
                        <dd className="text-lg font-medium text-gray-900">
                          {status?.x_configured ? 'Connected' : 'Not Connected'}
                        </dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <CheckCircle className={`h-6 w-6 ${status?.openai_configured ? 'text-green-400' : 'text-gray-400'}`} />
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">OpenAI</dt>
                        <dd className="text-lg font-medium text-gray-900">
                          {status?.openai_configured ? 'Connected' : 'Not Connected'}
                        </dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="bg-white shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">Quick Actions</h3>
                <div className="flex flex-wrap gap-4">
                  <button
                    onClick={handleFetchNow}
                    disabled={loading}
                    className="bg-green-500 text-white px-4 py-2 rounded-lg flex items-center space-x-2 disabled:opacity-50"
                  >
                    <Download className="w-4 h-4" />
                    <span>Fetch Now</span>
                  </button>
                  <button
                    onClick={handleGenerateNow}
                    disabled={loading}
                    className="bg-purple-500 text-white px-4 py-2 rounded-lg flex items-center space-x-2 disabled:opacity-50"
                  >
                    <Plus className="w-4 h-4" />
                    <span>Generate Now</span>
                  </button>
                  <button
                    onClick={loadData}
                    disabled={loading}
                    className="bg-blue-500 text-white px-4 py-2 rounded-lg flex items-center space-x-2 disabled:opacity-50"
                  >
                    <RefreshCw className="w-4 h-4" />
                    <span>Refresh</span>
                  </button>
                </div>
              </div>
            </div>

            {/* Recent Activity */}
            <div className="bg-white shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">Recent Posts</h3>
                <div className="space-y-3">
                  {posts.slice(0, 5).map((post) => (
                    <div key={post.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div className="flex items-center space-x-3">
                        {getStatusIcon(post.status)}
                        <div>
                          <p className="text-sm font-medium text-gray-900">
                            {post.content.substring(0, 60)}...
                          </p>
                          <p className="text-sm text-gray-500">
                            {new Date(post.created_at).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                      <span className={`px-2 py-1 text-xs font-semibold rounded-full capitalize ${
                        post.status === 'posted' ? 'bg-green-100 text-green-800' :
                        post.status === 'failed' ? 'bg-red-100 text-red-800' :
                        'bg-blue-100 text-blue-800'
                      }`}>
                        {post.status}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'topics' && (
          <div className="bg-white shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg leading-6 font-medium text-gray-900">Trending Topics</h3>
                <div className="flex items-center space-x-4">
                  <span className="text-sm text-gray-500">
                    {selectedTopics.length} selected
                  </span>
                  <button
                    onClick={handleGeneratePost}
                    disabled={selectedTopics.length === 0 || loading}
                    className="bg-blue-500 text-white px-4 py-2 rounded-lg disabled:opacity-50"
                  >
                    Generate Post
                  </button>
                </div>
              </div>
              
              <div className="space-y-3">
                {topics.map((topic) => (
                  <div 
                    key={topic.id} 
                    className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                      selectedTopics.includes(topic.id) 
                        ? 'border-blue-500 bg-blue-50' 
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                    onClick={() => {
                      if (selectedTopics.includes(topic.id)) {
                        setSelectedTopics(prev => prev.filter(id => id !== topic.id));
                      } else {
                        setSelectedTopics(prev => [...prev, topic.id]);
                      }
                    }}
                  >
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <h4 className="font-medium text-gray-900 mb-2">{topic.title}</h4>
                        <div className="flex items-center space-x-4 text-sm text-gray-500">
                          <span className="bg-gray-100 px-2 py-1 rounded capitalize">{topic.source}</span>
                          <span>Score: {topic.score}</span>
                          <span>Engagement: {topic.engagement}</span>
                          {topic.rank_score && <span>Rank: {topic.rank_score.toFixed(2)}</span>}
                        </div>
                      </div>
                      <a
                        href={topic.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-500 hover:text-blue-600"
                        onClick={(e) => e.stopPropagation()}
                      >
                        <Eye className="w-4 h-4" />
                      </a>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'posts' && (
          <div className="bg-white shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">LinkedIn Posts</h3>
              
              <div className="space-y-4">
                {posts.map((post) => (
                  <div key={post.id} className="border rounded-lg p-4">
                    <div className="flex justify-between items-start mb-3">
                      <div className="flex items-center space-x-2">
                        {getStatusIcon(post.status)}
                        <span className={`px-2 py-1 text-xs font-semibold rounded-full capitalize ${
                          post.status === 'posted' ? 'bg-green-100 text-green-800' :
                          post.status === 'failed' ? 'bg-red-100 text-red-800' :
                          'bg-blue-100 text-blue-800'
                        }`}>
                          {post.status}
                        </span>
                        <span className="text-sm text-gray-500">
                          {new Date(post.created_at).toLocaleString()}
                        </span>
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        <button
                          onClick={() => handleCopyPost(post.content)}
                          className="text-gray-500 hover:text-gray-700"
                          title="Copy to clipboard"
                        >
                          <Copy className="w-4 h-4" />
                        </button>
                        
                        {status?.linkedin_configured && post.status === 'queued' && (
                          <button
                            onClick={() => handlePublishPost(post.id)}
                            disabled={loading}
                            className="text-blue-500 hover:text-blue-700 disabled:opacity-50"
                            title="Publish to LinkedIn"
                          >
                            <Send className="w-4 h-4" />
                          </button>
                        )}
                        
                        {post.status !== 'posted' && (
                          <button
                            onClick={() => handleDeletePost(post.id)}
                            className="text-red-500 hover:text-red-700"
                            title="Delete post"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        )}
                      </div>
                    </div>
                    
                    <div className="bg-gray-50 rounded p-3 mb-3">
                      <pre className="whitespace-pre-wrap text-sm text-gray-800 font-sans">
                        {post.content}
                      </pre>
                    </div>
                    
                    <div className="text-xs text-gray-500">
                      Character count: {post.content.length}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'settings' && (
          <div className="bg-white shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">Settings</h3>
              
              {settings && (
                <div className="space-y-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Fetch Interval: {formatInterval(settings.fetch_interval)}
                    </label>
                    <input
                      type="range"
                      min="60"
                      max="86400"
                      value={settings.fetch_interval}
                      onChange={(e) => setSettings(prev => prev ? {...prev, fetch_interval: e.target.value} : null)}
                      className="w-full"
                    />
                    <div className="flex justify-between text-xs text-gray-500 mt-1">
                      <span>1m</span>
                      <span>24h</span>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Post Interval: {formatInterval(settings.post_interval)}
                    </label>
                    <input
                      type="range"
                      min="60"
                      max="43200"
                      value={settings.post_interval}
                      onChange={(e) => setSettings(prev => prev ? {...prev, post_interval: e.target.value} : null)}
                      className="w-full"
                    />
                    <div className="flex justify-between text-xs text-gray-500 mt-1">
                      <span>1m</span>
                      <span>12h</span>
                    </div>
                  </div>

                  <div>
                    <button
                      onClick={() => {
                        if (settings) {
                          apiService.updateSettings(settings);
                          setMessage('Settings saved');
                        }
                      }}
                      className="bg-blue-500 text-white px-4 py-2 rounded-lg"
                    >
                      Save Settings
                    </button>
                  </div>

                  <div className="border-t pt-6">
                    <h4 className="text-md font-medium text-gray-900 mb-3">API Configuration</h4>
                    <p className="text-sm text-gray-600 mb-4">
                      Configure API credentials in the .env file:
                    </p>
                    <div className="bg-gray-100 p-4 rounded text-xs font-mono">
                      REDDIT_CLIENT_ID=your_reddit_client_id<br/>
                      REDDIT_CLIENT_SECRET=your_reddit_client_secret<br/>
                      X_BEARER_TOKEN=your_x_bearer_token<br/>
                      LINKEDIN_ACCESS_TOKEN=your_linkedin_access_token<br/>
                      OPENAI_API_KEY=your_openai_api_key
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App

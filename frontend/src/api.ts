import axios from 'axios';
import { Topic, LinkedInPost, SystemLog, AppSettings, AppStatus } from './types';

const API_BASE = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const apiService = {
  // Status
  getStatus: (): Promise<AppStatus> =>
    api.get('/status').then(res => res.data),

  // Topics
  getTopics: (limit = 50, source?: string): Promise<Topic[]> =>
    api.get('/topics', { params: { limit, source } }).then(res => res.data),

  // Posts
  getPosts: (limit = 20, status?: string): Promise<LinkedInPost[]> =>
    api.get('/posts', { params: { limit, status } }).then(res => res.data),

  generatePost: (topicIds: number[]): Promise<any> =>
    api.post('/posts/generate', { topic_ids: topicIds }).then(res => res.data),

  publishPost: (postId: number): Promise<any> =>
    api.post(`/posts/${postId}/publish`).then(res => res.data),

  updatePost: (postId: number, content: string): Promise<any> =>
    api.put(`/posts/${postId}`, { content }).then(res => res.data),

  deletePost: (postId: number): Promise<any> =>
    api.delete(`/posts/${postId}`).then(res => res.data),

  // Settings
  getSettings: (): Promise<AppSettings> =>
    api.get('/settings').then(res => res.data),

  updateSettings: (settings: Partial<AppSettings>): Promise<any> =>
    api.put('/settings', settings).then(res => res.data),

  // Manual operations
  fetchNow: (): Promise<any> =>
    api.post('/fetch-now').then(res => res.data),

  generateNow: (): Promise<any> =>
    api.post('/generate-now').then(res => res.data),

  pauseScheduler: (): Promise<any> =>
    api.post('/scheduler/pause').then(res => res.data),

  resumeScheduler: (): Promise<any> =>
    api.post('/scheduler/resume').then(res => res.data),

  // Logs
  getLogs: (limit = 100, component?: string): Promise<SystemLog[]> =>
    api.get('/logs', { params: { limit, component } }).then(res => res.data),
};
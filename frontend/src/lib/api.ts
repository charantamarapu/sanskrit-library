import axios from 'axios';

// Use relative URL - will use same protocol as frontend
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 1800000, // 30 minutes
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.response.use(
  (response) => {
    console.log('API Response:', response);
    return response;
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

interface Grantha {
  id: number;
  title: string;
  file: string;
  commentaries: string[];
  uploaded_at: string;
}

interface Suggestion {
  id?: number;
  grantha: number | string;
  user_name: string;
  user_email: string;
  suggestion: string;
  status?: string;
}

export const granthaAPI = {
  list: () => api.get<Grantha[]>('/granthas/'),
  get: (id: number) => api.get<Grantha>(`/granthas/${id}/`),
  filter: (id: number, commentaries: string[]) => 
    api.post(`/granthas/${id}/filter/`, 
      { commentaries }, 
      { 
        responseType: 'blob',
        timeout: 1800000,
      }
    ),
  download: (id: number) => 
    api.get(`/granthas/${id}/download/`, 
      { 
        responseType: 'blob',
        timeout: 1800000,
      }
    ),
};

export const suggestionAPI = {
  create: (data: Suggestion) => api.post('/suggestions/', data),
};

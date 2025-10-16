import axios from 'axios';

const API_BASE = 'http://localhost:8000/api';

export const api = axios.create({
    baseURL: API_BASE,
    headers: {
        'Content-Type': 'application/json',
    },
    timeout: 10000, // 10 second timeout
});

// Add response interceptor for debugging
api.interceptors.response.use(
    response => {
        console.log('API Response:', response);
        return response;
    },
    error => {
        console.error('API Error:', error.response || error);
        return Promise.reject(error);
    }
);

// Grantha APIs
export const granthaAPI = {
    list: () => api.get('/granthas/'),
    get: (id: number) => api.get(`/granthas/${id}/`),
    upload: (formData: FormData) => {
        return api.post('/granthas/', formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
        });
    },
    delete: (id: number) => api.delete(`/granthas/${id}/`),
    update: (id: number, data: any) => api.patch(`/granthas/${id}/`, data),
    filter: (id: number, commentaries: string[]) =>
        api.post(`/granthas/${id}/filter/`, { commentaries }, { responseType: 'blob' }),
    download: (id: number) => api.get(`/granthas/${id}/download/`, { responseType: 'blob' }),
};

// Suggestion APIs
export const suggestionAPI = {
    list: () => api.get('/suggestions/'),
    create: (data: any) => api.post('/suggestions/', data),
};

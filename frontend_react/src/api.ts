import axios from 'axios';

// Types based on shared models
export interface User {
  username: string;
  password?: string;
  email?: string;
  full_name?: string;
  disabled?: boolean;
}

export interface Score {
  id?: number;
  title: string;
  composer: string;
  pdf_path?: string;
  number_of_play?: number;
  user_id?: number;
  difficulty?: string;
  difficulty_int?: number;
  year?: number;
  instrumentation?: string;
}

export interface Scores {
  scores: Score[];
}

export interface Response {
  response: string;
  score_id?: number;
}

export interface FullResponse {
  response: Response;
  message_history: any[];
}

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
const PUBLIC_API_URL = import.meta.env.VITE_PUBLIC_API_URL || "http://localhost:8000";

let _token: string | null = null;

export const setToken = (token: string | null) => {
  _token = token;
};

const getHeaders = () => {
  return _token ? { Authorization: `Bearer ${_token}` } : {};
};

export const api = {
  resetScoreCache: () => {
    // Client-side cache invalidation logic if needed
  },

  registerUser: async (newUser: User) => {
    const response = await axios.post(`${API_URL}/users`, newUser);
    return response.data;
  },

  loginUser: async (username: string, password: string) => {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);
    const response = await axios.post(`${API_URL}/token`, formData);
    return response.data;
  },

  getUser: async () => {
    const response = await axios.get(`${API_URL}/user`, { headers: getHeaders() });
    return response.data;
  },

  addScore: async (scoreData: Score) => {
    const response = await axios.post(`${API_URL}/scores`, scoreData, { headers: getHeaders() });
    return response.data;
  },

  deleteScore: async (scoreData: Score) => {
    if (scoreData.id) {
        await axios.delete(`${API_URL}/scores/${scoreData.id}`, { headers: getHeaders() });
    }
    if (scoreData.pdf_path) {
      await axios.delete(`${API_URL}/pdf/${scoreData.pdf_path}`, { headers: getHeaders() });
    }
  },

  addPlay: async (scoreId: number) => {
    const response = await axios.post(`${API_URL}/scores/${scoreId}/play`, {}, { headers: getHeaders() });
    return response.data;
  },

  getScores: async (): Promise<Scores> => {
    const response = await axios.get(`${API_URL}/scores`, { headers: getHeaders() });
    return { scores: response.data };
  },

  runImslpAgent: async (question: string, messageHistory: any[]) => {
    const response = await axios.post(`${API_URL}/imslp_agent`, null, {
      params: { prompt: question, message_history: JSON.stringify(messageHistory) },
      headers: getHeaders()
    });
    return response.data as FullResponse;
  },

  runAgent: async (question: string, messageHistory: any[]) => {
    // In the python version, it gets scores first to pass as deps
    const scores = await api.getScores(); 
    const response = await axios.post(`${API_URL}/agent`, null, {
      params: {
        prompt: question,
        deps: JSON.stringify(scores), 
        message_history: JSON.stringify(messageHistory)
      },
      headers: getHeaders()
    });
    return response.data as FullResponse;
  },

  isAdmin: async () => {
    const response = await axios.get(`${API_URL}/is_admin`, { headers: getHeaders() });
    return response.data;
  },

  uploadPdf: async (file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    const response = await axios.post(`${API_URL}/pdf`, formData, {
      headers: { ...getHeaders(), "Content-Type": "multipart/form-data" }
    });
    return response.data;
  },

  getPdfUrl: (fileId: string) => {
    const url = `${PUBLIC_API_URL}/pdf/${fileId}`;
    const viewerUrl = `${PUBLIC_API_URL}/pdfjs/web/viewer.html`;
    return `${viewerUrl}?file=${url}`;
  }
};

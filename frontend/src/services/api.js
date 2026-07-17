// src/services/api.js
// Centralized Axios client for OpsMind AI frontend.
// Base URL defaults to http://localhost:8000 (FastAPI backend).

import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 15000,
});

// Global response interceptor for graceful error logging
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API error:', error?.response?.data || error.message);
    return Promise.reject(error);
  }
);

// ── Inventory ─────────────────────────────────────────────────────────────────
export const fetchInventory = async () => {
  const res = await api.get('/inventory');
  return res.data;
};

// ── Forecasts ─────────────────────────────────────────────────────────────────
export const fetchForecasts = async (sku, horizon) => {
  const res = await api.get('/forecast', { params: { sku, horizon } });
  return res.data;
};

// ── Predictions (ML results) ──────────────────────────────────────────────────
export const fetchPredictions = async () => {
  const res = await api.get('/predict');
  return res.data;
};

// ── Decision Log ──────────────────────────────────────────────────────────────
export const fetchDecisions = async () => {
  const res = await api.get('/decision');
  return res.data;
};

// ── Ingestion trigger ─────────────────────────────────────────────────────────
export const triggerIngestion = async () => {
  const res = await api.post('/ingest');
  return res.data;
};

// ── Health check ──────────────────────────────────────────────────────────────
export const checkDatabaseHealth = async () => {
  const res = await api.get('/health');
  return res.data;
};

export default api;

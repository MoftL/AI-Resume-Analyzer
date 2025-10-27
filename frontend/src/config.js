/**
 * API Configuration
 */

export const API_BASE_URL = 'http://localhost:8000';

export const API_ENDPOINTS = {
  health: `${API_BASE_URL}/health`,
  analyze: `${API_BASE_URL}/analyze`,
  matchJobs: `${API_BASE_URL}/match-jobs`,
  searchJobs: `${API_BASE_URL}/jobs/search`,
};
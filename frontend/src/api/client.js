/**
 * Centralized API Client for Voice of Store Frontend.
 *
 * Connects to FastAPI backend with:
 * - Configurable VITE_API_BASE_URL (defaults to http://localhost:8000)
 * - Bearer JWT token authentication management
 * - Standardized error handling, query serialization, and timeouts
 */

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const API_PREFIX = '/api/v1';

class APIError extends Error {
  constructor(message, status, code, details) {
    super(message);
    this.name = 'APIError';
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

async function request(endpoint, options = {}) {
  const url = `${BASE_URL}${endpoint}`;
  const token = localStorage.getItem('vos_token');

  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), options.timeout || 12000);

  try {
    const response = await fetch(url, {
      ...options,
      headers,
      signal: controller.signal,
    });
    clearTimeout(timeoutId);

    // Handle 204 No Content
    if (response.status === 204) {
      return null;
    }

    const data = await response.json().catch(() => null);

    if (!response.ok) {
      const errorMsg = data?.error?.message || data?.detail || response.statusText || 'Request failed';
      const errorCode = data?.error?.code || 'HTTP_ERROR';
      const errorDetails = data?.error?.details || {};
      throw new APIError(errorMsg, response.status, errorCode, errorDetails);
    }

    return data;
  } catch (err) {
    clearTimeout(timeoutId);
    if (err.name === 'AbortError') {
      throw new APIError('Request timed out. Please check if the backend service is running.', 408, 'TIMEOUT', {});
    }
    if (err instanceof APIError) {
      throw err;
    }
    throw new APIError(err.message || 'Network connection failed', 0, 'NETWORK_ERROR', {});
  }
}

// Query string helper
function buildQuery(params = {}) {
  const filtered = Object.entries(params).filter(
    ([_, val]) => val !== undefined && val !== null && val !== '' && val !== 'All'
  );
  if (filtered.length === 0) return '';
  const searchParams = new URLSearchParams();
  for (const [key, val] of filtered) {
    searchParams.append(key, val);
  }
  return `?${searchParams.toString()}`;
}

export const api = {
  // 1. Health & Status
  health: {
	check: () => request('/health'),
	ready: () => request('/ready'),
  },

  // 2. Authentication
  auth: {
    login: async (email, password) => {
      const data = await request(`${API_PREFIX}/auth/login`, {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      });
      if (data?.access_token) {
        localStorage.setItem('vos_token', data.access_token);
      }
      return data;
    },
    getMe: () => request(`${API_PREFIX}/auth/me`),
    logout: () => {
      localStorage.removeItem('vos_token');
    },
  },

  // 3. User Notifications
  notifications: {
    list: (params = {}) => request(`${API_PREFIX}/notifications${buildQuery(params)}`),
    unreadCount: () => request(`${API_PREFIX}/notifications/unread-count`),
    markRead: (id) =>
      request(`${API_PREFIX}/notifications/${id}/read`, {
        method: 'PATCH',
      }),
    markAllRead: () =>
      request(`${API_PREFIX}/notifications/mark-all-read`, {
        method: 'POST',
      }),
  },

  // 4. Stores
  stores: {
    list: (params = {}) => request(`${API_PREFIX}/stores${buildQuery(params)}`),
    get: (id) => request(`${API_PREFIX}/stores/${id}`),
    create: (data) =>
      request(`${API_PREFIX}/stores`, {
        method: 'POST',
        body: JSON.stringify(data),
      }),
  },

  // 5. Feedback
  feedback: {
    list: (params = {}) => request(`${API_PREFIX}/feedback${buildQuery(params)}`),
    get: (id) => request(`${API_PREFIX}/feedback/${id}`),
    submit: (data) =>
      request(`${API_PREFIX}/feedback`, {
        method: 'POST',
        body: JSON.stringify(data),
      }),
  },

  // 6. Incidents
  incidents: {
    list: (params = {}) => request(`${API_PREFIX}/incidents${buildQuery(params)}`),
    get: (id) => request(`${API_PREFIX}/incidents/${id}`),
    getFeedback: (id) => request(`${API_PREFIX}/incidents/${id}/feedback`),
    updateStatus: (id, status, notes = '') =>
      request(`${API_PREFIX}/incidents/${id}/status`, {
        method: 'PATCH',
        body: JSON.stringify({ status, notes }),
      }),
  },

  // 7. Analytics
  analytics: {
    summary: (params = {}) => request(`${API_PREFIX}/analytics/summary${buildQuery(params)}`),
    comparisons: (params = {}) => request(`${API_PREFIX}/analytics/comparisons${buildQuery(params)}`),
  },

  // 8. Emerging Issue Alerts
  alerts: {
    list: (params = {}) => request(`${API_PREFIX}/alerts${buildQuery(params)}`),
    get: (id) => request(`${API_PREFIX}/alerts/${id}`),
    scan: (storeId) =>
      request(`${API_PREFIX}/alerts/scan${buildQuery({ store_id: storeId })}`, {
        method: 'POST',
      }),
    acknowledge: (id, notes = '') =>
      request(`${API_PREFIX}/alerts/${id}/acknowledge`, {
        method: 'POST',
        body: JSON.stringify({ notes }),
      }),
    resolve: (id, resolution_notes) =>
      request(`${API_PREFIX}/alerts/${id}/resolve`, {
        method: 'POST',
        body: JSON.stringify({ resolution_notes }),
      }),
  },

  // 9. Remediation Tasks (Action Queue)
  tasks: {
    list: (params = {}) => request(`${API_PREFIX}/tasks${buildQuery(params)}`),
    updateStatus: (id, status, notes = '') =>
      request(`${API_PREFIX}/tasks/${id}/status`, {
        method: 'PATCH',
        body: JSON.stringify({ status, notes }),
      }),
    create: (data) =>
      request(`${API_PREFIX}/tasks`, {
        method: 'POST',
        body: JSON.stringify(data),
      }),
  },

  // 10. Chronological Replay & Evaluation
  replay: {
    list: (params = {}) => request(`${API_PREFIX}/replay${buildQuery(params)}`),
    get: (id) => request(`${API_PREFIX}/replay/${id}`),
    create: (data) =>
      request(`${API_PREFIX}/replay`, {
        method: 'POST',
        body: JSON.stringify(data),
      }),
  },

  // 11. Regional Briefs (Weekly One-Page Briefs)
  regionalBriefs: {
    regions: () => request(`${API_PREFIX}/regional-briefs/regions`),
    list: (params = {}) => request(`${API_PREFIX}/regional-briefs${buildQuery(params)}`),
    getLatest: (region) => request(`${API_PREFIX}/regional-briefs/${encodeURIComponent(region)}/latest`),
    get: (id) => request(`${API_PREFIX}/regional-briefs/${id}`),
    getHtmlUrl: (id) => `${BASE_URL}${API_PREFIX}/regional-briefs/${id}/html`,
    generate: (data) =>
      request(`${API_PREFIX}/regional-briefs/generate`, {
        method: 'POST',
        body: JSON.stringify(data),
      }),
  },

  // 12. Owning Function Routing & Triage
  routing: {
    policy: () => request(`${API_PREFIX}/routing/policy`),
    assignments: (params = {}) => request(`${API_PREFIX}/routing/assignments${buildQuery(params)}`),
    reassign: (incidentId, data) =>
      request(`${API_PREFIX}/routing/incidents/${incidentId}/reassign`, {
        method: 'PATCH',
        body: JSON.stringify(data),
      }),
  },

  // 13. Escalation Precision Analytics & Review Queue
  precision: {
    metrics: (params = {}) => request(`${API_PREFIX}/analytics/escalation-precision${buildQuery(params)}`),
    queue: (params = {}) => request(`${API_PREFIX}/analytics/escalation-precision/queue${buildQuery(params)}`),
    review: (data) =>
      request(`${API_PREFIX}/analytics/escalation-precision/review`, {
        method: 'POST',
        body: JSON.stringify(data),
      }),
  },
};

export { BASE_URL, APIError };

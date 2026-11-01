const API_BASE = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, '');

async function fetchJson(endpoint, options = {}) {
  const res = await fetch(`${API_BASE}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Request failed with status ${res.status}`);
  }
  return res.json();
}

export const api = {
  // Dashboard & Health
  getHealth: () => fetchJson('/api/health'),
  getDashboardStats: () => fetchJson('/api/dashboard/stats'),

  // Tenders
  getTenders: () => fetchJson('/api/tenders'),
  getTender: (id) => fetchJson(`/api/tenders/${id}`),
  createTender: (data) => fetchJson('/api/tenders', { method: 'POST', body: JSON.stringify(data) }),
  deleteTender: (id) => fetchJson(`/api/tenders/${id}`, { method: 'DELETE' }),

  // Documents
  getTenderDocuments: (tenderId) => fetchJson(`/api/tenders/${tenderId}/documents`),
  uploadDocument: async (tenderId, formData) => {
    const res = await fetch(`${API_BASE}/api/tenders/${tenderId}/documents`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) throw new Error('File upload failed');
    return res.json();
  },
  deleteDocument: (id) => fetchJson(`/api/documents/${id}`, { method: 'DELETE' }),

  // Requirements & Compliance
  getRequirements: (tenderId) => fetchJson(`/api/tenders/${tenderId}/requirements`),
  updateRequirement: (id, data) => fetchJson(`/api/requirements/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
  getComplianceMatrix: (tenderId) => fetchJson(`/api/tenders/${tenderId}/compliance`),
  updateCompliance: (id, data) => fetchJson(`/api/compliance/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),

  // Risks & Readiness
  getRisks: (tenderId) => fetchJson(`/api/tenders/${tenderId}/risks`),
  updateRisk: (id, data) => fetchJson(`/api/risks/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
  getReadiness: (tenderId) => fetchJson(`/api/tenders/${tenderId}/readiness`),

  // Proposal Studio
  getProposals: (tenderId) => fetchJson(`/api/tenders/${tenderId}/proposals`),
  generateProposal: (tenderId, data) => fetchJson(`/api/tenders/${tenderId}/proposals/generate`, { method: 'POST', body: JSON.stringify(data) }),
  updateProposal: (id, data) => fetchJson(`/api/proposals/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),

  // Company Profile & Vault
  getCompany: () => fetchJson('/api/company'),
  updateCompany: (data) => fetchJson('/api/company', { method: 'PUT', body: JSON.stringify(data) }),
  getEvidenceVault: () => fetchJson('/api/company/evidence'),
  addEvidence: (params) => {
    const query = new URLSearchParams(params).toString();
    return fetchJson(`/api/company/evidence?${query}`, { method: 'POST' });
  },
  deleteEvidence: (id) => fetchJson(`/api/company/evidence/${id}`, { method: 'DELETE' }),

  // Voice & Q&A
  askVoiceQuery: (data) => fetchJson('/api/voice/ask', { method: 'POST', body: JSON.stringify(data) }),
};

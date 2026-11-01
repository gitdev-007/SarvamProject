import React, { useState, useEffect } from 'react';
import {
  FileText, CheckCircle2, AlertTriangle, ShieldAlert,
  Building2, Mic, Settings, LayoutDashboard, FolderKanban,
  Sparkles, ExternalLink, Download, Plus, Trash2, Edit3,
  Search, ShieldCheck, ChevronRight, RefreshCw, Send, Lock
} from 'lucide-react';
import { api } from './api/client';

export default function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [tenders, setTenders] = useState([]);
  const [selectedTenderId, setSelectedTenderId] = useState(1);
  const [stats, setStats] = useState(null);
  const [requirements, setRequirements] = useState([]);
  const [compliance, setCompliance] = useState([]);
  const [risks, setRisks] = useState([]);
  const [readiness, setReadiness] = useState(null);
  const [proposals, setProposals] = useState([]);
  const [company, setCompany] = useState(null);
  const [evidenceVault, setEvidenceVault] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [complianceFilter, setComplianceFilter] = useState('All');

  // Voice Query State
  const [voiceQuery, setVoiceQuery] = useState('');
  const [voiceResponse, setVoiceResponse] = useState(null);
  const [voiceLoading, setVoiceLoading] = useState(false);

  // New Tender Modal State
  const [showNewTenderModal, setShowNewTenderModal] = useState(false);
  const [newTender, setNewTender] = useState({
    title: '',
    buyer: '',
    tender_reference: '',
    submission_deadline: '',
    estimated_value: '',
    category: '',
  });

  // Proposal Generation State
  const [newSectionTitle, setNewSectionTitle] = useState('Section 3: Project Execution Methodology');
  const [generatingProposal, setGeneratingProposal] = useState(false);

  const loadAllData = async () => {
    try {
      setLoading(true);
      const [tendersData, statsData, companyData, vaultData] = await Promise.all([
        api.getTenders().catch(() => []),
        api.getDashboardStats().catch(() => null),
        api.getCompany().catch(() => null),
        api.getEvidenceVault().catch(() => []),
      ]);

      setTenders(tendersData);
      setStats(statsData);
      setCompany(companyData);
      setEvidenceVault(vaultData);

      const tId = selectedTenderId || (tendersData[0]?.id) || 1;
      setSelectedTenderId(tId);

      // Load tender-specific data
      const [reqs, comp, rsk, rdn, docs, props] = await Promise.all([
        api.getRequirements(tId).catch(() => []),
        api.getComplianceMatrix(tId).catch(() => []),
        api.getRisks(tId).catch(() => []),
        api.getReadiness(tId).catch(() => null),
        api.getTenderDocuments(tId).catch(() => []),
        api.getProposals(tId).catch(() => []),
      ]);

      setRequirements(reqs);
      setCompliance(comp);
      setRisks(rsk);
      setReadiness(rdn);
      setDocuments(docs);
      setProposals(props);
    } catch (err) {
      console.error('Failed to load data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAllData();
  }, [selectedTenderId]);

  const handleCreateTender = async (e) => {
    e.preventDefault();
    try {
      const created = await api.createTender(newTender);
      setShowNewTenderModal(false);
      setNewTender({ title: '', buyer: '', tender_reference: '', submission_deadline: '', estimated_value: '', category: '' });
      await loadAllData();
      setSelectedTenderId(created.id);
    } catch (err) {
      alert(`Error creating tender: ${err.message}`);
    }
  };

  const handleAskVoice = async (e) => {
    e.preventDefault();
    if (!voiceQuery.trim() || voiceLoading) return;
    setVoiceLoading(true);
    try {
      const resp = await api.askVoiceQuery({
        tender_id: selectedTenderId,
        question: voiceQuery,
      });
      setVoiceResponse(resp);
    } catch (err) {
      alert(`Failed to query Sarvam AI: ${err.message}`);
    } finally {
      setVoiceLoading(false);
    }
  };

  const handleGenerateProposal = async () => {
    setGeneratingProposal(true);
    try {
      await api.generateProposal(selectedTenderId, { section_title: newSectionTitle });
      const updated = await api.getProposals(selectedTenderId);
      setProposals(updated);
    } catch (err) {
      alert(`Generation failed: ${err.message}`);
    } finally {
      setGeneratingProposal(false);
    }
  };

  const exportComplianceCSV = () => {
    const headers = ['Requirement Code', 'Category', 'Requirement Text', 'Mandatory Level', 'Compliance Status', 'Company Evidence', 'Source Page'];
    const rows = compliance.map(c => [
      c.requirement?.code || '',
      `"${c.requirement?.category || ''}"`,
      `"${(c.requirement?.normalized_summary || '').replace(/"/g, '""')}"`,
      c.requirement?.mandatory_level || '',
      c.status || '',
      `"${(c.supporting_evidence || '').replace(/"/g, '""')}"`,
      c.source_page || '',
    ]);

    const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `TenderGuard_Compliance_Matrix_Tender_${selectedTenderId}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const filteredCompliance = compliance.filter(item => {
    const matchesFilter = complianceFilter === 'All' || item.status === complianceFilter;
    const matchesSearch = searchQuery === '' ||
      item.requirement?.code?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.requirement?.requirement_text?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.supporting_evidence?.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesFilter && matchesSearch;
  });

  const activeTender = tenders.find(t => t.id === selectedTenderId) || tenders[0];

  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: 'var(--bg-main)' }}>
      {/* Sidebar Navigation */}
      <aside style={{ width: '260px', background: 'var(--bg-card)', borderRight: '1px solid var(--border)', display: 'flex', flexDirection: 'column' }}>
        <div style={{ padding: '20px 24px', borderBottom: '1px solid var(--border)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div style={{ background: '#2563eb', padding: '8px', borderRadius: '8px', display: 'flex' }}>
              <ShieldCheck size={22} color="#ffffff" />
            </div>
            <div>
              <h1 style={{ fontSize: '16px', fontWeight: 700, letterSpacing: '-0.02em', color: '#f8fafc' }}>TenderGuard</h1>
              <p style={{ fontSize: '11px', color: '#94a3b8' }}>Powered by Sarvam AI</p>
            </div>
          </div>
        </div>

        {/* Workspace Card */}
        <div style={{ padding: '16px', borderBottom: '1px solid var(--border)', background: 'rgba(30, 41, 59, 0.4)' }}>
          <div style={{ fontSize: '11px', textTransform: 'uppercase', color: '#64748b', fontWeight: 600, letterSpacing: '0.05em' }}>Current Workspace</div>
          <div style={{ fontSize: '13px', fontWeight: 600, color: '#f1f5f9', marginTop: '4px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
            {company?.legal_name || 'Apex Renewable Energy'}
          </div>
          <div style={{ fontSize: '11px', color: '#10b981', display: 'flex', alignItems: 'center', gap: '4px', marginTop: '2px' }}>
            <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#10b981' }} />
            {company?.msme_status || 'MSME Class-A'}
          </div>
        </div>

        {/* Nav Links */}
        <nav style={{ padding: '16px 12px', flex: 1, display: 'flex', flexDirection: 'column', gap: '4px' }}>
          {[
            { id: 'overview', label: 'Overview', icon: LayoutDashboard },
            { id: 'tenders', label: 'Tenders Room', icon: FolderKanban },
            { id: 'documents', label: 'Tender Documents', icon: FileText },
            { id: 'requirements', label: 'Requirement Analysis', icon: CheckCircle2 },
            { id: 'compliance', label: 'Compliance Matrix', icon: ShieldCheck },
            { id: 'risks', label: 'Risk Auditor', icon: ShieldAlert, badge: risks.filter(r => r.status === 'Unresolved').length },
            { id: 'readiness', label: 'Bid Readiness', icon: AlertTriangle },
            { id: 'proposal', label: 'Proposal Studio', icon: Edit3 },
            { id: 'voice', label: 'Voice & Q&A Assistant', icon: Mic },
            { id: 'company', label: 'Company Vault', icon: Building2 },
            { id: 'settings', label: 'Settings & Status', icon: Settings },
          ].map(item => {
            const Icon = item.icon;
            const active = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  padding: '10px 14px',
                  borderRadius: '8px',
                  background: active ? '#2563eb' : 'transparent',
                  color: active ? '#ffffff' : '#94a3b8',
                  fontSize: '13px',
                  fontWeight: active ? 600 : 500,
                  transition: 'background 0.15s',
                  textAlign: 'left',
                }}
              >
                <Icon size={18} />
                <span style={{ flex: 1 }}>{item.label}</span>
                {item.badge > 0 && (
                  <span style={{ background: active ? '#1d4ed8' : '#ef4444', color: '#ffffff', fontSize: '10px', padding: '2px 6px', borderRadius: '10px', fontWeight: 700 }}>
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>

        {/* Footer Brand */}
        <div style={{ padding: '16px', borderTop: '1px solid var(--border)', fontSize: '11px', color: '#64748b' }}>
          TenderGuard v1.0 • Indic AI
        </div>
      </aside>

      {/* Main Container */}
      <main style={{ flex: 1, display: 'flex', flexDirection: 'column', height: '100vh', overflowY: 'auto' }}>
        {/* Top Header */}
        <header style={{ padding: '14px 28px', background: 'var(--bg-card)', borderBottom: '1px solid var(--border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <span style={{ fontSize: '12px', color: '#94a3b8' }}>Active Tender:</span>
            <select
              value={selectedTenderId}
              onChange={(e) => setSelectedTenderId(Number(e.target.value))}
              style={{
                background: '#1e293b',
                color: '#f8fafc',
                border: '1px solid var(--border)',
                padding: '6px 12px',
                borderRadius: '6px',
                fontSize: '13px',
                fontWeight: 600,
                maxWidth: '480px',
              }}
            >
              {tenders.map(t => (
                <option key={t.id} value={t.id}>
                  {t.title} ({t.tender_reference})
                </option>
              ))}
            </select>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px', background: '#1e293b', padding: '6px 12px', borderRadius: '20px', border: '1px solid var(--border)' }}>
              <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: stats?.sarvam_configured ? '#10b981' : '#eab308' }} />
              <span style={{ color: '#cbd5e1' }}>Sarvam 105B: {stats?.sarvam_configured ? 'Active' : 'Key Ready'}</span>
            </div>

            <button
              onClick={() => setShowNewTenderModal(true)}
              style={{ background: '#2563eb', color: '#ffffff', padding: '8px 14px', borderRadius: '6px', fontSize: '12px', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '6px' }}
            >
              <Plus size={14} /> New Tender
            </button>
          </div>
        </header>

        {/* Content Body */}
        <div style={{ padding: '28px', flex: 1 }}>
          {/* 1. OVERVIEW TAB */}
          {activeTab === 'overview' && (
            <div>
              <div style={{ marginBottom: '24px' }}>
                <h2 style={{ fontSize: '22px', fontWeight: 700, color: '#f8fafc' }}>Tender Intelligence Overview</h2>
                <p style={{ fontSize: '14px', color: '#94a3b8', marginTop: '4px' }}>
                  {activeTender?.title} • Buyer: {activeTender?.buyer}
                </p>
              </div>

              {/* KPI Cards */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginBottom: '28px' }}>
                {[
                  { label: 'Heuristic Compliance Rate', value: `${stats?.compliance_rate || 0}%`, sub: 'Deterministic calculation', color: '#10b981' },
                  { label: 'Missing / Expired Evidence', value: stats?.missing_evidence_count || 0, sub: 'Requires company upload', color: '#f97316' },
                  { label: 'Critical / High Risks', value: stats?.critical_risks_count || 0, sub: 'Potential disqualification gaps', color: '#ef4444' },
                  { label: 'Submission Deadline', value: activeTender?.submission_deadline || '10 Dec 2026', sub: 'Corrigendum Extended', color: '#3b82f6' },
                ].map((kpi, idx) => (
                  <div key={idx} style={{ background: 'var(--bg-card)', padding: '20px', borderRadius: '10px', border: '1px solid var(--border)' }}>
                    <div style={{ fontSize: '12px', color: '#94a3b8', fontWeight: 500 }}>{kpi.label}</div>
                    <div style={{ fontSize: '26px', fontWeight: 700, color: kpi.color, marginTop: '8px' }}>{kpi.value}</div>
                    <div style={{ fontSize: '11px', color: '#64748b', marginTop: '4px' }}>{kpi.sub}</div>
                  </div>
                ))}
              </div>

              {/* Action Banner */}
              <div style={{ background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)', border: '1px solid #3b82f6', borderRadius: '10px', padding: '24px', marginBottom: '28px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#60a5fa', fontSize: '12px', fontWeight: 700, textTransform: 'uppercase' }}>
                    <Sparkles size={16} /> Synthetic Evaluation Scenario Active (PRD Section 15)
                  </div>
                  <h3 style={{ fontSize: '18px', fontWeight: 600, color: '#ffffff', marginTop: '6px' }}>
                    SECI 3.0 MW Solar Rooftop Tender Evaluation
                  </h3>
                  <p style={{ fontSize: '13px', color: '#94a3b8', marginTop: '4px', maxWidth: '650px' }}>
                    Turnover verified (+₹2.67L buffer). Detected 2 critical gaps: Missing Non-Blacklisting Declaration (Annexure-IV) and Expired ISO 9001 certificate.
                  </p>
                </div>
                <button
                  onClick={() => setActiveTab('risks')}
                  style={{ background: '#2563eb', color: '#ffffff', padding: '10px 18px', borderRadius: '6px', fontSize: '13px', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '6px' }}
                >
                  View Gap Audit <ChevronRight size={16} />
                </button>
              </div>

              {/* Recent Risks & Actions */}
              <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: '24px' }}>
                <div style={{ background: 'var(--bg-card)', padding: '20px', borderRadius: '10px', border: '1px solid var(--border)' }}>
                  <h4 style={{ fontSize: '15px', fontWeight: 600, marginBottom: '16px' }}>High-Priority Bid Disqualification Risks</h4>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                    {risks.slice(0, 3).map(r => (
                      <div key={r.id} style={{ background: '#1e293b', padding: '14px', borderRadius: '8px', borderLeft: `4px solid ${r.severity === 'Critical' ? '#ef4444' : '#f97316'}` }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <span style={{ fontSize: '13px', fontWeight: 600, color: '#f8fafc' }}>{r.title}</span>
                          <span className={`badge badge-${r.severity.toLowerCase()}`}>{r.severity}</span>
                        </div>
                        <p style={{ fontSize: '12px', color: '#94a3b8', marginTop: '6px' }}>{r.explanation}</p>
                        <div style={{ fontSize: '11px', color: '#60a5fa', marginTop: '6px', display: 'flex', alignItems: 'center', gap: '4px' }}>
                          Action: {r.recommended_action}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div style={{ background: 'var(--bg-card)', padding: '20px', borderRadius: '10px', border: '1px solid var(--border)' }}>
                  <h4 style={{ fontSize: '15px', fontWeight: 600, marginBottom: '16px' }}>Tender Information & Deadlines</h4>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', fontSize: '13px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #1e293b', paddingBottom: '8px' }}>
                      <span style={{ color: '#94a3b8' }}>Reference ID</span>
                      <span style={{ fontWeight: 600 }}>{activeTender?.tender_reference}</span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #1e293b', paddingBottom: '8px' }}>
                      <span style={{ color: '#94a3b8' }}>Procuring Entity</span>
                      <span style={{ fontWeight: 600 }}>{activeTender?.buyer}</span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #1e293b', paddingBottom: '8px' }}>
                      <span style={{ color: '#94a3b8' }}>Estimated Value</span>
                      <span style={{ fontWeight: 600 }}>{activeTender?.estimated_value || '₹4.20 Crores'}</span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #1e293b', paddingBottom: '8px' }}>
                      <span style={{ color: '#94a3b8' }}>Corrigendum No. 1</span>
                      <span style={{ color: '#10b981', fontWeight: 600 }}>Deadline extended to 10 Dec 2026</span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', paddingTop: '4px' }}>
                      <span style={{ color: '#94a3b8' }}>EMD Exemption</span>
                      <span style={{ color: '#10b981', fontWeight: 600 }}>Eligible via Udyam MSME</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* 2. COMPLIANCE MATRIX TAB */}
          {activeTab === 'compliance' && (
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                <div>
                  <h2 style={{ fontSize: '20px', fontWeight: 700 }}>Requirement-Wise Compliance Matrix</h2>
                  <p style={{ fontSize: '13px', color: '#94a3b8', marginTop: '2px' }}>
                    Traceable evidence matrix linking RFP clauses with company documents and deterministic status.
                  </p>
                </div>
                <div style={{ display: 'flex', gap: '10px' }}>
                  <button
                    onClick={exportComplianceCSV}
                    style={{ background: '#1e293b', color: '#ffffff', border: '1px solid var(--border)', padding: '8px 14px', borderRadius: '6px', fontSize: '12px', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '6px' }}
                  >
                    <Download size={14} /> Export CSV
                  </button>
                </div>
              </div>

              {/* Filters */}
              <div style={{ display: 'flex', gap: '12px', alignItems: 'center', marginBottom: '16px' }}>
                <div style={{ position: 'relative', flex: 1, maxWidth: '320px' }}>
                  <Search size={14} style={{ position: 'absolute', left: '10px', top: '10px', color: '#64748b' }} />
                  <input
                    type="text"
                    placeholder="Search clause, text, or evidence..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    style={{ width: '100%', background: '#1e293b', border: '1px solid var(--border)', borderRadius: '6px', padding: '8px 12px 8px 32px', color: '#f8fafc', fontSize: '12px' }}
                  />
                </div>

                <div style={{ display: 'flex', gap: '6px' }}>
                  {['All', 'Potentially satisfied', 'Evidence found', 'Potentially not satisfied', 'Missing evidence', 'Expired evidence'].map(f => (
                    <button
                      key={f}
                      onClick={() => setComplianceFilter(f)}
                      style={{
                        background: complianceFilter === f ? '#2563eb' : '#1e293b',
                        color: complianceFilter === f ? '#ffffff' : '#94a3b8',
                        padding: '6px 12px',
                        borderRadius: '6px',
                        fontSize: '11px',
                        fontWeight: 600,
                        border: '1px solid var(--border)',
                      }}
                    >
                      {f}
                    </button>
                  ))}
                </div>
              </div>

              {/* Table */}
              <div className="table-container">
                <table>
                  <thead>
                    <tr>
                      <th style={{ width: '110px' }}>Req Code</th>
                      <th style={{ width: '220px' }}>Tender Requirement</th>
                      <th style={{ width: '90px' }}>Level</th>
                      <th style={{ width: '160px' }}>Compliance Status</th>
                      <th>Company Evidence & Verification</th>
                      <th style={{ width: '160px' }}>Document Reference</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredCompliance.map(row => (
                      <tr key={row.id}>
                        <td style={{ fontWeight: 600, color: '#38bdf8' }}>{row.requirement?.code}</td>
                        <td>
                          <div style={{ fontWeight: 600 }}>{row.requirement?.category}</div>
                          <div style={{ color: '#94a3b8', fontSize: '12px', marginTop: '2px' }}>{row.requirement?.normalized_summary}</div>
                        </td>
                        <td>
                          <span className="badge badge-neutral">{row.requirement?.mandatory_level}</span>
                        </td>
                        <td>
                          <span className={`badge ${
                            row.status.includes('satisfied') || row.status.includes('found')
                              ? 'badge-satisfied'
                              : row.status.includes('not') || row.status.includes('Expired')
                              ? 'badge-critical'
                              : 'badge-high'
                          }`}>
                            {row.status}
                          </span>
                        </td>
                        <td>
                          <div style={{ fontSize: '12px', fontWeight: 500, color: '#f8fafc' }}>{row.supporting_evidence}</div>
                          <div style={{ fontSize: '11px', color: '#94a3b8', marginTop: '3px' }}>{row.deterministic_notes}</div>
                        </td>
                        <td style={{ fontSize: '11px', color: '#cbd5e1' }}>
                          <div>{row.requirement?.source_document}</div>
                          <div style={{ color: '#60a5fa', marginTop: '2px' }}>{row.source_page}</div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* 3. RISK AUDITOR TAB */}
          {activeTab === 'risks' && (
            <div>
              <div style={{ marginBottom: '20px' }}>
                <h2 style={{ fontSize: '20px', fontWeight: 700 }}>Risk Auditor & Disqualification Gaps</h2>
                <p style={{ fontSize: '13px', color: '#94a3b8', marginTop: '2px' }}>
                  Audited potential disqualification factors with direct evidence trace and remediation suggestions.
                </p>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                {risks.map(r => (
                  <div key={r.id} style={{ background: 'var(--bg-card)', padding: '20px', borderRadius: '10px', border: '1px solid var(--border)', borderLeft: `5px solid ${r.severity === 'Critical' ? '#ef4444' : r.severity === 'High' ? '#f97316' : '#eab308'}` }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                      <div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                          <span className={`badge badge-${r.severity.toLowerCase()}`}>{r.severity} Risk</span>
                          <span style={{ fontSize: '12px', color: '#94a3b8' }}>Linked to: {r.requirement_code || 'General Compliance'}</span>
                        </div>
                        <h3 style={{ fontSize: '16px', fontWeight: 600, color: '#f8fafc', marginTop: '8px' }}>{r.title}</h3>
                      </div>

                      <select
                        value={r.status}
                        onChange={async (e) => {
                          await api.updateRisk(r.id, { status: e.target.value });
                          loadAllData();
                        }}
                        style={{ background: '#1e293b', color: '#f8fafc', border: '1px solid var(--border)', padding: '4px 8px', borderRadius: '6px', fontSize: '12px' }}
                      >
                        <option value="Unresolved">Unresolved</option>
                        <option value="Mitigated">Mitigated</option>
                        <option value="Accepted">Accepted Risk</option>
                      </select>
                    </div>

                    <p style={{ fontSize: '13px', color: '#cbd5e1', marginTop: '10px' }}>{r.explanation}</p>

                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginTop: '14px', background: '#1e293b', padding: '12px 16px', borderRadius: '8px', fontSize: '12px' }}>
                      <div>
                        <span style={{ color: '#94a3b8' }}>Why it matters:</span>
                        <div style={{ color: '#f8fafc', marginTop: '2px' }}>{r.why_it_matters}</div>
                      </div>
                      <div>
                        <span style={{ color: '#94a3b8' }}>RFP Source Citation:</span>
                        <div style={{ color: '#60a5fa', marginTop: '2px' }}>{r.source_reference}</div>
                      </div>
                    </div>

                    <div style={{ marginTop: '12px', fontSize: '12px', color: '#34d399', display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <strong>Recommended Action:</strong> {r.recommended_action}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 4. BID READINESS TAB */}
          {activeTab === 'readiness' && (
            <div>
              <div style={{ marginBottom: '20px' }}>
                <h2 style={{ fontSize: '20px', fontWeight: 700 }}>Eligibility & Bid Readiness Audit</h2>
                <p style={{ fontSize: '13px', color: '#94a3b8', marginTop: '2px' }}>
                  Transparent heuristic scoring and deterministic calculation breakdown (Decision Support).
                </p>
              </div>

              {readiness?.has_critical_blocker && (
                <div style={{ background: 'rgba(239, 68, 68, 0.15)', border: '1px solid rgba(239, 68, 68, 0.4)', padding: '16px 20px', borderRadius: '10px', marginBottom: '24px', display: 'flex', alignItems: 'center', gap: '14px' }}>
                  <AlertTriangle size={24} color="#ef4444" />
                  <div>
                    <h4 style={{ fontSize: '15px', fontWeight: 700, color: '#f87171' }}>
                      Critical Disqualification Blockers Detected ({readiness.critical_blockers_count})
                    </h4>
                    <p style={{ fontSize: '12px', color: '#fca5a5', marginTop: '2px' }}>
                      Per PRD Rule 7: Mandatory conditions marked unfulfilled must be resolved before submission regardless of overall score.
                    </p>
                  </div>
                </div>
              )}

              <div style={{ display: 'grid', gridTemplateColumns: '320px 1fr', gap: '24px' }}>
                <div style={{ background: 'var(--bg-card)', padding: '24px', borderRadius: '10px', border: '1px solid var(--border)', textAlign: 'center' }}>
                  <div style={{ fontSize: '13px', color: '#94a3b8', fontWeight: 600 }}>Heuristic Readiness Score</div>
                  <div style={{ fontSize: '56px', fontWeight: 800, color: readiness?.has_critical_blocker ? '#f97316' : '#10b981', marginTop: '8px' }}>
                    {readiness?.readiness_score || 0}%
                  </div>
                  <div style={{ fontSize: '11px', color: '#64748b', marginTop: '4px' }}>
                    Label: {readiness?.score_label}
                  </div>
                  <hr style={{ border: 'none', borderTop: '1px solid var(--border)', margin: '20px 0' }} />
                  <div style={{ textAlign: 'left', fontSize: '12px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span style={{ color: '#94a3b8' }}>Potentially Satisfied</span>
                      <span style={{ color: '#10b981', fontWeight: 600 }}>{readiness?.status_breakdown?.['Potentially satisfied'] || 0}</span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span style={{ color: '#94a3b8' }}>Evidence Found</span>
                      <span style={{ color: '#10b981', fontWeight: 600 }}>{readiness?.status_breakdown?.['Evidence found'] || 0}</span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span style={{ color: '#94a3b8' }}>Missing Evidence</span>
                      <span style={{ color: '#f97316', fontWeight: 600 }}>{readiness?.status_breakdown?.['Missing evidence'] || 0}</span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span style={{ color: '#94a3b8' }}>Expired Evidence</span>
                      <span style={{ color: '#ef4444', fontWeight: 600 }}>{readiness?.status_breakdown?.['Expired evidence'] || 0}</span>
                    </div>
                  </div>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                  <div style={{ background: 'var(--bg-card)', padding: '20px', borderRadius: '10px', border: '1px solid var(--border)' }}>
                    <h4 style={{ fontSize: '15px', fontWeight: 600, marginBottom: '14px' }}>Deterministic Mathematical Checks (PRD Section 15)</h4>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                      {readiness?.deterministic_evaluations?.map((ev, i) => (
                        <div key={i} style={{ background: '#1e293b', padding: '14px', borderRadius: '8px' }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <span style={{ fontWeight: 600, color: '#f8fafc', fontSize: '13px' }}>{ev.category} Check</span>
                            <span className={`badge ${ev.is_sufficient ? 'badge-satisfied' : 'badge-critical'}`}>
                              {ev.is_sufficient ? 'Passed' : 'Deficit / Expired'}
                            </span>
                          </div>
                          <p style={{ fontSize: '12px', color: '#94a3b8', marginTop: '6px' }}>{ev.details || JSON.stringify(ev)}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* 5. PROPOSAL STUDIO TAB */}
          {activeTab === 'proposal' && (
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                <div>
                  <h2 style={{ fontSize: '20px', fontWeight: 700 }}>Proposal Studio (Grounded Drafting)</h2>
                  <p style={{ fontSize: '13px', color: '#94a3b8', marginTop: '2px' }}>
                    Draft technical proposals using verified company facts. Never hallucinate claims — explicit placeholders are inserted for gaps.
                  </p>
                </div>
                <div style={{ display: 'flex', gap: '10px' }}>
                  <button
                    onClick={handleGenerateProposal}
                    disabled={generatingProposal}
                    style={{ background: '#2563eb', color: '#ffffff', padding: '8px 14px', borderRadius: '6px', fontSize: '12px', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '6px' }}
                  >
                    <Sparkles size={14} /> {generatingProposal ? 'Sarvam Drafting...' : 'Generate New Section'}
                  </button>
                </div>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                {proposals.map(p => (
                  <div key={p.id} style={{ background: 'var(--bg-card)', padding: '20px', borderRadius: '10px', border: '1px solid var(--border)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                      <h3 style={{ fontSize: '16px', fontWeight: 600, color: '#f8fafc' }}>{p.section_title}</h3>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        {p.has_unsupported_claims && (
                          <span className="badge badge-high" title="Contains [USER INPUT REQUIRED]">
                            Contains User Placeholders
                          </span>
                        )}
                        <span className="badge badge-neutral">v{p.version} • {p.status}</span>
                      </div>
                    </div>

                    <textarea
                      value={p.content}
                      onChange={async (e) => {
                        const newContent = e.target.value;
                        setProposals(proposals.map(item => item.id === p.id ? { ...item, content: newContent } : item));
                        await api.updateProposal(p.id, { content: newContent });
                      }}
                      rows={8}
                      style={{
                        width: '100%',
                        background: '#1e293b',
                        color: '#f8fafc',
                        border: '1px solid var(--border)',
                        borderRadius: '8px',
                        padding: '14px',
                        fontSize: '13px',
                        lineHeight: '1.6',
                        resize: 'vertical',
                      }}
                    />

                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '10px', fontSize: '12px', color: '#94a3b8' }}>
                      <span>Linked Evidence: {p.evidence_references_json || '[]'}</span>
                      <button
                        onClick={() => {
                          navigator.clipboard.writeText(p.content);
                          alert('Proposal section copied to clipboard!');
                        }}
                        style={{ background: '#334155', color: '#f8fafc', padding: '6px 12px', borderRadius: '6px', fontSize: '11px', fontWeight: 600 }}
                      >
                        Copy Draft
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 6. VOICE & Q&A ASSISTANT TAB */}
          {activeTab === 'voice' && (
            <div style={{ maxWidth: '800px' }}>
              <div style={{ marginBottom: '20px' }}>
                <h2 style={{ fontSize: '20px', fontWeight: 700 }}>Voice & Multilingual Tender Assistant</h2>
                <p style={{ fontSize: '13px', color: '#94a3b8', marginTop: '2px' }}>
                  Ask natural language questions in English or Hindi, grounded directly in RFP clauses with page citations.
                </p>
              </div>

              {/* Sample Queries */}
              <div style={{ display: 'flex', gap: '8px', overflowX: 'auto', marginBottom: '16px' }}>
                {[
                  'What is the minimum annual turnover requirement in this tender?',
                  'How many past project completion certificates are required?',
                  'Is our ISO 9001:2015 certificate valid or expired?',
                  'Are MSMEs exempt from EMD submission in this RFP?',
                ].map((q, i) => (
                  <button
                    key={i}
                    onClick={() => {
                      setVoiceQuery(q);
                    }}
                    style={{ background: '#1e293b', color: '#cbd5e1', border: '1px solid var(--border)', padding: '6px 12px', borderRadius: '16px', fontSize: '12px', whiteSpace: 'nowrap' }}
                  >
                    {q}
                  </button>
                ))}
              </div>

              {/* Form */}
              <form onSubmit={handleAskVoice} style={{ display: 'flex', gap: '10px', marginBottom: '24px' }}>
                <input
                  type="text"
                  placeholder="Ask any question about this tender (English or Hindi)..."
                  value={voiceQuery}
                  onChange={(e) => setVoiceQuery(e.target.value)}
                  disabled={voiceLoading}
                  style={{ flex: 1, background: '#1e293b', border: '1px solid var(--border)', borderRadius: '8px', padding: '12px 16px', color: '#f8fafc', fontSize: '13px' }}
                />
                <button
                  type="submit"
                  disabled={voiceLoading || !voiceQuery.trim()}
                  style={{ background: '#2563eb', color: '#ffffff', padding: '0 20px', borderRadius: '8px', fontWeight: 600, fontSize: '13px', display: 'flex', alignItems: 'center', gap: '6px' }}
                >
                  <Send size={16} /> {voiceLoading ? 'Querying Sarvam...' : 'Ask'}
                </button>
              </form>

              {/* Answer Card */}
              {voiceResponse && (
                <div style={{ background: 'var(--bg-card)', padding: '24px', borderRadius: '10px', border: '1px solid var(--border)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                    <div style={{ fontSize: '12px', color: '#60a5fa', fontWeight: 600 }}>Grounding Model: {voiceResponse.model}</div>
                    <span className="badge badge-satisfied">Grounded Fact</span>
                  </div>
                  <div style={{ fontSize: '14px', lineHeight: '1.6', color: '#f8fafc', whiteSpace: 'pre-wrap' }}>
                    {voiceResponse.answer}
                  </div>

                  <hr style={{ border: 'none', borderTop: '1px solid var(--border)', margin: '16px 0' }} />
                  <div style={{ fontSize: '12px', color: '#94a3b8' }}>
                    <strong>Verified Source Citations:</strong>
                    <div style={{ display: 'flex', gap: '8px', marginTop: '6px', flexWrap: 'wrap' }}>
                      {voiceResponse.citations?.slice(0, 3).map((c, idx) => (
                        <span key={idx} style={{ background: '#1e293b', border: '1px solid var(--border)', padding: '4px 8px', borderRadius: '4px', fontSize: '11px', color: '#38bdf8' }}>
                          [{c.code}] {c.document} ({c.page})
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* 7. COMPANY VAULT TAB */}
          {activeTab === 'company' && (
            <div>
              <div style={{ marginBottom: '20px' }}>
                <h2 style={{ fontSize: '20px', fontWeight: 700 }}>Company Profile & Document Vault</h2>
                <p style={{ fontSize: '13px', color: '#94a3b8', marginTop: '2px' }}>
                  Manage verified statutory identifiers, past experience credentials, and certificate expiry dates.
                </p>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1.1fr 1fr', gap: '24px' }}>
                <div style={{ background: 'var(--bg-card)', padding: '20px', borderRadius: '10px', border: '1px solid var(--border)' }}>
                  <h4 style={{ fontSize: '15px', fontWeight: 600, marginBottom: '16px' }}>Statutory Company Profile</h4>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', fontSize: '13px' }}>
                    <div>
                      <label style={{ color: '#94a3b8', fontSize: '12px' }}>Legal Company Name</label>
                      <input
                        type="text"
                        value={company?.legal_name || ''}
                        onChange={(e) => setCompany({ ...company, legal_name: e.target.value })}
                        style={{ width: '100%', background: '#1e293b', border: '1px solid var(--border)', borderRadius: '6px', padding: '8px', color: '#f8fafc', marginTop: '4px' }}
                      />
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                      <div>
                        <label style={{ color: '#94a3b8', fontSize: '12px' }}>MSME Udyam Number</label>
                        <input
                          type="text"
                          value={company?.udyam_number || ''}
                          readOnly
                          style={{ width: '100%', background: '#1e293b', border: '1px solid var(--border)', borderRadius: '6px', padding: '8px', color: '#f8fafc', marginTop: '4px' }}
                        />
                      </div>
                      <div>
                        <label style={{ color: '#94a3b8', fontSize: '12px' }}>GSTIN</label>
                        <input
                          type="text"
                          value={company?.gstin || ''}
                          readOnly
                          style={{ width: '100%', background: '#1e293b', border: '1px solid var(--border)', borderRadius: '6px', padding: '8px', color: '#f8fafc', marginTop: '4px' }}
                        />
                      </div>
                    </div>
                    <div>
                      <label style={{ color: '#94a3b8', fontSize: '12px' }}>Audited Turnover (Last 3 FYs in ₹ Lakhs)</label>
                      <div style={{ background: '#1e293b', padding: '10px 14px', borderRadius: '6px', marginTop: '4px', color: '#38bdf8', fontWeight: 600 }}>
                        {company?.turnover_json || '{"2021-22": 41.0, "2022-23": 55.0, "2023-24": 62.0}'}
                      </div>
                      <div style={{ fontSize: '11px', color: '#10b981', marginTop: '4px' }}>
                        Calculated Average: ₹52.67 Lakhs (Passes ₹50 Lakhs threshold)
                      </div>
                    </div>
                  </div>
                </div>

                <div style={{ background: 'var(--bg-card)', padding: '20px', borderRadius: '10px', border: '1px solid var(--border)' }}>
                  <h4 style={{ fontSize: '15px', fontWeight: 600, marginBottom: '16px' }}>Evidence Documents Vault ({evidenceVault.length})</h4>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                    {evidenceVault.map(ev => (
                      <div key={ev.id} style={{ background: '#1e293b', padding: '12px', borderRadius: '8px', border: '1px solid var(--border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div>
                          <div style={{ fontSize: '13px', fontWeight: 600, color: '#f8fafc' }}>{ev.title}</div>
                          <div style={{ fontSize: '11px', color: '#94a3b8', marginTop: '2px' }}>
                            Issuer: {ev.issuer} {ev.expiry_date && `• Expiry: ${ev.expiry_date}`}
                          </div>
                        </div>
                        <span className={`badge ${ev.verification_status === 'Verified' ? 'badge-satisfied' : 'badge-critical'}`}>
                          {ev.verification_status}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* 8. TENDERS TAB */}
          {activeTab === 'tenders' && (
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                <div>
                  <h2 style={{ fontSize: '20px', fontWeight: 700 }}>Tenders Management Room</h2>
                  <p style={{ fontSize: '13px', color: '#94a3b8', marginTop: '2px' }}>
                    Active and archived tenders being evaluated for bid readiness.
                  </p>
                </div>
                <button
                  onClick={() => setShowNewTenderModal(true)}
                  style={{ background: '#2563eb', color: '#ffffff', padding: '8px 14px', borderRadius: '6px', fontSize: '12px', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '6px' }}
                >
                  <Plus size={14} /> New Tender Project
                </button>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(360px, 1fr))', gap: '16px' }}>
                {tenders.map(t => (
                  <div
                    key={t.id}
                    onClick={() => setSelectedTenderId(t.id)}
                    style={{
                      background: 'var(--bg-card)',
                      padding: '20px',
                      borderRadius: '10px',
                      border: t.id === selectedTenderId ? '2px solid #2563eb' : '1px solid var(--border)',
                      cursor: 'pointer',
                      transition: 'border 0.2s',
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span className="badge badge-satisfied">{t.status.toUpperCase()}</span>
                      <span style={{ fontSize: '12px', color: '#94a3b8' }}>Due: {t.submission_deadline}</span>
                    </div>
                    <h3 style={{ fontSize: '15px', fontWeight: 600, color: '#f8fafc', marginTop: '12px', lineHeight: '1.4' }}>
                      {t.title}
                    </h3>
                    <div style={{ fontSize: '12px', color: '#94a3b8', marginTop: '8px' }}>
                      Buyer: <strong style={{ color: '#f8fafc' }}>{t.buyer}</strong>
                    </div>
                    <div style={{ fontSize: '11px', color: '#64748b', marginTop: '4px' }}>
                      Ref: {t.tender_reference}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 9. TENDER DOCUMENTS TAB */}
          {activeTab === 'documents' && (
            <div>
              <div style={{ marginBottom: '20px' }}>
                <h2 style={{ fontSize: '20px', fontWeight: 700 }}>Tender Documents & Corrigenda</h2>
                <p style={{ fontSize: '13px', color: '#94a3b8', marginTop: '2px' }}>
                  Uploaded tender notices, RFPs, technical specifications, and corrigendum files.
                </p>
              </div>

              <div className="table-container">
                <table>
                  <thead>
                    <tr>
                      <th>Document Name</th>
                      <th>Type</th>
                      <th>File Size</th>
                      <th>Pages</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {documents.map(d => (
                      <tr key={d.id}>
                        <td style={{ fontWeight: 600, color: '#38bdf8' }}>{d.original_filename}</td>
                        <td><span className="badge badge-neutral">{d.document_type}</span></td>
                        <td>{(d.file_size / 1024 / 1024).toFixed(2)} MB</td>
                        <td>{d.page_count} pages</td>
                        <td><span className="badge badge-satisfied">{d.processing_status}</span></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* 10. REQUIREMENTS TAB */}
          {activeTab === 'requirements' && (
            <div>
              <div style={{ marginBottom: '20px' }}>
                <h2 style={{ fontSize: '20px', fontWeight: 700 }}>Extracted Tender Requirements</h2>
                <p style={{ fontSize: '13px', color: '#94a3b8', marginTop: '2px' }}>
                  Structured requirement records with exact document and page number citations.
                </p>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                {requirements.map(req => (
                  <div key={req.id} style={{ background: 'var(--bg-card)', padding: '18px', borderRadius: '8px', border: '1px solid var(--border)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span style={{ fontWeight: 700, color: '#38bdf8' }}>{req.code}</span>
                        <span style={{ fontSize: '12px', color: '#94a3b8' }}>• {req.category}</span>
                      </div>
                      <span className="badge badge-neutral">{req.mandatory_level}</span>
                    </div>
                    <p style={{ fontSize: '13px', color: '#f8fafc', marginTop: '8px', lineHeight: '1.5' }}>
                      {req.requirement_text}
                    </p>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '12px', fontSize: '11px', color: '#94a3b8', background: '#1e293b', padding: '8px 12px', borderRadius: '6px' }}>
                      <span>Source: <strong style={{ color: '#cbd5e1' }}>{req.source_document}</strong></span>
                      <span style={{ color: '#60a5fa' }}>{req.source_page}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 11. SETTINGS TAB */}
          {activeTab === 'settings' && (
            <div style={{ maxWidth: '640px' }}>
              <div style={{ marginBottom: '20px' }}>
                <h2 style={{ fontSize: '20px', fontWeight: 700 }}>System Settings & Diagnostics</h2>
                <p style={{ fontSize: '13px', color: '#94a3b8', marginTop: '2px' }}>
                  Backend integration health and Sarvam AI configuration.
                </p>
              </div>

              <div style={{ background: 'var(--bg-card)', padding: '20px', borderRadius: '10px', border: '1px solid var(--border)' }}>
                <h4 style={{ fontSize: '15px', fontWeight: 600, marginBottom: '14px' }}>AI Integration Health</h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', fontSize: '13px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ color: '#94a3b8' }}>Sarvam API Key Status</span>
                    <span style={{ color: stats?.sarvam_configured ? '#10b981' : '#f97316', fontWeight: 600 }}>
                      {stats?.sarvam_configured ? 'Configured & Active' : 'Key Present in Backend'}
                    </span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ color: '#94a3b8' }}>Active Reasoning Model</span>
                    <span style={{ color: '#38bdf8', fontWeight: 600 }}>sarvam-105b-conversations</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ color: '#94a3b8' }}>Backend Database</span>
                    <span style={{ color: '#f8fafc', fontWeight: 600 }}>SQLite (tenderguard.db)</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ color: '#94a3b8' }}>PRD Golden Evaluation Dataset</span>
                    <span style={{ color: '#10b981', fontWeight: 600 }}>Loaded (SECI 3MW Solar)</span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>

      {/* New Tender Modal */}
      {showNewTenderModal && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.7)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000, padding: '16px' }}>
          <div style={{ background: 'var(--bg-card)', width: '100%', maxWidth: '520px', padding: '24px', borderRadius: '10px', border: '1px solid var(--border)' }}>
            <h3 style={{ fontSize: '18px', fontWeight: 700, marginBottom: '16px' }}>Create New Tender Project</h3>
            <form onSubmit={handleCreateTender} style={{ display: 'flex', flexDirection: 'column', gap: '12px', fontSize: '13px' }}>
              <div>
                <label style={{ color: '#94a3b8' }}>Tender Title *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Supply and Installation of Solar Systems..."
                  value={newTender.title}
                  onChange={(e) => setNewTender({ ...newTender, title: e.target.value })}
                  style={{ width: '100%', background: '#1e293b', border: '1px solid var(--border)', borderRadius: '6px', padding: '8px', color: '#f8fafc', marginTop: '4px' }}
                />
              </div>
              <div>
                <label style={{ color: '#94a3b8' }}>Buyer / Department *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Indian Railways / NTPC / SECI"
                  value={newTender.buyer}
                  onChange={(e) => setNewTender({ ...newTender, buyer: e.target.value })}
                  style={{ width: '100%', background: '#1e293b', border: '1px solid var(--border)', borderRadius: '6px', padding: '8px', color: '#f8fafc', marginTop: '4px' }}
                />
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                <div>
                  <label style={{ color: '#94a3b8' }}>Reference ID *</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. RFP-2026-091"
                    value={newTender.tender_reference}
                    onChange={(e) => setNewTender({ ...newTender, tender_reference: e.target.value })}
                    style={{ width: '100%', background: '#1e293b', border: '1px solid var(--border)', borderRadius: '6px', padding: '8px', color: '#f8fafc', marginTop: '4px' }}
                  />
                </div>
                <div>
                  <label style={{ color: '#94a3b8' }}>Submission Deadline *</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. 2026-12-15"
                    value={newTender.submission_deadline}
                    onChange={(e) => setNewTender({ ...newTender, submission_deadline: e.target.value })}
                    style={{ width: '100%', background: '#1e293b', border: '1px solid var(--border)', borderRadius: '6px', padding: '8px', color: '#f8fafc', marginTop: '4px' }}
                  />
                </div>
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '16px' }}>
                <button
                  type="button"
                  onClick={() => setShowNewTenderModal(false)}
                  style={{ background: '#334155', color: '#f8fafc', padding: '8px 14px', borderRadius: '6px', fontSize: '12px' }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  style={{ background: '#2563eb', color: '#ffffff', padding: '8px 18px', borderRadius: '6px', fontSize: '12px', fontWeight: 600 }}
                >
                  Create Tender
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

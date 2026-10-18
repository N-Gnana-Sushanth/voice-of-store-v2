import React, { useState, useEffect } from 'react';
import {
  ClipboardList,
  CheckCircle2,
  Clock,
  AlertCircle,
  Sparkles,
  Search,
  Filter,
  Check,
  Store,
  RefreshCw,
  RotateCcw,
  Users,
  ShieldAlert,
  ArrowRightLeft,
  X,
  Building,
  HelpCircle,
} from 'lucide-react';
import Sidebar from '../components/Sidebar';
import Header from '../components/Header';
import { api } from '../api/client';
import { useApp } from '../context/AppContext';

const INITIAL_TASKS = [
  {
    id: 'ACT-101',
    title: 'Dispatch technician for Walk-in Freezer #2',
    store: 'Store #128 • Chennai',
    owner: 'Store Ops',
    ownerTag: 'store-ops',
    severity: 'High',
    status: 'In Progress',
    sla: '4 hours remaining',
    slaUrgent: true,
    reported: '16 Oct 2026',
  },
  {
    id: 'ACT-102',
    title: 'Quarantine unlabeled bakery items & audit packaging',
    store: 'Store #074 • Pune',
    owner: 'Quality & Compliance',
    ownerTag: 'quality',
    severity: 'High',
    status: 'Open',
    sla: '2 hours remaining',
    slaUrgent: true,
    reported: '16 Oct 2026',
  },
  {
    id: 'ACT-103',
    title: 'Conduct customer service retraining for cashiers',
    store: 'Store #302 • Bengaluru',
    owner: 'HR',
    ownerTag: 'hr',
    severity: 'Medium',
    status: 'Open',
    sla: '2 days remaining',
    slaUrgent: false,
    reported: '15 Oct 2026',
  },
  {
    id: 'ACT-104',
    title: 'Emergency restock order for rice, oil, and flour',
    store: 'Store #412 • Coimbatore',
    owner: 'Supply Chain',
    ownerTag: 'supply',
    severity: 'Medium',
    status: 'Resolved',
    sla: 'Completed in 1.4 days',
    slaUrgent: false,
    reported: '15 Oct 2026',
  },
  {
    id: 'ACT-105',
    title: 'Debug payment gateway timeouts during peak billing',
    store: 'Chainwide (Digital App)',
    owner: 'Digital',
    ownerTag: 'digital',
    severity: 'Medium',
    status: 'In Progress',
    sla: '1 day remaining',
    slaUrgent: false,
    reported: '15 Oct 2026',
  },
];

const DEPARTMENTS = [
  'Store Ops',
  'Supply Chain',
  'Merchandising',
  'Digital',
  'HR',
  'Quality & Compliance',
];

export default function ActionQueuePage() {
  const { isLive: globalIsLive } = useApp();
  const [activeTab, setActiveTab] = useState('tasks'); // 'tasks' | 'routing'
  const [tasks, setTasks] = useState(INITIAL_TASKS);
  const [filterStatus, setFilterStatus] = useState('All');
  const [isLive, setIsLive] = useState(false);
  const [loading, setLoading] = useState(false);
  const [updatingId, setUpdatingId] = useState(null);

  // Routing state
  const [routingGroups, setRoutingGroups] = useState([]);
  const [routingLoading, setRoutingLoading] = useState(false);
  const [selectedDeptFilter, setSelectedDeptFilter] = useState('All');
  const [needsReviewOnly, setNeedsReviewOnly] = useState(false);

  // Reassignment modal
  const [reassignModalIncident, setReassignModalIncident] = useState(null);
  const [targetDept, setTargetDept] = useState('Store Ops');
  const [reassignReason, setReassignReason] = useState('');
  const [reassigning, setReassigning] = useState(false);

  const loadTasks = async () => {
    setLoading(true);
    try {
      const res = await api.tasks.list();
      if (res && res.length > 0) {
        setIsLive(true);
        const mapped = res.map((t) => ({
          id: t.task_id,
          title: t.title,
          store: t.store_name,
          owner: t.owner,
          ownerTag: t.owner_tag,
          severity: t.severity,
          status: t.status,
          sla: t.sla_window,
          slaUrgent: t.sla_urgent,
          reported: new Date(t.reported_date).toLocaleDateString('en-GB', {
            day: '2-digit',
            month: 'short',
            year: 'numeric',
          }),
        }));
        setTasks(mapped);
      } else {
        setTasks(INITIAL_TASKS);
      }
    } catch (err) {
      console.warn('Backend unavailable, using local tasks:', err.message);
      setIsLive(false);
      setTasks(INITIAL_TASKS);
    } finally {
      setLoading(false);
    }
  };

  const loadRoutingAssignments = async () => {
    setRoutingLoading(true);
    try {
      const params = {};
      if (selectedDeptFilter !== 'All') params.department = selectedDeptFilter;
      if (needsReviewOnly) params.needs_review_only = true;

      const res = await api.routing.assignments(params);
      if (res && res.length > 0) {
        setRoutingGroups(res);
      } else {
        // Fallback demo routing groups
        setRoutingGroups(
          DEPARTMENTS.map((dept) => ({
            department: dept,
            total_assigned: dept === 'Store Ops' ? 14 : dept === 'Quality & Compliance' ? 8 : 4,
            open_count: dept === 'Store Ops' ? 9 : 3,
            needs_review_count: dept === 'Store Ops' ? 2 : 0,
            critical_count: dept === 'Quality & Compliance' ? 2 : dept === 'Store Ops' ? 1 : 0,
            incidents: [
              {
                id: `INC-${dept.slice(0, 3).toUpperCase()}-01`,
                category: dept === 'Store Ops' ? 'Equipment' : dept === 'Quality & Compliance' ? 'Allergens' : 'Customer Service',
                store_name: 'Store #128 • Chennai',
                store_region: 'South',
                severity: dept === 'Quality & Compliance' ? 'CRITICAL' : 'HIGH',
                status: 'OPEN',
                primary_owner: dept,
                secondary_owner: dept === 'Quality & Compliance' ? 'Store Ops' : null,
                needs_human_review: dept === 'Store Ops',
                actionability_score: 0.92,
                evidence_summary: 'Temperature gauge showing 12C in walk-in freezer; milk spoiling.',
                feedback_count: 5,
                first_seen_at: new Date(Date.now() - 3600000 * 5).toISOString(),
                routing_history: [{ action: 'INITIAL_AUTO_ROUTE', owner: dept }],
              },
            ],
          }))
        );
      }
    } catch (err) {
      console.warn('Could not fetch routing assignments:', err.message);
    } finally {
      setRoutingLoading(false);
    }
  };

  useEffect(() => {
    loadTasks();
  }, []);

  useEffect(() => {
    if (activeTab === 'routing') {
      loadRoutingAssignments();
    }
  }, [activeTab, selectedDeptFilter, needsReviewOnly]);

  const toggleTaskStatus = async (id) => {
    const task = tasks.find((t) => t.id === id);
    if (!task) return;

    const nextStatus = task.status === 'Resolved' ? 'Open' : 'Resolved';

    // Optimistic update
    setTasks((prev) =>
      prev.map((t) => {
        if (t.id === id) {
          return {
            ...t,
            status: nextStatus,
            sla: nextStatus === 'Resolved' ? 'Completed' : '1 day remaining',
            slaUrgent: false,
          };
        }
        return t;
      })
    );

    setUpdatingId(id);
    try {
      await api.tasks.updateStatus(id, nextStatus, `Status changed to ${nextStatus} by Sushanth`);
    } catch (err) {
      console.warn('Could not persist status to backend, local state updated:', err.message);
    } finally {
      setUpdatingId(null);
    }
  };

  const handleOpenReassign = (incident) => {
    setReassignModalIncident(incident);
    setTargetDept(incident.primary_owner || 'Store Ops');
    setReassignReason('');
  };

  const handleConfirmReassign = async () => {
    if (!reassignModalIncident || !reassignReason.trim()) return;
    setReassigning(true);
    try {
      await api.routing.reassign(reassignModalIncident.id, {
        new_owner: targetDept,
        reason: reassignReason,
        mark_review_complete: true,
      });
      setReassignModalIncident(null);
      loadRoutingAssignments();
    } catch (err) {
      console.error('Failed to reassign incident:', err.message);
      alert(`Could not reassign: ${err.message}`);
    } finally {
      setReassigning(false);
    }
  };

  const filteredTasks = tasks.filter((t) => {
    if (filterStatus === 'All') return true;
    return t.status === filterStatus;
  });

  const openCount = tasks.filter((t) => t.status === 'Open').length;
  const inProgressCount = tasks.filter((t) => t.status === 'In Progress').length;
  const resolvedCount = tasks.filter((t) => t.status === 'Resolved').length;

  // Flattened routing incidents
  const allRoutingIncidents = routingGroups.flatMap((g) => g.incidents || []);

  return (
    <div className="app-container">
      <Sidebar />
      <div className="app-main">
        <Header searchPlaceholder="Search action tasks, ticket IDs, stores..." />

        <main className="page-content">
          {/* Header */}
          <div className="page-header-row">
            <div className="page-title-group">
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <h1>Action Queue</h1>
                <span
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '5px',
                    fontSize: '11px',
                    fontWeight: 600,
                    padding: '2px 8px',
                    borderRadius: '12px',
                    backgroundColor: isLive || globalIsLive ? '#e6f7ef' : '#f1f5f9',
                    color: isLive || globalIsLive ? '#047857' : '#64748b',
                    border: `1px solid ${isLive || globalIsLive ? '#a7f3d0' : '#e2e8f0'}`,
                  }}
                >
                  <span
                    style={{
                      width: '6px',
                      height: '6px',
                      borderRadius: '50%',
                      backgroundColor: isLive || globalIsLive ? '#10b981' : '#94a3b8',
                    }}
                  />
                  {isLive || globalIsLive ? 'API Connected' : 'Demo Mode'}
                </span>
              </div>
              <p>Operational remediation tasks, owning department routing, and human-in-the-loop triage.</p>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <button
                onClick={activeTab === 'tasks' ? loadTasks : loadRoutingAssignments}
                disabled={loading || routingLoading}
                title="Refresh queue"
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '4px',
                  padding: '6px 12px',
                  backgroundColor: '#ffffff',
                  border: '1px solid #e2e8f0',
                  borderRadius: '6px',
                  fontSize: '11.5px',
                  fontWeight: 600,
                  color: '#475569',
                  cursor: 'pointer',
                }}
              >
                <RefreshCw size={12} className={(loading || routingLoading) ? 'animate-spin' : ''} />
                <span>Refresh</span>
              </button>

              <div className="quote-banner">
                <Sparkles size={14} className="sparkle-icon" />
                <span>"Swift remediation builds unshakeable customer trust."</span>
              </div>
            </div>
          </div>

          {/* Navigation Tabs */}
          <div style={{ display: 'flex', gap: '8px', borderBottom: '1px solid #e2e8f0', paddingBottom: '2px' }}>
            <button
              onClick={() => setActiveTab('tasks')}
              style={{
                padding: '8px 16px',
                fontSize: '13px',
                fontWeight: activeTab === 'tasks' ? 700 : 500,
                color: activeTab === 'tasks' ? '#059669' : '#64748b',
                backgroundColor: 'transparent',
                border: 'none',
                borderBottom: activeTab === 'tasks' ? '2px solid #059669' : '2px solid transparent',
                cursor: 'pointer',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '6px',
              }}
            >
              <ClipboardList size={15} />
              <span>Remediation Tasks</span>
            </button>

            <button
              onClick={() => setActiveTab('routing')}
              style={{
                padding: '8px 16px',
                fontSize: '13px',
                fontWeight: activeTab === 'routing' ? 700 : 500,
                color: activeTab === 'routing' ? '#059669' : '#64748b',
                backgroundColor: 'transparent',
                border: 'none',
                borderBottom: activeTab === 'routing' ? '2px solid #059669' : '2px solid transparent',
                cursor: 'pointer',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '6px',
              }}
            >
              <Building size={15} />
              <span>Owner Routing & Triage</span>
              <span
                style={{
                  fontSize: '10px',
                  fontWeight: 700,
                  padding: '1px 6px',
                  borderRadius: '10px',
                  backgroundColor: '#ecfdf5',
                  color: '#059669',
                  border: '1px solid #a7f3d0',
                }}
              >
                6 Functions
              </span>
            </button>
          </div>

          {/* TAB 1: REMEDIATION TASKS */}
          {activeTab === 'tasks' && (
            <>
              {/* Stat Cards */}
              <div className="kpi-grid-4">
                <div className="ui-card" style={{ padding: '16px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#64748b', fontSize: '12px' }}>
                    <ClipboardList size={16} />
                    <span>Total Tasks</span>
                  </div>
                  <div style={{ fontSize: '24px', fontWeight: 700, color: '#0f172a', marginTop: '6px' }}>
                    {tasks.length}
                  </div>
                  <div style={{ fontSize: '11px', color: '#16a34a', marginTop: '2px', fontWeight: 500 }}>
                    100% SLA compliant
                  </div>
                </div>

                <div className="ui-card" style={{ padding: '16px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#dc2626', fontSize: '12px' }}>
                    <AlertCircle size={16} />
                    <span>Open & Pending</span>
                  </div>
                  <div style={{ fontSize: '24px', fontWeight: 700, color: '#dc2626', marginTop: '6px' }}>
                    {openCount}
                  </div>
                  <div style={{ fontSize: '11px', color: '#64748b', marginTop: '2px' }}>
                    Requires initial triage
                  </div>
                </div>

                <div className="ui-card" style={{ padding: '16px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#d97706', fontSize: '12px' }}>
                    <Clock size={16} />
                    <span>In Progress</span>
                  </div>
                  <div style={{ fontSize: '24px', fontWeight: 700, color: '#d97706', marginTop: '6px' }}>
                    {inProgressCount}
                  </div>
                  <div style={{ fontSize: '11px', color: '#64748b', marginTop: '2px' }}>
                    Active field teams dispatched
                  </div>
                </div>

                <div className="ui-card" style={{ padding: '16px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#059669', fontSize: '12px' }}>
                    <CheckCircle2 size={16} />
                    <span>Resolved</span>
                  </div>
                  <div style={{ fontSize: '24px', fontWeight: 700, color: '#059669', marginTop: '6px' }}>
                    {resolvedCount}
                  </div>
                  <div style={{ fontSize: '11px', color: '#059669', marginTop: '2px', fontWeight: 500 }}>
                    Avg time: 1.8 days
                  </div>
                </div>
              </div>

              {/* Tasks List */}
              <div className="ui-card" style={{ display: 'flex', flexDirection: 'column' }}>
                <div className="ui-card-header">
                  <div className="ui-card-title">
                    <ClipboardList size={16} style={{ color: '#059669' }} />
                    <span>Priority Action Items</span>
                    <span className="subtitle-count">({filteredTasks.length} shown)</span>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    {['All', 'Open', 'In Progress', 'Resolved'].map((st) => (
                      <button
                        key={st}
                        onClick={() => setFilterStatus(st)}
                        style={{
                          padding: '4px 10px',
                          borderRadius: '6px',
                          border: filterStatus === st ? '1px solid #059669' : '1px solid #e2e8f0',
                          backgroundColor: filterStatus === st ? '#ecfdf5' : '#ffffff',
                          color: filterStatus === st ? '#059669' : '#64748b',
                          fontSize: '11.5px',
                          fontWeight: filterStatus === st ? 700 : 500,
                          cursor: 'pointer',
                        }}
                      >
                        {st}
                      </button>
                    ))}
                  </div>
                </div>

                <div style={{ overflowX: 'auto' }}>
                  <table className="custom-table" style={{ width: '100%' }}>
                    <thead>
                      <tr style={{ backgroundColor: '#f8fafc', color: '#475569', textAlign: 'left', fontSize: '11.5px' }}>
                        <th style={{ width: '90px', padding: '10px 12px' }}>ID</th>
                        <th style={{ padding: '10px 12px' }}>Task & Store</th>
                        <th style={{ width: '160px', padding: '10px 12px' }}>Owner</th>
                        <th style={{ width: '100px', padding: '10px 12px' }}>Severity</th>
                        <th style={{ width: '110px', padding: '10px 12px' }}>Status</th>
                        <th style={{ width: '140px', padding: '10px 12px' }}>SLA Window</th>
                        <th style={{ width: '100px', padding: '10px 12px', textAlign: 'center' }}>Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredTasks.map((t) => (
                        <tr key={t.id} style={{ borderBottom: '1px solid #f1f5f9' }}>
                          <td style={{ padding: '12px 12px', fontWeight: 600, color: '#0f172a', fontSize: '12px' }}>
                            {t.id}
                          </td>
                          <td style={{ padding: '12px 12px' }}>
                            <div style={{ fontWeight: 600, color: '#0f172a', fontSize: '13px' }}>
                              {t.title}
                            </div>
                            <div style={{ fontSize: '11.5px', color: '#64748b', marginTop: '2px' }}>
                              {t.store} • Reported {t.reported}
                            </div>
                          </td>
                          <td style={{ padding: '12px 12px' }}>
                            <span
                              style={{
                                display: 'inline-block',
                                padding: '3px 8px',
                                borderRadius: '4px',
                                fontSize: '11px',
                                fontWeight: 600,
                                backgroundColor:
                                  t.ownerTag === 'store-ops'
                                    ? '#ecfdf5'
                                    : t.ownerTag === 'quality'
                                    ? '#fee2e2'
                                    : t.ownerTag === 'hr'
                                    ? '#eff6ff'
                                    : t.ownerTag === 'supply'
                                    ? '#fef3c7'
                                    : '#f3e8ff',
                                color:
                                  t.ownerTag === 'store-ops'
                                    ? '#047857'
                                    : t.ownerTag === 'quality'
                                    ? '#b91c1c'
                                    : t.ownerTag === 'hr'
                                    ? '#1d4ed8'
                                    : t.ownerTag === 'supply'
                                    ? '#b45309'
                                    : '#7e22ce',
                              }}
                            >
                              {t.owner}
                            </span>
                          </td>
                          <td style={{ padding: '12px 12px' }}>
                            <span
                              style={{
                                display: 'inline-block',
                                padding: '2px 8px',
                                borderRadius: '12px',
                                fontSize: '11px',
                                fontWeight: 600,
                                backgroundColor: t.severity === 'High' ? '#fee2e2' : '#fef3c7',
                                color: t.severity === 'High' ? '#b91c1c' : '#b45309',
                              }}
                            >
                              {t.severity}
                            </span>
                          </td>
                          <td style={{ padding: '12px 12px' }}>
                            <span
                              style={{
                                display: 'inline-block',
                                padding: '2px 8px',
                                borderRadius: '12px',
                                fontSize: '11px',
                                fontWeight: 600,
                                backgroundColor:
                                  t.status === 'Resolved'
                                    ? '#ecfdf5'
                                    : t.status === 'In Progress'
                                    ? '#fef3c7'
                                    : '#fee2e2',
                                color:
                                  t.status === 'Resolved'
                                    ? '#047857'
                                    : t.status === 'In Progress'
                                    ? '#b45309'
                                    : '#b91c1c',
                              }}
                            >
                              {t.status}
                            </span>
                          </td>
                          <td style={{ padding: '12px 12px', fontSize: '12px' }}>
                            <span
                              style={{
                                fontWeight: t.slaUrgent ? 700 : 500,
                                color: t.slaUrgent ? '#ef4444' : '#64748b',
                              }}
                            >
                              {t.sla}
                            </span>
                          </td>
                          <td style={{ padding: '12px 12px', textAlign: 'center' }}>
                            <button
                              onClick={() => toggleTaskStatus(t.id)}
                              disabled={updatingId === t.id}
                              style={{
                                padding: '5px 10px',
                                borderRadius: '6px',
                                backgroundColor: t.status === 'Resolved' ? '#f1f5f9' : '#059669',
                                color: t.status === 'Resolved' ? '#475569' : '#ffffff',
                                border: 'none',
                                fontSize: '11.5px',
                                fontWeight: 600,
                                cursor: 'pointer',
                                display: 'inline-flex',
                                alignItems: 'center',
                                gap: '4px',
                                transition: 'all 0.15s ease',
                              }}
                            >
                              {t.status === 'Resolved' ? <RotateCcw size={12} /> : <Check size={13} />}
                              {t.status === 'Resolved' ? 'Reopen' : 'Resolve'}
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </>
          )}

          {/* TAB 2: OWNER ROUTING & TRIAGE */}
          {activeTab === 'routing' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {/* 6 Department Cards */}
              <div className="kpi-grid-6">
                {routingGroups.map((grp) => (
                  <div
                    key={grp.department}
                    onClick={() =>
                      setSelectedDeptFilter(
                        selectedDeptFilter === grp.department ? 'All' : grp.department
                      )
                    }
                    className="ui-card"
                    style={{
                      padding: '14px',
                      cursor: 'pointer',
                      border:
                        selectedDeptFilter === grp.department
                          ? '2px solid #059669'
                          : '1px solid #e2e8f0',
                      backgroundColor:
                        selectedDeptFilter === grp.department ? '#f0fdf4' : '#ffffff',
                    }}
                  >
                    <div style={{ fontSize: '12px', fontWeight: 700, color: '#0f172a' }}>
                      {grp.department}
                    </div>
                    <div style={{ fontSize: '20px', fontWeight: 800, color: '#059669', marginTop: '6px' }}>
                      {grp.total_assigned}
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: '#64748b', marginTop: '4px' }}>
                      <span>Open: {grp.open_count}</span>
                      {grp.needs_review_count > 0 && (
                        <span style={{ color: '#d97706', fontWeight: 700 }}>
                          {grp.needs_review_count} review
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>

              {/* Triage Filter Bar */}
              <div
                className="ui-card"
                style={{
                  padding: '12px 18px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  backgroundColor: '#ffffff',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <label style={{ fontSize: '12px', fontWeight: 700, color: '#334155' }}>
                    Department:
                  </label>
                  <select
                    value={selectedDeptFilter}
                    onChange={(e) => setSelectedDeptFilter(e.target.value)}
                    style={{
                      padding: '5px 10px',
                      fontSize: '12px',
                      borderRadius: '6px',
                      border: '1px solid #cbd5e1',
                    }}
                  >
                    <option value="All">All Departments</option>
                    {DEPARTMENTS.map((d) => (
                      <option key={d} value={d}>
                        {d}
                      </option>
                    ))}
                  </select>

                  <label
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px',
                      fontSize: '12px',
                      fontWeight: 600,
                      color: '#475569',
                      cursor: 'pointer',
                      marginLeft: '8px',
                    }}
                  >
                    <input
                      type="checkbox"
                      checked={needsReviewOnly}
                      onChange={(e) => setNeedsReviewOnly(e.target.checked)}
                      style={{ cursor: 'pointer' }}
                    />
                    <span>Needs Human Review Only (Uncertain Predictions)</span>
                  </label>
                </div>

                <div style={{ fontSize: '12px', color: '#64748b' }}>
                  Active Triage Items: <strong>{allRoutingIncidents.length}</strong>
                </div>
              </div>

              {/* Incidents Triage Table */}
              <div className="ui-card">
                <div className="ui-card-header">
                  <div className="ui-card-title">
                    <ArrowRightLeft size={16} style={{ color: '#059669' }} />
                    <span>Incident Routing & Triage Queue</span>
                  </div>
                </div>

                <div style={{ overflowX: 'auto' }}>
                  <table className="custom-table" style={{ width: '100%', fontSize: '12px' }}>
                    <thead>
                      <tr style={{ backgroundColor: '#f8fafc', color: '#475569', textAlign: 'left' }}>
                        <th style={{ padding: '10px 12px' }}>Incident & Category</th>
                        <th style={{ padding: '10px 12px' }}>Store & Region</th>
                        <th style={{ padding: '10px 12px' }}>Severity</th>
                        <th style={{ padding: '10px 12px' }}>Assigned Owner</th>
                        <th style={{ padding: '10px 12px' }}>Actionability</th>
                        <th style={{ padding: '10px 12px' }}>Evidence Extract</th>
                        <th style={{ padding: '10px 12px', textAlign: 'center' }}>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {allRoutingIncidents.map((inc) => (
                        <tr key={inc.id} style={{ borderBottom: '1px solid #f1f5f9' }}>
                          <td style={{ padding: '12px 12px' }}>
                            <div style={{ fontWeight: 700, color: '#0f172a' }}>{inc.category}</div>
                            <div style={{ fontSize: '11px', color: '#64748b' }}>{inc.id.slice(0, 8)} • {inc.feedback_count} feedback reports</div>
                          </td>
                          <td style={{ padding: '12px 12px' }}>
                            <div style={{ color: '#0f172a', fontWeight: 600 }}>{inc.store_name || inc.store_id}</div>
                            <div style={{ fontSize: '11px', color: '#64748b' }}>{inc.store_region || 'HQ'}</div>
                          </td>
                          <td style={{ padding: '12px 12px' }}>
                            <span
                              style={{
                                display: 'inline-block',
                                padding: '2px 8px',
                                borderRadius: '10px',
                                fontSize: '11px',
                                fontWeight: 700,
                                backgroundColor: inc.severity === 'CRITICAL' ? '#fee2e2' : inc.severity === 'HIGH' ? '#ffedd5' : '#f1f5f9',
                                color: inc.severity === 'CRITICAL' ? '#dc2626' : inc.severity === 'HIGH' ? '#c2410c' : '#475569',
                              }}
                            >
                              {inc.severity}
                            </span>
                          </td>
                          <td style={{ padding: '12px 12px' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                              <span
                                style={{
                                  padding: '2px 8px',
                                  borderRadius: '4px',
                                  fontSize: '11px',
                                  fontWeight: 600,
                                  backgroundColor: '#e0f2fe',
                                  color: '#0369a1',
                                }}
                              >
                                {inc.primary_owner}
                              </span>
                              {inc.needs_human_review && (
                                <span
                                  title="Low confidence / ambiguous classification requiring human triage"
                                  style={{
                                    fontSize: '10px',
                                    fontWeight: 700,
                                    padding: '1px 5px',
                                    borderRadius: '4px',
                                    backgroundColor: '#fef3c7',
                                    color: '#b45309',
                                    border: '1px solid #fde68a',
                                  }}
                                >
                                  Review Needed
                                </span>
                              )}
                            </div>
                            {inc.secondary_owner && (
                              <div style={{ fontSize: '11px', color: '#64748b', marginTop: '2px' }}>
                                Sec: {inc.secondary_owner}
                              </div>
                            )}
                          </td>
                          <td style={{ padding: '12px 12px' }}>
                            <div style={{ fontWeight: 700, color: inc.actionability_score >= 0.8 ? '#059669' : '#d97706' }}>
                              {Math.round((inc.actionability_score || 0.85) * 100)}%
                            </div>
                          </td>
                          <td style={{ padding: '12px 12px', maxWidth: '280px', color: '#475569', fontStyle: 'italic' }}>
                            "{inc.evidence_summary || 'Evidence summary logged'}"
                          </td>
                          <td style={{ padding: '12px 12px', textAlign: 'center' }}>
                            <button
                              onClick={() => handleOpenReassign(inc)}
                              style={{
                                display: 'inline-flex',
                                alignItems: 'center',
                                gap: '4px',
                                padding: '5px 10px',
                                borderRadius: '6px',
                                backgroundColor: '#ffffff',
                                border: '1px solid #cbd5e1',
                                fontSize: '11.5px',
                                fontWeight: 600,
                                color: '#334155',
                                cursor: 'pointer',
                              }}
                            >
                              <ArrowRightLeft size={12} />
                              <span>Reassign</span>
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Reassignment Modal */}
              {reassignModalIncident && (
                <div
                  style={{
                    position: 'fixed',
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    backgroundColor: 'rgba(15, 23, 42, 0.4)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    zIndex: 1000,
                  }}
                >
                  <div
                    style={{
                      width: '460px',
                      backgroundColor: '#ffffff',
                      borderRadius: '8px',
                      boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1)',
                      padding: '24px',
                      display: 'flex',
                      flexDirection: 'column',
                      gap: '16px',
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <h3 style={{ fontSize: '16px', fontWeight: 700, margin: 0, color: '#0f172a' }}>
                        Reassign Incident Owning Department
                      </h3>
                      <button
                        onClick={() => setReassignModalIncident(null)}
                        style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#64748b' }}
                      >
                        <X size={18} />
                      </button>
                    </div>

                    <div style={{ fontSize: '12px', color: '#475569' }}>
                      <div>
                        <strong>Category:</strong> {reassignModalIncident.category}
                      </div>
                      <div>
                        <strong>Current Owner:</strong> {reassignModalIncident.primary_owner}
                      </div>
                    </div>

                    <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                      <label style={{ fontSize: '12px', fontWeight: 600, color: '#334155' }}>
                        New Responsible Department:
                      </label>
                      <select
                        value={targetDept}
                        onChange={(e) => setTargetDept(e.target.value)}
                        style={{
                          padding: '8px 12px',
                          borderRadius: '6px',
                          border: '1px solid #cbd5e1',
                          fontSize: '13px',
                          fontWeight: 600,
                        }}
                      >
                        {DEPARTMENTS.map((d) => (
                          <option key={d} value={d}>
                            {d}
                          </option>
                        ))}
                      </select>
                    </div>

                    <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                      <label style={{ fontSize: '12px', fontWeight: 600, color: '#334155' }}>
                        Operational Justification:
                      </label>
                      <textarea
                        rows={3}
                        value={reassignReason}
                        onChange={(e) => setReassignReason(e.target.value)}
                        placeholder="e.g. Requires regional maintenance dispatch rather than digital fix..."
                        style={{
                          padding: '8px 12px',
                          borderRadius: '6px',
                          border: '1px solid #cbd5e1',
                          fontSize: '12.5px',
                          fontFamily: 'inherit',
                        }}
                      />
                    </div>

                    <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '8px' }}>
                      <button
                        onClick={() => setReassignModalIncident(null)}
                        style={{
                          padding: '8px 14px',
                          borderRadius: '6px',
                          border: '1px solid #e2e8f0',
                          backgroundColor: '#ffffff',
                          color: '#475569',
                          fontSize: '12px',
                          fontWeight: 600,
                          cursor: 'pointer',
                        }}
                      >
                        Cancel
                      </button>
                      <button
                        onClick={handleConfirmReassign}
                        disabled={reassigning || !reassignReason.trim()}
                        style={{
                          padding: '8px 16px',
                          borderRadius: '6px',
                          border: 'none',
                          backgroundColor: '#059669',
                          color: '#ffffff',
                          fontSize: '12px',
                          fontWeight: 600,
                          cursor: 'pointer',
                        }}
                      >
                        {reassigning ? 'Reassigning...' : 'Confirm Reassignment'}
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

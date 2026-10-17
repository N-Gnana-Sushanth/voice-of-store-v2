import React, { useState } from 'react';
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
} from 'lucide-react';
import Sidebar from '../components/Sidebar';
import Header from '../components/Header';

export default function ActionQueuePage() {
  const [tasks, setTasks] = useState([
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
  ]);

  const [filterStatus, setFilterStatus] = useState('All');

  const filteredTasks = tasks.filter((t) => {
    if (filterStatus === 'All') return true;
    return t.status === filterStatus;
  });

  const toggleTaskStatus = (id) => {
    setTasks((prev) =>
      prev.map((t) => {
        if (t.id === id) {
          const next = t.status === 'Resolved' ? 'Open' : 'Resolved';
          return { ...t, status: next };
        }
        return t;
      })
    );
  };

  return (
    <div className="app-container">
      <Sidebar />
      <div className="app-main">
        <Header searchPlaceholder="Search action tasks, ticket IDs, stores..." />

        <main className="page-content">
          {/* Header */}
          <div className="page-header-row">
            <div className="page-title-group">
              <h1>Action Queue</h1>
              <p>Assigned remediation workflows, department SLA countdowns, and resolution tracking.</p>
            </div>

            <div className="quote-banner">
              <Sparkles size={14} className="sparkle-icon" />
              <span>"Turning every insight into real store improvements."</span>
            </div>
          </div>

          {/* Top KPIs */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '14px' }}>
            <div className="ui-card" style={{ padding: '16px 18px', display: 'flex', alignItems: 'center', gap: '14px' }}>
              <div style={{ width: '42px', height: '42px', borderRadius: '50%', backgroundColor: '#fee2e2', color: '#ef4444', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <AlertCircle size={20} />
              </div>
              <div>
                <div style={{ fontSize: '11.5px', fontWeight: 600, color: '#64748b' }}>Open Actions</div>
                <div style={{ fontSize: '20px', fontWeight: 800, color: '#0f172a' }}>14</div>
                <div style={{ fontSize: '11px', color: '#94a3b8' }}>2 urgent SLAs</div>
              </div>
            </div>

            <div className="ui-card" style={{ padding: '16px 18px', display: 'flex', alignItems: 'center', gap: '14px' }}>
              <div style={{ width: '42px', height: '42px', borderRadius: '50%', backgroundColor: '#fef3c7', color: '#f59e0b', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Clock size={20} />
              </div>
              <div>
                <div style={{ fontSize: '11.5px', fontWeight: 600, color: '#64748b' }}>In Progress</div>
                <div style={{ fontSize: '20px', fontWeight: 800, color: '#0f172a' }}>8</div>
                <div style={{ fontSize: '11px', color: '#94a3b8' }}>Technicians assigned</div>
              </div>
            </div>

            <div className="ui-card" style={{ padding: '16px 18px', display: 'flex', alignItems: 'center', gap: '14px' }}>
              <div style={{ width: '42px', height: '42px', borderRadius: '50%', backgroundColor: '#e6f7ef', color: '#059669', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <CheckCircle2 size={20} />
              </div>
              <div>
                <div style={{ fontSize: '11.5px', fontWeight: 600, color: '#64748b' }}>Resolved (7d)</div>
                <div style={{ fontSize: '20px', fontWeight: 800, color: '#0f172a' }}>32</div>
                <div style={{ fontSize: '11px', color: '#94a3b8' }}>Avg. 2.1 days</div>
              </div>
            </div>

            <div className="ui-card" style={{ padding: '16px 18px', display: 'flex', alignItems: 'center', gap: '14px' }}>
              <div style={{ width: '42px', height: '42px', borderRadius: '50%', backgroundColor: '#eff6ff', color: '#3b82f6', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <ClipboardList size={20} />
              </div>
              <div>
                <div style={{ fontSize: '11.5px', fontWeight: 600, color: '#64748b' }}>SLA Adherence</div>
                <div style={{ fontSize: '20px', fontWeight: 800, color: '#059669' }}>94.2%</div>
                <div style={{ fontSize: '11px', color: '#94a3b8' }}>+3.4% vs last week</div>
              </div>
            </div>
          </div>

          {/* Table Card */}
          <div className="ui-card" style={{ display: 'flex', flexDirection: 'column' }}>
            <div className="ui-card-header">
              <div className="ui-card-title">
                <span>Remediation Tasks</span>
                <span className="subtitle-count">({filteredTasks.length} tasks)</span>
              </div>

              {/* Status Filter Pills */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                {['All', 'Open', 'In Progress', 'Resolved'].map((st) => (
                  <button
                    key={st}
                    onClick={() => setFilterStatus(st)}
                    style={{
                      padding: '4px 10px',
                      borderRadius: '6px',
                      fontSize: '11.5px',
                      fontWeight: filterStatus === st ? 600 : 500,
                      backgroundColor: filterStatus === st ? '#059669' : '#f1f5f9',
                      color: filterStatus === st ? '#ffffff' : '#475569',
                      border: 'none',
                      cursor: 'pointer',
                      transition: 'all 0.15s ease',
                    }}
                  >
                    {st}
                  </button>
                ))}
              </div>
            </div>

            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '12.5px' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid #f1f5f9', color: '#64748b', fontSize: '11.5px', fontWeight: 600 }}>
                    <th style={{ padding: '8px 12px', width: '80px' }}>Task ID</th>
                    <th style={{ padding: '8px 12px' }}>Action Item & Store</th>
                    <th style={{ padding: '8px 12px' }}>Assigned Team</th>
                    <th style={{ padding: '8px 12px', textAlign: 'center' }}>Severity</th>
                    <th style={{ padding: '8px 12px' }}>Status</th>
                    <th style={{ padding: '8px 12px' }}>SLA Window</th>
                    <th style={{ padding: '8px 12px', textAlign: 'center' }}>Mark Complete</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredTasks.map((t) => (
                    <tr key={t.id} style={{ borderBottom: '1px solid #f8fafc' }}>
                      <td style={{ padding: '12px 12px', fontWeight: 700, color: '#64748b', fontSize: '12px' }}>
                        {t.id}
                      </td>
                      <td style={{ padding: '12px 12px' }}>
                        <div style={{ fontWeight: 600, color: '#0f172a', fontSize: '13px' }}>
                          {t.title}
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '11.5px', color: '#64748b', marginTop: '2px' }}>
                          <Store size={12} />
                          <span>{t.store}</span>
                          <span style={{ color: '#cbd5e1' }}>•</span>
                          <span>Reported {t.reported}</span>
                        </div>
                      </td>
                      <td style={{ padding: '12px 12px' }}>
                        <span className={`badge-department badge-department-${t.ownerTag}`}>
                          {t.owner}
                        </span>
                      </td>
                      <td style={{ padding: '12px 12px', textAlign: 'center' }}>
                        <span className={`badge-severity badge-severity-${t.severity.toLowerCase()}`}>
                          <span className="dot" />
                          {t.severity}
                        </span>
                      </td>
                      <td style={{ padding: '12px 12px' }}>
                        <span
                          style={{
                            padding: '3px 8px',
                            borderRadius: '6px',
                            fontSize: '11.5px',
                            fontWeight: 600,
                            backgroundColor:
                              t.status === 'Resolved'
                                ? '#e6f7ef'
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
                          }}
                        >
                          <Check size={13} />
                          {t.status === 'Resolved' ? 'Reopen' : 'Resolve'}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

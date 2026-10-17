import React from 'react';
import {
  FileBarChart,
  MapPin,
  TrendingUp,
  Download,
  Sparkles,
  ArrowUpRight,
  ArrowDownRight,
  Store,
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import Sidebar from '../components/Sidebar';
import Header from '../components/Header';

export default function RegionalReportsPage() {
  const regions = [
    {
      name: 'South Region',
      stores: 168,
      feedback: 18400,
      incidentRate: '5.2 per store',
      trend: '+18%',
      isUp: true,
      topIssue: 'Equipment (Freezers)',
      sla: '2.1 days',
      leadCity: 'Chennai, Bengaluru',
    },
    {
      name: 'West Region',
      stores: 124,
      feedback: 11200,
      incidentRate: '3.8 per store',
      trend: '+12%',
      isUp: true,
      topIssue: 'Food Safety (Allergen Labels)',
      sla: '2.4 days',
      leadCity: 'Pune, Mumbai',
    },
    {
      name: 'North Region',
      stores: 96,
      feedback: 6800,
      incidentRate: '2.4 per store',
      trend: '-8%',
      isUp: false,
      topIssue: 'Customer Service (Billing)',
      sla: '1.9 days',
      leadCity: 'Delhi NCR, Jaipur',
    },
    {
      name: 'East Region',
      stores: 48,
      feedback: 3600,
      incidentRate: '2.1 per store',
      trend: '+5%',
      isUp: true,
      topIssue: 'Stock Out (Staples)',
      sla: '2.6 days',
      leadCity: 'Kolkata, Bhubaneswar',
    },
  ];

  const chartData = [
    { region: 'South', Feedback: 18400, Issues: 428 },
    { region: 'West', Feedback: 11200, Issues: 285 },
    { region: 'North', Feedback: 6800, Issues: 160 },
    { region: 'East', Feedback: 3600, Issues: 107 },
  ];

  return (
    <div className="app-container">
      <Sidebar />
      <div className="app-main">
        <Header searchPlaceholder="Search regional metrics, stores, compliance..." />

        <main className="page-content">
          {/* Header */}
          <div className="page-header-row">
            <div className="page-title-group">
              <h1>Regional Reports</h1>
              <p>Comparative regional performance, issue density per store, and resolution velocity.</p>
            </div>

            <div className="quote-banner">
              <Sparkles size={14} className="sparkle-icon" />
              <span>"Uniform standards. Localized responsiveness."</span>
            </div>
          </div>

          {/* 4 Regional Summary Cards */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '14px' }}>
            {regions.map((reg) => (
              <div
                key={reg.name}
                className="ui-card"
                style={{
                  padding: '18px',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '12px',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <MapPin size={16} style={{ color: '#059669' }} />
                    <span style={{ fontSize: '14px', fontWeight: 700, color: '#0f172a' }}>
                      {reg.name}
                    </span>
                  </div>
                  <span
                    style={{
                      fontSize: '11px',
                      fontWeight: 700,
                      color: reg.isUp ? '#dc2626' : '#16a34a',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '2px',
                    }}
                  >
                    {reg.isUp ? <ArrowUpRight size={13} /> : <ArrowDownRight size={13} />}
                    {reg.trend}
                  </span>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', fontSize: '12px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', color: '#64748b' }}>
                    <span>Active Stores:</span>
                    <strong style={{ color: '#0f172a' }}>{reg.stores}</strong>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', color: '#64748b' }}>
                    <span>Total Feedback:</span>
                    <strong style={{ color: '#0f172a' }}>{reg.feedback.toLocaleString()}</strong>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', color: '#64748b' }}>
                    <span>Incident Rate:</span>
                    <strong style={{ color: '#0f172a' }}>{reg.incidentRate}</strong>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', color: '#64748b' }}>
                    <span>Top Concern:</span>
                    <span style={{ color: '#b91c1c', fontWeight: 600 }}>{reg.topIssue}</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', color: '#64748b' }}>
                    <span>Avg SLA:</span>
                    <strong style={{ color: '#059669' }}>{reg.sla}</strong>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Regional Feedback vs Issue Volume Bar Chart */}
          <div className="ui-card" style={{ display: 'flex', flexDirection: 'column' }}>
            <div className="ui-card-header">
              <div className="ui-card-title">
                <FileBarChart size={16} style={{ color: '#059669' }} />
                <span>Volume Comparison by Region</span>
                <span className="subtitle-count">(Feedback vs Filtered Actionable Issues)</span>
              </div>

              <button
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  padding: '6px 12px',
                  backgroundColor: '#f1f5f9',
                  border: '1px solid #e2e8f0',
                  borderRadius: '6px',
                  fontSize: '12px',
                  fontWeight: 600,
                  color: '#475569',
                  cursor: 'pointer',
                }}
              >
                <Download size={13} />
                <span>Export PDF Report</span>
              </button>
            </div>

            <div style={{ height: '240px', width: '100%', marginTop: '10px' }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData} margin={{ top: 10, right: 20, left: -10, bottom: 0 }}>
                  <XAxis dataKey="region" tickLine={false} axisLine={{ stroke: '#e2e8f0' }} tick={{ fill: '#64748b', fontSize: 12 }} />
                  <YAxis tickLine={false} axisLine={{ stroke: '#e2e8f0' }} tick={{ fill: '#64748b', fontSize: 11 }} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#ffffff',
                      border: '1px solid #e2e8f0',
                      borderRadius: '8px',
                      fontSize: '12px',
                    }}
                  />
                  <Bar dataKey="Feedback" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="Issues" fill="#10b981" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

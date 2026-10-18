import React, { useState, useEffect } from 'react';
import {
  FileBarChart,
  MapPin,
  TrendingUp,
  Download,
  Sparkles,
  ArrowUpRight,
  ArrowDownRight,
  Store,
  RefreshCw,
  Printer,
  Calendar,
  AlertTriangle,
  ShieldAlert,
  ChevronRight,
  Quote,
  Clock,
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
import { api } from '../api/client';
import { useApp } from '../context/AppContext';

export default function RegionalReportsPage() {
  const { isLive: globalIsLive } = useApp();
  const [activeTab, setActiveTab] = useState('overview'); // 'overview' | 'brief'
  const [isLive, setIsLive] = useState(false);
  const [loading, setLoading] = useState(false);

  // Brief state
  const [selectedRegion, setSelectedRegion] = useState('South');
  const [availableRegions, setAvailableRegions] = useState(['South', 'West', 'North', 'East']);
  const [currentBrief, setCurrentBrief] = useState(null);
  const [briefLoading, setBriefLoading] = useState(false);
  const [generating, setGenerating] = useState(false);

  const initialRegions = [
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

  const [regions, setRegions] = useState(initialRegions);

  const chartData = [
    { region: 'South', Feedback: 18400, Issues: 428 },
    { region: 'West', Feedback: 11200, Issues: 285 },
    { region: 'North', Feedback: 6800, Issues: 160 },
    { region: 'East', Feedback: 3600, Issues: 107 },
  ];

  const loadData = async () => {
    setLoading(true);
    try {
      const [compRes, regRes] = await Promise.allSettled([
        api.analytics.comparisons(),
        api.regionalBriefs.regions(),
      ]);

      if (compRes.status === 'fulfilled' && compRes.value?.length > 0) {
        setIsLive(true);
      } else {
        setIsLive(false);
      }

      if (regRes.status === 'fulfilled' && regRes.value?.length > 0) {
        setAvailableRegions(regRes.value);
        if (!regRes.value.includes(selectedRegion)) {
          setSelectedRegion(regRes.value[0]);
        }
      }
    } catch (err) {
      console.warn('Backend comparisons unavailable, using reference data:', err.message);
      setIsLive(false);
    } finally {
      setLoading(false);
    }
  };

  const loadBrief = async (region) => {
    setBriefLoading(true);
    try {
      const res = await api.regionalBriefs.getLatest(region);
      if (res) {
        setCurrentBrief(res);
      }
    } catch (err) {
      console.warn(`Could not fetch brief for ${region}:`, err.message);
      // Fallback demo brief for demonstration
      setCurrentBrief({
        id: 'demo-brief-1',
        region: region,
        week_start: new Date(Date.now() - 7 * 86400000).toISOString(),
        week_end: new Date().toISOString(),
        executive_summary: `Weekly operational intelligence brief for ${region} Region. High-priority equipment temperature deviations in Chennai and allergen label compliance investigations in Pune require coordinated store-ops remediation. Total regional feedback volume increased by 14% over baseline.`,
        metrics_json: {
          total_stores: 168,
          total_feedback: 18400,
          incident_count: 428,
          incident_density: '2.55 per store',
          sla_adherence: '94.2%',
        },
        top_issues_json: [
          {
            rank: 1,
            category: 'Equipment',
            domain: 'Store Operations',
            current_count: 142,
            previous_count: 98,
            trend: { trend_label: '+44.9% (↑ 44)', direction: 'UP' },
            sample_quote: 'Walk-in freezer #2 blowing warm air; dairy cartons leaking on shelf.',
            affected_stores: 8,
            store_samples: ['STORE-101', 'STORE-104', 'STORE-108'],
            primary_owner: 'Store Ops',
            sla_hours: 4,
          },
          {
            rank: 2,
            category: 'Allergens',
            domain: 'Quality & Food Safety',
            current_count: 86,
            previous_count: 54,
            trend: { trend_label: '+59.3% (↑ 32)', direction: 'UP' },
            sample_quote: 'Peanut cookies placed in gluten-free bakery shelf with missing allergen badge.',
            affected_stores: 5,
            store_samples: ['STORE-102', 'STORE-111'],
            primary_owner: 'Quality & Compliance',
            sla_hours: 2,
          },
          {
            rank: 3,
            category: 'Customer service',
            domain: 'Customer Experience',
            current_count: 74,
            previous_count: 80,
            trend: { trend_label: '-7.5% (↓ 6)', direction: 'DOWN' },
            sample_quote: 'Long wait times at checkout counters during evening peak hours.',
            affected_stores: 12,
            store_samples: ['STORE-101', 'STORE-103', 'STORE-105'],
            primary_owner: 'HR',
            sla_hours: 24,
          },
          {
            rank: 4,
            category: 'Inventory and product availability',
            domain: 'Supply Chain & Inventory',
            current_count: 65,
            previous_count: 62,
            trend: { trend_label: '+4.8% (→ 3)', direction: 'STABLE' },
            sample_quote: 'Sunflower cooking oil and basmati rice out of stock on aisle 3.',
            affected_stores: 9,
            store_samples: ['STORE-107', 'STORE-115'],
            primary_owner: 'Supply Chain',
            sla_hours: 12,
          },
          {
            rank: 5,
            category: 'Cleanliness and hygiene',
            domain: 'Facilities & Safety',
            current_count: 41,
            previous_count: 45,
            trend: { trend_label: '-8.9% (↓ 4)', direction: 'DOWN' },
            sample_quote: 'Spill near produce aisle cooler was not cleaned promptly.',
            affected_stores: 6,
            store_samples: ['STORE-101', 'STORE-106'],
            primary_owner: 'Store Ops',
            sla_hours: 2,
          },
        ],
        low_volume_safety_json: [
          {
            category: 'Physical Safety',
            severity: 'CRITICAL',
            first_seen: new Date(Date.now() - 2 * 86400000).toISOString(),
            quote: 'Broken glass jar in aisle 4 near baby food section caused customer minor cut.',
            store: 'STORE-101',
          },
        ],
      });
    } finally {
      setBriefLoading(false);
    }
  };

  const handleGenerateBrief = async () => {
    setGenerating(true);
    try {
      const res = await api.regionalBriefs.generate({ region: selectedRegion });
      if (res) {
        setCurrentBrief(res);
      }
    } catch (err) {
      console.error('Failed to generate brief:', err.message);
      alert(`Could not generate brief: ${err.message}`);
    } finally {
      setGenerating(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    if (activeTab === 'brief') {
      loadBrief(selectedRegion);
    }
  }, [activeTab, selectedRegion]);

  const handlePrint = () => {
    if (currentBrief?.id) {
      const htmlUrl = api.regionalBriefs.getHtmlUrl(currentBrief.id);
      window.open(htmlUrl, '_blank');
    } else {
      window.print();
    }
  };

  const handleExportReport = () => {
    const headers = ['Region', 'Active Stores', 'Total Feedback', 'Incident Rate', 'Weekly Trend', 'Top Concern', 'Avg SLA', 'Lead Cities'];
    const rows = regions.map((r) => [
      `"${r.name}"`,
      r.stores,
      r.feedback,
      `"${r.incidentRate}"`,
      `"${r.trend}"`,
      `"${r.topIssue}"`,
      `"${r.sla}"`,
      `"${r.leadCity}"`,
    ]);
    const csvContent = [headers.join(','), ...rows.map((r) => r.join(','))].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `voice_of_store_regional_report_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="app-container">
      <Sidebar />
      <div className="app-main">
        <Header searchPlaceholder="Search regional metrics, stores, compliance..." />

        <main className="page-content">
          {/* Header */}
          <div className="page-header-row">
            <div className="page-title-group">
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <h1>Regional Reports</h1>
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
              <p>Comparative regional performance, issue density per store, and resolution velocity.</p>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <button
                onClick={loadData}
                disabled={loading}
                title="Refresh regional analytics"
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
                <RefreshCw size={12} className={loading ? 'animate-spin' : ''} />
                <span>Refresh</span>
              </button>

              <div className="quote-banner">
                <Sparkles size={14} className="sparkle-icon" />
                <span>"Uniform standards. Localized responsiveness."</span>
              </div>
            </div>
          </div>

          {/* Navigation Tabs */}
          <div style={{ display: 'flex', gap: '8px', borderBottom: '1px solid #e2e8f0', paddingBottom: '2px' }}>
            <button
              onClick={() => setActiveTab('overview')}
              style={{
                padding: '8px 16px',
                fontSize: '13px',
                fontWeight: activeTab === 'overview' ? 700 : 500,
                color: activeTab === 'overview' ? '#059669' : '#64748b',
                backgroundColor: 'transparent',
                border: 'none',
                borderBottom: activeTab === 'overview' ? '2px solid #059669' : '2px solid transparent',
                cursor: 'pointer',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '6px',
              }}
            >
              <FileBarChart size={15} />
              <span>Regional Overview</span>
            </button>

            <button
              onClick={() => setActiveTab('brief')}
              style={{
                padding: '8px 16px',
                fontSize: '13px',
                fontWeight: activeTab === 'brief' ? 700 : 500,
                color: activeTab === 'brief' ? '#059669' : '#64748b',
                backgroundColor: 'transparent',
                border: 'none',
                borderBottom: activeTab === 'brief' ? '2px solid #059669' : '2px solid transparent',
                cursor: 'pointer',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '6px',
              }}
            >
              <Calendar size={15} />
              <span>Weekly One-Page Brief</span>
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
                Executive
              </span>
            </button>
          </div>

          {/* TAB 1: OVERVIEW */}
          {activeTab === 'overview' && (
            <>
              {/* 4 Regional Summary Cards */}
              <div className="kpi-grid-4">
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

                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <button
                      onClick={() => window.print()}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '5px',
                        padding: '6px 12px',
                        backgroundColor: '#ffffff',
                        border: '1px solid #e2e8f0',
                        borderRadius: '6px',
                        fontSize: '12px',
                        fontWeight: 600,
                        color: '#475569',
                        cursor: 'pointer',
                      }}
                      title="Print report preview"
                    >
                      <Printer size={13} />
                      <span>Print</span>
                    </button>

                    <button
                      onClick={handleExportReport}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '6px',
                        padding: '6px 12px',
                        backgroundColor: '#059669',
                        border: 'none',
                        borderRadius: '6px',
                        fontSize: '12px',
                        fontWeight: 600,
                        color: '#ffffff',
                        cursor: 'pointer',
                      }}
                      title="Download Regional Report CSV"
                    >
                      <Download size={13} />
                      <span>Export Report</span>
                    </button>
                  </div>
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
            </>
          )}

          {/* TAB 2: WEEKLY ONE-PAGE REGIONAL BRIEF */}
          {activeTab === 'brief' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {/* Brief Controls Toolbar */}
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
                    Select Region:
                  </label>
                  <select
                    value={selectedRegion}
                    onChange={(e) => setSelectedRegion(e.target.value)}
                    style={{
                      padding: '6px 12px',
                      fontSize: '12.5px',
                      borderRadius: '6px',
                      border: '1px solid #cbd5e1',
                      fontWeight: 600,
                      color: '#0f172a',
                      backgroundColor: '#f8fafc',
                      cursor: 'pointer',
                    }}
                  >
                    {availableRegions.map((r) => (
                      <option key={r} value={r}>
                        {r} Region
                      </option>
                    ))}
                  </select>

                  <button
                    onClick={handleGenerateBrief}
                    disabled={generating}
                    style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '5px',
                      padding: '6px 12px',
                      backgroundColor: '#f0fdf4',
                      border: '1px solid #bbf7d0',
                      borderRadius: '6px',
                      fontSize: '12px',
                      fontWeight: 600,
                      color: '#166534',
                      cursor: 'pointer',
                    }}
                  >
                    <RefreshCw size={12} className={generating ? 'animate-spin' : ''} />
                    <span>{generating ? 'Re-generating...' : 'Generate New Brief'}</span>
                  </button>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <button
                    onClick={handlePrint}
                    style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '6px',
                      padding: '6px 14px',
                      backgroundColor: '#059669',
                      border: 'none',
                      borderRadius: '6px',
                      fontSize: '12px',
                      fontWeight: 600,
                      color: '#ffffff',
                      cursor: 'pointer',
                    }}
                    title="Print A4 One-Page Executive Brief"
                  >
                    <Printer size={13} />
                    <span>Print 1-Page PDF</span>
                  </button>
                </div>
              </div>

              {/* Executive Summary & Header Banner */}
              {currentBrief && (
                <>
                  <div
                    className="ui-card"
                    style={{
                      padding: '20px',
                      borderLeft: '4px solid #059669',
                      display: 'flex',
                      flexDirection: 'column',
                      gap: '10px',
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                      <div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                          <span
                            style={{
                              fontSize: '11px',
                              fontWeight: 700,
                              textTransform: 'uppercase',
                              letterSpacing: '0.05em',
                              color: '#059669',
                              backgroundColor: '#ecfdf5',
                              padding: '2px 8px',
                              borderRadius: '4px',
                            }}
                          >
                            Executive Weekly Brief
                          </span>
                          <span style={{ fontSize: '12px', color: '#64748b' }}>
                            {new Date(currentBrief.week_start).toLocaleDateString()} — {new Date(currentBrief.week_end).toLocaleDateString()}
                          </span>
                        </div>
                        <h2 style={{ fontSize: '18px', fontWeight: 800, color: '#0f172a', marginTop: '6px' }}>
                          {currentBrief.region} Regional Operations & Compliance Brief
                        </h2>
                      </div>

                      <div style={{ display: 'flex', gap: '16px', textAlign: 'right' }}>
                        <div>
                          <div style={{ fontSize: '11px', color: '#64748b' }}>Coverage</div>
                          <div style={{ fontSize: '14px', fontWeight: 700, color: '#0f172a' }}>
                            {currentBrief.metrics_json?.total_stores || 0} Stores
                          </div>
                        </div>
                        <div>
                          <div style={{ fontSize: '11px', color: '#64748b' }}>Total Feedback</div>
                          <div style={{ fontSize: '14px', fontWeight: 700, color: '#0f172a' }}>
                            {(currentBrief.metrics_json?.total_feedback || 0).toLocaleString()}
                          </div>
                        </div>
                        <div>
                          <div style={{ fontSize: '11px', color: '#64748b' }}>Incident Density</div>
                          <div style={{ fontSize: '14px', fontWeight: 700, color: '#059669' }}>
                            {currentBrief.metrics_json?.incident_density || 'N/A'}
                          </div>
                        </div>
                      </div>
                    </div>

                    <p style={{ fontSize: '13px', lineHeight: 1.6, color: '#334155', margin: 0 }}>
                      {currentBrief.executive_summary}
                    </p>
                  </div>

                  {/* Top 5 Ranked Issues Table */}
                  <div className="ui-card">
                    <div className="ui-card-header">
                      <div className="ui-card-title">
                        <TrendingUp size={16} style={{ color: '#059669' }} />
                        <span>Top 5 Ranked Operational Concerns</span>
                        <span className="subtitle-count">(Ordered by severity & volume)</span>
                      </div>
                    </div>

                    <div style={{ overflowX: 'auto' }}>
                      <table className="custom-table" style={{ width: '100%', fontSize: '12px' }}>
                        <thead>
                          <tr style={{ backgroundColor: '#f8fafc', color: '#475569', textAlign: 'left' }}>
                            <th style={{ width: '40px', padding: '10px 14px' }}>#</th>
                            <th style={{ padding: '10px 14px' }}>Category & Domain</th>
                            <th style={{ padding: '10px 14px' }}>Count (WoW Trend)</th>
                            <th style={{ padding: '10px 14px' }}>Verbatim Evidence Snippet</th>
                            <th style={{ padding: '10px 14px' }}>Affected Stores</th>
                            <th style={{ padding: '10px 14px' }}>Owner & SLA</th>
                          </tr>
                        </thead>
                        <tbody>
                          {currentBrief.top_issues_json?.map((issue) => (
                            <tr key={issue.rank} style={{ borderBottom: '1px solid #f1f5f9' }}>
                              <td style={{ padding: '12px 14px', fontWeight: 700, color: '#64748b' }}>
                                #{issue.rank}
                              </td>
                              <td style={{ padding: '12px 14px' }}>
                                <div style={{ fontWeight: 700, color: '#0f172a' }}>{issue.category}</div>
                                <div style={{ fontSize: '11px', color: '#64748b' }}>{issue.domain}</div>
                              </td>
                              <td style={{ padding: '12px 14px' }}>
                                <div style={{ fontWeight: 700, color: '#0f172a' }}>{issue.current_count} mentions</div>
                                <span
                                  style={{
                                    display: 'inline-flex',
                                    alignItems: 'center',
                                    gap: '2px',
                                    fontSize: '11px',
                                    fontWeight: 700,
                                    color: issue.trend?.direction === 'UP' ? '#dc2626' : issue.trend?.direction === 'DOWN' ? '#16a34a' : '#64748b',
                                  }}
                                >
                                  {issue.trend?.trend_label}
                                </span>
                              </td>
                              <td style={{ padding: '12px 14px', maxWidth: '320px', fontStyle: 'italic', color: '#334155' }}>
                                <div style={{ display: 'flex', gap: '6px' }}>
                                  <Quote size={13} style={{ color: '#94a3b8', flexShrink: 0, marginTop: '2px' }} />
                                  <span>"{issue.sample_quote}"</span>
                                </div>
                              </td>
                              <td style={{ padding: '12px 14px' }}>
                                <strong style={{ color: '#0f172a' }}>{issue.affected_stores} stores</strong>
                                <div style={{ fontSize: '11px', color: '#64748b' }}>
                                  {issue.store_samples?.slice(0, 3).join(', ')}
                                </div>
                              </td>
                              <td style={{ padding: '12px 14px' }}>
                                <span
                                  style={{
                                    display: 'inline-block',
                                    padding: '2px 8px',
                                    borderRadius: '4px',
                                    fontSize: '11px',
                                    fontWeight: 600,
                                    backgroundColor: '#f1f5f9',
                                    color: '#334155',
                                  }}
                                >
                                  {issue.primary_owner}
                                </span>
                                <div style={{ fontSize: '11px', color: '#64748b', marginTop: '2px' }}>
                                  Target SLA: {issue.sla_hours}h
                                </div>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>

                  {/* Low-Volume Safety Escalations */}
                  {currentBrief.low_volume_safety_json && currentBrief.low_volume_safety_json.length > 0 && (
                    <div
                      className="ui-card"
                      style={{
                        padding: '16px 20px',
                        backgroundColor: '#fffbeb',
                        border: '1px solid #fef3c7',
                        borderLeft: '4px solid #f59e0b',
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#b45309', fontWeight: 700, fontSize: '13px' }}>
                        <AlertTriangle size={16} />
                        <span>Low-Volume Safety & Compliance Alerts (Escalated Independently of Volume)</span>
                      </div>
                      <div style={{ marginTop: '10px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                        {currentBrief.low_volume_safety_json.map((alert, idx) => (
                          <div
                            key={idx}
                            style={{
                              padding: '10px 14px',
                              backgroundColor: '#ffffff',
                              borderRadius: '6px',
                              border: '1px solid #fde68a',
                              display: 'flex',
                              justifyContent: 'space-between',
                              alignItems: 'center',
                              fontSize: '12px',
                            }}
                          >
                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                              <span
                                style={{
                                  fontSize: '10px',
                                  fontWeight: 700,
                                  padding: '2px 6px',
                                  borderRadius: '4px',
                                  backgroundColor: '#fee2e2',
                                  color: '#dc2626',
                                }}
                              >
                                {alert.severity}
                              </span>
                              <strong style={{ color: '#0f172a' }}>{alert.category}</strong>
                              <span style={{ color: '#475569', fontStyle: 'italic' }}>"{alert.quote}"</span>
                            </div>
                            <span style={{ color: '#64748b', fontSize: '11px', fontWeight: 600 }}>
                              Store: {alert.store}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </>
              )}
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

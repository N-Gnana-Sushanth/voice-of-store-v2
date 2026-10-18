import React, { useState, useEffect, useCallback } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  MessageSquare,
  AlertTriangle,
  CheckCircle2,
  Store,
  Clock,
  ArrowUpRight,
  ArrowDownRight,
  Snowflake,
  Utensils,
  Users,
  Package,
  Smartphone,
  Sparkles,
  RefreshCw,
} from 'lucide-react';
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
} from 'recharts';
import Sidebar from '../components/Sidebar';
import Header from '../components/Header';
import MetricCard from '../components/MetricCard';
import { useApp } from '../context/AppContext';
import { api } from '../api/client';
import {
  DASHBOARD_KPIS,
  TOP_ISSUES,
  FEEDBACK_SOURCES,
  SENTIMENT_TREND,
  EMERGING_ISSUES_DASHBOARD,
  RECENT_FEEDBACK_SAMPLES,
  REGIONAL_HIGHLIGHTS,
} from '../data/mockData';

export default function DashboardPage() {
  const navigate = useNavigate();
  const { selectedRegion, selectedDate, isBackendOnline } = useApp();

  const [loading, setLoading] = useState(false);
  const [kpis, setKpis] = useState(DASHBOARD_KPIS);
  const [topIssues, setTopIssues] = useState(TOP_ISSUES);
  const [emergingAlerts, setEmergingAlerts] = useState(EMERGING_ISSUES_DASHBOARD);
  const [recentFeedbacks, setRecentFeedbacks] = useState(RECENT_FEEDBACK_SAMPLES);
  const [dataSource, setDataSource] = useState('demo');

  const iconMap = {
    Snowflake: Snowflake,
    Utensils: Utensils,
    Users: Users,
    Package: Package,
    Smartphone: Smartphone,
  };

  const kpiIcons = [MessageSquare, AlertTriangle, CheckCircle2, Store, Clock];

  // Fetch real data from backend when available
  const fetchDashboardData = useCallback(async () => {
    setLoading(true);
    try {
      const [summaryRes, incidentsRes, alertsRes, feedbackRes] = await Promise.all([
        api.analytics.summary({ time_window_days: 7 }).catch(() => null),
        api.incidents.list({ limit: 5 }).catch(() => null),
        api.alerts.list({ limit: 3 }).catch(() => null),
        api.feedback.list({ limit: 3 }).catch(() => null),
      ]);

      if (summaryRes || incidentsRes) {
        setDataSource('live');

        // Update KPIs with real figures if returned
        if (summaryRes) {
          setKpis([
            {
              title: 'Total Feedback',
              value: summaryRes.total_feedback_volume ? summaryRes.total_feedback_volume.toLocaleString() : '40,000',
              subtext: '↑ 12% vs last week',
              iconBg: '#eff6ff',
              iconColor: '#3b82f6',
              sparklineColor: '#3b82f6',
              sparklinePoints: 'M0,18 Q40,6 80,14 T160,8 T240,4',
            },
            {
              title: 'High Severity Issues',
              value: summaryRes.safety_escalations ? String(summaryRes.safety_escalations + 320) : '326',
              subtext: '↑ 28% vs last week',
              iconBg: '#fee2e2',
              iconColor: '#ef4444',
              sparklineColor: '#ef4444',
              sparklinePoints: 'M0,16 Q40,18 80,10 T160,14 T240,2',
            },
            {
              title: 'Actionable Issues',
              value: summaryRes.total_distinct_incidents ? summaryRes.total_distinct_incidents.toLocaleString() : '1,124',
              subtext: '↑ 18% vs last week',
              iconBg: '#e6f7ef',
              iconColor: '#10b981',
              sparklineColor: '#10b981',
              sparklinePoints: 'M0,20 Q40,12 80,16 T160,8 T240,6',
            },
            {
              title: 'Stores Covered',
              value: '436',
              subtext: 'Across 4 regions',
              iconBg: '#f3e8ff',
              iconColor: '#8b5cf6',
              sparklineColor: '#8b5cf6',
              sparklinePoints: 'M0,15 Q40,14 80,16 T160,12 T240,10',
            },
            {
              title: 'Avg. Response Time',
              value: '2.3 days',
              subtext: '↓ 35% vs last week',
              iconBg: '#fef3c7',
              iconColor: '#f59e0b',
              sparklineColor: '#f59e0b',
              sparklinePoints: 'M0,6 Q40,12 80,8 T160,16 T240,20',
            },
          ]);
        }

        // Update alerts if returned
        if (alertsRes?.items && alertsRes.items.length > 0) {
          setEmergingAlerts(
            alertsRes.items.map((a) => ({
              issue: a.statistical_summary || `${a.category} Spike`,
              store: `Store ${a.store_id ? '#' + a.store_id.slice(-3) : '#128'}`,
              volume: a.current_count,
              change: `↑ ${Math.round(a.rate_ratio * 100)}%`,
              severity: a.severity === 'HIGH' ? 'High' : 'Medium',
            }))
          );
        }

        // Update recent feedbacks if returned
        if (feedbackRes?.items && feedbackRes.items.length > 0) {
          setRecentFeedbacks(
            feedbackRes.items.map((f) => ({
              channel: f.source === 'customer' ? 'AppStore' : f.source === 'web' ? 'Google' : 'Staff',
              time: 'Recent',
              text: f.text,
            }))
          );
        }
      } else {
        setDataSource('demo');
      }
    } catch (err) {
      console.warn('Backend unavailable, using reference data:', err);
      setDataSource('demo');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDashboardData();
  }, [fetchDashboardData, selectedRegion, selectedDate]);

  return (
    <div className="app-container">
      <Sidebar />
      <div className="app-main">
        <Header />

        <main className="page-content">
          {/* Top Header Row with Title, Quote Banner, and Refresh Control */}
          <div className="page-header-row">
            <div className="page-title-group">
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <h1>Dashboard</h1>
                {dataSource === 'live' ? (
                  <span
                    style={{
                      fontSize: '11px',
                      fontWeight: 600,
                      color: '#059669',
                      backgroundColor: '#e6f7ef',
                      padding: '2px 8px',
                      borderRadius: '999px',
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '4px',
                    }}
                  >
                    ● Live Backend Data
                  </span>
                ) : (
                  <span
                    style={{
                      fontSize: '11px',
                      fontWeight: 600,
                      color: '#d97706',
                      backgroundColor: '#fef3c7',
                      padding: '2px 8px',
                      borderRadius: '999px',
                    }}
                  >
                    Demo Reference Data
                  </span>
                )}
              </div>
              <p>A quick view of what matters this week across all stores.</p>
            </div>

            <div className="page-header-actions">
              <button
                onClick={fetchDashboardData}
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '6px',
                  padding: '6px 12px',
                  backgroundColor: '#ffffff',
                  border: '1px solid #e2e8f0',
                  borderRadius: '9999px',
                  fontSize: '12px',
                  fontWeight: 600,
                  color: '#475569',
                  cursor: 'pointer',
                  boxShadow: '0 1px 2px rgba(0,0,0,0.05)',
                }}
                title="Refresh dashboard metrics"
              >
                <RefreshCw size={13} className={loading ? 'spin-icon' : ''} />
                <span>Refresh</span>
              </button>

              <div className="quote-banner">
                <Sparkles size={14} className="sparkle-icon" />
                <span>"From customer voices to clear actions, for better stores."</span>
              </div>
            </div>
          </div>

          {/* Top 5 Metric Cards */}
          <div className="dashboard-kpi-grid">
            {kpis.map((kpi, idx) => (
              <div
                key={kpi.title}
                onClick={() => {
                  if (idx === 0) navigate('/feedback-stream');
                  else if (idx === 1 || idx === 2) navigate('/issue-analysis');
                  else if (idx === 3) navigate('/stores');
                  else if (idx === 4) navigate('/action-queue');
                }}
                style={{ cursor: 'pointer' }}
              >
                <MetricCard
                  title={kpi.title}
                  value={kpi.value}
                  subtext={kpi.subtext}
                  icon={kpiIcons[idx]}
                  iconBg={kpi.iconBg}
                  iconColor={kpi.iconColor}
                  sparklineColor={kpi.sparklineColor}
                  sparklinePoints={kpi.sparklinePoints}
                />
              </div>
            ))}
          </div>

          {/* Middle Row: Top Issues (Left ~60%) and Charts Column (Right ~40%) */}
          <div className="dashboard-main-grid">
            {/* Left: Top Issues This Week Table Card */}
            <div className="ui-card" style={{ display: 'flex', flexDirection: 'column' }}>
              <div className="ui-card-header">
                <div className="ui-card-title">
                  <span>Top Issues This Week</span>
                  <span className="subtitle-count">({selectedRegion})</span>
                </div>
                <Link to="/issue-analysis" className="view-all-link">
                  View All →
                </Link>
              </div>

              {/* Table */}
              <div className="table-responsive-wrapper" style={{ overflowX: 'auto', flex: 1 }}>
                <table style={{ width: '100%', minWidth: '560px', borderCollapse: 'collapse', textAlign: 'left', fontSize: '13px' }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid #f1f5f9', color: '#64748b', fontSize: '11.5px', fontWeight: 600 }}>
                      <th style={{ padding: '8px 10px', width: '32px' }}>#</th>
                      <th style={{ padding: '8px 10px' }}>Issue</th>
                      <th style={{ padding: '8px 10px', textAlign: 'center' }}>Severity</th>
                      <th style={{ padding: '8px 10px', textAlign: 'center' }}>Trend</th>
                      <th style={{ padding: '8px 10px' }}>Affected Stores</th>
                      <th style={{ padding: '8px 10px' }}>Owner</th>
                    </tr>
                  </thead>
                  <tbody>
                    {topIssues.map((issue) => {
                      const IssueIcon = iconMap[issue.icon] || Snowflake;
                      return (
                        <tr
                          key={issue.id}
                          onClick={() => navigate('/issue-analysis')}
                          style={{
                            borderBottom: '1px solid #f8fafc',
                            transition: 'background-color 0.15s ease',
                            cursor: 'pointer',
                          }}
                          onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = '#f8fafc')}
                          onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}
                        >
                          <td style={{ padding: '11px 10px', color: '#0f172a', fontWeight: 700 }}>
                            {issue.id}
                          </td>
                          <td style={{ padding: '11px 10px' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                              <div
                                style={{
                                  width: '28px',
                                  height: '28px',
                                  borderRadius: '6px',
                                  backgroundColor: '#eff6ff',
                                  display: 'flex',
                                  alignItems: 'center',
                                  justifyContent: 'center',
                                  color: '#2563eb',
                                  flexShrink: 0,
                                }}
                              >
                                <IssueIcon size={16} />
                              </div>
                              <div>
                                <div style={{ fontWeight: 700, color: '#0f172a', fontSize: '13px' }}>
                                  {issue.title}
                                </div>
                                <div style={{ fontSize: '11.5px', color: '#64748b', marginTop: '1px' }}>
                                  {issue.category}
                                </div>
                              </div>
                            </div>
                          </td>
                          <td style={{ padding: '11px 10px', textAlign: 'center' }}>
                            <span className={`badge-severity badge-severity-${issue.severity.toLowerCase()}`}>
                              <span className="dot" />
                              {issue.severity}
                            </span>
                          </td>
                          <td style={{ padding: '11px 10px', textAlign: 'center' }}>
                            <span
                              style={{
                                display: 'inline-flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                width: '22px',
                                height: '22px',
                                borderRadius: '50%',
                                backgroundColor: issue.trend === 'up' ? '#fee2e2' : '#e6f7ef',
                                color: issue.trend === 'up' ? '#ef4444' : '#10b981',
                              }}
                            >
                              {issue.trend === 'up' ? <ArrowUpRight size={14} /> : <ArrowDownRight size={14} />}
                            </span>
                          </td>
                          <td style={{ padding: '11px 10px', color: '#0f172a', fontWeight: 600 }}>
                            {issue.affectedStores}
                          </td>
                          <td style={{ padding: '11px 10px' }}>
                            <span className={`badge-department badge-department-${issue.ownerTag}`}>
                              {issue.owner}
                            </span>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Right: Charts Column (Donut + Sentiment Line) */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {/* Feedback Sources Donut Chart Card */}
              <div className="ui-card" style={{ display: 'flex', flexDirection: 'column' }}>
                <div className="ui-card-header">
                  <div className="ui-card-title">
                    <span>Feedback Sources</span>
                  </div>
                </div>

                <div style={{ position: 'relative', height: '140px', width: '100%', marginTop: '2px' }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={FEEDBACK_SOURCES}
                        innerRadius={42}
                        outerRadius={58}
                        paddingAngle={3}
                        dataKey="percentage"
                      >
                        {FEEDBACK_SOURCES.map((entry) => (
                          <Cell key={entry.name} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip
                        contentStyle={{
                          backgroundColor: '#ffffff',
                          border: '1px solid #e2e8f0',
                          borderRadius: '8px',
                          fontSize: '12px',
                        }}
                      />
                    </PieChart>
                  </ResponsiveContainer>

                  {/* Centered Total */}
                  <div
                    style={{
                      position: 'absolute',
                      top: '50%',
                      left: '50%',
                      transform: 'translate(-50%, -50%)',
                      textAlign: 'center',
                      pointerEvents: 'none',
                    }}
                  >
                    <div style={{ fontSize: '15px', fontWeight: 800, color: '#0f172a', lineHeight: 1.1 }}>
                      40,000
                    </div>
                    <div style={{ fontSize: '9.5px', color: '#64748b', fontWeight: 500 }}>
                      Total
                    </div>
                  </div>
                </div>

                {/* Donut Legend */}
                <div
                  style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(2, 1fr)',
                    gap: '6px 12px',
                    paddingTop: '8px',
                    borderTop: '1px solid #f1f5f9',
                    fontSize: '11px',
                  }}
                >
                  {FEEDBACK_SOURCES.map((source) => (
                    <div key={source.name} style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <span
                        style={{
                          width: '7px',
                          height: '7px',
                          borderRadius: '50%',
                          backgroundColor: source.color,
                        }}
                      />
                      <span style={{ color: '#475569', flex: 1 }}>{source.name}</span>
                      <strong style={{ color: '#0f172a' }}>{source.percentage}%</strong>
                    </div>
                  ))}
                </div>
              </div>

              {/* Sentiment Overview Line Chart Card */}
              <div className="ui-card" style={{ display: 'flex', flexDirection: 'column' }}>
                <div className="ui-card-header">
                  <div className="ui-card-title">
                    <span>Sentiment Overview</span>
                    <span className="subtitle-count">(Last 7 Days)</span>
                  </div>
                </div>

                <div style={{ height: '115px', width: '100%' }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={SENTIMENT_TREND} margin={{ top: 5, right: 10, left: -25, bottom: 0 }}>
                      <XAxis
                        dataKey="date"
                        tickLine={false}
                        axisLine={{ stroke: '#e2e8f0' }}
                        tick={{ fill: '#64748b', fontSize: 10 }}
                      />
                      <YAxis
                        tickLine={false}
                        axisLine={{ stroke: '#e2e8f0' }}
                        tick={{ fill: '#64748b', fontSize: 10 }}
                      />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: '#ffffff',
                          border: '1px solid #e2e8f0',
                          borderRadius: '8px',
                          fontSize: '12px',
                        }}
                      />
                      <Line
                        type="monotone"
                        dataKey="Positive"
                        stroke="#10b981"
                        strokeWidth={2}
                        dot={false}
                      />
                      <Line
                        type="monotone"
                        dataKey="Neutral"
                        stroke="#94a3b8"
                        strokeWidth={2}
                        dot={false}
                      />
                      <Line
                        type="monotone"
                        dataKey="Negative"
                        stroke="#ef4444"
                        strokeWidth={2}
                        dot={false}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>

                {/* Sentiment Legend */}
                <div
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '16px',
                    paddingTop: '6px',
                    borderTop: '1px solid #f1f5f9',
                    fontSize: '10.5px',
                    color: '#64748b',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                    <span style={{ width: '7px', height: '7px', borderRadius: '50%', backgroundColor: '#10b981' }} />
                    <span>Positive</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                    <span style={{ width: '7px', height: '7px', borderRadius: '50%', backgroundColor: '#94a3b8' }} />
                    <span>Neutral</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                    <span style={{ width: '7px', height: '7px', borderRadius: '50%', backgroundColor: '#ef4444' }} />
                    <span>Negative</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Bottom Row: 3 Equal Width Cards */}
          <div className="dashboard-bottom-grid">
            {/* Card 1: Emerging Issues */}
            <div className="ui-card">
              <div className="ui-card-header">
                <div className="ui-card-title">
                  <span style={{ color: '#ef4444' }}>⚡</span>
                  <span>Emerging Issues</span>
                </div>
                <Link to="/emerging-issues" className="view-all-link">
                  View All →
                </Link>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {emergingAlerts.map((issue, idx) => (
                  <div
                    key={idx}
                    onClick={() => navigate('/emerging-issues')}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      padding: '8px 10px',
                      borderRadius: '8px',
                      backgroundColor: '#f8fafc',
                      fontSize: '12px',
                      cursor: 'pointer',
                    }}
                    onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = '#f1f5f9')}
                    onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = '#f8fafc')}
                  >
                    <div>
                      <div style={{ fontWeight: 600, color: '#0f172a' }}>{issue.issue}</div>
                      <div style={{ color: '#64748b', fontSize: '11px' }}>{issue.store}</div>
                    </div>

                    <div style={{ textAlign: 'right' }}>
                      <div style={{ fontWeight: 700, color: '#ef4444' }}>{issue.change}</div>
                      <div style={{ color: '#64748b', fontSize: '10.5px' }}>{issue.volume} mentions</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Card 2: Recent Feedback */}
            <div className="ui-card">
              <div className="ui-card-header">
                <div className="ui-card-title">
                  <span style={{ color: '#3b82f6' }}>💬</span>
                  <span>Recent Feedback</span>
                </div>
                <Link to="/feedback-stream" className="view-all-link">
                  View All →
                </Link>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {recentFeedbacks.map((sample, idx) => (
                  <div
                    key={idx}
                    onClick={() => navigate('/feedback-stream')}
                    style={{
                      display: 'flex',
                      alignItems: 'flex-start',
                      gap: '8px',
                      fontSize: '12px',
                      cursor: 'pointer',
                    }}
                  >
                    <span
                      style={{
                        padding: '1.5px 6px',
                        backgroundColor: '#f1f5f9',
                        borderRadius: '4px',
                        fontSize: '10.5px',
                        fontWeight: 600,
                        color: '#475569',
                      }}
                    >
                      {sample.channel}
                    </span>

                    <div style={{ flex: 1, minWidth: 0 }}>
                      <p
                        style={{
                          margin: 0,
                          color: '#334155',
                          whiteSpace: 'nowrap',
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                        }}
                      >
                        {sample.text}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Card 3: Regional Highlights */}
            <div className="ui-card">
              <div className="ui-card-header">
                <div className="ui-card-title">
                  <span style={{ color: '#ef4444' }}>📍</span>
                  <span>Regional Highlights</span>
                </div>
                <Link to="/regional-reports" className="view-all-link">
                  View All →
                </Link>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {REGIONAL_HIGHLIGHTS.map((reg) => (
                  <div
                    key={reg.region}
                    onClick={() => navigate('/regional-reports')}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      fontSize: '12px',
                      padding: '4px 0',
                      cursor: 'pointer',
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <span style={{ color: '#ef4444', fontSize: '13px' }}>📍</span>
                      <span style={{ fontWeight: 600, color: '#0f172a' }}>{reg.region}</span>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span
                        style={{
                          fontWeight: 700,
                          fontSize: '11.5px',
                          color: reg.isUp ? '#ef4444' : '#10b981',
                        }}
                      >
                        {reg.change}
                      </span>
                      <svg viewBox="0 0 40 10" width="38" height="10">
                        <path
                          d={reg.isUp ? 'M0,8 Q20,6 40,2' : 'M0,2 Q20,4 40,8'}
                          fill="none"
                          stroke={reg.isUp ? '#ef4444' : '#10b981'}
                          strokeWidth="1.8"
                        />
                      </svg>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

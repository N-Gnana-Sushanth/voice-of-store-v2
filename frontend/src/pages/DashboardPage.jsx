import React from 'react';
import { Link } from 'react-router-dom';
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
  ChevronDown,
  Sparkles,
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
  const iconMap = {
    Snowflake: Snowflake,
    Utensils: Utensils,
    Users: Users,
    Package: Package,
    Smartphone: Smartphone,
  };

  const kpiIcons = [MessageSquare, AlertTriangle, CheckCircle2, Store, Clock];

  return (
    <div className="app-container">
      <Sidebar />
      <div className="app-main">
        <Header />

        <main className="page-content">
          {/* Top Header Row with Title and Quote Banner */}
          <div className="page-header-row">
            <div className="page-title-group">
              <h1>Dashboard</h1>
              <p>A quick view of what matters this week across all stores.</p>
            </div>

            <div className="quote-banner">
              <Sparkles size={14} className="sparkle-icon" />
              <span>"From customer voices to clear actions, for better stores."</span>
            </div>
          </div>

          {/* Top 5 Metric Cards */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '14px' }}>
            {DASHBOARD_KPIS.map((kpi, idx) => (
              <MetricCard
                key={kpi.title}
                title={kpi.title}
                value={kpi.value}
                subtext={kpi.subtext}
                icon={kpiIcons[idx]}
                iconBg={kpi.iconBg}
                iconColor={kpi.iconColor}
                sparklineColor={kpi.sparklineColor}
                sparklinePoints={kpi.sparklinePoints}
              />
            ))}
          </div>

          {/* Middle Row: Top Issues (Left ~60%) and Charts Column (Right ~40%) */}
          <div style={{ display: 'grid', gridTemplateColumns: '1.45fr 1fr', gap: '16px' }}>
            {/* Left: Top Issues This Week Table Card */}
            <div className="ui-card" style={{ display: 'flex', flexDirection: 'column' }}>
              <div className="ui-card-header">
                <div className="ui-card-title">
                  <span>Top Issues This Week</span>
                  <span className="subtitle-count">(All Regions)</span>
                </div>
                <Link to="/issue-analysis" className="view-all-link">
                  View All →
                </Link>
              </div>

              {/* Table */}
              <div style={{ overflowX: 'auto', flex: 1 }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '13px' }}>
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
                    {TOP_ISSUES.map((issue) => {
                      const IssueIcon = iconMap[issue.icon] || Snowflake;
                      return (
                        <tr
                          key={issue.id}
                          style={{
                            borderBottom: '1px solid #f8fafc',
                            transition: 'background-color 0.15s ease',
                          }}
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
                                <div style={{ fontSize: '11px', color: '#64748b' }}>
                                  {issue.category}
                                </div>
                              </div>
                            </div>
                          </td>
                          <td style={{ padding: '11px 10px', textAlign: 'center' }}>
                            <span className={`badge-severity ${issue.severity.toLowerCase()}`}>
                              {issue.severity}
                            </span>
                          </td>
                          <td style={{ padding: '11px 10px', textAlign: 'center' }}>
                            {issue.trend === 'up' ? (
                              <ArrowUpRight size={17} style={{ color: '#ef4444', margin: '0 auto' }} />
                            ) : (
                              <ArrowDownRight size={17} style={{ color: '#10b981', margin: '0 auto' }} />
                            )}
                          </td>
                          <td style={{ padding: '11px 10px', fontSize: '12.5px', color: '#334155', fontWeight: 500 }}>
                            {issue.affectedStores}
                          </td>
                          <td style={{ padding: '11px 10px' }}>
                            <span className={`tag-owner ${issue.ownerTag}`}>
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

            {/* Right Column: Feedback Sources + Sentiment Overview */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {/* Feedback Sources Card */}
              <div className="ui-card">
                <div className="ui-card-header" style={{ marginBottom: '6px' }}>
                  <div className="ui-card-title">
                    <span>Feedback Sources</span>
                    <span className="subtitle-count">(This Week)</span>
                  </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                  {/* Donut Chart with Center Text */}
                  <div style={{ width: '130px', height: '130px', position: 'relative', flexShrink: 0 }}>
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={FEEDBACK_SOURCES}
                          innerRadius={42}
                          outerRadius={60}
                          paddingAngle={3}
                          dataKey="count"
                        >
                          {FEEDBACK_SOURCES.map((entry) => (
                            <Cell key={entry.name} fill={entry.color} />
                          ))}
                        </Pie>
                      </PieChart>
                    </ResponsiveContainer>
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
                      <div style={{ fontSize: '14px', fontWeight: 800, color: '#0f172a', lineHeight: 1.1 }}>
                        40,000
                      </div>
                      <div style={{ fontSize: '9px', color: '#64748b', fontWeight: 500 }}>
                        Total Feedback
                      </div>
                    </div>
                  </div>

                  {/* Legend Details */}
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', flex: 1 }}>
                    {FEEDBACK_SOURCES.map((src) => (
                      <div
                        key={src.name}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'space-between',
                          fontSize: '11.5px',
                        }}
                      >
                        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                          <span
                            style={{
                              width: '8px',
                              height: '8px',
                              borderRadius: '50%',
                              backgroundColor: src.color,
                            }}
                          />
                          <span style={{ color: '#334155', fontWeight: 600 }}>{src.name}</span>
                        </div>
                        <span style={{ color: '#64748b', fontWeight: 500 }}>
                          {src.percentage}% ({src.count.toLocaleString()})
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Sentiment Overview Card */}
              <div className="ui-card">
                <div className="ui-card-header" style={{ marginBottom: '8px' }}>
                  <div className="ui-card-title">
                    <span>Sentiment Overview</span>
                  </div>
                  <div
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '4px',
                      fontSize: '11.5px',
                      color: '#475569',
                      border: '1px solid #e2e8f0',
                      borderRadius: '6px',
                      padding: '3px 8px',
                      backgroundColor: '#ffffff',
                    }}
                  >
                    <span>This Week</span>
                    <ChevronDown size={13} />
                  </div>
                </div>

                {/* Sentiment Legend */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '14px', marginBottom: '8px', fontSize: '11px', fontWeight: 600 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <span style={{ width: '7px', height: '7px', borderRadius: '50%', backgroundColor: '#10b981' }} />
                    <span style={{ color: '#475569' }}>Positive</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <span style={{ width: '7px', height: '7px', borderRadius: '50%', backgroundColor: '#3b82f6' }} />
                    <span style={{ color: '#475569' }}>Neutral</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <span style={{ width: '7px', height: '7px', borderRadius: '50%', backgroundColor: '#ef4444' }} />
                    <span style={{ color: '#475569' }}>Negative</span>
                  </div>
                </div>

                {/* Line Chart */}
                <div style={{ width: '100%', height: '80px' }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={SENTIMENT_TREND} margin={{ top: 4, right: 4, left: -24, bottom: 0 }}>
                      <XAxis dataKey="date" tick={{ fontSize: 9.5, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
                      <YAxis tick={{ fontSize: 9, fill: '#94a3b8' }} axisLine={false} tickLine={false} tickCount={3} />
                      <Tooltip contentStyle={{ fontSize: '11px', borderRadius: '6px' }} />
                      <Line type="monotone" dataKey="Positive" stroke="#10b981" strokeWidth={2} dot={false} />
                      <Line type="monotone" dataKey="Neutral" stroke="#3b82f6" strokeWidth={2} dot={false} />
                      <Line type="monotone" dataKey="Negative" stroke="#ef4444" strokeWidth={2} dot={false} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          </div>

          {/* Bottom Row: 3 Cards */}
          <div style={{ display: 'grid', gridTemplateColumns: '1.25fr 1fr 0.85fr', gap: '16px' }}>
            {/* Card 1: Emerging Issues (Early Warnings) */}
            <div className="ui-card">
              <div className="ui-card-header">
                <div className="ui-card-title">
                  <span style={{ color: '#ef4444' }}>⚠️</span>
                  <span>Emerging Issues</span>
                  <span className="subtitle-count">(Early Warnings)</span>
                  <span
                    style={{
                      width: '18px',
                      height: '18px',
                      borderRadius: '50%',
                      backgroundColor: '#fee2e2',
                      color: '#ef4444',
                      fontSize: '11px',
                      fontWeight: 700,
                      display: 'inline-flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}
                  >
                    3
                  </span>
                </div>
                <Link to="/emerging-issues" className="view-all-link">
                  View All →
                </Link>
              </div>

              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '12px' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid #f1f5f9', color: '#64748b', fontSize: '10.5px', fontWeight: 600 }}>
                    <th style={{ padding: '6px 8px' }}>Issue</th>
                    <th style={{ padding: '6px 8px' }}>Store</th>
                    <th style={{ padding: '6px 8px', textAlign: 'center' }}>Current Vol</th>
                    <th style={{ padding: '6px 8px' }}>Change (WoW)</th>
                    <th style={{ padding: '6px 8px', textAlign: 'center' }}>Severity</th>
                  </tr>
                </thead>
                <tbody>
                  {EMERGING_ISSUES_DASHBOARD.map((item, idx) => (
                    <tr key={idx} style={{ borderBottom: '1px solid #f8fafc' }}>
                      <td style={{ padding: '8px 8px', fontWeight: 600, color: '#0f172a' }}>
                        {item.issue}
                      </td>
                      <td style={{ padding: '8px 8px', color: '#64748b' }}>
                        {item.store}
                      </td>
                      <td style={{ padding: '8px 8px', textAlign: 'center', fontWeight: 700, color: '#0f172a' }}>
                        {item.volume}
                      </td>
                      <td style={{ padding: '8px 8px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                          <span style={{ color: '#ef4444', fontWeight: 700, fontSize: '11px' }}>
                            {item.change}
                          </span>
                          <svg viewBox="0 0 50 12" width="45" height="12">
                            <path d="M0,10 Q25,8 50,2" fill="none" stroke="#ef4444" strokeWidth="1.8" />
                          </svg>
                        </div>
                      </td>
                      <td style={{ padding: '8px 8px', textAlign: 'center' }}>
                        <span className="badge-severity high">
                          {item.severity}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Card 2: Recent Feedback Samples */}
            <div className="ui-card">
              <div className="ui-card-header">
                <div className="ui-card-title">
                  <span>📑 Recent Feedback Samples</span>
                </div>
                <Link to="/feedback-stream" className="view-all-link">
                  View All →
                </Link>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {RECENT_FEEDBACK_SAMPLES.map((sample, idx) => (
                  <div
                    key={idx}
                    style={{
                      display: 'flex',
                      alignItems: 'flex-start',
                      gap: '10px',
                      paddingBottom: idx !== RECENT_FEEDBACK_SAMPLES.length - 1 ? '10px' : '0',
                      borderBottom: idx !== RECENT_FEEDBACK_SAMPLES.length - 1 ? '1px solid #f1f5f9' : 'none',
                    }}
                  >
                    {/* Channel Icon */}
                    <div
                      style={{
                        width: '26px',
                        height: '26px',
                        borderRadius: sample.channel === 'Google' ? '50%' : '6px',
                        backgroundColor: sample.channel === 'Google' ? '#fee2e2' : sample.channel === 'AppStore' ? '#e0f2fe' : '#dcfce7',
                        color: sample.channel === 'Google' ? '#ef4444' : sample.channel === 'AppStore' ? '#0284c7' : '#16a34a',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontSize: '11px',
                        fontWeight: 800,
                        flexShrink: 0,
                      }}
                    >
                      {sample.channel === 'Google' ? 'G' : sample.channel === 'AppStore' ? 'A' : '💬'}
                    </div>

                    <div style={{ flex: 1, minWidth: 0 }}>
                      <span style={{ fontSize: '10.5px', color: '#94a3b8', display: 'block', marginBottom: '2px' }}>
                        {sample.time}
                      </span>
                      <p
                        style={{
                          fontSize: '12px',
                          fontWeight: 500,
                          color: '#1e293b',
                          lineHeight: 1.35,
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
                <Link to="/issue-analysis" className="view-all-link">
                  View All →
                </Link>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {REGIONAL_HIGHLIGHTS.map((reg) => (
                  <div
                    key={reg.region}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      fontSize: '12px',
                      padding: '4px 0',
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

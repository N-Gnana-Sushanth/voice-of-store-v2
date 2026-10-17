import React from 'react';
import {
  Sparkles,
  TrendingUp,
  CheckCircle2,
  Clock,
  ShieldAlert,
  AlertTriangle,
  Snowflake,
  Utensils,
  Users,
  Store,
  ArrowUpRight,
  Trophy,
  ExternalLink,
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
import {
  EMERGING_DETAILED_CARDS,
  EMERGING_TREND_COMPARISON,
  EMERGING_CHANNEL_BREAKDOWN,
  PLANTED_EVALUATIONS,
} from '../data/mockData';

export default function EmergingIssuesPage() {
  const iconMap = {
    Snowflake: Snowflake,
    Utensils: Utensils,
    Users: Users,
  };

  const kpis = [
    {
      title: 'Planted Incidents Detected',
      value: '3 / 3 (100%)',
      subtext: 'All ground truth found',
      icon: CheckCircle2,
      iconBg: '#e6f7ef',
      iconColor: '#059669',
    },
    {
      title: 'Avg. Lead Time',
      value: '10.0 days',
      subtext: 'Before peak severity',
      icon: Clock,
      iconBg: '#eff6ff',
      iconColor: '#3b82f6',
    },
    {
      title: 'False Positive Rate',
      value: '0.0%',
      subtext: 'High precision baseline',
      icon: ShieldAlert,
      iconBg: '#f3e8ff',
      iconColor: '#8b5cf6',
    },
    {
      title: 'Active Emerging Spikes',
      value: '3 issues',
      subtext: 'Requiring investigation',
      icon: AlertTriangle,
      iconBg: '#fee2e2',
      iconColor: '#ef4444',
    },
  ];

  return (
    <div className="app-container">
      <Sidebar />
      <div className="app-main">
        <Header searchPlaceholder="Search emerging issues, anomaly spikes, ground truth..." />

        <main className="page-content">
          {/* Page Header */}
          <div className="page-header-row">
            <div className="page-title-group">
              <h1>Emerging Issues & Planted Evaluation</h1>
              <p>Early detection algorithms, anomaly spikes, and validation against known incidents.</p>
            </div>

            <div className="quote-banner">
              <Sparkles size={14} className="sparkle-icon" />
              <span>"Catch it as a whisper before it becomes a roar."</span>
            </div>
          </div>

          {/* Top 4 KPI Cards */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '14px' }}>
            {kpis.map((kpi) => {
              const Icon = kpi.icon;
              return (
                <div
                  key={kpi.title}
                  className="ui-card"
                  style={{
                    padding: '16px 18px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '14px',
                  }}
                >
                  <div
                    style={{
                      width: '42px',
                      height: '42px',
                      borderRadius: '50%',
                      backgroundColor: kpi.iconBg,
                      color: kpi.iconColor,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      flexShrink: 0,
                    }}
                  >
                    <Icon size={20} />
                  </div>
                  <div>
                    <div style={{ fontSize: '11.5px', fontWeight: 600, color: '#64748b' }}>
                      {kpi.title}
                    </div>
                    <div style={{ fontSize: '20px', fontWeight: 800, color: '#0f172a', lineHeight: 1.2 }}>
                      {kpi.value}
                    </div>
                    <div style={{ fontSize: '11px', color: '#94a3b8', marginTop: '2px' }}>
                      {kpi.subtext}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Middle Row: Left Column 3 Detailed Cards + Right Column 2 Charts */}
          <div style={{ display: 'grid', gridTemplateColumns: '1.45fr 1fr', gap: '16px' }}>
            {/* Left Column: 3 Detailed Emerging Issue Cards */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div
                style={{
                  fontSize: '14px',
                  fontWeight: 700,
                  color: '#0f172a',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                }}
              >
                <span>Active Emerging Issues</span>
                <span
                  style={{
                    fontSize: '11px',
                    fontWeight: 600,
                    padding: '2px 8px',
                    backgroundColor: '#fee2e2',
                    color: '#b91c1c',
                    borderRadius: '999px',
                  }}
                >
                  3 Spikes Detected
                </span>
              </div>

              {EMERGING_DETAILED_CARDS.map((card) => {
                const Icon = iconMap[card.icon] || Snowflake;
                return (
                  <div
                    key={card.id}
                    className="ui-card"
                    style={{
                      padding: '18px 20px',
                      display: 'flex',
                      flexDirection: 'column',
                      gap: '12px',
                      borderLeft: `4px solid ${card.severity === 'High' ? '#ef4444' : '#f97316'}`,
                    }}
                  >
                    {/* Top Row: Icon + Title + Department Badge + Severity Badge */}
                    <div
                      style={{
                        display: 'flex',
                        alignItems: 'flex-start',
                        justifyContent: 'space-between',
                        gap: '12px',
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <div
                          style={{
                            width: '34px',
                            height: '34px',
                            borderRadius: '8px',
                            backgroundColor: card.iconBg,
                            color: card.iconColor,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            flexShrink: 0,
                          }}
                        >
                          <Icon size={18} />
                        </div>
                        <div>
                          <div style={{ fontSize: '14px', fontWeight: 700, color: '#0f172a' }}>
                            {card.title}
                          </div>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginTop: '4px' }}>
                            <span style={{ fontSize: '11.5px', color: '#64748b' }}>
                              {card.tagCategory}
                            </span>
                            <span style={{ color: '#cbd5e1' }}>•</span>
                            <span className={`badge-department badge-department-${card.tagOwnerType}`}>
                              {card.tagOwner}
                            </span>
                          </div>
                        </div>
                      </div>

                      <span className={`badge-severity badge-severity-${card.severity.toLowerCase()}`}>
                        <span className="dot" />
                        {card.severity}
                      </span>
                    </div>

                    {/* Narrative Description */}
                    <p style={{ fontSize: '12.5px', color: '#475569', lineHeight: 1.45, margin: 0 }}>
                      {card.narrative}
                    </p>

                    {/* Stats Metric Bar */}
                    <div
                      style={{
                        display: 'grid',
                        gridTemplateColumns: 'repeat(4, 1fr)',
                        gap: '8px',
                        backgroundColor: '#f8fafc',
                        padding: '10px 14px',
                        borderRadius: '8px',
                        border: '1px solid #f1f5f9',
                      }}
                    >
                      <div>
                        <div style={{ fontSize: '11px', color: '#64748b' }}>Current Mentions</div>
                        <div style={{ fontSize: '15px', fontWeight: 800, color: '#0f172a' }}>
                          {card.currentMentions}
                        </div>
                      </div>
                      <div>
                        <div style={{ fontSize: '11px', color: '#64748b' }}>Prev. Week</div>
                        <div style={{ fontSize: '15px', fontWeight: 800, color: '#64748b' }}>
                          {card.previousWeek}
                        </div>
                      </div>
                      <div>
                        <div style={{ fontSize: '11px', color: '#64748b' }}>Weekly Surge</div>
                        <div style={{ fontSize: '15px', fontWeight: 800, color: '#b91c1c' }}>
                          {card.increasePct}
                        </div>
                      </div>
                      <div>
                        <div style={{ fontSize: '11px', color: '#64748b' }}>Primary Store</div>
                        <div style={{ fontSize: '13px', fontWeight: 700, color: '#0f172a' }}>
                          {card.store}
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Right Column: Charts */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {/* Trend Comparison Chart Card */}
              <div className="ui-card" style={{ display: 'flex', flexDirection: 'column' }}>
                <div className="ui-card-header">
                  <div className="ui-card-title">
                    <span>Trend Comparison</span>
                    <span className="subtitle-count">(Spike vs Normal)</span>
                  </div>
                </div>

                <div style={{ height: '190px', width: '100%', marginTop: '6px' }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={EMERGING_TREND_COMPARISON} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                      <XAxis
                        dataKey="date"
                        tickLine={false}
                        axisLine={{ stroke: '#e2e8f0' }}
                        tick={{ fill: '#64748b', fontSize: 11 }}
                      />
                      <YAxis
                        tickLine={false}
                        axisLine={{ stroke: '#e2e8f0' }}
                        tick={{ fill: '#64748b', fontSize: 11 }}
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
                        dataKey="currentIssue"
                        name="Current Spike (Store #128)"
                        stroke="#ef4444"
                        strokeWidth={2.4}
                        dot={{ r: 3, fill: '#ef4444' }}
                      />
                      <Line
                        type="monotone"
                        dataKey="sameIssueOther"
                        name="Same Issue (Other Stores)"
                        stroke="#f97316"
                        strokeWidth={1.8}
                        dot={false}
                      />
                      <Line
                        type="monotone"
                        dataKey="overallAvg"
                        name="Overall Issue Avg"
                        stroke="#94a3b8"
                        strokeWidth={1.5}
                        strokeDasharray="4 4"
                        dot={false}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>

                {/* Legend */}
                <div
                  style={{
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '4px',
                    paddingTop: '10px',
                    borderTop: '1px solid #f1f5f9',
                    fontSize: '11px',
                    color: '#64748b',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#ef4444' }} />
                    <span style={{ color: '#0f172a', fontWeight: 600 }}>Current Spike (Store #128)</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#f97316' }} />
                    <span>Same Issue (Other Stores Avg)</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <span style={{ width: '8px', height: '2px', backgroundColor: '#94a3b8' }} />
                    <span>Overall Chain Avg</span>
                  </div>
                </div>
              </div>

              {/* Channel Breakdown Donut Chart Card */}
              <div className="ui-card" style={{ display: 'flex', flexDirection: 'column' }}>
                <div className="ui-card-header">
                  <div className="ui-card-title">
                    <span>Channel Breakdown</span>
                    <span className="subtitle-count">(Where whispers come from)</span>
                  </div>
                </div>

                <div style={{ position: 'relative', height: '140px', width: '100%' }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={EMERGING_CHANNEL_BREAKDOWN}
                        innerRadius={40}
                        outerRadius={56}
                        paddingAngle={3}
                        dataKey="count"
                      >
                        {EMERGING_CHANNEL_BREAKDOWN.map((entry) => (
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
                </div>

                <div
                  style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(2, 1fr)',
                    gap: '6px',
                    paddingTop: '8px',
                    borderTop: '1px solid #f1f5f9',
                    fontSize: '11px',
                  }}
                >
                  {EMERGING_CHANNEL_BREAKDOWN.map((entry) => (
                    <div key={entry.name} style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                      <span style={{ width: '7px', height: '7px', borderRadius: '50%', backgroundColor: entry.color }} />
                      <span style={{ color: '#475569' }}>{entry.name}:</span>
                      <strong style={{ color: '#0f172a' }}>{entry.percentage}%</strong>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Bottom Section: Planted Incident Detection Table Card */}
          <div className="ui-card" style={{ display: 'flex', flexDirection: 'column' }}>
            <div className="ui-card-header">
              <div className="ui-card-title">
                <Trophy size={16} style={{ color: '#059669' }} />
                <span>Planted Incident Evaluation</span>
                <span className="subtitle-count">(Validation against Ground Truth)</span>
              </div>
            </div>

            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '12.5px' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid #f1f5f9', color: '#64748b', fontSize: '11.5px', fontWeight: 600 }}>
                    <th style={{ padding: '8px 12px' }}>Planted Ground Truth Incident</th>
                    <th style={{ padding: '8px 12px' }}>First Detected</th>
                    <th style={{ padding: '8px 12px' }}>Actual Crisis Peak</th>
                    <th style={{ padding: '8px 12px' }}>Early Warning Lead Time</th>
                    <th style={{ padding: '8px 12px', textAlign: 'center' }}>Detection Status</th>
                  </tr>
                </thead>
                <tbody>
                  {PLANTED_EVALUATIONS.map((row) => (
                    <tr
                      key={row.incident}
                      style={{
                        borderBottom: '1px solid #f8fafc',
                      }}
                    >
                      <td style={{ padding: '12px 12px', fontWeight: 600, color: '#0f172a' }}>
                        {row.incident}
                      </td>
                      <td style={{ padding: '12px 12px', color: '#334155' }}>
                        {row.firstDetected}
                      </td>
                      <td style={{ padding: '12px 12px', color: '#64748b' }}>
                        {row.actualPeak}
                      </td>
                      <td style={{ padding: '12px 12px', color: '#059669', fontWeight: 700 }}>
                        {row.leadTime}
                      </td>
                      <td style={{ padding: '12px 12px', textAlign: 'center' }}>
                        <span
                          style={{
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '4px',
                            padding: '3px 10px',
                            backgroundColor: '#e6f7ef',
                            color: '#047857',
                            border: '1px solid #a7f3d0',
                            borderRadius: '999px',
                            fontSize: '11.5px',
                            fontWeight: 600,
                          }}
                        >
                          <CheckCircle2 size={12} />
                          {row.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Bottom Trophy Banner */}
            <div
              style={{
                margin: '14px 0 2px 0',
                backgroundColor: '#eaf7f0',
                border: '1px solid #bbf7d0',
                borderRadius: '8px',
                padding: '10px 14px',
                display: 'flex',
                alignItems: 'center',
                gap: '10px',
                fontSize: '12.5px',
                color: '#065f46',
                fontWeight: 600,
              }}
            >
              <Trophy size={17} style={{ color: '#059669', flexShrink: 0 }} />
              <span>
                100% Detection Rate: All 3 planted incidents were detected an average of 10.0 days before they peaked in complaint volume.
              </span>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

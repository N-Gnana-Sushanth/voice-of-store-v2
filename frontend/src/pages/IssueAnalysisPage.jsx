import React, { useState, useEffect } from 'react';
import {
  Snowflake,
  Utensils,
  Users,
  Package,
  Smartphone,
  Sparkles,
  TrendingUp,
  AlertTriangle,
  Lightbulb,
  Store,
  ArrowUpRight,
  ArrowDownRight,
  Download,
  RefreshCw,
  Filter,
  X,
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
import IndiaMap from '../components/IndiaMap';
import { api } from '../api/client';
import { useApp } from '../context/AppContext';
import {
  TOP_ISSUES,
  ISSUE_ANALYSIS_CATEGORIES,
  ISSUE_TREND_WEEKLY,
  SEVERITY_DISTRIBUTION,
} from '../data/mockData';

export default function IssueAnalysisPage() {
  const { isLive: globalIsLive } = useApp();
  const [incidents, setIncidents] = useState(TOP_ISSUES);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [isLive, setIsLive] = useState(false);
  const [loading, setLoading] = useState(false);

  const iconMap = {
    Snowflake: Snowflake,
    Utensils: Utensils,
    Users: Users,
    Package: Package,
    Smartphone: Smartphone,
  };

  const loadData = async () => {
    setLoading(true);
    try {
      const res = await api.incidents.list({ limit: 50 });
      if (res?.items && res.items.length > 0) {
        setIsLive(true);
        const mapped = res.items.map((inc, idx) => ({
          id: idx + 1,
          title: inc.metadata?.title || `${inc.category} Issue at ${inc.store_id}`,
          category: inc.category,
          severity: inc.severity,
          affectedStores: inc.metadata?.store_number || inc.store_id || '1 store',
          owner: inc.metadata?.owner || (inc.severity === 'High' ? 'Quality & Compliance' : 'Store Ops'),
          ownerTag: inc.severity === 'High' ? 'quality' : 'store-ops',
          evidence: inc.evidence_summary || 'Customer reports multiple issues with temperature and labeling.',
          icon: inc.category.toLowerCase().includes('food')
            ? 'Utensils'
            : inc.category.toLowerCase().includes('service')
            ? 'Users'
            : 'Snowflake',
        }));
        setIncidents(mapped);
      } else {
        setIncidents(TOP_ISSUES);
      }
    } catch (err) {
      console.warn('Backend unavailable or no incidents found, using reference demo data:', err.message);
      setIsLive(false);
      setIncidents(TOP_ISSUES);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const maxCategoryCount = Math.max(...ISSUE_ANALYSIS_CATEGORIES.map((c) => c.count));

  // Category filtering
  const filteredIssues = incidents.filter((issue) => {
    if (!selectedCategory) return true;
    const catLower = issue.category.toLowerCase();
    const selLower = selectedCategory.toLowerCase();
    return catLower.includes(selLower) || selLower.includes(catLower);
  });

  // Export report as CSV
  const handleExportReport = () => {
    const headers = ['#', 'Issue Title', 'Category', 'Severity', 'Affected Stores', 'Owner', 'Evidence Excerpt'];
    const rows = filteredIssues.map((issue) => [
      issue.id,
      `"${(issue.title || '').replace(/"/g, '""')}"`,
      `"${(issue.category || '').replace(/"/g, '""')}"`,
      issue.severity,
      `"${issue.affectedStores || ''}"`,
      `"${issue.owner || ''}"`,
      `"${(issue.evidence || '').replace(/"/g, '""')}"`,
    ]);
    const csvContent = [headers.join(','), ...rows.map((r) => r.join(','))].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `voice_of_store_issue_analysis_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="app-container">
      <Sidebar />
      <div className="app-main">
        <Header searchPlaceholder="Search issues, categories, root causes..." />

        <main className="page-content">
          {/* Page Header */}
          <div className="page-header-row">
            <div className="page-title-group">
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <h1>Issue Analysis</h1>
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
              <p>Deep dive into categorised issues, root causes, and geographic spread.</p>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <button
                onClick={loadData}
                disabled={loading}
                title="Refresh issues from backend"
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '5px',
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

              <button
                onClick={handleExportReport}
                title="Export filtered analysis as CSV"
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '6px',
                  padding: '6px 12px',
                  backgroundColor: '#059669',
                  color: '#ffffff',
                  border: 'none',
                  borderRadius: '6px',
                  fontSize: '11.5px',
                  fontWeight: 600,
                  cursor: 'pointer',
                }}
              >
                <Download size={12} />
                <span>Export Report</span>
              </button>

              <div className="quote-banner">
                <Sparkles size={14} className="sparkle-icon" />
                <span>"Every problem solved at one store is a lesson for all."</span>
              </div>
            </div>
          </div>

          {/* Top Section: 3 Cards Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: '1.1fr 1.3fr 0.9fr', gap: '16px' }}>
            {/* 1. Issues by Category (Horizontal Bars) */}
            <div className="ui-card" style={{ display: 'flex', flexDirection: 'column' }}>
              <div className="ui-card-header">
                <div className="ui-card-title">
                  <span>Issues by Category</span>
                  <span className="subtitle-count">(Click to filter table)</span>
                </div>
                {selectedCategory && (
                  <button
                    onClick={() => setSelectedCategory(null)}
                    style={{
                      background: 'none',
                      border: 'none',
                      color: '#059669',
                      fontSize: '11.5px',
                      fontWeight: 600,
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '3px',
                    }}
                  >
                    <span>Clear Filter</span>
                    <X size={12} />
                  </button>
                )}
              </div>

              <div
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '8px',
                  padding: '2px 0',
                  flex: 1,
                  justifyContent: 'space-between',
                }}
              >
                {ISSUE_ANALYSIS_CATEGORIES.map((cat) => {
                  const isSelected = selectedCategory === cat.name;
                  return (
                    <div
                      key={cat.name}
                      onClick={() => setSelectedCategory(isSelected ? null : cat.name)}
                      style={{
                        display: 'flex',
                        flexDirection: 'column',
                        gap: '3px',
                        cursor: 'pointer',
                        padding: '3px 6px',
                        borderRadius: '6px',
                        backgroundColor: isSelected ? '#f0fdf4' : 'transparent',
                        border: isSelected ? '1px solid #bbf7d0' : '1px solid transparent',
                        transition: 'all 0.15s ease',
                      }}
                      title={`Click to filter table by ${cat.name}`}
                    >
                      <div
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'space-between',
                          fontSize: '11.5px',
                        }}
                      >
                        <span style={{ fontWeight: isSelected ? 700 : 600, color: isSelected ? '#047857' : '#334155' }}>
                          {cat.name}
                        </span>
                        <span style={{ fontWeight: 700, color: isSelected ? '#047857' : '#0f172a' }}>
                          {cat.count}
                        </span>
                      </div>
                      {/* Progress track */}
                      <div
                        style={{
                          height: '7px',
                          backgroundColor: '#f1f5f9',
                          borderRadius: '4px',
                          overflow: 'hidden',
                        }}
                      >
                        <div
                          style={{
                            width: `${(cat.count / maxCategoryCount) * 100}%`,
                            height: '100%',
                            backgroundColor: cat.color,
                            borderRadius: '4px',
                          }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* 2. Issue Trend (Last 7 Days Multi-line Chart) */}
            <div className="ui-card" style={{ display: 'flex', flexDirection: 'column' }}>
              <div className="ui-card-header">
                <div className="ui-card-title">
                  <span>Issue Trend</span>
                  <span className="subtitle-count">(Last 7 Days)</span>
                </div>
              </div>

              <div style={{ height: '240px', width: '100%', marginTop: '6px' }}>
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={ISSUE_TREND_WEEKLY} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
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
                        boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
                      }}
                    />
                    <Line
                      type="monotone"
                      dataKey="Equipment"
                      name="Equipment"
                      stroke="#3b82f6"
                      strokeWidth={2.2}
                      dot={false}
                    />
                    <Line
                      type="monotone"
                      dataKey="FoodSafety"
                      name="Food Safety"
                      stroke="#f97316"
                      strokeWidth={2.2}
                      dot={false}
                    />
                    <Line
                      type="monotone"
                      dataKey="CustomerService"
                      name="Customer Service"
                      stroke="#8b5cf6"
                      strokeWidth={2.2}
                      dot={false}
                    />
                    <Line
                      type="monotone"
                      dataKey="Inventory"
                      name="Inventory"
                      stroke="#10b981"
                      strokeWidth={2.2}
                      dot={false}
                    />
                    <Line
                      type="monotone"
                      dataKey="Payments"
                      name="Payments"
                      stroke="#ef4444"
                      strokeWidth={2.2}
                      dot={false}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>

              {/* Chart Legend */}
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '12px',
                  flexWrap: 'wrap',
                  paddingTop: '10px',
                  borderTop: '1px solid #f1f5f9',
                  fontSize: '11px',
                  color: '#64748b',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                  <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#3b82f6' }} />
                  <span>Equipment</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                  <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#f97316' }} />
                  <span>Food Safety</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                  <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#8b5cf6' }} />
                  <span>Customer Service</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                  <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#10b981' }} />
                  <span>Inventory</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                  <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#ef4444' }} />
                  <span>Payments</span>
                </div>
              </div>
            </div>

            {/* 3. Severity Distribution (Donut Chart) */}
            <div className="ui-card" style={{ display: 'flex', flexDirection: 'column' }}>
              <div className="ui-card-header">
                <div className="ui-card-title">
                  <span>Severity Distribution</span>
                </div>
              </div>

              <div style={{ position: 'relative', height: '170px', width: '100%', marginTop: '4px' }}>
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={SEVERITY_DISTRIBUTION}
                      innerRadius={48}
                      outerRadius={68}
                      paddingAngle={4}
                      dataKey="count"
                    >
                      {SEVERITY_DISTRIBUTION.map((entry) => (
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

                {/* Donut Center Label */}
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
                  <div style={{ fontSize: '18px', fontWeight: 800, color: '#0f172a', lineHeight: 1.1 }}>
                    1,124
                  </div>
                  <div style={{ fontSize: '10px', color: '#64748b', fontWeight: 500 }}>
                    Total Issues
                  </div>
                </div>
              </div>

              {/* Severity Legend Rows */}
              <div
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '6px',
                  paddingTop: '10px',
                  borderTop: '1px solid #f1f5f9',
                }}
              >
                {SEVERITY_DISTRIBUTION.map((s) => (
                  <div
                    key={s.name}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      fontSize: '11.5px',
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: s.color }} />
                      <span style={{ color: '#334155', fontWeight: 500 }}>{s.name} Severity</span>
                    </div>
                    <div>
                      <strong style={{ color: '#0f172a' }}>{s.count}</strong>
                      <span style={{ color: '#64748b', marginLeft: '4px' }}>({s.percentage}%)</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Bottom Section: Top Issues with Evidence + Geographic Spread */}
          <div style={{ display: 'grid', gridTemplateColumns: '1.45fr 1fr', gap: '16px' }}>
            {/* Left: Top Issues with Evidence Table */}
            <div className="ui-card" style={{ display: 'flex', flexDirection: 'column' }}>
              <div className="ui-card-header">
                <div className="ui-card-title">
                  <span>Top Issues with Evidence</span>
                  <span className="subtitle-count">
                    {selectedCategory
                      ? `(Filtered by "${selectedCategory}": ${filteredIssues.length} found)`
                      : '(Ranked by impact & frequency)'}
                  </span>
                </div>
                {selectedCategory && (
                  <button
                    onClick={() => setSelectedCategory(null)}
                    style={{
                      padding: '3px 8px',
                      backgroundColor: '#f1f5f9',
                      border: '1px solid #e2e8f0',
                      borderRadius: '4px',
                      fontSize: '11px',
                      fontWeight: 600,
                      color: '#475569',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '4px',
                    }}
                  >
                    <Filter size={11} />
                    <span>Reset Filter</span>
                  </button>
                )}
              </div>

              <div style={{ overflowX: 'auto', flex: 1 }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '12.5px' }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid #f1f5f9', color: '#64748b', fontSize: '11.5px', fontWeight: 600 }}>
                      <th style={{ padding: '8px 10px', width: '28px' }}>#</th>
                      <th style={{ padding: '8px 10px' }}>Issue & Evidence Excerpt</th>
                      <th style={{ padding: '8px 10px' }}>Category</th>
                      <th style={{ padding: '8px 10px', textAlign: 'center' }}>Severity</th>
                      <th style={{ padding: '8px 10px' }}>Affected Stores</th>
                      <th style={{ padding: '8px 10px' }}>Owner</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredIssues.map((issue) => {
                      const IssueIcon = iconMap[issue.icon] || Snowflake;
                      return (
                        <tr
                          key={issue.id}
                          style={{
                            borderBottom: '1px solid #f8fafc',
                            transition: 'background-color 0.1s ease',
                          }}
                        >
                          <td style={{ padding: '10px 10px', color: '#94a3b8', fontWeight: 600 }}>
                            {issue.id}
                          </td>
                          <td style={{ padding: '10px 10px' }}>
                            <div style={{ display: 'flex', alignItems: 'flex-start', gap: '8px' }}>
                              <div
                                style={{
                                  width: '26px',
                                  height: '26px',
                                  borderRadius: '6px',
                                  backgroundColor: '#f1f5f9',
                                  color: '#475569',
                                  display: 'flex',
                                  alignItems: 'center',
                                  justifyContent: 'center',
                                  flexShrink: 0,
                                  marginTop: '2px',
                                }}
                              >
                                <IssueIcon size={14} />
                              </div>
                              <div>
                                <div style={{ fontWeight: 600, color: '#0f172a' }}>{issue.title}</div>
                                <div
                                  style={{
                                    fontSize: '11.5px',
                                    color: '#64748b',
                                    fontStyle: 'italic',
                                    marginTop: '2px',
                                    maxWidth: '280px',
                                  }}
                                >
                                  "{issue.evidence}"
                                </div>
                              </div>
                            </div>
                          </td>
                          <td style={{ padding: '10px 10px', color: '#475569', fontSize: '11.5px' }}>
                            {issue.category}
                          </td>
                          <td style={{ padding: '10px 10px', textAlign: 'center' }}>
                            <span className={`badge-severity badge-severity-${issue.severity.toLowerCase()}`}>
                              <span className="dot" />
                              {issue.severity}
                            </span>
                          </td>
                          <td style={{ padding: '10px 10px', color: '#334155', fontWeight: 600 }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                              <Store size={13} style={{ color: '#64748b' }} />
                              <span>{issue.affectedStores}</span>
                            </div>
                          </td>
                          <td style={{ padding: '10px 10px' }}>
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

            {/* Right: Geographic Spread & Key Insights Column */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {/* Geographic Spread (India) Card */}
              <div className="ui-card" style={{ padding: '16px 18px' }}>
                <div className="ui-card-header" style={{ marginBottom: '10px' }}>
                  <div className="ui-card-title">
                    <span>Geographic Spread</span>
                    <span className="subtitle-count">(India Stores)</span>
                  </div>
                </div>

                <IndiaMap />
              </div>

              {/* Key Insights Callout Card */}
              <div
                className="ui-card"
                style={{
                  padding: '16px 18px',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '10px',
                }}
              >
                <div className="ui-card-title" style={{ marginBottom: '2px' }}>
                  <Lightbulb size={15} style={{ color: '#059669' }} />
                  <span>Key Insights</span>
                </div>

                <div
                  style={{
                    backgroundColor: '#eaf7f0',
                    border: '1px solid #bbf7d0',
                    borderRadius: '8px',
                    padding: '8px 12px',
                    fontSize: '12px',
                    color: '#065f46',
                    lineHeight: 1.4,
                  }}
                >
                  <strong>⚡ South region</strong> accounts for 48% of all freezer-related issues this week.
                </div>

                <div
                  style={{
                    backgroundColor: '#fef3c7',
                    border: '1px solid #fde68a',
                    borderRadius: '8px',
                    padding: '8px 12px',
                    fontSize: '12px',
                    color: '#92400e',
                    lineHeight: 1.4,
                  }}
                >
                  <strong>⚠ Food safety</strong> mislabeling concentrated in West (Pune & Mumbai stores).
                </div>

                <div
                  style={{
                    backgroundColor: '#eff6ff',
                    border: '1px solid #bfdbfe',
                    borderRadius: '8px',
                    padding: '8px 12px',
                    fontSize: '12px',
                    color: '#1e40af',
                    lineHeight: 1.4,
                  }}
                >
                  <strong>✓ Resolution time</strong> in North improved by 1.2 days compared to last week.
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

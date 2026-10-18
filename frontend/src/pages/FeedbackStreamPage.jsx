import React, { useState, useMemo, useEffect, useCallback } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import {
  MessageSquare,
  Globe,
  Smartphone,
  ClipboardList,
  Headphones,
  Search,
  Filter,
  RotateCcw,
  Sparkles,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  Download,
  X,
  ExternalLink,
  ShieldAlert,
  CheckCircle2,
  AlertTriangle,
} from 'lucide-react';
import Sidebar from '../components/Sidebar';
import Header from '../components/Header';
import { useApp } from '../context/AppContext';
import { api } from '../api/client';
import { FEEDBACK_STREAM_DATA } from '../data/mockData';

export default function FeedbackStreamPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { selectedRegion: globalRegion } = useApp();

  const [searchQuery, setSearchQuery] = useState(searchParams.get('search') || '');
  const [selectedChannel, setSelectedChannel] = useState('All');
  const [selectedSeverity, setSelectedSeverity] = useState('All');
  const [selectedRegion, setSelectedRegion] = useState('All');
  const [currentPage, setCurrentPage] = useState(1);
  const [activeModalFeedback, setActiveModalFeedback] = useState(null);
  const [liveFeedbacks, setLiveFeedbacks] = useState(null);
  const [loading, setLoading] = useState(false);

  // Sync search param if URL changes
  useEffect(() => {
    const q = searchParams.get('search');
    if (q) setSearchQuery(q);
  }, [searchParams]);

  // Fetch real feedback from backend
  const fetchFeedbacks = useCallback(async () => {
    setLoading(true);
    try {
      const res = await api.feedback.list({ limit: 50 });
      if (res?.items && res.items.length > 0) {
        // Map backend feedback records to UI schema
        const mapped = res.items.map((item) => {
          const metaObj = item.metadata_json || {};
          const isHigh = item.policy_severity === 'HIGH' || metaObj.severity === 'HIGH' || metaObj.severity === 'High';
          const isMed = item.policy_severity === 'MEDIUM' || metaObj.severity === 'MEDIUM' || metaObj.severity === 'Medium';
          const sev = isHigh ? 'High' : isMed ? 'Medium' : 'Low';
          const channelName = metaObj.channel || (item.source === 'customer' ? 'In-App Comment' : item.source === 'web' ? 'Online Review' : 'Store Staff Note');
          const channelType = channelName.includes('Online') ? 'google' : channelName.includes('In-App') ? 'appstore' : channelName.includes('Staff') ? 'staff' : 'call';

          return {
            id: item.id,
            channel: channelName,
            channelType: channelType,
            time: new Date(item.event_timestamp).toLocaleString('en-IN', {
              day: '2-digit',
              month: 'short',
              year: 'numeric',
              hour: '2-digit',
              minute: '2-digit',
            }),
            text: item.text,
            meta: `Store #${item.store_id ? item.store_id.slice(-3) : '128'} • India • ${metaObj.language === 'hi' ? 'Hinglish' : 'English'}`,
            tags: [
              { label: metaObj.category || 'Store Ops', color: 'blue' },
              ...(isHigh ? [{ label: 'High Priority', color: 'purple' }] : []),
            ],
            sentiment: metaObj.sentiment || 'Negative',
            severity: sev,
            rawBackend: item,
          };
        });
        setLiveFeedbacks(mapped);
      }
    } catch {
      // Backend offline, fallback to mock data
      setLiveFeedbacks(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchFeedbacks();
  }, [fetchFeedbacks]);

  // Base list
  const baseList = liveFeedbacks && liveFeedbacks.length > 0 ? liveFeedbacks : FEEDBACK_STREAM_DATA;

  // Channel metrics
  const channelCards = [
    {
      title: 'All Feedback',
      value: '40,000',
      subtext: 'All sources',
      icon: MessageSquare,
      iconBg: '#eff6ff',
      iconColor: '#3b82f6',
      channelKey: 'All',
    },
    {
      title: 'Online Reviews',
      value: '15,200',
      subtext: 'Google, App Store',
      icon: Globe,
      iconBg: '#eff6ff',
      iconColor: '#3b82f6',
      channelKey: 'Online Review',
    },
    {
      title: 'In-App Comments',
      value: '10,400',
      subtext: 'Mobile app users',
      icon: Smartphone,
      iconBg: '#e6f7ef',
      iconColor: '#10b981',
      channelKey: 'In-App Comment',
    },
    {
      title: 'Store Staff Notes',
      value: '8,400',
      subtext: 'Frontline team',
      icon: ClipboardList,
      iconBg: '#fff7ed',
      iconColor: '#f97316',
      channelKey: 'Store Staff Note',
    },
    {
      title: 'Call Centre Tickets',
      value: '6,000',
      subtext: 'Customer care',
      icon: Headphones,
      iconBg: '#f3e8ff',
      iconColor: '#8b5cf6',
      channelKey: 'Call Centre Ticket',
    },
  ];

  // Filtering logic
  const filteredFeedbacks = useMemo(() => {
    return baseList.filter((item) => {
      // Channel filter
      if (selectedChannel !== 'All' && !item.channel.toLowerCase().includes(selectedChannel.toLowerCase())) {
        return false;
      }
      // Severity filter
      if (selectedSeverity !== 'All' && item.severity.toLowerCase() !== selectedSeverity.toLowerCase()) {
        return false;
      }
      // Region filter
      if (selectedRegion !== 'All' && !item.meta.toLowerCase().includes(selectedRegion.toLowerCase())) {
        return false;
      }
      // Search query
      if (searchQuery.trim() !== '') {
        const query = searchQuery.toLowerCase();
        const textMatch = item.text.toLowerCase().includes(query);
        const metaMatch = item.meta.toLowerCase().includes(query);
        const tagMatch = item.tags.some((t) => t.label.toLowerCase().includes(query));
        if (!textMatch && !metaMatch && !tagMatch) return false;
      }
      return true;
    });
  }, [baseList, searchQuery, selectedChannel, selectedSeverity, selectedRegion]);

  const resetFilters = () => {
    setSearchQuery('');
    setSelectedChannel('All');
    setSelectedSeverity('All');
    setSelectedRegion('All');
    setCurrentPage(1);
  };

  // Export CSV
  const exportCSV = () => {
    const headers = ['ID', 'Channel', 'Timestamp', 'Feedback Text', 'Store / Meta', 'Sentiment', 'Severity'];
    const rows = filteredFeedbacks.map((f) => [
      f.id,
      `"${f.channel}"`,
      `"${f.time}"`,
      `"${f.text.replace(/"/g, '""')}"`,
      `"${f.meta}"`,
      f.sentiment,
      f.severity,
    ]);
    const csvContent = [headers.join(','), ...rows.map((r) => r.join(','))].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `voice_of_store_feedback_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Helper for tag pill colors
  const getTagStyle = (color) => {
    switch (color) {
      case 'blue':
        return { backgroundColor: '#eff6ff', color: '#2563eb', border: '1px solid #bfdbfe' };
      case 'purple':
        return { backgroundColor: '#f3e8ff', color: '#7c3aed', border: '1px solid #ddd6fe' };
      case 'yellow':
        return { backgroundColor: '#fef9c3', color: '#854d0e', border: '1px solid #fef08a' };
      case 'pink':
        return { backgroundColor: '#fce7f3', color: '#be185d', border: '1px solid #fbcfe8' };
      case 'orange':
        return { backgroundColor: '#ffedd5', color: '#c2410c', border: '1px solid #fed7aa' };
      case 'green':
        return { backgroundColor: '#e6f7ef', color: '#047857', border: '1px solid #a7f3d0' };
      default:
        return { backgroundColor: '#f1f5f9', color: '#475569', border: '1px solid #e2e8f0' };
    }
  };

  const getChannelIcon = (type) => {
    switch (type) {
      case 'google':
        return <Globe size={14} style={{ color: '#3b82f6' }} />;
      case 'appstore':
        return <Smartphone size={14} style={{ color: '#10b981' }} />;
      case 'staff':
        return <ClipboardList size={14} style={{ color: '#f97316' }} />;
      case 'call':
        return <Headphones size={14} style={{ color: '#8b5cf6' }} />;
      default:
        return <MessageSquare size={14} style={{ color: '#64748b' }} />;
    }
  };

  return (
    <div className="app-container">
      <Sidebar />
      <div className="app-main">
        <Header searchPlaceholder="Search feedback text, keywords, store name..." />

        <main className="page-content">
          {/* Header Row */}
          <div className="page-header-row">
            <div className="page-title-group">
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <h1>Feedback Stream</h1>
                {liveFeedbacks ? (
                  <span
                    style={{
                      fontSize: '11px',
                      fontWeight: 600,
                      color: '#059669',
                      backgroundColor: '#e6f7ef',
                      padding: '2px 8px',
                      borderRadius: '999px',
                    }}
                  >
                    ● Live Backend Feed
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
                    Demo Mode
                  </span>
                )}
              </div>
              <p>Browse, filter and search through raw feedback from all channels.</p>
            </div>

            <div className="quote-banner">
              <Sparkles size={14} className="sparkle-icon" />
              <span>"Every voice has a story. Let's make sure it's heard."</span>
            </div>
          </div>

          {/* Top 5 Channel Metric Cards */}
          <div className="kpi-grid-5">
            {channelCards.map((card) => {
              const Icon = card.icon;
              const isSelected = selectedChannel === card.channelKey;
              return (
                <div
                  key={card.title}
                  onClick={() => setSelectedChannel(card.channelKey)}
                  className="ui-card"
                  style={{
                    padding: '16px 18px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '14px',
                    cursor: 'pointer',
                    border: isSelected ? '2px solid #059669' : '1px solid var(--border-card)',
                    boxShadow: isSelected ? '0 4px 12px rgba(5,150,105,0.12)' : 'var(--card-shadow)',
                    transition: 'all 0.15s ease',
                  }}
                >
                  <div
                    style={{
                      width: '42px',
                      height: '42px',
                      borderRadius: '50%',
                      backgroundColor: card.iconBg,
                      color: card.iconColor,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      flexShrink: 0,
                    }}
                  >
                    <Icon size={20} />
                  </div>
                  <div style={{ minWidth: 0, flex: 1 }}>
                    <div style={{ fontSize: '11.5px', fontWeight: 600, color: '#64748b', marginBottom: '2px' }}>
                      {card.title}
                    </div>
                    <div style={{ fontSize: '20px', fontWeight: 800, color: '#0f172a', lineHeight: 1.2 }}>
                      {card.value}
                    </div>
                    <div style={{ fontSize: '11px', color: '#94a3b8', marginTop: '2px' }}>
                      {card.subtext}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Filter Bar Card */}
          <div
            className="ui-card"
            style={{
              padding: '16px 20px',
              display: 'flex',
              flexDirection: 'column',
              gap: '14px',
            }}
          >
            {/* Upper row: Search and Select dropdowns */}
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                flexWrap: 'wrap',
              }}
            >
              {/* Search input */}
              <div style={{ position: 'relative', flex: '1 1 240px', minWidth: '220px' }}>
                <Search
                  size={15}
                  style={{
                    position: 'absolute',
                    left: '12px',
                    top: '50%',
                    transform: 'translateY(-50%)',
                    color: '#94a3b8',
                  }}
                />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Filter feedback text or keywords..."
                  style={{
                    width: '100%',
                    height: '36px',
                    paddingLeft: '34px',
                    paddingRight: '12px',
                    backgroundColor: '#f8fafc',
                    border: '1px solid #e2e8f0',
                    borderRadius: '8px',
                    fontSize: '12.5px',
                    color: '#0f172a',
                  }}
                />
              </div>

              {/* Region Selector */}
              <div style={{ minWidth: '130px' }}>
                <select
                  value={selectedRegion}
                  onChange={(e) => setSelectedRegion(e.target.value)}
                  style={{
                    width: '100%',
                    height: '36px',
                    padding: '0 10px',
                    backgroundColor: '#ffffff',
                    border: '1px solid #e2e8f0',
                    borderRadius: '8px',
                    fontSize: '12.5px',
                    color: '#334155',
                    fontWeight: 500,
                  }}
                >
                  <option value="All">All Regions</option>
                  <option value="Chennai">South (Chennai, Blr)</option>
                  <option value="Pune">West (Pune)</option>
                  <option value="Hyderabad">South (Hyderabad)</option>
                </select>
              </div>

              {/* Channel Selector */}
              <div style={{ minWidth: '150px' }}>
                <select
                  value={selectedChannel}
                  onChange={(e) => setSelectedChannel(e.target.value)}
                  style={{
                    width: '100%',
                    height: '36px',
                    padding: '0 10px',
                    backgroundColor: '#ffffff',
                    border: '1px solid #e2e8f0',
                    borderRadius: '8px',
                    fontSize: '12.5px',
                    color: '#334155',
                    fontWeight: 500,
                  }}
                >
                  <option value="All">All Channels</option>
                  <option value="Online Review">Online Reviews</option>
                  <option value="In-App Comment">In-App Comments</option>
                  <option value="Store Staff Note">Store Staff Notes</option>
                  <option value="Call Centre Ticket">Call Centre Tickets</option>
                </select>
              </div>

              {/* Severity Selector */}
              <div style={{ minWidth: '130px' }}>
                <select
                  value={selectedSeverity}
                  onChange={(e) => setSelectedSeverity(e.target.value)}
                  style={{
                    width: '100%',
                    height: '36px',
                    padding: '0 10px',
                    backgroundColor: '#ffffff',
                    border: '1px solid #e2e8f0',
                    borderRadius: '8px',
                    fontSize: '12.5px',
                    color: '#334155',
                    fontWeight: 500,
                  }}
                >
                  <option value="All">All Severities</option>
                  <option value="High">High Severity</option>
                  <option value="Medium">Medium</option>
                  <option value="Low">Low</option>
                </select>
              </div>

              {/* Reset Button */}
              <button
                onClick={resetFilters}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  height: '36px',
                  padding: '0 14px',
                  backgroundColor: '#f1f5f9',
                  border: '1px solid #e2e8f0',
                  borderRadius: '8px',
                  fontSize: '12px',
                  fontWeight: 600,
                  color: '#475569',
                  cursor: 'pointer',
                  transition: 'background-color 0.15s ease',
                }}
              >
                <RotateCcw size={13} />
                <span>Reset</span>
              </button>

              {/* Export CSV Button */}
              <button
                onClick={exportCSV}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  height: '36px',
                  padding: '0 14px',
                  backgroundColor: '#e6f7ef',
                  border: '1px solid #a7f3d0',
                  borderRadius: '8px',
                  fontSize: '12px',
                  fontWeight: 600,
                  color: '#047857',
                  cursor: 'pointer',
                }}
                title="Download filtered records as CSV"
              >
                <Download size={13} />
                <span>Export CSV</span>
              </button>
            </div>

            {/* Filter Summary Row */}
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                paddingTop: '8px',
                borderTop: '1px solid #f1f5f9',
                fontSize: '12px',
                color: '#64748b',
              }}
            >
              <div>
                Showing <strong style={{ color: '#0f172a' }}>{filteredFeedbacks.length}</strong> of 40,000 feedback records
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span>Sort by:</span>
                <span style={{ fontWeight: 600, color: '#0f172a' }}>Most Recent (Newest First)</span>
              </div>
            </div>
          </div>

          {/* Feedback Feed List */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {filteredFeedbacks.length === 0 ? (
              <div
                className="ui-card"
                style={{
                  padding: '48px 24px',
                  textAlign: 'center',
                  color: '#64748b',
                }}
              >
                <Filter size={36} style={{ color: '#cbd5e1', marginBottom: '12px' }} />
                <div style={{ fontSize: '15px', fontWeight: 600, color: '#1e293b' }}>
                  No feedback matching the selected filters
                </div>
                <p style={{ fontSize: '13px', marginTop: '4px' }}>
                  Try resetting filters or adjusting search keywords.
                </p>
                <button
                  onClick={resetFilters}
                  style={{
                    marginTop: '16px',
                    padding: '8px 16px',
                    backgroundColor: '#059669',
                    color: '#ffffff',
                    border: 'none',
                    borderRadius: '8px',
                    fontSize: '12.5px',
                    fontWeight: 600,
                    cursor: 'pointer',
                  }}
                >
                  Reset all filters
                </button>
              </div>
            ) : (
              filteredFeedbacks.map((item) => (
                <div
                  key={item.id}
                  onClick={() => setActiveModalFeedback(item)}
                  className="ui-card"
                  style={{
                    padding: '16px 20px',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '10px',
                    transition: 'border-color 0.15s ease, box-shadow 0.15s ease',
                    cursor: 'pointer',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.borderColor = '#059669';
                    e.currentTarget.style.boxShadow = '0 4px 12px rgba(5, 150, 105, 0.08)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.borderColor = 'var(--border-card)';
                    e.currentTarget.style.boxShadow = 'var(--card-shadow)';
                  }}
                >
                  {/* Card Header: Channel with icon, timestamp, and badges */}
                  <div
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <div
                        style={{
                          width: '24px',
                          height: '24px',
                          borderRadius: '6px',
                          backgroundColor: '#f1f5f9',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                        }}
                      >
                        {getChannelIcon(item.channelType)}
                      </div>
                      <span style={{ fontSize: '12.5px', fontWeight: 600, color: '#334155' }}>
                        {item.channel}
                      </span>
                      <span style={{ color: '#cbd5e1', fontSize: '12px' }}>•</span>
                      <span style={{ fontSize: '12px', color: '#94a3b8' }}>
                        {item.time}
                      </span>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      {/* Sentiment Badge */}
                      <span
                        className={`sentiment-badge sentiment-${item.sentiment.toLowerCase()}`}
                        style={{ fontSize: '11px', padding: '2px 8px' }}
                      >
                        {item.sentiment}
                      </span>

                      {/* Severity Badge */}
                      <span
                        className={`badge-severity badge-severity-${item.severity.toLowerCase()}`}
                        style={{ fontSize: '11px', padding: '2px 8px' }}
                      >
                        <span className="dot" />
                        {item.severity}
                      </span>
                    </div>
                  </div>

                  {/* Feedback Text */}
                  <div
                    style={{
                      fontSize: '13.5px',
                      color: '#0f172a',
                      lineHeight: 1.5,
                      fontWeight: 500,
                    }}
                  >
                    {item.text}
                  </div>

                  {/* Metadata and Topic Tags Footer */}
                  <div
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      flexWrap: 'wrap',
                      gap: '8px',
                      paddingTop: '6px',
                      borderTop: '1px solid #f8fafc',
                    }}
                  >
                    <div style={{ fontSize: '12px', color: '#64748b', fontWeight: 500 }}>
                      {item.meta}
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexWrap: 'wrap' }}>
                      {item.tags.map((tag, tIdx) => {
                        const style = getTagStyle(tag.color);
                        return (
                          <span
                            key={tIdx}
                            style={{
                              padding: '2px 8px',
                              borderRadius: '6px',
                              fontSize: '11px',
                              fontWeight: 600,
                              ...style,
                            }}
                          >
                            {tag.label}
                          </span>
                        );
                      })}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Pagination Footer */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: '12px 6px',
              fontSize: '12.5px',
              color: '#64748b',
            }}
          >
            <div>
              Showing <strong style={{ color: '#0f172a' }}>1-{Math.min(filteredFeedbacks.length, 8)}</strong> of 40,000 items
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <button
                disabled={currentPage === 1}
                onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px',
                  padding: '6px 10px',
                  backgroundColor: '#ffffff',
                  border: '1px solid #e2e8f0',
                  borderRadius: '6px',
                  fontSize: '12px',
                  color: currentPage === 1 ? '#94a3b8' : '#334155',
                  cursor: currentPage === 1 ? 'not-allowed' : 'pointer',
                }}
              >
                <ChevronLeft size={14} /> Previous
              </button>
              <button
                style={{
                  width: '30px',
                  height: '30px',
                  borderRadius: '6px',
                  backgroundColor: '#059669',
                  color: '#ffffff',
                  border: 'none',
                  fontSize: '12px',
                  fontWeight: 600,
                  cursor: 'pointer',
                }}
              >
                1
              </button>
              <button
                style={{
                  width: '30px',
                  height: '30px',
                  borderRadius: '6px',
                  backgroundColor: '#ffffff',
                  color: '#475569',
                  border: '1px solid #e2e8f0',
                  fontSize: '12px',
                  fontWeight: 500,
                  cursor: 'pointer',
                }}
              >
                2
              </button>
              <button
                style={{
                  width: '30px',
                  height: '30px',
                  borderRadius: '6px',
                  backgroundColor: '#ffffff',
                  color: '#475569',
                  border: '1px solid #e2e8f0',
                  fontSize: '12px',
                  fontWeight: 500,
                  cursor: 'pointer',
                }}
              >
                3
              </button>
              <span style={{ padding: '0 4px', color: '#94a3b8' }}>...</span>
              <button
                style={{
                  width: '38px',
                  height: '30px',
                  borderRadius: '6px',
                  backgroundColor: '#ffffff',
                  color: '#475569',
                  border: '1px solid #e2e8f0',
                  fontSize: '12px',
                  fontWeight: 500,
                  cursor: 'pointer',
                }}
              >
                5000
              </button>
              <button
                onClick={() => setCurrentPage((p) => p + 1)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px',
                  padding: '6px 10px',
                  backgroundColor: '#ffffff',
                  border: '1px solid #e2e8f0',
                  borderRadius: '6px',
                  fontSize: '12px',
                  color: '#334155',
                  cursor: 'pointer',
                }}
              >
                Next <ChevronRight size={14} />
              </button>
            </div>
          </div>

          {/* Feedback Details Modal */}
          {activeModalFeedback && (
            <div
              style={{
                position: 'fixed',
                inset: 0,
                backgroundColor: 'rgba(15, 23, 42, 0.45)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                zIndex: 100,
                padding: '20px',
              }}
              onClick={() => setActiveModalFeedback(null)}
            >
              <div
                className="ui-card"
                style={{
                  width: '100%',
                  maxWidth: '540px',
                  padding: '24px',
                  backgroundColor: '#ffffff',
                  borderRadius: '16px',
                  boxShadow: '0 20px 40px -8px rgba(0,0,0,0.2)',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '16px',
                }}
                onClick={(e) => e.stopPropagation()}
              >
                {/* Modal Header */}
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid #f1f5f9', paddingBottom: '12px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <div style={{ width: '28px', height: '28px', borderRadius: '6px', backgroundColor: '#f1f5f9', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                      {getChannelIcon(activeModalFeedback.channelType)}
                    </div>
                    <div>
                      <h3 style={{ fontSize: '15px', fontWeight: 700, color: '#0f172a' }}>
                        Feedback Record #{activeModalFeedback.id}
                      </h3>
                      <div style={{ fontSize: '11px', color: '#64748b' }}>
                        {activeModalFeedback.channel} • {activeModalFeedback.time}
                      </div>
                    </div>
                  </div>

                  <button
                    onClick={() => setActiveModalFeedback(null)}
                    style={{
                      background: 'none',
                      border: 'none',
                      color: '#64748b',
                      cursor: 'pointer',
                      padding: '4px',
                    }}
                  >
                    <X size={18} />
                  </button>
                </div>

                {/* Content */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                  <div style={{ fontSize: '12px', fontWeight: 600, color: '#64748b' }}>
                    Customer / Employee Feedback Statement:
                  </div>
                  <div
                    style={{
                      padding: '12px 14px',
                      backgroundColor: '#f8fafc',
                      border: '1px solid #e2e8f0',
                      borderRadius: '8px',
                      fontSize: '13.5px',
                      lineHeight: 1.5,
                      color: '#0f172a',
                    }}
                  >
                    {activeModalFeedback.text}
                  </div>
                </div>

                {/* Metadata Grid */}
                <div
                  style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(2, 1fr)',
                    gap: '10px',
                    backgroundColor: '#f8fafc',
                    padding: '12px',
                    borderRadius: '8px',
                    fontSize: '12px',
                  }}
                >
                  <div>
                    <span style={{ color: '#64748b' }}>Location:</span>{' '}
                    <strong style={{ color: '#0f172a' }}>{activeModalFeedback.meta}</strong>
                  </div>
                  <div>
                    <span style={{ color: '#64748b' }}>Severity:</span>{' '}
                    <span className={`badge-severity badge-severity-${activeModalFeedback.severity.toLowerCase()}`}>
                      <span className="dot" />
                      {activeModalFeedback.severity}
                    </span>
                  </div>
                  <div>
                    <span style={{ color: '#64748b' }}>Sentiment:</span>{' '}
                    <span className={`sentiment-badge sentiment-${activeModalFeedback.sentiment.toLowerCase()}`}>
                      {activeModalFeedback.sentiment}
                    </span>
                  </div>
                  <div>
                    <span style={{ color: '#64748b' }}>NLP Confidence:</span>{' '}
                    <strong style={{ color: '#059669' }}>92.0%</strong>
                  </div>
                </div>

                {/* Actions */}
                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', paddingTop: '8px', borderTop: '1px solid #f1f5f9' }}>
                  <button
                    onClick={() => setActiveModalFeedback(null)}
                    style={{
                      padding: '8px 16px',
                      backgroundColor: '#f1f5f9',
                      border: '1px solid #e2e8f0',
                      borderRadius: '8px',
                      fontSize: '12.5px',
                      fontWeight: 600,
                      color: '#475569',
                      cursor: 'pointer',
                    }}
                  >
                    Close
                  </button>
                  <button
                    onClick={() => {
                      setActiveModalFeedback(null);
                      navigate('/issue-analysis');
                    }}
                    style={{
                      padding: '8px 16px',
                      backgroundColor: '#059669',
                      color: '#ffffff',
                      border: 'none',
                      borderRadius: '8px',
                      fontSize: '12.5px',
                      fontWeight: 600,
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px',
                    }}
                  >
                    <span>View Consolidated Incident</span>
                    <ExternalLink size={13} />
                  </button>
                </div>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

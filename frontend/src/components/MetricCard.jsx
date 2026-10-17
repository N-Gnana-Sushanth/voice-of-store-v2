import React from 'react';

export default function MetricCard({
  title,
  value,
  subtext,
  icon: Icon,
  iconBg = '#eff6ff',
  iconColor = '#3b82f6',
  trendType = 'up', // 'up', 'down', 'neutral'
  sparklineColor = '#3b82f6',
  sparklinePoints = 'M0,18 Q30,6 60,15 T120,8 T180,14 T240,4',
}) {
  return (
    <div
      style={{
        backgroundColor: '#ffffff',
        border: '1px solid var(--border-card)',
        borderRadius: '14px',
        padding: '16px 18px 12px 18px',
        boxShadow: 'var(--shadow-card)',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      {/* Top Header with Title and Circle Icon */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <span style={{ fontSize: '12.5px', fontWeight: 600, color: '#64748b' }}>
          {title}
        </span>
        <div
          style={{
            width: '34px',
            height: '34px',
            borderRadius: '50%',
            backgroundColor: iconBg,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexShrink: 0,
          }}
        >
          {Icon && <Icon size={17} style={{ color: iconColor }} strokeWidth={2.2} />}
        </div>
      </div>

      {/* Main Metric Value */}
      <div style={{ marginTop: '8px', marginBottom: '4px' }}>
        <span
          style={{
            fontSize: '25px',
            fontWeight: 800,
            color: '#0f172a',
            letterSpacing: '-0.02em',
            lineHeight: 1.1,
          }}
        >
          {value}
        </span>
      </div>

      {/* Subtext / Trend */}
      <div style={{ fontSize: '11.5px', fontWeight: 600, color: '#64748b', display: 'flex', alignItems: 'center', gap: '4px' }}>
        {subtext.startsWith('↑') && (
          <span style={{ color: '#059669', fontWeight: 700 }}>{subtext}</span>
        )}
        {subtext.startsWith('↓') && (
          <span style={{ color: '#059669', fontWeight: 700 }}>{subtext}</span>
        )}
        {!subtext.startsWith('↑') && !subtext.startsWith('↓') && (
          <span style={{ color: '#64748b' }}>{subtext}</span>
        )}
      </div>

      {/* Bottom Sparkline Wave */}
      <div style={{ width: '100%', height: '22px', marginTop: '6px' }}>
        <svg viewBox="0 0 240 24" width="100%" height="100%" preserveAspectRatio="none">
          <path
            d={sparklinePoints}
            fill="none"
            stroke={sparklineColor}
            strokeWidth="2.2"
            strokeLinecap="round"
          />
        </svg>
      </div>
    </div>
  );
}

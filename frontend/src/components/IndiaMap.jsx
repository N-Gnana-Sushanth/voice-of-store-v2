import React from 'react';

export default function IndiaMap() {
  const legendItems = [
    { label: '> 50', color: '#047857' },
    { label: '30 – 50', color: '#059669' },
    { label: '15 – 30', color: '#10b981' },
    { label: '5 – 15', color: '#6ee7b7' },
    { label: '< 5', color: '#a7f3d0' },
  ];

  const regionBars = [
    { name: 'South', value: 48, barColor: '#f87171' },
    { name: 'West', value: 32, barColor: '#fb923c' },
    { name: 'North', value: 18, barColor: '#4ade80' },
    { name: 'East', value: 12, barColor: '#2dd4bf' },
  ];

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '20px', width: '100%' }}>
      {/* India Map Geometric Representation */}
      <div style={{ width: '130px', height: '150px', position: 'relative', flexShrink: 0 }}>
        <svg viewBox="0 0 140 160" width="100%" height="100%">
          {/* North Region (Kashmir, Punjab, Delhi) */}
          <path
            d="M50,15 L68,10 L80,22 L72,36 L52,38 L42,26 Z"
            fill="#6ee7b7"
            stroke="#ffffff"
            strokeWidth="1.2"
          />
          {/* North-Central (UP, Rajasthan) */}
          <path
            d="M32,38 L52,38 L72,36 L82,48 L76,64 L46,62 L30,52 Z"
            fill="#a7f3d0"
            stroke="#ffffff"
            strokeWidth="1.2"
          />
          {/* West Region (Gujarat, Maharashtra) */}
          <path
            d="M16,56 L38,58 L46,62 L52,86 L36,94 L22,78 Z"
            fill="#059669"
            stroke="#ffffff"
            strokeWidth="1.2"
          />
          {/* Central (MP, Chhattisgarh) */}
          <path
            d="M46,62 L76,64 L86,76 L68,90 L52,86 Z"
            fill="#34d399"
            stroke="#ffffff"
            strokeWidth="1.2"
          />
          {/* East Region (Bihar, Bengal, Odisha, Northeast) */}
          <path
            d="M76,64 L96,62 L106,56 L124,54 L126,70 L108,76 L86,76 Z"
            fill="#a7f3d0"
            stroke="#ffffff"
            strokeWidth="1.2"
          />
          {/* South Region (Karnataka, AP, TN, Kerala) */}
          <path
            d="M36,94 L52,86 L68,90 L62,118 L54,142 L42,128 L36,104 Z"
            fill="#047857"
            stroke="#ffffff"
            strokeWidth="1.2"
          />
        </svg>

        {/* Floating map legend */}
        <div style={{ position: 'absolute', right: '-4px', bottom: '10px', fontSize: '9px', lineHeight: 1.3 }}>
          <span style={{ fontSize: '9px', fontWeight: 600, color: '#64748b', display: 'block', marginBottom: '2px' }}>
            Issue Rate<br />(per 100 stores)
          </span>
          {legendItems.map((item) => (
            <div key={item.label} style={{ display: 'flex', alignItems: 'center', gap: '4px', marginBottom: '1.5px' }}>
              <span style={{ width: '8px', height: '8px', backgroundColor: item.color, borderRadius: '2px' }} />
              <span style={{ color: '#475569', fontSize: '9px', fontWeight: 500 }}>{item.label}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Region Bar Chart Breakdown */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '8px' }}>
        {regionBars.map((r) => (
          <div key={r.name} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ width: '40px', fontSize: '11.5px', fontWeight: 600, color: '#334155' }}>
              {r.name}
            </span>
            {/* Progress Track */}
            <div
              style={{
                flex: 1,
                height: '11px',
                backgroundColor: '#f1f5f9',
                borderRadius: '6px',
                overflow: 'hidden',
                position: 'relative',
              }}
            >
              <div
                style={{
                  width: `${(r.value / 60) * 100}%`,
                  height: '100%',
                  backgroundColor: r.barColor,
                  borderRadius: '6px',
                }}
              />
            </div>
            <span style={{ width: '20px', fontSize: '11.5px', fontWeight: 700, color: '#0f172a', textAlign: 'right' }}>
              {r.value}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

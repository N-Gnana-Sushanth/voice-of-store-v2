import React from 'react';
import { Link } from 'react-router-dom';

export default function BrandLogo({ to = '/', showSubtitle = true, size = 'default' }) {
  const isLarge = size === 'large';

  return (
    <Link
      to={to}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '10px',
        textDecoration: 'none',
        userSelect: 'none',
      }}
    >
      {/* Green Shopping Bag with Audio Waves */}
      <div
        style={{
          width: isLarge ? '40px' : '34px',
          height: isLarge ? '40px' : '34px',
          backgroundColor: '#059669',
          borderRadius: '9px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          position: 'relative',
          boxShadow: '0 2px 5px rgba(5, 150, 105, 0.25)',
          flexShrink: 0,
        }}
      >
        {/* Bag Handle */}
        <div
          style={{
            position: 'absolute',
            top: '-4px',
            width: isLarge ? '16px' : '14px',
            height: '7px',
            border: '2.5px solid #059669',
            borderBottom: 'none',
            borderRadius: '6px 6px 0 0',
          }}
        />
        {/* 3 Audio Wave Lines inside bag */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: isLarge ? '3px' : '2.5px',
            height: '16px',
          }}
        >
          <span
            style={{
              width: '2.5px',
              height: '8px',
              backgroundColor: '#ffffff',
              borderRadius: '2px',
            }}
          />
          <span
            style={{
              width: '2.5px',
              height: '14px',
              backgroundColor: '#ffffff',
              borderRadius: '2px',
            }}
          />
          <span
            style={{
              width: '2.5px',
              height: '8px',
              backgroundColor: '#ffffff',
              borderRadius: '2px',
            }}
          />
        </div>
      </div>

      {/* Brand Text */}
      <div style={{ display: 'flex', flexDirection: 'column', lineHeight: 1.15 }}>
        <span
          style={{
            fontSize: isLarge ? '17px' : '15px',
            fontWeight: 800,
            color: '#0f172a',
            letterSpacing: '-0.02em',
          }}
        >
          Voice-of-Store
        </span>
        {showSubtitle && (
          <span
            style={{
              fontSize: isLarge ? '11px' : '10.5px',
              fontWeight: 500,
              color: '#64748b',
              marginTop: '2px',
              letterSpacing: '-0.01em',
            }}
          >
            Turning Store Chatter Into Action
          </span>
        )}
      </div>
    </Link>
  );
}

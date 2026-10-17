import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  MessageSquareText,
  AlertTriangle,
  TrendingUp,
  ClipboardList,
  FileBarChart,
  Store,
  Settings,
} from 'lucide-react';
import BrandLogo from './BrandLogo';

export default function Sidebar() {
  const location = useLocation();

  const navItems = [
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { name: 'Feedback Stream', path: '/feedback-stream', icon: MessageSquareText },
    { name: 'Issue Analysis', path: '/issue-analysis', icon: AlertTriangle },
    { name: 'Emerging Issues', path: '/emerging-issues', icon: TrendingUp },
    { name: 'Action Queue', path: '/action-queue', icon: ClipboardList },
    { name: 'Regional Reports', path: '/regional-reports', icon: FileBarChart },
    { name: 'Stores', path: '/stores', icon: Store },
    { name: 'Settings', path: '/settings', icon: Settings },
  ];

  // Dynamic bottom slogan matching the reference screenshot for each page
  const getBannerText = () => {
    switch (location.pathname) {
      case '/feedback-stream':
        return 'Listen to every voice. Build better stores.';
      case '/issue-analysis':
        return 'Real voices. Real insights. Better stores.';
      case '/emerging-issues':
        return 'Spot small problems today. Prevent big ones tomorrow.';
      case '/dashboard':
      default:
        return 'Every voice makes a better store.';
    }
  };

  return (
    <aside
      style={{
        width: 'var(--sidebar-width)',
        backgroundColor: '#ffffff',
        borderRight: '1px solid var(--border-card)',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
        padding: '18px 0',
        minHeight: '100vh',
        flexShrink: 0,
      }}
    >
      <div>
        {/* Top Logo */}
        <div style={{ padding: '0 20px 22px 20px' }}>
          <BrandLogo to="/dashboard" />
        </div>

        {/* Navigation List */}
        <nav style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;

            return (
              <NavLink
                key={item.path}
                to={item.path}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  padding: '9.5px 20px',
                  fontSize: '13px',
                  fontWeight: isActive ? 600 : 500,
                  color: isActive ? '#059669' : '#475569',
                  backgroundColor: isActive ? '#e6f7ef' : 'transparent',
                  position: 'relative',
                  transition: 'all 0.15s ease',
                  textDecoration: 'none',
                  borderRadius: isActive ? '0 10px 10px 0' : '0',
                  marginRight: isActive ? '12px' : '0',
                }}
              >
                {/* Active Left Indicator Bar */}
                {isActive && (
                  <span
                    style={{
                      position: 'absolute',
                      left: 0,
                      top: 0,
                      bottom: 0,
                      width: '4px',
                      backgroundColor: '#059669',
                      borderRadius: '0 2px 2px 0',
                    }}
                  />
                )}
                <Icon
                  size={17}
                  strokeWidth={isActive ? 2.3 : 1.8}
                  style={{ color: isActive ? '#059669' : '#64748b' }}
                />
                <span>{item.name}</span>
              </NavLink>
            );
          })}
        </nav>
      </div>

      {/* Bottom Store Illustration Card */}
      <div style={{ padding: '0 16px' }}>
        <div
          style={{
            backgroundColor: '#eaf5ef',
            borderRadius: '16px',
            padding: '16px 14px',
            textAlign: 'center',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            boxShadow: 'inset 0 1px 2px rgba(255,255,255,0.6)',
          }}
        >
          {/* Store Vector Illustration */}
          <div
            style={{
              width: '74px',
              height: '52px',
              position: 'relative',
              marginBottom: '10px',
            }}
          >
            <svg viewBox="0 0 100 70" width="100%" height="100%">
              {/* Background Trees */}
              <circle cx="16" cy="38" r="12" fill="#22c55e" opacity="0.9" />
              <rect x="14" y="44" width="4" height="18" fill="#854d0e" />
              <circle cx="84" cy="38" r="12" fill="#16a34a" opacity="0.9" />
              <rect x="82" y="44" width="4" height="18" fill="#854d0e" />

              {/* Store Building Base */}
              <rect x="22" y="26" width="56" height="36" rx="2" fill="#ffffff" stroke="#cbd5e1" strokeWidth="1.5" />
              {/* Store Window & Door */}
              <rect x="27" y="38" width="16" height="18" rx="2" fill="#38bdf8" opacity="0.75" />
              <rect x="47" y="36" width="13" height="26" rx="1.5" fill="#f8fafc" stroke="#94a3b8" strokeWidth="1" />
              <circle cx="56" cy="48" r="1.5" fill="#64748b" />
              <rect x="63" y="38" width="11" height="18" rx="2" fill="#38bdf8" opacity="0.75" />

              {/* Red & White Striped Awning */}
              <path
                d="M18 26 L24 16 L76 16 L82 26 Z"
                fill="#f87171"
              />
              {/* Awning stripes */}
              <polygon points="26,16 32,16 30,26 24,26" fill="#ffffff" />
              <polygon points="38,16 44,16 42,26 36,26" fill="#ffffff" />
              <polygon points="50,16 56,16 54,26 48,26" fill="#ffffff" />
              <polygon points="62,16 68,16 66,26 60,26" fill="#ffffff" />
              <polygon points="74,16 80,16 78,26 72,26" fill="#ffffff" />
            </svg>
          </div>

          <p
            style={{
              fontSize: '12.5px',
              fontWeight: 700,
              color: '#0f172a',
              lineHeight: 1.35,
              marginBottom: '8px',
            }}
          >
            {getBannerText()}
          </p>

          {/* Green underline pill */}
          <div
            style={{
              width: '26px',
              height: '3.5px',
              backgroundColor: '#059669',
              borderRadius: '2px',
            }}
          />
        </div>
      </div>
    </aside>
  );
}

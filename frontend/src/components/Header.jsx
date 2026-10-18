import React, { useState, useRef, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import {
  Search,
  Calendar,
  MapPin,
  Bell,
  ChevronDown,
  CheckCircle2,
  AlertTriangle,
  Info,
  ShieldAlert,
  LogOut,
  Settings,
  ExternalLink,
  Check,
  RefreshCw,
  X,
  Menu,
} from 'lucide-react';
import { useApp } from '../context/AppContext';

export default function Header({ searchPlaceholder = "Search stores, issues, keywords..." }) {
  const navigate = useNavigate();
  const {
    user,
    selectedDate,
    setSelectedDate,
    selectedRegion,
    setSelectedRegion,
    notifications,
    unreadCount,
    isBackendOnline,
    notificationsLoading,
    refreshNotifications,
    markNotificationAsRead,
    markAllNotificationsAsRead,
    logout,
    toggleSidebar,
  } = useApp();

  const [showDateDropdown, setShowDateDropdown] = useState(false);
  const [showRegionDropdown, setShowRegionDropdown] = useState(false);
  const [showNotificationPanel, setShowNotificationPanel] = useState(false);
  const [showProfileMenu, setShowProfileMenu] = useState(false);
  const [searchValue, setSearchValue] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [showSearchResults, setShowSearchResults] = useState(false);

  const notifRef = useRef(null);
  const profileRef = useRef(null);
  const dateRef = useRef(null);
  const regionRef = useRef(null);
  const searchRef = useRef(null);

  const dateOptions = [
    "Week of 12 Oct - 18 Oct 2026",
    "Week of 05 Oct - 11 Oct 2026",
    "Week of 28 Sep - 04 Oct 2026",
    "Last 30 Days",
  ];

  const regionOptions = [
    "All Regions",
    "South Region (Chennai, Bengaluru, Hyderabad)",
    "West Region (Pune, Mumbai)",
    "North Region (Delhi, NCR)",
    "East Region (Kolkata)",
  ];

  // Close menus on outside click or Escape
  useEffect(() => {
    function handleClickOutside(event) {
      if (notifRef.current && !notifRef.current.contains(event.target)) {
        setShowNotificationPanel(false);
      }
      if (profileRef.current && !profileRef.current.contains(event.target)) {
        setShowProfileMenu(false);
      }
      if (dateRef.current && !dateRef.current.contains(event.target)) {
        setShowDateDropdown(false);
      }
      if (regionRef.current && !regionRef.current.contains(event.target)) {
        setShowRegionDropdown(false);
      }
      if (searchRef.current && !searchRef.current.contains(event.target)) {
        setShowSearchResults(false);
      }
    }

    function handleKeyDown(event) {
      if (event.key === 'Escape') {
        setShowNotificationPanel(false);
        setShowProfileMenu(false);
        setShowDateDropdown(false);
        setShowRegionDropdown(false);
        setShowSearchResults(false);
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, []);

  // Quick search simulation
  const handleSearchChange = (e) => {
    const val = e.target.value;
    setSearchValue(val);
    if (val.trim().length >= 2) {
      const q = val.toLowerCase();
      const mockMatches = [
        { type: 'Issue', title: 'Broken / Faulty Freezer', link: '/issue-analysis', sub: 'Equipment & Maintenance' },
        { type: 'Issue', title: 'Missing / Mislabeled Allergen Info', link: '/issue-analysis', sub: 'Food Safety' },
        { type: 'Store', title: 'Store #128 — T. Nagar (Chennai)', link: '/stores', sub: 'Active Spike Alert' },
        { type: 'Store', title: 'Store #074 — Kothrud (Pune)', link: '/stores', sub: 'Active Spike Alert' },
        { type: 'Feedback', title: 'Freezer not working again 😡 food spoiled', link: '/feedback-stream', sub: 'Online Review' },
      ].filter((item) => item.title.toLowerCase().includes(q) || item.sub.toLowerCase().includes(q));
      setSearchResults(mockMatches);
      setShowSearchResults(true);
    } else {
      setSearchResults([]);
      setShowSearchResults(false);
    }
  };

  const handleSearchSubmit = (e) => {
    if (e.key === 'Enter' && searchValue.trim()) {
      setShowSearchResults(false);
      navigate(`/feedback-stream?search=${encodeURIComponent(searchValue.trim())}`);
    }
  };

  const getSeverityIcon = (severity) => {
    switch (severity?.toUpperCase()) {
      case 'CRITICAL':
      case 'HIGH':
        return <AlertTriangle size={15} style={{ color: '#ef4444' }} />;
      case 'WARNING':
        return <ShieldAlert size={15} style={{ color: '#f59e0b' }} />;
      default:
        return <Info size={15} style={{ color: '#3b82f6' }} />;
    }
  };

  return (
    <header className="app-header">
      {/* Search Bar & Mobile Menu */}
      <div className="header-left-group">
        <button
          className="mobile-menu-btn"
          onClick={toggleSidebar}
          title="Open navigation menu"
          aria-label="Open navigation menu"
        >
          <Menu size={18} />
        </button>

        <div ref={searchRef} className="header-search-box">
          <Search
            size={16}
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
          value={searchValue}
          onChange={handleSearchChange}
          onKeyDown={handleSearchSubmit}
          placeholder={searchPlaceholder}
          style={{
            width: '100%',
            height: '38px',
            paddingLeft: '36px',
            paddingRight: '12px',
            backgroundColor: '#f8fafc',
            border: '1px solid #e2e8f0',
            borderRadius: '9px',
            fontSize: '13px',
            color: '#0f172a',
            transition: 'border-color 0.15s ease',
          }}
        />

        {/* Search Results Dropdown */}
        {showSearchResults && (
          <div
            style={{
              position: 'absolute',
              top: '44px',
              left: 0,
              right: 0,
              backgroundColor: '#ffffff',
              border: '1px solid #e2e8f0',
              borderRadius: '10px',
              boxShadow: '0 10px 25px -5px rgba(0,0,0,0.1)',
              padding: '6px',
              zIndex: 50,
              maxHeight: '280px',
              overflowY: 'auto',
            }}
          >
            {searchResults.length === 0 ? (
              <div style={{ padding: '10px 12px', fontSize: '12px', color: '#64748b', textAlign: 'center' }}>
                No quick matches. Press <kbd style={{ padding: '2px 4px', backgroundColor: '#f1f5f9', borderRadius: '4px' }}>Enter</kbd> to search Feedback Stream.
              </div>
            ) : (
              searchResults.map((item, idx) => (
                <div
                  key={idx}
                  onClick={() => {
                    setShowSearchResults(false);
                    navigate(item.link);
                  }}
                  style={{
                    padding: '8px 12px',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    fontSize: '12.5px',
                    backgroundColor: '#ffffff',
                    transition: 'background-color 0.1s ease',
                  }}
                  onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = '#f8fafc')}
                  onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = '#ffffff')}
                >
                  <div>
                    <div style={{ fontWeight: 600, color: '#0f172a' }}>{item.title}</div>
                    <div style={{ fontSize: '11px', color: '#64748b' }}>{item.sub}</div>
                  </div>
                  <span
                    style={{
                      fontSize: '10.5px',
                      fontWeight: 600,
                      padding: '2px 6px',
                      borderRadius: '4px',
                      backgroundColor: '#eff6ff',
                      color: '#2563eb',
                    }}
                  >
                    {item.type}
                  </span>
                </div>
              ))
            )}
          </div>
        )}
      </div>
      </div>

      {/* Right Controls */}
      <div className="header-controls" style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        {/* Date Filter Dropdown */}
        <div ref={dateRef} style={{ position: 'relative' }}>
          <button
            className="date-filter-btn"
            onClick={() => {
              setShowDateDropdown(!showDateDropdown);
              setShowRegionDropdown(false);
              setShowNotificationPanel(false);
              setShowProfileMenu(false);
            }}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              height: '38px',
              padding: '0 12px',
              backgroundColor: '#ffffff',
              border: '1px solid #e2e8f0',
              borderRadius: '9px',
              fontSize: '12.5px',
              fontWeight: 600,
              color: '#334155',
              cursor: 'pointer',
              whiteSpace: 'nowrap',
            }}
          >
            <Calendar size={15} style={{ color: '#059669' }} />
            <span>{selectedDate}</span>
            <ChevronDown size={14} style={{ color: '#64748b' }} />
          </button>

          {showDateDropdown && (
            <div
              style={{
                position: 'absolute',
                top: '44px',
                right: 0,
                backgroundColor: '#ffffff',
                border: '1px solid #e2e8f0',
                borderRadius: '10px',
                boxShadow: '0 10px 25px -5px rgba(0,0,0,0.1)',
                minWidth: '240px',
                maxWidth: 'calc(100vw - 24px)',
                padding: '6px',
                zIndex: 50,
              }}
            >
              {dateOptions.map((opt) => (
                <div
                  key={opt}
                  onClick={() => {
                    setSelectedDate(opt);
                    setShowDateDropdown(false);
                  }}
                  style={{
                    padding: '8px 12px',
                    fontSize: '12.5px',
                    fontWeight: opt === selectedDate ? 600 : 400,
                    color: opt === selectedDate ? '#059669' : '#334155',
                    backgroundColor: opt === selectedDate ? '#e6f7ef' : 'transparent',
                    borderRadius: '6px',
                    cursor: 'pointer',
                  }}
                >
                  {opt}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Region Filter Dropdown */}
        <div ref={regionRef} style={{ position: 'relative' }}>
          <button
            className="region-filter-btn"
            onClick={() => {
              setShowRegionDropdown(!showRegionDropdown);
              setShowDateDropdown(false);
              setShowNotificationPanel(false);
              setShowProfileMenu(false);
            }}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              height: '38px',
              padding: '0 12px',
              backgroundColor: '#ffffff',
              border: '1px solid #e2e8f0',
              borderRadius: '9px',
              fontSize: '12.5px',
              fontWeight: 600,
              color: '#334155',
              cursor: 'pointer',
              whiteSpace: 'nowrap',
            }}
          >
            <MapPin size={15} style={{ color: '#059669' }} />
            <span>{selectedRegion}</span>
            <ChevronDown size={14} style={{ color: '#64748b' }} />
          </button>

          {showRegionDropdown && (
            <div
              style={{
                position: 'absolute',
                top: '44px',
                right: 0,
                backgroundColor: '#ffffff',
                border: '1px solid #e2e8f0',
                borderRadius: '10px',
                boxShadow: '0 10px 25px -5px rgba(0,0,0,0.1)',
                minWidth: '260px',
                maxWidth: 'calc(100vw - 24px)',
                padding: '6px',
                zIndex: 50,
              }}
            >
              {regionOptions.map((reg) => (
                <div
                  key={reg}
                  onClick={() => {
                    setSelectedRegion(reg);
                    setShowRegionDropdown(false);
                  }}
                  style={{
                    padding: '8px 12px',
                    fontSize: '12.5px',
                    fontWeight: reg === selectedRegion ? 600 : 400,
                    color: reg === selectedRegion ? '#059669' : '#334155',
                    backgroundColor: reg === selectedRegion ? '#e6f7ef' : 'transparent',
                    borderRadius: '6px',
                    cursor: 'pointer',
                  }}
                >
                  {reg}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Notification Bell with Badge and Dropdown Panel */}
        <div ref={notifRef} style={{ position: 'relative', margin: '0 4px' }}>
          <button
            onClick={() => {
              setShowNotificationPanel(!showNotificationPanel);
              setShowProfileMenu(false);
              setShowDateDropdown(false);
              setShowRegionDropdown(false);
            }}
            style={{
              width: '36px',
              height: '36px',
              borderRadius: '9px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              backgroundColor: showNotificationPanel ? '#e6f7ef' : '#f8fafc',
              border: showNotificationPanel ? '1px solid #a7f3d0' : '1px solid #e2e8f0',
              color: showNotificationPanel ? '#059669' : '#475569',
              cursor: 'pointer',
              position: 'relative',
              transition: 'all 0.15s ease',
            }}
          >
            <Bell size={17} />
            {/* Unread badge count */}
            {unreadCount > 0 && (
              <span
                style={{
                  position: 'absolute',
                  top: '-3px',
                  right: '-3px',
                  minWidth: '17px',
                  height: '17px',
                  padding: '0 4px',
                  backgroundColor: '#ef4444',
                  color: '#ffffff',
                  borderRadius: '999px',
                  fontSize: '10px',
                  fontWeight: 700,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  border: '1.5px solid #ffffff',
                }}
              >
                {unreadCount}
              </span>
            )}
          </button>

          {/* Real Notification Dropdown Panel */}
          {showNotificationPanel && (
            <div
              style={{
                position: 'absolute',
                top: '46px',
                right: 0,
                width: '360px',
                maxWidth: 'calc(100vw - 24px)',
                backgroundColor: '#ffffff',
                border: '1px solid #e2e8f0',
                borderRadius: '12px',
                boxShadow: '0 12px 30px -4px rgba(0,0,0,0.12)',
                zIndex: 60,
                display: 'flex',
                flexDirection: 'column',
                overflow: 'hidden',
              }}
            >
              {/* Panel Header */}
              <div
                style={{
                  padding: '12px 16px',
                  borderBottom: '1px solid #f1f5f9',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  backgroundColor: '#fafbfc',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{ fontSize: '13.5px', fontWeight: 700, color: '#0f172a' }}>
                    Notifications
                  </span>
                  {unreadCount > 0 && (
                    <span
                      style={{
                        padding: '1px 6px',
                        backgroundColor: '#fee2e2',
                        color: '#b91c1c',
                        borderRadius: '999px',
                        fontSize: '10.5px',
                        fontWeight: 700,
                      }}
                    >
                      {unreadCount} unread
                    </span>
                  )}
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  {unreadCount > 0 && (
                    <button
                      onClick={markAllNotificationsAsRead}
                      style={{
                        fontSize: '11px',
                        color: '#059669',
                        fontWeight: 600,
                        background: 'none',
                        border: 'none',
                        cursor: 'pointer',
                      }}
                    >
                      Mark all read
                    </button>
                  )}
                  <button
                    onClick={refreshNotifications}
                    style={{
                      background: 'none',
                      border: 'none',
                      color: '#64748b',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                    }}
                    title="Refresh notifications"
                  >
                    <RefreshCw size={13} className={notificationsLoading ? 'spin-icon' : ''} />
                  </button>
                </div>
              </div>

              {/* Notification Items List */}
              <div style={{ maxHeight: '340px', overflowY: 'auto' }}>
                {notificationsLoading && notifications.length === 0 ? (
                  <div style={{ padding: '24px', textAlign: 'center', fontSize: '12.5px', color: '#64748b' }}>
                    Loading notifications...
                  </div>
                ) : notifications.length === 0 ? (
                  <div style={{ padding: '32px 16px', textAlign: 'center', color: '#64748b' }}>
                    <CheckCircle2 size={28} style={{ color: '#059669', margin: '0 auto 8px auto' }} />
                    <div style={{ fontSize: '13px', fontWeight: 600, color: '#0f172a' }}>
                      All caught up!
                    </div>
                    <div style={{ fontSize: '11.5px', marginTop: '2px' }}>
                      No new emerging alerts or compliance notices.
                    </div>
                  </div>
                ) : (
                  notifications.map((notif) => (
                    <div
                      key={notif.id}
                      onClick={() => {
                        markNotificationAsRead(notif.id);
                        if (notif.link) {
                          setShowNotificationPanel(false);
                          navigate(notif.link);
                        }
                      }}
                      style={{
                        padding: '12px 16px',
                        borderBottom: '1px solid #f8fafc',
                        backgroundColor: notif.is_read ? '#ffffff' : '#f8fdfa',
                        cursor: 'pointer',
                        transition: 'background-color 0.1s ease',
                        position: 'relative',
                      }}
                      onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = '#f1f7f4')}
                      onMouseLeave={(e) =>
                        (e.currentTarget.style.backgroundColor = notif.is_read ? '#ffffff' : '#f8fdfa')
                      }
                    >
                      {/* Unread dot */}
                      {!notif.is_read && (
                        <span
                          style={{
                            position: 'absolute',
                            left: '6px',
                            top: '16px',
                            width: '5px',
                            height: '5px',
                            backgroundColor: '#059669',
                            borderRadius: '50%',
                          }}
                        />
                      )}
                      <div style={{ display: 'flex', alignItems: 'flex-start', gap: '8px' }}>
                        <div style={{ marginTop: '2px', flexShrink: 0 }}>
                          {getSeverityIcon(notif.severity)}
                        </div>
                        <div style={{ flex: 1, minWidth: 0 }}>
                          <div
                            style={{
                              fontSize: '12.5px',
                              fontWeight: notif.is_read ? 600 : 700,
                              color: '#0f172a',
                              lineHeight: 1.3,
                            }}
                          >
                            {notif.title}
                          </div>
                          <div
                            style={{
                              fontSize: '11.5px',
                              color: '#475569',
                              marginTop: '2px',
                              lineHeight: 1.4,
                            }}
                          >
                            {notif.message}
                          </div>
                          <div
                            style={{
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'space-between',
                              marginTop: '6px',
                              fontSize: '10.5px',
                              color: '#94a3b8',
                            }}
                          >
                            <span>
                              {new Date(notif.created_at).toLocaleTimeString([], {
                                hour: '2-digit',
                                minute: '2-digit',
                              })}
                            </span>
                            {notif.link && (
                              <span style={{ color: '#059669', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '2px' }}>
                                View <ExternalLink size={10} />
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>

        {/* User Profile Avatar with Dropdown Menu */}
        <div ref={profileRef} style={{ position: 'relative' }}>
          <div
            onClick={() => {
              setShowProfileMenu(!showProfileMenu);
              setShowNotificationPanel(false);
              setShowDateDropdown(false);
              setShowRegionDropdown(false);
            }}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
              marginLeft: '4px',
              paddingLeft: '6px',
              borderLeft: '1px solid #e2e8f0',
              cursor: 'pointer',
              userSelect: 'none',
            }}
          >
            <div
              style={{
                width: '34px',
                height: '34px',
                borderRadius: '50%',
                backgroundColor: '#0f766e',
                color: '#ffffff',
                fontSize: '12px',
                fontWeight: 700,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                letterSpacing: '0.05em',
              }}
            >
              {user.initials || 'SU'}
            </div>
            <div className="header-profile-text" style={{ display: 'flex', flexDirection: 'column', lineHeight: 1.2 }}>
              <span style={{ fontSize: '12.5px', fontWeight: 700, color: '#0f172a' }}>
                {user.name || 'Sushanth'}
              </span>
              <span style={{ fontSize: '10.5px', fontWeight: 500, color: '#64748b' }}>
                {user.role || 'HQ Analyst'}
              </span>
            </div>
            <ChevronDown size={14} style={{ color: '#64748b' }} />
          </div>

          {/* User Profile Dropdown Menu */}
          {showProfileMenu && (
            <div
              style={{
                position: 'absolute',
                top: '46px',
                right: 0,
                width: '240px',
                maxWidth: 'calc(100vw - 24px)',
                backgroundColor: '#ffffff',
                border: '1px solid #e2e8f0',
                borderRadius: '10px',
                boxShadow: '0 10px 25px -5px rgba(0,0,0,0.12)',
                padding: '6px',
                zIndex: 60,
              }}
            >
              {/* User details header */}
              <div
                style={{
                  padding: '8px 10px 10px 10px',
                  borderBottom: '1px solid #f1f5f9',
                  marginBottom: '4px',
                }}
              >
                <div style={{ fontSize: '13px', fontWeight: 700, color: '#0f172a' }}>
                  {user.name}
                </div>
                <div style={{ fontSize: '11px', color: '#64748b' }}>
                  {user.email || 'sushanth@voiceofstore.internal'}
                </div>
                {/* Live backend connectivity badge */}
                <div
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '5px',
                    marginTop: '6px',
                    fontSize: '10.5px',
                    fontWeight: 600,
                    color: isBackendOnline ? '#059669' : '#d97706',
                    backgroundColor: isBackendOnline ? '#e6f7ef' : '#fef3c7',
                    padding: '2px 7px',
                    borderRadius: '4px',
                  }}
                >
                  <span
                    style={{
                      width: '6px',
                      height: '6px',
                      borderRadius: '50%',
                      backgroundColor: isBackendOnline ? '#059669' : '#d97706',
                    }}
                  />
                  <span>{isBackendOnline ? 'API Connected (v1.0.0)' : 'Demo Mode (Offline)'}</span>
                </div>
              </div>

              {/* Navigation links */}
              <div
                onClick={() => {
                  setShowProfileMenu(false);
                  navigate('/settings');
                }}
                style={{
                  padding: '8px 10px',
                  fontSize: '12.5px',
                  color: '#334155',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                }}
                onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = '#f8fafc')}
                onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}
              >
                <Settings size={14} style={{ color: '#64748b' }} />
                <span>Account Settings</span>
              </div>

              <div
                onClick={() => {
                  setShowProfileMenu(false);
                  logout();
                }}
                style={{
                  padding: '8px 10px',
                  fontSize: '12.5px',
                  color: '#ef4444',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                }}
                onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = '#fee2e2')}
                onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}
              >
                <LogOut size={14} />
                <span>Log Out</span>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}

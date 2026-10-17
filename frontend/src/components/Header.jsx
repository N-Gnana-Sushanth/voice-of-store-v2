import React, { useState } from 'react';
import { Search, Calendar, MapPin, Bell, ChevronDown } from 'lucide-react';
import { USER_PROFILE } from '../data/mockData';

export default function Header({ searchPlaceholder = "Search stores, issues, keywords..." }) {
  const [selectedDate, setSelectedDate] = useState("Week of 12 Oct - 18 Oct 2026");
  const [selectedRegion, setSelectedRegion] = useState("All Regions");
  const [showDateDropdown, setShowDateDropdown] = useState(false);
  const [showRegionDropdown, setShowRegionDropdown] = useState(false);
  const [searchValue, setSearchValue] = useState("");

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

  return (
    <header
      style={{
        height: 'var(--header-height)',
        backgroundColor: '#ffffff',
        borderBottom: '1px solid var(--border-card)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 24px',
        position: 'sticky',
        top: 0,
        zIndex: 40,
        flexShrink: 0,
      }}
    >
      {/* Search Bar */}
      <div style={{ position: 'relative', width: '340px' }}>
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
          onChange={(e) => setSearchValue(e.target.value)}
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
      </div>

      {/* Right Controls */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        {/* Date Filter Dropdown */}
        <div style={{ position: 'relative' }}>
          <button
            onClick={() => {
              setShowDateDropdown(!showDateDropdown);
              setShowRegionDropdown(false);
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
        <div style={{ position: 'relative' }}>
          <button
            onClick={() => {
              setShowRegionDropdown(!showRegionDropdown);
              setShowDateDropdown(false);
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

        {/* Notification Bell */}
        <div style={{ position: 'relative', margin: '0 4px' }}>
          <button
            style={{
              width: '36px',
              height: '36px',
              borderRadius: '9px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              backgroundColor: '#f8fafc',
              border: '1px solid #e2e8f0',
              color: '#475569',
            }}
          >
            <Bell size={17} />
          </button>
          {/* Red indicator dot */}
          <span
            style={{
              position: 'absolute',
              top: '7px',
              right: '7px',
              width: '7px',
              height: '7px',
              backgroundColor: '#ef4444',
              borderRadius: '50%',
              border: '1.5px solid #ffffff',
            }}
          />
        </div>

        {/* User Avatar */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            marginLeft: '4px',
            paddingLeft: '6px',
            borderLeft: '1px solid #e2e8f0',
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
            {USER_PROFILE.initials}
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', lineHeight: 1.2 }}>
            <span style={{ fontSize: '12.5px', fontWeight: 700, color: '#0f172a' }}>
              {USER_PROFILE.name}
            </span>
            <span style={{ fontSize: '10.5px', fontWeight: 500, color: '#64748b' }}>
              HQ Analyst
            </span>
          </div>
        </div>
      </div>
    </header>
  );
}

import React, { useState } from 'react';
import {
  Store,
  MapPin,
  Search,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  Sparkles,
  Building2,
  Users,
} from 'lucide-react';
import Sidebar from '../components/Sidebar';
import Header from '../components/Header';

export default function StoresPage() {
  const [search, setSearch] = useState('');
  const [selectedRegion, setSelectedRegion] = useState('All');

  const stores = [
    {
      id: 'STR-128',
      name: 'Store #128 — T. Nagar',
      city: 'Chennai',
      region: 'South',
      format: 'Hypermarket (45,000 sq.ft)',
      manager: 'R. Senthil Kumar',
      activeIssues: 18,
      status: 'Spike Alert',
      severity: 'High',
    },
    {
      id: 'STR-074',
      name: 'Store #074 — Kothrud',
      city: 'Pune',
      region: 'West',
      format: 'Supermarket (22,000 sq.ft)',
      manager: 'Pooja Deshmukh',
      activeIssues: 14,
      status: 'Spike Alert',
      severity: 'High',
    },
    {
      id: 'STR-302',
      name: 'Store #302 — Koramangala',
      city: 'Bengaluru',
      region: 'South',
      format: 'Express Store (8,500 sq.ft)',
      manager: 'Arun Varma',
      activeIssues: 9,
      status: 'Warning',
      severity: 'Medium',
    },
    {
      id: 'STR-215',
      name: 'Store #215 — Banjara Hills',
      city: 'Hyderabad',
      region: 'South',
      format: 'Supermarket (25,000 sq.ft)',
      manager: 'K. Narsimha',
      activeIssues: 6,
      status: 'Normal',
      severity: 'Low',
    },
    {
      id: 'STR-091',
      name: 'Store #091 — MVP Colony',
      city: 'Visakhapatnam',
      region: 'South',
      format: 'Express Store (10,000 sq.ft)',
      manager: 'Suresh Raju',
      activeIssues: 2,
      status: 'Normal',
      severity: 'Low',
    },
    {
      id: 'STR-412',
      name: 'Store #412 — Gandhipuram',
      city: 'Coimbatore',
      region: 'South',
      format: 'Supermarket (18,000 sq.ft)',
      manager: 'M. Anand',
      activeIssues: 5,
      status: 'Normal',
      severity: 'Low',
    },
    {
      id: 'STR-501',
      name: 'Store #501 — Andheri West',
      city: 'Mumbai',
      region: 'West',
      format: 'Hypermarket (38,000 sq.ft)',
      manager: 'Neha Shah',
      activeIssues: 8,
      status: 'Monitoring',
      severity: 'Medium',
    },
    {
      id: 'STR-604',
      name: 'Store #604 — South Extension',
      city: 'Delhi',
      region: 'North',
      format: 'Supermarket (20,000 sq.ft)',
      manager: 'Vikram Malhotra',
      activeIssues: 3,
      status: 'Normal',
      severity: 'Low',
    },
  ];

  const filteredStores = stores.filter((s) => {
    if (selectedRegion !== 'All' && s.region !== selectedRegion) return false;
    if (search.trim() !== '') {
      const q = search.toLowerCase();
      return (
        s.name.toLowerCase().includes(q) ||
        s.city.toLowerCase().includes(q) ||
        s.id.toLowerCase().includes(q)
      );
    }
    return true;
  });

  return (
    <div className="app-container">
      <Sidebar />
      <div className="app-main">
        <Header searchPlaceholder="Search store ID, location, manager..." />

        <main className="page-content">
          {/* Header */}
          <div className="page-header-row">
            <div className="page-title-group">
              <h1>Stores Directory</h1>
              <p>Network of 436 nationwide retail stores, formats, operational contacts, and live alert statuses.</p>
            </div>

            <div className="quote-banner">
              <Sparkles size={14} className="sparkle-icon" />
              <span>"Every store team is on the frontlines of our promise."</span>
            </div>
          </div>

          {/* Search & Filter Toolbar */}
          <div
            className="ui-card"
            style={{
              padding: '14px 18px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              gap: '12px',
              flexWrap: 'wrap',
            }}
          >
            <div style={{ position: 'relative', width: '320px' }}>
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
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search store name, city, ID..."
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

            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontSize: '12px', color: '#64748b' }}>Region:</span>
              {['All', 'South', 'West', 'North', 'East'].map((r) => (
                <button
                  key={r}
                  onClick={() => setSelectedRegion(r)}
                  style={{
                    padding: '5px 12px',
                    borderRadius: '6px',
                    fontSize: '12px',
                    fontWeight: selectedRegion === r ? 600 : 500,
                    backgroundColor: selectedRegion === r ? '#059669' : '#f1f5f9',
                    color: selectedRegion === r ? '#ffffff' : '#475569',
                    border: 'none',
                    cursor: 'pointer',
                  }}
                >
                  {r}
                </button>
              ))}
            </div>
          </div>

          {/* Store Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(290px, 1fr))', gap: '14px' }}>
            {filteredStores.map((store) => (
              <div
                key={store.id}
                className="ui-card"
                style={{
                  padding: '18px',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '12px',
                  borderTop: store.severity === 'High' ? '3px solid #ef4444' : store.severity === 'Medium' ? '3px solid #f97316' : '3px solid #10b981',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
                  <div>
                    <span style={{ fontSize: '11px', fontWeight: 700, color: '#64748b' }}>
                      {store.id}
                    </span>
                    <h3 style={{ fontSize: '14px', fontWeight: 700, color: '#0f172a', marginTop: '2px' }}>
                      {store.name}
                    </h3>
                  </div>

                  <span
                    className={`badge-severity badge-severity-${store.severity.toLowerCase()}`}
                    style={{ fontSize: '11px' }}
                  >
                    <span className="dot" />
                    {store.status}
                  </span>
                </div>

                <div style={{ fontSize: '12px', color: '#64748b', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <MapPin size={13} style={{ color: '#059669' }} />
                    <span>{store.city} ({store.region} Region)</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <Building2 size={13} style={{ color: '#64748b' }} />
                    <span>{store.format}</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <Users size={13} style={{ color: '#64748b' }} />
                    <span>Store Manager: {store.manager}</span>
                  </div>
                </div>

                <div
                  style={{
                    paddingTop: '10px',
                    borderTop: '1px solid #f1f5f9',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                  }}
                >
                  <span style={{ fontSize: '12px', color: '#64748b' }}>
                    Active Issues: <strong style={{ color: store.activeIssues > 10 ? '#ef4444' : '#0f172a' }}>{store.activeIssues}</strong>
                  </span>
                  <button
                    style={{
                      background: 'none',
                      border: 'none',
                      color: '#059669',
                      fontSize: '12px',
                      fontWeight: 600,
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '4px',
                    }}
                  >
                    Details <ArrowRight size={13} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </main>
      </div>
    </div>
  );
}

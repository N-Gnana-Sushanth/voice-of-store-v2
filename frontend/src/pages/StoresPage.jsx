import React, { useState, useEffect } from 'react';
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
  RefreshCw,
  X,
  Phone,
  Mail,
  Clock,
  ShieldAlert,
} from 'lucide-react';
import Sidebar from '../components/Sidebar';
import Header from '../components/Header';
import { api } from '../api/client';
import { useApp } from '../context/AppContext';

const DEFAULT_STORES = [
  {
    id: 'STR-128',
    name: 'Store #128 — T. Nagar',
    city: 'Chennai',
    region: 'South',
    format: 'Hypermarket (45,000 sq.ft)',
    manager: 'R. Senthil Kumar',
    managerPhone: '+91 98401 23456',
    managerEmail: 'senthil.k@voiceofstore.internal',
    activeIssues: 18,
    status: 'Spike Alert',
    severity: 'High',
    hours: '08:00 AM – 10:30 PM',
  },
  {
    id: 'STR-074',
    name: 'Store #074 — Kothrud',
    city: 'Pune',
    region: 'West',
    format: 'Supermarket (22,000 sq.ft)',
    manager: 'Pooja Deshmukh',
    managerPhone: '+91 98220 54321',
    managerEmail: 'pooja.d@voiceofstore.internal',
    activeIssues: 14,
    status: 'Spike Alert',
    severity: 'High',
    hours: '08:30 AM – 10:00 PM',
  },
  {
    id: 'STR-302',
    name: 'Store #302 — Koramangala',
    city: 'Bengaluru',
    region: 'South',
    format: 'Express Store (8,500 sq.ft)',
    manager: 'Arun Varma',
    managerPhone: '+91 98450 67890',
    managerEmail: 'arun.v@voiceofstore.internal',
    activeIssues: 9,
    status: 'Warning',
    severity: 'Medium',
    hours: '07:00 AM – 11:00 PM',
  },
  {
    id: 'STR-215',
    name: 'Store #215 — Banjara Hills',
    city: 'Hyderabad',
    region: 'South',
    format: 'Supermarket (25,000 sq.ft)',
    manager: 'K. Narsimha',
    managerPhone: '+91 98490 11223',
    managerEmail: 'narsimha.k@voiceofstore.internal',
    activeIssues: 6,
    status: 'Normal',
    severity: 'Low',
    hours: '08:00 AM – 10:00 PM',
  },
  {
    id: 'STR-091',
    name: 'Store #091 — MVP Colony',
    city: 'Visakhapatnam',
    region: 'South',
    format: 'Express Store (10,000 sq.ft)',
    manager: 'Suresh Raju',
    managerPhone: '+91 98480 33445',
    managerEmail: 'suresh.r@voiceofstore.internal',
    activeIssues: 2,
    status: 'Normal',
    severity: 'Low',
    hours: '08:00 AM – 10:00 PM',
  },
  {
    id: 'STR-412',
    name: 'Store #412 — Gandhipuram',
    city: 'Coimbatore',
    region: 'South',
    format: 'Supermarket (18,000 sq.ft)',
    manager: 'M. Anand',
    managerPhone: '+91 98420 55667',
    managerEmail: 'anand.m@voiceofstore.internal',
    activeIssues: 5,
    status: 'Normal',
    severity: 'Low',
    hours: '08:00 AM – 10:00 PM',
  },
  {
    id: 'STR-501',
    name: 'Store #501 — Andheri West',
    city: 'Mumbai',
    region: 'West',
    format: 'Hypermarket (38,000 sq.ft)',
    manager: 'Neha Shah',
    managerPhone: '+91 98200 77889',
    managerEmail: 'neha.s@voiceofstore.internal',
    activeIssues: 8,
    status: 'Monitoring',
    severity: 'Medium',
    hours: '08:00 AM – 11:00 PM',
  },
  {
    id: 'STR-604',
    name: 'Store #604 — South Extension',
    city: 'Delhi',
    region: 'North',
    format: 'Supermarket (20,000 sq.ft)',
    manager: 'Vikram Malhotra',
    managerPhone: '+91 98110 99001',
    managerEmail: 'vikram.m@voiceofstore.internal',
    activeIssues: 3,
    status: 'Normal',
    severity: 'Low',
    hours: '08:30 AM – 10:30 PM',
  },
];

export default function StoresPage() {
  const { isLive: globalIsLive } = useApp();
  const [stores, setStores] = useState(DEFAULT_STORES);
  const [search, setSearch] = useState('');
  const [selectedRegion, setSelectedRegion] = useState('All');
  const [isLive, setIsLive] = useState(false);
  const [loading, setLoading] = useState(false);
  const [selectedStore, setSelectedStore] = useState(null);

  const loadStores = async () => {
    setLoading(true);
    try {
      const res = await api.stores.list();
      if (res && res.length > 0) {
        setIsLive(true);
        // Enrich backend stores with layout metadata
        const enriched = res.map((s, idx) => {
          const fallback = DEFAULT_STORES.find((ds) => ds.id === s.id) || DEFAULT_STORES[idx % DEFAULT_STORES.length];
          return {
            id: s.id,
            name: s.name,
            city: s.city,
            region: s.region,
            format: fallback?.format || 'Supermarket (20,000 sq.ft)',
            manager: fallback?.manager || 'Store Manager',
            managerPhone: fallback?.managerPhone || '+91 98000 00000',
            managerEmail: fallback?.managerEmail || `${s.id.toLowerCase()}@voiceofstore.internal`,
            activeIssues: fallback?.activeIssues || 4,
            status: fallback?.status || 'Normal',
            severity: fallback?.severity || 'Low',
            hours: fallback?.hours || '08:00 AM – 10:00 PM',
          };
        });
        setStores(enriched);
      } else {
        setStores(DEFAULT_STORES);
      }
    } catch (err) {
      console.warn('Backend stores API unavailable, using reference stores:', err.message);
      setIsLive(false);
      setStores(DEFAULT_STORES);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadStores();
  }, []);

  const filteredStores = stores.filter((s) => {
    if (selectedRegion !== 'All' && s.region !== selectedRegion) return false;
    if (search.trim() !== '') {
      const q = search.toLowerCase();
      return (
        s.name.toLowerCase().includes(q) ||
        s.city.toLowerCase().includes(q) ||
        s.id.toLowerCase().includes(q) ||
        s.manager.toLowerCase().includes(q)
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
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <h1>Stores Directory</h1>
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
              <p>Network of nationwide retail stores, formats, operational contacts, and live alert statuses.</p>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <button
                onClick={loadStores}
                disabled={loading}
                title="Refresh stores directory"
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '4px',
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

              <div className="quote-banner">
                <Sparkles size={14} className="sparkle-icon" />
                <span>"Every store team is on the frontlines of our promise."</span>
              </div>
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
                    transition: 'all 0.15s ease',
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
                  borderTop:
                    store.severity === 'High'
                      ? '3px solid #ef4444'
                      : store.severity === 'Medium'
                      ? '3px solid #f97316'
                      : '3px solid #10b981',
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
                    onClick={() => setSelectedStore(store)}
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

          {/* Store Details Modal */}
          {selectedStore && (
            <div
              style={{
                position: 'fixed',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                backgroundColor: 'rgba(15, 23, 42, 0.45)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                zIndex: 1000,
                padding: '20px',
              }}
              onClick={() => setSelectedStore(null)}
            >
              <div
                style={{
                  backgroundColor: '#ffffff',
                  borderRadius: '12px',
                  maxWidth: '520px',
                  width: '100%',
                  boxShadow: '0 20px 25px -5px rgba(0,0,0,0.1), 0 10px 10px -5px rgba(0,0,0,0.04)',
                  overflow: 'hidden',
                }}
                onClick={(e) => e.stopPropagation()}
              >
                {/* Modal Header */}
                <div
                  style={{
                    padding: '16px 20px',
                    borderBottom: '1px solid #f1f5f9',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    backgroundColor: '#f8fafc',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <Store size={18} style={{ color: '#059669' }} />
                    <h3 style={{ fontSize: '15px', fontWeight: 700, color: '#0f172a', margin: 0 }}>
                      {selectedStore.name}
                    </h3>
                  </div>
                  <button
                    onClick={() => setSelectedStore(null)}
                    style={{
                      background: 'none',
                      border: 'none',
                      cursor: 'pointer',
                      color: '#94a3b8',
                      padding: '4px',
                      borderRadius: '4px',
                    }}
                  >
                    <X size={18} />
                  </button>
                </div>

                {/* Modal Body */}
                <div style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <span style={{ fontSize: '12px', color: '#64748b', fontWeight: 600 }}>
                      Store ID: {selectedStore.id}
                    </span>
                    <span className={`badge-severity badge-severity-${selectedStore.severity.toLowerCase()}`}>
                      <span className="dot" />
                      {selectedStore.status}
                    </span>
                  </div>

                  <div
                    style={{
                      backgroundColor: '#f8fafc',
                      borderRadius: '8px',
                      padding: '14px',
                      display: 'flex',
                      flexDirection: 'column',
                      gap: '8px',
                      fontSize: '12.5px',
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#334155' }}>
                      <MapPin size={14} style={{ color: '#059669', flexShrink: 0 }} />
                      <span>{selectedStore.city}, {selectedStore.region} Region</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#334155' }}>
                      <Building2 size={14} style={{ color: '#64748b', flexShrink: 0 }} />
                      <span>Format: {selectedStore.format}</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#334155' }}>
                      <Clock size={14} style={{ color: '#64748b', flexShrink: 0 }} />
                      <span>Operating Hours: {selectedStore.hours}</span>
                    </div>
                  </div>

                  <div>
                    <h4 style={{ fontSize: '13px', fontWeight: 700, color: '#0f172a', marginBottom: '8px' }}>
                      Store Operations Contact
                    </h4>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', fontSize: '12px', color: '#475569' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <Users size={14} style={{ color: '#64748b' }} />
                        <span>Manager: <strong>{selectedStore.manager}</strong></span>
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <Phone size={14} style={{ color: '#64748b' }} />
                        <span>Phone: {selectedStore.managerPhone}</span>
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <Mail size={14} style={{ color: '#64748b' }} />
                        <span>Email: {selectedStore.managerEmail}</span>
                      </div>
                    </div>
                  </div>

                  <div
                    style={{
                      borderTop: '1px solid #f1f5f9',
                      paddingTop: '14px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      fontSize: '12px',
                    }}
                  >
                    <span style={{ color: '#64748b' }}>
                      Open Remediation Incidents: <strong style={{ color: selectedStore.activeIssues > 10 ? '#ef4444' : '#059669' }}>{selectedStore.activeIssues}</strong>
                    </span>
                    <button
                      onClick={() => setSelectedStore(null)}
                      style={{
                        padding: '6px 14px',
                        backgroundColor: '#059669',
                        color: '#ffffff',
                        border: 'none',
                        borderRadius: '6px',
                        fontSize: '12px',
                        fontWeight: 600,
                        cursor: 'pointer',
                      }}
                    >
                      Close
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

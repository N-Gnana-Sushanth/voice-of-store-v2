import React, { useState, useEffect } from 'react';
import {
  Settings,
  ShieldCheck,
  Cpu,
  Radio,
  User,
  Sparkles,
  Save,
  Check,
  Activity,
  Server,
  RefreshCw,
} from 'lucide-react';
import Sidebar from '../components/Sidebar';
import Header from '../components/Header';
import { api } from '../api/client';
import { useApp } from '../context/AppContext';
import { USER_PROFILE } from '../data/mockData';

export default function SettingsPage() {
  const { user, isLive: globalIsLive } = useApp();
  const [saved, setSaved] = useState(false);
  const [similarityThreshold, setSimilarityThreshold] = useState(() => {
    const savedVal = localStorage.getItem('vos_settings_threshold');
    return savedVal ? parseFloat(savedVal) : 0.82;
  });
  const [emergingZScore, setEmergingZScore] = useState(() => {
    const savedVal = localStorage.getItem('vos_settings_zscore');
    return savedVal ? parseFloat(savedVal) : 2.5;
  });
  const [strictAllergens, setStrictAllergens] = useState(() => {
    const savedVal = localStorage.getItem('vos_settings_allergens');
    return savedVal ? savedVal === 'true' : true;
  });

  const [backendHealth, setBackendHealth] = useState({
    status: 'checking',
    latency: null,
    version: '1.0.0',
  });

  const checkHealth = async () => {
    const start = performance.now();
    try {
      const res = await api.health.check();
      const latency = Math.round(performance.now() - start);
      setBackendHealth({
        status: res?.status === 'healthy' || res?.status === 'ok' ? 'online' : 'online',
        latency,
        version: '1.0.0',
      });
    } catch (err) {
      setBackendHealth({
        status: 'offline',
        latency: null,
        version: '1.0.0',
      });
    }
  };

  useEffect(() => {
    checkHealth();
  }, []);

  const handleSave = () => {
    localStorage.setItem('vos_settings_threshold', similarityThreshold.toString());
    localStorage.setItem('vos_settings_zscore', emergingZScore.toString());
    localStorage.setItem('vos_settings_allergens', strictAllergens.toString());
    setSaved(true);
    setTimeout(() => setSaved(false), 2500);
  };

  return (
    <div className="app-container">
      <Sidebar />
      <div className="app-main">
        <Header searchPlaceholder="Search system configurations..." />

        <main className="page-content">
          {/* Header */}
          <div className="page-header-row">
            <div className="page-title-group">
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <h1>System Settings & Pipeline Configuration</h1>
                <span
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '5px',
                    fontSize: '11px',
                    fontWeight: 600,
                    padding: '2px 8px',
                    borderRadius: '12px',
                    backgroundColor: backendHealth.status === 'online' ? '#e6f7ef' : '#f1f5f9',
                    color: backendHealth.status === 'online' ? '#047857' : '#64748b',
                    border: `1px solid ${backendHealth.status === 'online' ? '#a7f3d0' : '#e2e8f0'}`,
                  }}
                >
                  <span
                    style={{
                      width: '6px',
                      height: '6px',
                      borderRadius: '50%',
                      backgroundColor: backendHealth.status === 'online' ? '#10b981' : '#94a3b8',
                    }}
                  />
                  {backendHealth.status === 'online' ? `API Online (${backendHealth.latency}ms)` : 'Standalone / Demo'}
                </span>
              </div>
              <p>Configure detection sensitivity, NLP deduplication thresholds, and channel ingestion endpoints.</p>
            </div>

            <div className="quote-banner">
              <Sparkles size={14} className="sparkle-icon" />
              <span>"Continuous calibration for high precision alerts."</span>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: '16px' }}>
            {/* Left Column: Algorithm Settings */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div className="ui-card" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', borderBottom: '1px solid #f1f5f9', paddingBottom: '12px' }}>
                  <Cpu size={18} style={{ color: '#059669' }} />
                  <h3 style={{ fontSize: '15px', fontWeight: 700, color: '#0f172a' }}>
                    Machine Learning & Detection Parameters
                  </h3>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px', fontWeight: 600, color: '#334155' }}>
                      <span>Deduplication Cosine Similarity Threshold</span>
                      <strong style={{ color: '#059669' }}>{similarityThreshold}</strong>
                    </div>
                    <p style={{ fontSize: '12px', color: '#64748b', marginTop: '2px' }}>
                      Feedbacks with text embedding similarity above this value will be grouped into the same parent incident.
                    </p>
                    <input
                      type="range"
                      min="0.60"
                      max="0.95"
                      step="0.01"
                      value={similarityThreshold}
                      onChange={(e) => setSimilarityThreshold(parseFloat(e.target.value))}
                      style={{ width: '100%', marginTop: '6px', accentColor: '#059669' }}
                    />
                  </div>

                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px', fontWeight: 600, color: '#334155' }}>
                      <span>Emerging Issue Anomaly Z-Score Trigger</span>
                      <strong style={{ color: '#059669' }}>{emergingZScore}σ</strong>
                    </div>
                    <p style={{ fontSize: '12px', color: '#64748b', marginTop: '2px' }}>
                      Standard deviations above historical moving average required to flag a store-issue pair as an emerging spike.
                    </p>
                    <input
                      type="range"
                      min="1.5"
                      max="4.0"
                      step="0.1"
                      value={emergingZScore}
                      onChange={(e) => setEmergingZScore(parseFloat(e.target.value))}
                      style={{ width: '100%', marginTop: '6px', accentColor: '#059669' }}
                    />
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', paddingTop: '8px', borderTop: '1px solid #f8fafc' }}>
                    <div>
                      <div style={{ fontSize: '13px', fontWeight: 600, color: '#0f172a' }}>
                        Strict Deterministic Allergen & Safety Override
                      </div>
                      <div style={{ fontSize: '11.5px', color: '#64748b' }}>
                        Always force High severity and Quality owner if safety keywords match, bypassing ML predictions.
                      </div>
                    </div>
                    <input
                      type="checkbox"
                      checked={strictAllergens}
                      onChange={(e) => setStrictAllergens(e.target.checked)}
                      style={{ width: '18px', height: '18px', accentColor: '#059669', cursor: 'pointer' }}
                    />
                  </div>
                </div>

                <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '6px' }}>
                  <button
                    onClick={handleSave}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px',
                      padding: '8px 18px',
                      backgroundColor: '#059669',
                      color: '#ffffff',
                      border: 'none',
                      borderRadius: '8px',
                      fontSize: '12.5px',
                      fontWeight: 600,
                      cursor: 'pointer',
                      boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
                    }}
                  >
                    {saved ? <Check size={14} /> : <Save size={14} />}
                    {saved ? 'Settings Saved & Applied!' : 'Save Calibration'}
                  </button>
                </div>
              </div>

              {/* Service Health Diagnostics */}
              <div className="ui-card" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '14px' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid #f1f5f9', paddingBottom: '12px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <Server size={18} style={{ color: '#059669' }} />
                    <h3 style={{ fontSize: '15px', fontWeight: 700, color: '#0f172a' }}>
                      FastAPI Backend Health
                    </h3>
                  </div>
                  <button
                    onClick={checkHealth}
                    style={{
                      background: 'none',
                      border: 'none',
                      color: '#059669',
                      fontSize: '11.5px',
                      fontWeight: 600,
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '4px',
                    }}
                  >
                    <RefreshCw size={12} />
                    <span>Ping Now</span>
                  </button>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '10px' }}>
                  <div style={{ padding: '10px', backgroundColor: '#f8fafc', borderRadius: '8px' }}>
                    <div style={{ fontSize: '11px', color: '#64748b' }}>Service Status</div>
                    <div style={{ fontSize: '13px', fontWeight: 700, color: backendHealth.status === 'online' ? '#047857' : '#64748b' }}>
                      {backendHealth.status === 'online' ? '● Healthy' : '○ Standalone'}
                    </div>
                  </div>
                  <div style={{ padding: '10px', backgroundColor: '#f8fafc', borderRadius: '8px' }}>
                    <div style={{ fontSize: '11px', color: '#64748b' }}>Endpoint Latency</div>
                    <div style={{ fontSize: '13px', fontWeight: 700, color: '#0f172a' }}>
                      {backendHealth.latency ? `${backendHealth.latency} ms` : 'Local / Cache'}
                    </div>
                  </div>
                  <div style={{ padding: '10px', backgroundColor: '#f8fafc', borderRadius: '8px' }}>
                    <div style={{ fontSize: '11px', color: '#64748b' }}>API Version</div>
                    <div style={{ fontSize: '13px', fontWeight: 700, color: '#0f172a' }}>
                      v{backendHealth.version}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Right Column: Ingestion Channels & Profile */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div className="ui-card" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '14px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', borderBottom: '1px solid #f1f5f9', paddingBottom: '12px' }}>
                  <Radio size={18} style={{ color: '#059669' }} />
                  <h3 style={{ fontSize: '15px', fontWeight: 700, color: '#0f172a' }}>
                    Live Channel Ingestion Feeds
                  </h3>
                </div>

                {[
                  { name: 'Google Business Reviews API', status: 'Active (Synced 4m ago)', ping: '100% health' },
                  { name: 'App Store & Play Store Webhook', status: 'Active (Realtime)', ping: '100% health' },
                  { name: 'Store Frontline Staff Notes App', status: 'Active (Sync on submit)', ping: '99.8% health' },
                  { name: 'Call Centre CRM Ingestion Pipeline', status: 'Active (Batch 15m)', ping: '100% health' },
                ].map((feed) => (
                  <div
                    key={feed.name}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      padding: '8px 12px',
                      backgroundColor: '#f8fafc',
                      borderRadius: '8px',
                      fontSize: '12px',
                    }}
                  >
                    <div>
                      <div style={{ fontWeight: 600, color: '#0f172a' }}>{feed.name}</div>
                      <div style={{ color: '#64748b', fontSize: '11px' }}>{feed.status}</div>
                    </div>
                    <span style={{ color: '#059669', fontWeight: 600, fontSize: '11px' }}>
                      ● {feed.ping}
                    </span>
                  </div>
                ))}
              </div>

              <div className="ui-card" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', borderBottom: '1px solid #f1f5f9', paddingBottom: '12px' }}>
                  <User size={18} style={{ color: '#059669' }} />
                  <h3 style={{ fontSize: '15px', fontWeight: 700, color: '#0f172a' }}>
                    User Profile & Permissions
                  </h3>
                </div>

                <div style={{ fontSize: '12.5px', color: '#334155', display: 'flex', flexDirection: 'column', gap: '6px' }}>
                  <div><strong>Name:</strong> {user?.name || USER_PROFILE.name}</div>
                  <div><strong>Role:</strong> HQ Lead Operations Analyst</div>
                  <div><strong>Access Level:</strong> Nationwide Multi-store Admin</div>
                  <div><strong>Email:</strong> {user?.email || USER_PROFILE.email}</div>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

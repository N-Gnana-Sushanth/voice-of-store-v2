import React, { useState } from 'react';
import {
  Settings,
  ShieldCheck,
  Cpu,
  Radio,
  User,
  Sparkles,
  Save,
  Check,
} from 'lucide-react';
import Sidebar from '../components/Sidebar';
import Header from '../components/Header';

export default function SettingsPage() {
  const [saved, setSaved] = useState(false);
  const [similarityThreshold, setSimilarityThreshold] = useState(0.82);
  const [emergingZScore, setEmergingZScore] = useState(2.5);
  const [strictAllergens, setStrictAllergens] = useState(true);

  const handleSave = () => {
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
              <h1>System Settings & Pipeline Configuration</h1>
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
                      backgroundColor: saved ? '#059669' : '#059669',
                      color: '#ffffff',
                      border: 'none',
                      borderRadius: '8px',
                      fontSize: '12.5px',
                      fontWeight: 600,
                      cursor: 'pointer',
                    }}
                  >
                    {saved ? <Check size={14} /> : <Save size={14} />}
                    {saved ? 'Settings Saved!' : 'Save Calibration'}
                  </button>
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
                  <div><strong>Name:</strong> Tabraiz</div>
                  <div><strong>Role:</strong> HQ Lead Operations Analyst</div>
                  <div><strong>Access Level:</strong> Nationwide Multi-store Admin</div>
                  <div><strong>Email:</strong> tabraiz@voiceofstore.internal</div>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

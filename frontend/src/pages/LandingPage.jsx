import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  Sparkles,
  Zap,
  Users,
  BarChart3,
  ArrowRight,
  Play,
  MessageSquare,
  Brain,
  Target,
  Database,
  CheckSquare,
  Headphones,
} from 'lucide-react';
import BrandLogo from '../components/BrandLogo';

export default function LandingPage() {
  const navigate = useNavigate();

  return (
    <div style={{ backgroundColor: '#ffffff', minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Top Navbar */}
      <header
        style={{
          height: '72px',
          padding: '0 48px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          borderBottom: '1px solid #f1f5f9',
          position: 'sticky',
          top: 0,
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          backdropFilter: 'blur(8px)',
          zIndex: 50,
        }}
      >
        <BrandLogo to="/" size="large" />

        {/* Center Nav Links */}
        <nav style={{ display: 'flex', alignItems: 'center', gap: '32px' }}>
          <a
            href="#home"
            style={{
              fontSize: '14px',
              fontWeight: 600,
              color: '#059669',
              position: 'relative',
              paddingBottom: '6px',
            }}
          >
            Home
            {/* Green active underline */}
            <span
              style={{
                position: 'absolute',
                bottom: 0,
                left: 0,
                right: 0,
                height: '2.5px',
                backgroundColor: '#059669',
                borderRadius: '2px',
              }}
            />
          </a>
          <a href="#how-it-works" style={{ fontSize: '14px', fontWeight: 500, color: '#334155' }}>
            How it Works
          </a>
          <Link to="/dashboard" style={{ fontSize: '14px', fontWeight: 500, color: '#334155' }}>
            Insights
          </Link>
          <Link to="/dashboard" style={{ fontSize: '14px', fontWeight: 500, color: '#334155' }}>
            Regions
          </Link>
          <Link to="/dashboard" style={{ fontSize: '14px', fontWeight: 500, color: '#334155' }}>
            Reports
          </Link>
        </nav>

        {/* Right Get Started Button */}
        <button
          onClick={() => navigate('/dashboard')}
          style={{
            backgroundColor: '#047857',
            color: '#ffffff',
            padding: '10px 22px',
            borderRadius: '9999px',
            fontSize: '13.5px',
            fontWeight: 600,
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
            boxShadow: '0 4px 12px rgba(4, 120, 87, 0.25)',
            transition: 'background-color 0.15s ease',
          }}
        >
          <span>Get Started</span>
          <ArrowRight size={15} />
        </button>
      </header>

      {/* Hero Section */}
      <section
        id="home"
        style={{
          padding: '48px 48px 36px 48px',
          maxWidth: '1400px',
          width: '100%',
          margin: '0 auto',
          position: 'relative',
        }}
      >
        <div style={{ display: 'grid', gridTemplateColumns: '1.05fr 1.15fr', gap: '32px', alignItems: 'center' }}>
          {/* Left Hero Content */}
          <div>
            {/* Pill Badge */}
            <div
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '6px',
                backgroundColor: '#e6f7ef',
                border: '1px solid #bbf7d0',
                borderRadius: '9999px',
                padding: '6px 14px',
                fontSize: '12px',
                fontWeight: 700,
                color: '#059669',
                letterSpacing: '0.04em',
                marginBottom: '20px',
              }}
            >
              <Sparkles size={14} />
              <span>AI-POWERED RETAIL INTELLIGENCE</span>
            </div>

            {/* Main Headline */}
            <h1
              style={{
                fontSize: '52px',
                fontWeight: 800,
                color: '#0f172a',
                lineHeight: 1.12,
                letterSpacing: '-0.03em',
                marginBottom: '20px',
              }}
            >
              Turning Store <br />
              Chatter <span style={{ color: '#059669' }}>Into Action</span>
            </h1>

            {/* Subtitle */}
            <p
              style={{
                fontSize: '16.5px',
                color: '#475569',
                lineHeight: 1.6,
                maxWidth: '480px',
                marginBottom: '24px',
              }}
            >
              Convert customer reviews, app feedback, store-staff notes and support tickets into clear, prioritised
              actions for every store.
            </p>

            {/* Feature Bullets */}
            <div
              style={{
                display: 'flex',
                flexWrap: 'wrap',
                alignItems: 'center',
                gap: '20px',
                fontSize: '13.5px',
                fontWeight: 600,
                color: '#1e293b',
                marginBottom: '32px',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Zap size={16} style={{ color: '#059669' }} />
                <span>Detect issues early</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Users size={16} style={{ color: '#059669' }} />
                <span>Route to right team</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <BarChart3 size={16} style={{ color: '#059669' }} />
                <span>Keep stores better, happier</span>
              </div>
            </div>

            {/* CTA Buttons */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
              <button
                onClick={() => navigate('/dashboard')}
                style={{
                  backgroundColor: '#047857',
                  color: '#ffffff',
                  padding: '13px 26px',
                  borderRadius: '9999px',
                  fontSize: '14.5px',
                  fontWeight: 600,
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '8px',
                  boxShadow: '0 4px 14px rgba(4, 120, 87, 0.3)',
                }}
              >
                <span>Explore Insights</span>
                <ArrowRight size={16} />
              </button>

              <button
                onClick={() => navigate('/dashboard')}
                style={{
                  backgroundColor: '#ffffff',
                  color: '#1e293b',
                  border: '1px solid #e2e8f0',
                  padding: '13px 24px',
                  borderRadius: '9999px',
                  fontSize: '14.5px',
                  fontWeight: 600,
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '8px',
                }}
              >
                <div
                  style={{
                    width: '24px',
                    height: '24px',
                    borderRadius: '50%',
                    backgroundColor: '#e6f7ef',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: '#059669',
                  }}
                >
                  <Play size={12} fill="#059669" />
                </div>
                <span>Watch Demo</span>
              </button>
            </div>
          </div>

          {/* Right Hero Graphic with Floating Cards and Laptop Mockup */}
          <div
            style={{
              position: 'relative',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              minHeight: '440px',
            }}
          >
            {/* Background ambient aisle blur overlay */}
            <div
              style={{
                position: 'absolute',
                top: 0,
                right: '-40px',
                width: '560px',
                height: '420px',
                background: 'radial-gradient(ellipse at center, rgba(167, 243, 208, 0.25) 0%, rgba(255,255,255,0) 70%)',
                zIndex: 0,
                pointerEvents: 'none',
              }}
            />

            {/* Left Floating Cards Stack */}
            <div
              style={{
                position: 'absolute',
                left: '-10px',
                top: '15px',
                display: 'flex',
                flexDirection: 'column',
                gap: '12px',
                zIndex: 20,
                width: '235px',
              }}
            >
              {/* Card 1: Google Review */}
              <div
                style={{
                  backgroundColor: '#ffffff',
                  borderRadius: '12px',
                  padding: '10px 12px',
                  boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
                  border: '1px solid #f1f5f9',
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: '10px',
                }}
              >
                <div
                  style={{
                    width: '28px',
                    height: '28px',
                    borderRadius: '50%',
                    backgroundColor: '#fff',
                    border: '1px solid #e2e8f0',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '14px',
                    fontWeight: 700,
                    color: '#ea4335',
                    flexShrink: 0,
                  }}
                >
                  G
                </div>
                <div>
                  <div style={{ fontSize: '11.5px', fontWeight: 700, color: '#0f172a' }}>
                    Freezer not working again 😡
                  </div>
                  <div style={{ fontSize: '10px', color: '#f59e0b', marginTop: '2px' }}>
                    ★★☆☆☆ <span style={{ color: '#94a3b8' }}>2 hours ago</span>
                  </div>
                </div>
              </div>

              {/* Card 2: App Store Comment */}
              <div
                style={{
                  backgroundColor: '#ffffff',
                  borderRadius: '12px',
                  padding: '10px 12px',
                  boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
                  border: '1px solid #f1f5f9',
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: '10px',
                }}
              >
                <div
                  style={{
                    width: '28px',
                    height: '28px',
                    borderRadius: '7px',
                    backgroundColor: '#0284c7',
                    color: '#ffffff',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '14px',
                    fontWeight: 800,
                    flexShrink: 0,
                  }}
                >
                  A
                </div>
                <div>
                  <div style={{ fontSize: '11.5px', fontWeight: 700, color: '#0f172a' }}>
                    Milk section me bahut smell hai :(
                  </div>
                  <div style={{ fontSize: '10px', color: '#f59e0b', marginTop: '2px' }}>
                    ★☆☆☆☆ <span style={{ color: '#94a3b8' }}>1 day ago</span>
                  </div>
                </div>
              </div>

              {/* Card 3: WhatsApp / Staff Note */}
              <div
                style={{
                  backgroundColor: '#ffffff',
                  borderRadius: '12px',
                  padding: '10px 12px',
                  boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
                  border: '1px solid #f1f5f9',
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: '10px',
                }}
              >
                <div
                  style={{
                    width: '28px',
                    height: '28px',
                    borderRadius: '50%',
                    backgroundColor: '#22c55e',
                    color: '#ffffff',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '13px',
                    flexShrink: 0,
                  }}
                >
                  💬
                </div>
                <div>
                  <div style={{ fontSize: '11.5px', fontWeight: 700, color: '#0f172a' }}>
                    Stock khatam ho gaya aaj bhi...
                  </div>
                  <div style={{ fontSize: '10px', color: '#94a3b8', marginTop: '2px' }}>
                    🕒 3 hours ago
                  </div>
                </div>
              </div>

              {/* Card 4: Support Ticket */}
              <div
                style={{
                  backgroundColor: '#ffffff',
                  borderRadius: '12px',
                  padding: '10px 12px',
                  boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
                  border: '1px solid #f1f5f9',
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: '10px',
                }}
              >
                <div
                  style={{
                    width: '28px',
                    height: '28px',
                    borderRadius: '50%',
                    backgroundColor: '#eff6ff',
                    color: '#3b82f6',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    flexShrink: 0,
                  }}
                >
                  <Headphones size={15} />
                </div>
                <div>
                  <div style={{ fontSize: '11.5px', fontWeight: 700, color: '#0f172a' }}>
                    Customer complained about rude staff.
                  </div>
                  <div style={{ fontSize: '10px', color: '#94a3b8', marginTop: '2px' }}>
                    5 hours ago
                  </div>
                </div>
              </div>
            </div>

            {/* Multi-colored dotted connector paths */}
            <svg
              style={{
                position: 'absolute',
                left: '190px',
                top: '50px',
                width: '120px',
                height: '260px',
                zIndex: 15,
                pointerEvents: 'none',
              }}
            >
              <path d="M10,20 Q60,60 95,95" stroke="#10b981" strokeWidth="2" strokeDasharray="3,3" fill="none" />
              <path d="M10,80 Q55,95 95,100" stroke="#ef4444" strokeWidth="2" strokeDasharray="3,3" fill="none" />
              <path d="M10,140 Q55,115 95,105" stroke="#3b82f6" strokeWidth="2" strokeDasharray="3,3" fill="none" />
              <path d="M10,200 Q60,135 95,110" stroke="#f59e0b" strokeWidth="2" strokeDasharray="3,3" fill="none" />
            </svg>

            {/* 3D Angled Laptop Frame */}
            <div
              style={{
                position: 'relative',
                width: '460px',
                zIndex: 10,
                transform: 'perspective(1000px) rotateY(-8deg) rotateX(4deg)',
                transformStyle: 'preserve-3d',
                boxShadow: '0 25px 50px -12px rgba(15, 23, 42, 0.25)',
                borderRadius: '16px',
                overflow: 'hidden',
                border: '10px solid #1e293b',
                backgroundColor: '#ffffff',
              }}
            >
              {/* Laptop Screen Header */}
              <div
                style={{
                  height: '24px',
                  backgroundColor: '#f8fafc',
                  borderBottom: '1px solid #e2e8f0',
                  display: 'flex',
                  alignItems: 'center',
                  padding: '0 10px',
                  gap: '6px',
                }}
              >
                <div style={{ width: '7px', height: '7px', borderRadius: '50%', backgroundColor: '#ef4444' }} />
                <div style={{ width: '7px', height: '7px', borderRadius: '50%', backgroundColor: '#f59e0b' }} />
                <div style={{ width: '7px', height: '7px', borderRadius: '50%', backgroundColor: '#10b981' }} />
                <span style={{ fontSize: '9px', fontWeight: 700, color: '#059669', marginLeft: '6px' }}>
                  Voice-of-Store
                </span>
              </div>

              {/* Laptop Screen Body Preview */}
              <div style={{ padding: '12px', backgroundColor: '#f1f7f4' }}>
                <div style={{ fontSize: '11px', fontWeight: 800, color: '#0f172a', marginBottom: '8px' }}>
                  Key Insights This Week
                </div>
                {/* Mini Metric Cards */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '6px', marginBottom: '10px' }}>
                  <div style={{ backgroundColor: '#fff', padding: '6px', borderRadius: '6px', textAlign: 'center' }}>
                    <div style={{ fontSize: '11px', fontWeight: 800 }}>40,000</div>
                    <div style={{ fontSize: '8px', color: '#64748b' }}>Total Feedback</div>
                  </div>
                  <div style={{ backgroundColor: '#fff', padding: '6px', borderRadius: '6px', textAlign: 'center' }}>
                    <div style={{ fontSize: '11px', fontWeight: 800, color: '#ef4444' }}>326</div>
                    <div style={{ fontSize: '8px', color: '#64748b' }}>High Severity</div>
                  </div>
                  <div style={{ backgroundColor: '#fff', padding: '6px', borderRadius: '6px', textAlign: 'center' }}>
                    <div style={{ fontSize: '11px', fontWeight: 800, color: '#10b981' }}>1,124</div>
                    <div style={{ fontSize: '8px', color: '#64748b' }}>Actionable</div>
                  </div>
                  <div style={{ backgroundColor: '#fff', padding: '6px', borderRadius: '6px', textAlign: 'center' }}>
                    <div style={{ fontSize: '11px', fontWeight: 800, color: '#8b5cf6' }}>436</div>
                    <div style={{ fontSize: '8px', color: '#64748b' }}>Stores</div>
                  </div>
                </div>

                {/* Mini Top Issues Table */}
                <div style={{ backgroundColor: '#fff', borderRadius: '8px', padding: '8px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '9px', fontWeight: 700, marginBottom: '6px' }}>
                    <span>Top Issues</span>
                    <span style={{ color: '#2563eb' }}>View All →</span>
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', fontSize: '8.5px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span>❄️ Broken / Faulty Freezer</span>
                      <span style={{ color: '#ef4444' }}>↗</span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span>🍴 Missing Allergen Label</span>
                      <span style={{ color: '#ef4444' }}>↗</span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span>👥 Rude Staff Behaviour</span>
                      <span style={{ color: '#ef4444' }}>↗</span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span>📦 Stock Out - Popular Items</span>
                      <span style={{ color: '#10b981' }}>↘</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* 4 Horizontal Feature Cards Container */}
        <div
          style={{
            marginTop: '56px',
            backgroundColor: '#edf7f2',
            borderRadius: '24px',
            padding: '24px',
            border: '1px solid #d1fae5',
          }}
        >
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px' }}>
            {/* Card 1 */}
            <div
              style={{
                backgroundColor: '#ffffff',
                borderRadius: '16px',
                padding: '20px 16px',
                display: 'flex',
                alignItems: 'center',
                gap: '14px',
                boxShadow: '0 1px 3px rgba(0,0,0,0.04)',
              }}
            >
              <div
                style={{
                  width: '44px',
                  height: '44px',
                  borderRadius: '50%',
                  backgroundColor: '#fee2e2',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#ef4444',
                  flexShrink: 0,
                }}
              >
                <MessageSquare size={20} />
              </div>
              <div>
                <div style={{ fontSize: '14px', fontWeight: 800, color: '#0f172a' }}>
                  Multiple Sources
                </div>
                <div style={{ fontSize: '12px', color: '#64748b', marginTop: '2px' }}>
                  Reviews, app comments, staff notes, support tickets
                </div>
              </div>
            </div>

            {/* Card 2 */}
            <div
              style={{
                backgroundColor: '#ffffff',
                borderRadius: '16px',
                padding: '20px 16px',
                display: 'flex',
                alignItems: 'center',
                gap: '14px',
                boxShadow: '0 1px 3px rgba(0,0,0,0.04)',
              }}
            >
              <div
                style={{
                  width: '44px',
                  height: '44px',
                  borderRadius: '50%',
                  backgroundColor: '#f3e8ff',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#8b5cf6',
                  flexShrink: 0,
                }}
              >
                <Brain size={20} />
              </div>
              <div>
                <div style={{ fontSize: '14px', fontWeight: 800, color: '#0f172a' }}>
                  AI Understands
                </div>
                <div style={{ fontSize: '12px', color: '#64748b', marginTop: '2px' }}>
                  Code-mixed, multilingual and noisy text
                </div>
              </div>
            </div>

            {/* Card 3 */}
            <div
              style={{
                backgroundColor: '#ffffff',
                borderRadius: '16px',
                padding: '20px 16px',
                display: 'flex',
                alignItems: 'center',
                gap: '14px',
                boxShadow: '0 1px 3px rgba(0,0,0,0.04)',
              }}
            >
              <div
                style={{
                  width: '44px',
                  height: '44px',
                  borderRadius: '50%',
                  backgroundColor: '#e6f7ef',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#10b981',
                  flexShrink: 0,
                }}
              >
                <Target size={20} />
              </div>
              <div>
                <div style={{ fontSize: '14px', fontWeight: 800, color: '#0f172a' }}>
                  Finds Real Issues
                </div>
                <div style={{ fontSize: '12px', color: '#64748b', marginTop: '2px' }}>
                  Prioritises what needs action the most
                </div>
              </div>
            </div>

            {/* Card 4 */}
            <div
              style={{
                backgroundColor: '#ffffff',
                borderRadius: '16px',
                padding: '20px 16px',
                display: 'flex',
                alignItems: 'center',
                gap: '14px',
                boxShadow: '0 1px 3px rgba(0,0,0,0.04)',
              }}
            >
              <div
                style={{
                  width: '44px',
                  height: '44px',
                  borderRadius: '50%',
                  backgroundColor: '#eff6ff',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#3b82f6',
                  flexShrink: 0,
                }}
              >
                <Users size={20} />
              </div>
              <div>
                <div style={{ fontSize: '14px', fontWeight: 800, color: '#0f172a' }}>
                  Routes to Owners
                </div>
                <div style={{ fontSize: '12px', color: '#64748b', marginTop: '2px' }}>
                  Sends to the right team with clear escalation rules
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* "How It Works" Section */}
      <section
        id="how-it-works"
        style={{
          padding: '48px 48px 72px 48px',
          maxWidth: '1400px',
          width: '100%',
          margin: '0 auto',
          textAlign: 'center',
        }}
      >
        <h2
          style={{
            fontSize: '32px',
            fontWeight: 800,
            color: '#0f172a',
            letterSpacing: '-0.02em',
            marginBottom: '6px',
          }}
        >
          How It Works
        </h2>
        <p style={{ fontSize: '15px', color: '#64748b', marginBottom: '40px' }}>
          From messy feedback to clear actions in a few simple steps
        </p>

        {/* 4 Process Step Cards */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '16px', flexWrap: 'wrap' }}>
          {/* Step 1 */}
          <div
            style={{
              backgroundColor: '#ffffff',
              border: '1px solid #e2e8f0',
              borderRadius: '16px',
              padding: '20px 18px',
              width: '240px',
              textAlign: 'left',
              display: 'flex',
              alignItems: 'center',
              gap: '14px',
              boxShadow: '0 2px 6px rgba(0,0,0,0.03)',
            }}
          >
            <div
              style={{
                width: '44px',
                height: '44px',
                borderRadius: '50%',
                backgroundColor: '#eff6ff',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#3b82f6',
                flexShrink: 0,
              }}
            >
              <Database size={20} />
            </div>
            <div>
              <div style={{ fontSize: '13.5px', fontWeight: 800, color: '#0f172a' }}>
                1. Collect
              </div>
              <div style={{ fontSize: '11.5px', color: '#64748b', marginTop: '2px', lineHeight: 1.35 }}>
                Ingest feedback from 4 different channels
              </div>
            </div>
          </div>

          <span style={{ color: '#94a3b8', fontSize: '20px' }}>→</span>

          {/* Step 2 */}
          <div
            style={{
              backgroundColor: '#ffffff',
              border: '1px solid #e2e8f0',
              borderRadius: '16px',
              padding: '20px 18px',
              width: '240px',
              textAlign: 'left',
              display: 'flex',
              alignItems: 'center',
              gap: '14px',
              boxShadow: '0 2px 6px rgba(0,0,0,0.03)',
            }}
          >
            <div
              style={{
                width: '44px',
                height: '44px',
                borderRadius: '50%',
                backgroundColor: '#f3e8ff',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#8b5cf6',
                flexShrink: 0,
              }}
            >
              <Brain size={20} />
            </div>
            <div>
              <div style={{ fontSize: '13.5px', fontWeight: 800, color: '#0f172a' }}>
                2. Understand
              </div>
              <div style={{ fontSize: '11.5px', color: '#64748b', marginTop: '2px', lineHeight: 1.35 }}>
                Clean, translate and classify issues using AI
              </div>
            </div>
          </div>

          <span style={{ color: '#94a3b8', fontSize: '20px' }}>→</span>

          {/* Step 3 */}
          <div
            style={{
              backgroundColor: '#ffffff',
              border: '1px solid #e2e8f0',
              borderRadius: '16px',
              padding: '20px 18px',
              width: '240px',
              textAlign: 'left',
              display: 'flex',
              alignItems: 'center',
              gap: '14px',
              boxShadow: '0 2px 6px rgba(0,0,0,0.03)',
            }}
          >
            <div
              style={{
                width: '44px',
                height: '44px',
                borderRadius: '50%',
                backgroundColor: '#e6f7ef',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#10b981',
                flexShrink: 0,
              }}
            >
              <CheckSquare size={20} />
            </div>
            <div>
              <div style={{ fontSize: '13.5px', fontWeight: 800, color: '#0f172a' }}>
                3. Prioritise
              </div>
              <div style={{ fontSize: '11.5px', color: '#64748b', marginTop: '2px', lineHeight: 1.35 }}>
                Detect emerging issues and assess severity
              </div>
            </div>
          </div>

          <span style={{ color: '#94a3b8', fontSize: '20px' }}>→</span>

          {/* Step 4 */}
          <div
            style={{
              backgroundColor: '#ffffff',
              border: '1px solid #e2e8f0',
              borderRadius: '16px',
              padding: '20px 18px',
              width: '240px',
              textAlign: 'left',
              display: 'flex',
              alignItems: 'center',
              gap: '14px',
              boxShadow: '0 2px 6px rgba(0,0,0,0.03)',
            }}
          >
            <div
              style={{
                width: '44px',
                height: '44px',
                borderRadius: '50%',
                backgroundColor: '#ffedd5',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#f97316',
                flexShrink: 0,
              }}
            >
              <Users size={20} />
            </div>
            <div>
              <div style={{ fontSize: '13.5px', fontWeight: 800, color: '#0f172a' }}>
                4. Take Action
              </div>
              <div style={{ fontSize: '11.5px', color: '#64748b', marginTop: '2px', lineHeight: 1.35 }}>
                Generate a weekly brief and route to the right owner
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

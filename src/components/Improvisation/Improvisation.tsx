import React from 'react';
import { usePredictorStore } from '../../store/usePredictorStore';
import { Cpu, TrendingUp, CheckCircle, Sparkles } from 'lucide-react';

export const Improvisation: React.FC = () => {
  const { improvisationData } = usePredictorStore();

  if (!improvisationData) {
    return (
      <section className="tab-view active">
        <div className="glass-card">
          <p style={{ color: 'var(--text-muted)' }}>Loading AI Self-Improvisation analytics...</p>
        </div>
      </section>
    );
  }

  return (
    <section className="tab-view active">
      <div className="glass-card">
        <div className="card-header">
          <div className="card-title-group">
            <h2 className="card-title">🤖 AI Self-Improvisation & Precision Analytics</h2>
            <p className="card-subtitle">Continuous autonomous feedback loop optimizing prediction precision over time</p>
          </div>
          <span className="badge-pill pill-green">
            <Cpu size={14} style={{ display: 'inline', marginRight: 4 }} />
            Autonomous Optimization Engine
          </span>
        </div>

        {/* Stats Badges */}
        <div className="improvisation-stat-row">
          <div className="stat-badge large cyan">
            <TrendingUp size={28} className="stat-icon cyan" />
            <div>
              <div className="val" style={{ color: 'var(--primary-cyan)', fontSize: '2rem' }}>
                +{improvisationData.precision_gain_pct}%
              </div>
              <div className="lbl">Precision Gain</div>
            </div>
          </div>

          <div className="stat-badge large gold">
            <Sparkles size={28} className="stat-icon gold" />
            <div>
              <div className="val" style={{ color: 'var(--accent-gold)', fontSize: '2rem' }}>
                {improvisationData.improvisation_score_pct}%
              </div>
              <div className="lbl">Improvisation Score</div>
            </div>
          </div>
        </div>

        {/* Upgrades List */}
        <h4 style={{ color: '#fff', marginTop: 28, marginBottom: 16, fontSize: '1.1rem' }}>
          Implemented AI System Upgrades:
        </h4>

        <div className="improvisation-grid">
          {improvisationData.recommendations.map((rec, idx) => (
            <div key={idx} className="improvisation-card">
              <div className="card-top">
                <strong className="rec-title">
                  <CheckCircle size={16} style={{ color: 'var(--accent-green)', display: 'inline', marginRight: 6 }} />
                  {rec.title}
                </strong>
                <span className="badge-pill pill-green">{rec.impact}</span>
              </div>
              <p className="rec-details">{rec.details}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

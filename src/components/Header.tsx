import React from 'react';
import { Activity, Shield, Users, Trophy } from 'lucide-react';

export const Header: React.FC = () => {
  return (
    <header className="hero-header">
      <div className="brand-title">
        <h1>⚽ PREMIER LEAGUE 2026–27 AI PREDICTOR HUB</h1>
        <p>10,000 Monte Carlo Season Simulations • Multi-Model Machine Learning Stacking Engine</p>
      </div>

      <div className="hero-stats">
        <div className="stat-badge">
          <Activity size={18} className="stat-icon cyan" />
          <div>
            <div className="val">10,000</div>
            <div className="lbl">Simulations</div>
          </div>
        </div>

        <div className="stat-badge">
          <Shield size={18} className="stat-icon purple" />
          <div>
            <div className="val">10,804</div>
            <div className="lbl">Matches Ingested</div>
          </div>
        </div>

        <div className="stat-badge">
          <Users size={18} className="stat-icon green" />
          <div>
            <div className="val">609</div>
            <div className="lbl">Players Tracked</div>
          </div>
        </div>

        <div className="stat-badge">
          <Trophy size={18} className="stat-icon gold" />
          <div>
            <div className="val" style={{ color: 'var(--accent-gold)' }}>380</div>
            <div className="lbl">2-Leg Fixtures</div>
          </div>
        </div>
      </div>
    </header>
  );
};

import React from 'react';
import { usePredictorStore } from '../../store/usePredictorStore';
import { Sparkles, DollarSign, Briefcase } from 'lucide-react';

export const Transfers: React.FC = () => {
  const { uiData } = usePredictorStore();

  if (!uiData) return null;

  return (
    <section className="tab-view active">
      {/* Darkhorse Prospects */}
      <div className="glass-card">
        <div className="card-header">
          <div className="card-title-group">
            <h2 className="card-title">🔍 Emerging Young Darkhorses & Breakout Prospects</h2>
            <p className="card-subtitle">Scouting algorithm identifying undervalued high-ceiling talent under £10M</p>
          </div>
          <span className="badge-pill pill-green">
            <Sparkles size={14} style={{ display: 'inline', marginRight: 4 }} />
            High Potential Index
          </span>
        </div>

        <div className="data-table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>Rank</th>
                <th>Player</th>
                <th>Club</th>
                <th>Position</th>
                <th>Price (£M)</th>
                <th>Darkhorse Potential Score</th>
              </tr>
            </thead>
            <tbody>
              {uiData.darkhorses.map((p, idx) => (
                <tr key={`${p.web_name}-${idx}`}>
                  <td><span className="badge-pill pill-cyan">#{idx + 1}</span></td>
                  <td><strong>{p.web_name}</strong></td>
                  <td>{p.team_name}</td>
                  <td>{p.position}</td>
                  <td>£{p.price_m}M</td>
                  <td><span className="badge-pill pill-green">{p.darkhorse_potential_score}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Transfer Market Valuations */}
      <div className="glass-card" style={{ marginTop: 28 }}>
        <div className="card-header">
          <div className="card-title-group">
            <h2 className="card-title">💶 Transfer Market Valuations & Weekly Wage Demands</h2>
            <p className="card-subtitle">Predictive econometric regression based on age, performance, and club revenue</p>
          </div>
          <span className="badge-pill pill-purple">
            <DollarSign size={14} style={{ display: 'inline', marginRight: 4 }} />
            Valuation Model
          </span>
        </div>

        <div className="data-table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>Rank</th>
                <th>Player</th>
                <th>Club</th>
                <th>Position</th>
                <th>Predicted Market Value (€M)</th>
                <th>Predicted Weekly Wage (£k/wk)</th>
              </tr>
            </thead>
            <tbody>
              {uiData.transfers.map((p, idx) => (
                <tr key={`${p.web_name}-${idx}`}>
                  <td><span className="badge-pill pill-purple">#{idx + 1}</span></td>
                  <td><strong>{p.web_name}</strong></td>
                  <td>{p.team_name}</td>
                  <td>{p.position}</td>
                  <td><strong style={{ color: 'var(--accent-gold)' }}>€{p.predicted_market_value_eur_m}M</strong></td>
                  <td><span className="badge-pill pill-cyan">£{p.predicted_weekly_salary_k}k/wk</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Club Owner Strategic Behavioral Profiles */}
      <div className="glass-card" style={{ marginTop: 28 }}>
        <div className="card-header">
          <div className="card-title-group">
            <h2 className="card-title">💼 Club Owner Strategic Behavioral Profiles</h2>
            <p className="card-subtitle">Ownership spend patterns, risk tolerance, and window strategy analysis</p>
          </div>
          <span className="badge-pill pill-cyan">
            <Briefcase size={14} style={{ display: 'inline', marginRight: 4 }} />
            Strategic Profiling
          </span>
        </div>

        <div className="owners-grid">
          {uiData.owners.map((row) => (
            <div key={row.team_name} className="owner-card">
              <div className="team-name">{row.team_name}</div>
              <div className="owner-grp">
                Owner: <strong>{row.owner_group}</strong>
              </div>
              <div className="archetype">
                Archetype: <span className="badge-pill pill-purple" style={{ fontSize: '0.75rem', padding: '2px 8px' }}>{row.investment_archetype}</span>
              </div>
              <div className="budget-line">
                Avg Window Budget: <strong>{row.avg_window_budget_m}</strong>
              </div>
              <div className="action-text">{row.predictive_action_summary}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

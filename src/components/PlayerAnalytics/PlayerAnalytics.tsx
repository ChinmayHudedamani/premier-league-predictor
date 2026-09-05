import React from 'react';
import { usePredictorStore } from '../../store/usePredictorStore';
import { Star, Award } from 'lucide-react';

export const PlayerAnalytics: React.FC = () => {
  const { uiData } = usePredictorStore();

  if (!uiData) return null;

  return (
    <section className="tab-view active">
      {/* POTS Section */}
      <div className="glass-card">
        <div className="card-header">
          <div className="card-title-group">
            <h2 className="card-title">🌟 Player of the Season (POTS) Candidates</h2>
            <p className="card-subtitle">Ranked by combined Machine Learning POTS Index (xG, xA, OVR, Team Success)</p>
          </div>
          <span className="badge-pill pill-purple">Underlying xG & xA Model</span>
        </div>

        <div className="data-table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>Rank</th>
                <th>Player</th>
                <th>Club</th>
                <th>Position</th>
                <th>EA FC27 OVR</th>
                <th>POTS Index</th>
                <th>Expected Goals (xG)</th>
                <th>Expected Assists (xA)</th>
                <th>Form</th>
              </tr>
            </thead>
            <tbody>
              {uiData.pots.map((p, idx) => (
                <tr key={`${p.web_name}-${idx}`}>
                  <td>
                    <span className={`badge-pill ${idx === 0 ? 'pill-gold' : 'pill-purple'}`}>
                      {idx === 0 && <Star size={12} style={{ display: 'inline', marginRight: 3 }} />}
                      #{idx + 1}
                    </span>
                  </td>
                  <td><strong>{p.web_name}</strong></td>
                  <td>{p.team_name}</td>
                  <td>{p.position}</td>
                  <td><span className="badge-pill pill-gold">{p.fifa_ovr} OVR</span></td>
                  <td><strong style={{ color: 'var(--primary-cyan)' }}>{p.pots_score.toFixed(3)}</strong></td>
                  <td>{p.expected_goals}</td>
                  <td>{p.expected_assists}</td>
                  <td><span className="badge-pill pill-cyan">{p.form}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Golden Boot Section */}
      <div className="glass-card" style={{ marginTop: 28 }}>
        <div className="card-header">
          <div className="card-title-group">
            <h2 className="card-title">🥇 Golden Boot (Top Goalscorer) Leaderboard</h2>
            <p className="card-subtitle">Expected goal volume and historical finishing efficiency predictions</p>
          </div>
          <span className="badge-pill pill-gold">Goal Projections</span>
        </div>

        <div className="data-table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>Rank</th>
                <th>Player</th>
                <th>Club</th>
                <th>Position</th>
                <th>Goals Scored</th>
                <th>Expected Goals (xG)</th>
                <th>Golden Boot Score</th>
              </tr>
            </thead>
            <tbody>
              {uiData.golden_boot.map((p, idx) => (
                <tr key={`${p.web_name}-${idx}`}>
                  <td>
                    <span className={`badge-pill ${idx === 0 ? 'pill-gold' : 'pill-cyan'}`}>
                      {idx === 0 && <Award size={12} style={{ display: 'inline', marginRight: 3 }} />}
                      #{idx + 1}
                    </span>
                  </td>
                  <td><strong>{p.web_name}</strong></td>
                  <td>{p.team_name}</td>
                  <td>{p.position}</td>
                  <td><strong style={{ color: 'var(--accent-gold)' }}>{p.goals_scored} goals</strong></td>
                  <td>{p.expected_goals} xG</td>
                  <td><span className="badge-pill pill-gold">{p.golden_boot_score.toFixed(3)}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
};

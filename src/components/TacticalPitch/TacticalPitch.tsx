import React from 'react';
import { usePredictorStore } from '../../store/usePredictorStore';
import { Star, Shield, Users } from 'lucide-react';

export const TacticalPitch: React.FC = () => {
  const { uiData, selectedSquadTeam, setSquadTeam } = usePredictorStore();

  if (!uiData) return null;

  const currentTeam = selectedSquadTeam || uiData.teams[0];
  const squadData = uiData.team_squads ? uiData.team_squads[currentTeam] : null;
  const bestPlayer = squadData?.best_player;
  const formation11 = squadData?.tactical_formation_11 || [];
  const squadList = squadData?.squad || [];

  return (
    <section className="tab-view active">
      <div className="glass-card">
        {/* Header & Team Selection */}
        <div className="card-header">
          <div className="card-title-group">
            <h2 className="card-title">🛡️ Premier League Squad & EA FC27 Tactical Lineup</h2>
            <p className="card-subtitle">Explore tactical 4-3-3 positions, player ratings, and complete roster profiles</p>
          </div>
          <div style={{ minWidth: 260 }}>
            <select
              className="team-select"
              value={currentTeam}
              onChange={(e) => setSquadTeam(e.target.value)}
            >
              {uiData.teams.map((t) => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Best Player MVP Banner */}
        {bestPlayer ? (
          <div className="best-player-card">
            <div className="key-badge">{bestPlayer.fifa_ovr}</div>
            <div className="best-player-details">
              <span className="badge-pill pill-gold">
                <Star size={14} style={{ display: 'inline', marginRight: 4 }} />
                KEY MAN / TEAM MVP
              </span>
              <h3>{bestPlayer.web_name}</h3>
              <p>
                {currentTeam} • {bestPlayer.position} • Form: <strong>{bestPlayer.form}</strong> • Expected Goals: <strong>{bestPlayer.expected_goals} xG</strong> • Price: <strong>£{bestPlayer.price_m}M</strong>
              </p>
            </div>
          </div>
        ) : (
          <div className="best-player-card">
            <div className="key-badge">--</div>
            <div className="best-player-details">
              <span className="badge-pill pill-gold">KEY MAN</span>
              <h3>Select a Club</h3>
              <p>Select a club from the dropdown to view squad roster & tactical formation.</p>
            </div>
          </div>
        )}

        {/* EA SPORTS FC 27 Tactical Football Pitch */}
        <div className="pitch-section-header">
          <h3 className="section-subtitle cyan">
            🎮 EA SPORTS FC 27 Tactical Lineup Pitch View (4-3-3 Formation)
          </h3>
          <span className="badge-pill pill-purple">Interactive Pitch</span>
        </div>

        <div className="tactical-pitch-container">
          <div className="pitch-center-line" />
          <div className="pitch-center-circle" />
          <div className="pitch-penalty-box-top" />
          <div className="pitch-penalty-box-bottom" />

          {formation11.map((p, idx) => (
            <div
              key={`${p.web_name}-${idx}`}
              className="fut-pitch-card"
              style={{ left: `${p.x}%`, top: `${p.y}%` }}
            >
              <div className="fut-card-frame">
                <div className="fut-ovr-badge">{p.fifa_ovr}</div>
                <div className="fut-role-badge">{p.role}</div>
              </div>
              <div className="fut-player-name-tag">{p.web_name}</div>
            </div>
          ))}
        </div>

        {/* Squad Roster Table */}
        <h3 className="section-subtitle" style={{ marginTop: 36, color: '#fff' }}>
          📋 Complete Team Squad Roster & EA FC Ratings ({squadList.length} Players)
        </h3>

        <div className="data-table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>No.</th>
                <th>Player</th>
                <th>Position</th>
                <th>EA FC27 OVR</th>
                <th>Price (£M)</th>
                <th>Expected Goals (xG)</th>
                <th>Expected Assists (xA)</th>
                <th>Current Form</th>
              </tr>
            </thead>
            <tbody>
              {squadList.map((p, idx) => (
                <tr key={`${p.web_name}-${idx}`}>
                  <td><span className="badge-pill pill-purple">#{idx + 1}</span></td>
                  <td><strong>{p.web_name}</strong></td>
                  <td>{p.position}</td>
                  <td><span className="badge-pill pill-gold">{p.fifa_ovr} OVR</span></td>
                  <td>£{p.price_m}M</td>
                  <td>{p.expected_goals}</td>
                  <td>{p.expected_assists}</td>
                  <td><span className="badge-pill pill-cyan">{p.form}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
};

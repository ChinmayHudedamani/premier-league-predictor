import React from 'react';
import { usePredictorStore } from '../../store/usePredictorStore';
import { Zap, AlertTriangle, Shield, Trophy } from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Cell,
} from 'recharts';

export const MatchPredictor: React.FC = () => {
  const {
    uiData,
    selectedHomeTeam,
    selectedAwayTeam,
    prediction,
    setHomeTeam,
    setAwayTeam,
    calculateMatchPrediction,
  } = usePredictorStore();

  if (!uiData) return null;

  const isSameTeam = Boolean(selectedHomeTeam && selectedAwayTeam && selectedHomeTeam === selectedAwayTeam);

  const l1 = prediction?.leg1_home;
  const l2 = prediction?.leg2_away;
  const agg = prediction?.aggregate_2leg;

  // Recharts data for win probabilities
  const probChartData = l1
    ? [
        { name: `${selectedHomeTeam} Win`, prob: parseFloat(l1.home_win_pct), color: '#00f2fe' },
        { name: 'Draw', prob: parseFloat(l1.draw_pct), color: '#94a3b8' },
        { name: `${selectedAwayTeam} Win`, prob: parseFloat(l1.away_win_pct), color: '#ffd700' },
      ]
    : [];

  // xG Comparison data for Recharts
  const xgChartData = l1
    ? [
        { team: selectedHomeTeam, xG: parseFloat(l1.home_xg), fill: '#00f2fe' },
        { team: selectedAwayTeam, xG: parseFloat(l1.away_xg), fill: '#ffd700' },
      ]
    : [];

  return (
    <section className="tab-view active">
      <div className="glass-card">
        <div className="card-header">
          <div className="card-title-group">
            <h2 className="card-title">🎮 Manual 2-Leg Head-to-Head Match Predictor</h2>
            <p className="card-subtitle">Simulate Poisson goal distributions, reverse home legs, and aggregate outcomes</p>
          </div>
          <span className="badge-pill pill-cyan">Poisson & Multi-Model Stacking AI</span>
        </div>

        {/* Team Selector Grid */}
        <div className="predictor-grid">
          {/* Home Team */}
          <div className="team-selector-card">
            <label htmlFor="homeTeamSelect">Select Home Team (Leg 1)</label>
            <select
              id="homeTeamSelect"
              className="team-select"
              value={selectedHomeTeam}
              onChange={(e) => setHomeTeam(e.target.value)}
            >
              <option value="" disabled>-- Select Home Team --</option>
              {uiData.teams.map((t) => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>
            <div className="team-badge-large home">
              <Shield size={24} className="badge-icon" />
              <span>{selectedHomeTeam || 'Home Team'}</span>
            </div>
          </div>

          {/* VS Badge */}
          <div className="vs-badge">VS</div>

          {/* Away Team */}
          <div className="team-selector-card">
            <label htmlFor="awayTeamSelect">Select Away Team (Leg 1)</label>
            <select
              id="awayTeamSelect"
              className="team-select"
              value={selectedAwayTeam}
              onChange={(e) => setAwayTeam(e.target.value)}
            >
              <option value="" disabled>-- Select Away Team --</option>
              {uiData.teams.map((t) => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>
            <div className="team-badge-large away">
              <Shield size={24} className="badge-icon" />
              <span>{selectedAwayTeam || 'Away Team'}</span>
            </div>
          </div>
        </div>

        {/* Action Button */}
        <button
          className="predict-action-btn"
          onClick={() => calculateMatchPrediction()}
          disabled={!selectedHomeTeam || !selectedAwayTeam || isSameTeam}
        >
          <Zap size={18} />
          <span>Calculate Match Prediction</span>
        </button>

        {isSameTeam && (
          <div className="alert-box error">
            <AlertTriangle size={20} />
            <span>⚠️ Home Team and Away Team must be different Premier League clubs!</span>
          </div>
        )}

        {prediction && !isSameTeam && l1 && (
          <>
            {/* Leg 1 Header */}
            <h3 className="section-subtitle cyan">
              🏟️ LEG 1 MATCH PREDICTION ({selectedHomeTeam.toUpperCase()} HOME VENUE)
            </h3>

            {/* Results Grid */}
            <div className="match-results-display">
              {/* Metric 1: Outcome Probabilities with Recharts */}
              <div className="metric-box">
                <div className="box-title">Match Outcome Probabilities</div>
                <div style={{ height: 130, width: '100%', marginTop: 8 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={probChartData}
                      layout="vertical"
                      margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                    >
                      <XAxis type="number" domain={[0, 100]} unit="%" stroke="#64748b" tick={{ fontSize: 11 }} />
                      <YAxis dataKey="name" type="category" stroke="#cbd5e1" tick={{ fontSize: 12 }} width={90} />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: 'rgba(18, 24, 38, 0.95)',
                          borderColor: 'rgba(255, 255, 255, 0.2)',
                          borderRadius: 8,
                          color: '#fff',
                        }}
                        formatter={(val: number) => [`${val}%`, 'Probability']}
                      />
                      <Bar dataKey="prob" radius={[0, 6, 6, 0]}>
                        {probChartData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Metric 2: Expected Goals with Recharts */}
              <div className="metric-box">
                <div className="box-title">Expected Goals (xG) Comparison</div>
                <div className="comparison-stat">
                  <span className="num home-num">{l1.home_xg}</span>
                  <span className="vs-text">vs</span>
                  <span className="num away-num">{l1.away_xg}</span>
                </div>
                <div style={{ height: 75, width: '100%', marginTop: 4 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={xgChartData} margin={{ top: 0, right: 10, left: 10, bottom: 0 }}>
                      <XAxis dataKey="team" stroke="#64748b" tick={{ fontSize: 11 }} />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: 'rgba(18, 24, 38, 0.95)',
                          borderColor: 'rgba(255, 255, 255, 0.2)',
                          borderRadius: 8,
                          color: '#fff',
                        }}
                        formatter={(val: number) => [`${val} xG`, 'Expected Goals']}
                      />
                      <Bar dataKey="xG" radius={[6, 6, 0, 0]}>
                        {xgChartData.map((entry, index) => (
                          <Cell key={`cell-xg-${index}`} fill={entry.fill} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Metric 3: Possession Split */}
              <div className="metric-box">
                <div className="box-title">Predicted Possession Split</div>
                <div className="comparison-stat">
                  <span className="num home-num">{l1.home_poss}%</span>
                  <span className="vs-text">-</span>
                  <span className="num away-num">{l1.away_poss}%</span>
                </div>
                <div className="poss-track-bar">
                  <div className="poss-fill-home" style={{ width: `${l1.home_poss}%` }} />
                  <div className="poss-fill-away" style={{ width: `${l1.away_poss}%` }} />
                </div>
              </div>

              {/* Metric 4: Likely Scoreline */}
              <div className="metric-box highlight">
                <div className="box-title">Most Likely Scoreline</div>
                <div className="scoreline-val">{l1.predicted_scoreline}</div>
                <div className="scoreline-venue">{l1.venue}</div>
              </div>
            </div>

            {/* Leg 2 & Aggregate Banner */}
            {l2 && agg && (
              <div className="leg2-aggregate-card">
                <div className="leg2-header">
                  <span>Reverse Leg 2 ({selectedAwayTeam} Home Venue)</span>
                  <span className="badge-pill pill-gold">Leg 2: {l2.predicted_scoreline}</span>
                </div>
                <div className="leg2-stats-row">
                  <div>
                    Home Win Prob: <strong>{l2.home_win_pct}%</strong> | Expected Goals: <strong>{l2.home_xg} - {l2.away_xg}</strong>
                  </div>
                  <div>
                    Possession: <strong>{l2.home_poss}% - {l2.away_poss}%</strong>
                  </div>
                </div>

                <div className="aggregate-divider">
                  <div className="agg-badge">
                    <Trophy size={18} className="gold-icon" />
                    <span>2-LEG AGGREGATE OUTCOME</span>
                  </div>
                  <div className="agg-winner">
                    Winner: <strong className="winner-name">{agg.winner}</strong>
                    <span className="agg-score">({agg.aggregate_scoreline})</span>
                  </div>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </section>
  );
};

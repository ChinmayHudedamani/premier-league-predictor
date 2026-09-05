import React from 'react';
import { usePredictorStore } from '../../store/usePredictorStore';
import { Trophy, BarChart3 } from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
} from 'recharts';

export const Standings: React.FC = () => {
  const { uiData } = usePredictorStore();

  if (!uiData) return null;

  // Top 8 teams chart data
  const chartData = uiData.standings.slice(0, 8).map((row) => ({
    team: row.team,
    titleWin: row['title_win_prob_%'] ?? row.title_win_prob ?? 0,
    top4: row['top4_prob_%'] ?? row.top4_prob ?? 0,
    points: row.avg_projected_points,
  }));

  return (
    <section className="tab-view active">
      <div className="glass-card">
        <div className="card-header">
          <div className="card-title-group">
            <h2 className="card-title">🏆 Premier League 2026–27 Projected Standings</h2>
            <p className="card-subtitle">Aggregated from 10,000 Monte Carlo season outcome simulations</p>
          </div>
          <span className="badge-pill pill-gold">10,000 Season Simulations</span>
        </div>

        {/* Title Race & Top 4 Probability Chart */}
        <div className="standings-chart-card">
          <div className="chart-header">
            <div className="box-title">
              <BarChart3 size={16} style={{ display: 'inline', marginRight: 6, color: 'var(--primary-cyan)' }} />
              Top Contenders: Title Race % & Top 4 Champions League Qualification Probability
            </div>
          </div>
          <div style={{ width: '100%', height: 260 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={chartData}
                margin={{ top: 20, right: 30, left: 0, bottom: 20 }}
              >
                <XAxis dataKey="team" stroke="#94a3b8" tick={{ fontSize: 11 }} />
                <YAxis unit="%" stroke="#94a3b8" tick={{ fontSize: 11 }} domain={[0, 100]} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'rgba(18, 24, 38, 0.95)',
                    borderColor: 'rgba(255, 255, 255, 0.2)',
                    borderRadius: 8,
                    color: '#fff',
                  }}
                  formatter={(val: number) => [`${val}%`]}
                />
                <Legend wrapperStyle={{ paddingTop: 10, fontSize: 12 }} />
                <Bar name="Title Win %" dataKey="titleWin" fill="#ffd700" radius={[4, 4, 0, 0]} />
                <Bar name="Top 4 %" dataKey="top4" fill="#00f2fe" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Complete Table */}
        <div className="data-table-wrapper" style={{ marginTop: 24 }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Rank</th>
                <th>Team</th>
                <th>Title Win %</th>
                <th>Top 4 %</th>
                <th>Relegation %</th>
                <th>Projected Points</th>
                <th>Elo Rating</th>
              </tr>
            </thead>
            <tbody>
              {uiData.standings.map((row, idx) => {
                const rank = idx + 1;
                const titleProb = row['title_win_prob_%'] ?? row.title_win_prob ?? 0;
                const top4Prob = row['top4_prob_%'] ?? row.top4_prob ?? 0;
                const relProb = row['relegation_prob_%'] ?? row.relegation_prob ?? 0;
                const elo = uiData.team_stats[row.team]?.elo || 1600;

                let rankBadge = <span className="badge-pill pill-cyan">#{rank}</span>;
                if (rank === 1) {
                  rankBadge = <span className="badge-pill pill-gold"><Trophy size={12} style={{ display: 'inline', marginRight: 3 }} /> #{rank}</span>;
                } else if (rank <= 4) {
                  rankBadge = <span className="badge-pill pill-purple">#{rank}</span>;
                } else if (rank >= 18) {
                  rankBadge = <span className="badge-pill pill-red">#{rank}</span>;
                }

                return (
                  <tr key={row.team}>
                    <td>{rankBadge}</td>
                    <td><strong>{row.team}</strong></td>
                    <td>
                      <span style={{ color: titleProb > 10 ? 'var(--accent-gold)' : 'inherit', fontWeight: titleProb > 10 ? 700 : 400 }}>
                        {titleProb}%
                      </span>
                    </td>
                    <td>{top4Prob}%</td>
                    <td>
                      <span style={{ color: relProb > 25 ? 'var(--accent-red)' : 'inherit' }}>
                        {relProb}%
                      </span>
                    </td>
                    <td><strong>{row.avg_projected_points} pts</strong></td>
                    <td>{elo} Elo</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
};

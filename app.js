let uiData = null;

document.addEventListener('DOMContentLoaded', () => {
  initApp();
});

async function initApp() {
  try {
    const res = await fetch('data/ui_data.json');
    uiData = await res.json();
    
    setupTabSwitching();
    setupPredictorDropdowns();
    setupSquadTeamSelect();
    renderStandingsTable();
    renderPotsTable();
    renderGoldenBootTable();
    renderDarkhorsesTable();
    renderTransfersTable();
    renderOwnersGrid();
    renderImprovisationSection();
    
  } catch (err) {
    console.error('Error loading ui_data.json:', err);
  }
}

function setupTabSwitching() {
  const btns = document.querySelectorAll('.tab-btn');
  btns.forEach(btn => {
    btn.addEventListener('click', () => {
      btns.forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.tab-view').forEach(v => v.classList.remove('active'));
      
      btn.classList.add('active');
      const targetId = btn.getAttribute('data-tab');
      const targetView = document.getElementById(targetId);
      if (targetView) targetView.classList.add('active');
    });
  });
}

function setupPredictorDropdowns() {
  const homeSelect = document.getElementById('homeTeamSelect');
  const awaySelect = document.getElementById('awayTeamSelect');
  const predictBtn = document.getElementById('predictMatchBtn');
  
  if (!homeSelect || !awaySelect || !uiData) return;
  
  homeSelect.innerHTML = '<option value="" disabled selected>-- Select Home Team --</option>';
  awaySelect.innerHTML = '<option value="" disabled selected>-- Select Away Team --</option>';
  
  uiData.teams.forEach(team => {
    const optH = document.createElement('option');
    optH.value = team;
    optH.textContent = team;
    homeSelect.appendChild(optH);
    
    const optA = document.createElement('option');
    optA.value = team;
    optA.textContent = team;
    awaySelect.appendChild(optA);
  });
  
  const handleSelectionChange = () => {
    const homeVal = homeSelect.value;
    const awayVal = awaySelect.value;
    
    if (homeVal) {
      document.getElementById('homeBadgeName').textContent = homeVal;
    }
    if (awayVal) {
      document.getElementById('awayBadgeName').textContent = awayVal;
    }
    
    if (homeVal && awayVal) {
      calculateMatchPrediction(homeVal, awayVal);
    }
  };
  
  homeSelect.onchange = handleSelectionChange;
  awaySelect.onchange = handleSelectionChange;
  
  if (predictBtn) {
    predictBtn.onclick = () => {
      const h = homeSelect.value;
      const a = awaySelect.value;
      if (!h || !a) {
        alert("Please select both a Home Team and an Away Team from the dropdowns!");
        return;
      }
      calculateMatchPrediction(h, a);
    };
  }
}

async function calculateMatchPrediction(homeTeam, awayTeam) {
  if (!homeTeam || !awayTeam) return;
  
  if (homeTeam === awayTeam) {
    document.getElementById('predictedScoreline').textContent = 'Invalid Match';
    const l2Box = document.getElementById('leg2PredictionBox');
    if (l2Box) {
      l2Box.innerHTML = `
        <div style="text-align:center; color:var(--accent-red); font-weight:700; padding:10px">
          ⚠️ Home Team and Away Team must be different Premier League clubs!
        </div>
      `;
    }
    return;
  }

  // Update Section Headers
  document.getElementById('leg1HeaderTitle').textContent = `🏟️ LEG 1 MATCH PREDICTION (${homeTeam.toUpperCase()} HOME VENUE)`;

  try {
    const apiRes = await fetch(`/api/predict?home=${encodeURIComponent(homeTeam)}&away=${encodeURIComponent(awayTeam)}`);
    if (apiRes.ok) {
      const pred = await apiRes.json();
      render2LegPrediction(pred);
      return;
    }
  } catch (e) {
    console.warn("Backend API fetch unreachable, running client-side prediction engine:", e);
  }

  // Guaranteed Client-Side Poisson Prediction Engine
  const homeStats = uiData.team_stats[homeTeam] || { elo: 1600, attack_rating: 1.0, defence_rating: 1.0 };
  const awayStats = uiData.team_stats[awayTeam] || { elo: 1600, attack_rating: 1.0, defence_rating: 1.0 };
  
  // Leg 1: homeTeam at Home
  const l1_home_xg = Math.max(0.2, homeStats.attack_rating * awayStats.defence_rating * uiData.home_advantage);
  const l1_away_xg = Math.max(0.2, awayStats.attack_rating * homeStats.defence_rating * 1.05);
  
  const l1_res = runPoissonSimulation(l1_home_xg, l1_away_xg);
  
  const eloHomePow = Math.pow(homeStats.elo, 1.25);
  const eloAwayPow = Math.pow(awayStats.elo, 1.25);
  const l1_home_poss = Math.round((eloHomePow / (eloHomePow + eloAwayPow)) * 100);
  const l1_away_poss = 100 - l1_home_poss;

  // Leg 2: awayTeam at Home
  const l2_home_xg = Math.max(0.2, awayStats.attack_rating * homeStats.defence_rating * uiData.home_advantage);
  const l2_away_xg = Math.max(0.2, homeStats.attack_rating * awayStats.defence_rating * 1.05);
  const l2_res = runPoissonSimulation(l2_home_xg, l2_away_xg);

  // Aggregate Calculation
  const t1_goals = l1_res.likelyHomeG + l2_res.likelyAwayG;
  const t2_goals = l1_res.likelyAwayG + l2_res.likelyHomeG;
  
  let agg_winner = "Tie (Penalties)";
  if (t1_goals > t2_goals) agg_winner = homeTeam;
  else if (t2_goals > t1_goals) agg_winner = awayTeam;
  
  const clientPred = {
    home_team: homeTeam,
    away_team: awayTeam,
    leg1_home: {
      venue: `${homeTeam} Stadium (Home)`,
      home_win_pct: l1_res.pctHome,
      draw_pct: l1_res.pctDraw,
      away_win_pct: l1_res.pctAway,
      home_xg: l1_home_xg.toFixed(2),
      away_xg: l1_away_xg.toFixed(2),
      home_poss: l1_home_poss,
      away_poss: l1_away_poss,
      predicted_scoreline: `${l1_res.likelyHomeG} - ${l1_res.likelyAwayG}`
    },
    leg2_away: {
      venue: `${awayTeam} Stadium (Home)`,
      home_win_pct: l2_res.pctHome,
      draw_pct: l2_res.pctDraw,
      away_win_pct: l2_res.pctAway,
      home_xg: l2_home_xg.toFixed(2),
      away_xg: l2_away_xg.toFixed(2),
      home_poss: l1_away_poss,
      away_poss: l1_home_poss,
      predicted_scoreline: `${l2_res.likelyHomeG} - ${l2_res.likelyAwayG}`
    },
    aggregate_2leg: {
      winner: agg_winner,
      aggregate_scoreline: `${homeTeam} ${t1_goals} - ${t2_goals} ${awayTeam}`
    }
  };

  render2LegPrediction(clientPred);
}

function runPoissonSimulation(lambdaHome, lambdaAway) {
  const maxGoals = 7;
  const homeProbs = [];
  const awayProbs = [];
  
  for (let g = 0; g < maxGoals; g++) {
    homeProbs[g] = poissonPMF(g, lambdaHome);
    awayProbs[g] = poissonPMF(g, lambdaAway);
  }
  
  let pHomeWin = 0, pDraw = 0, pAwayWin = 0;
  let maxProb = -1, likelyHomeG = 0, likelyAwayG = 0;
  
  for (let h = 0; h < maxGoals; h++) {
    for (let a = 0; a < maxGoals; a++) {
      const p = homeProbs[h] * awayProbs[a];
      if (h > a) pHomeWin += p;
      else if (h === a) pDraw += p;
      else pAwayWin += p;
      if (p > maxProb) { maxProb = p; likelyHomeG = h; likelyAwayG = a; }
    }
  }
  
  const sumP = pHomeWin + pDraw + pAwayWin;
  return {
    pctHome: ((pHomeWin / sumP) * 100).toFixed(1),
    pctDraw: ((pDraw / sumP) * 100).toFixed(1),
    pctAway: ((pAwayWin / sumP) * 100).toFixed(1),
    likelyHomeG: likelyHomeG,
    likelyAwayG: likelyAwayG
  };
}

function render2LegPrediction(pred) {
  const l1 = pred.leg1_home;
  const l2 = pred.leg2_away;
  const agg = pred.aggregate_2leg;
  
  updateMatchUI(l1.home_win_pct, l1.draw_pct, l1.away_win_pct, l1.home_xg, l1.away_xg, l1.home_poss, l1.away_poss, l1.predicted_scoreline);
  
  const l2Box = document.getElementById('leg2PredictionBox');
  if (l2Box) {
    l2Box.innerHTML = `
      <div style="font-size:0.85rem; color:var(--text-muted); text-transform:uppercase; margin-bottom:8px">Reverse Leg 2 (${pred.away_team} Home Venue)</div>
      <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px">
        <div>Win Prob: <strong>${l2.home_win_pct}%</strong> | Expected Goals: <strong>${l2.home_xg} - ${l2.away_xg}</strong></div>
        <div style="color:var(--accent-gold); font-weight:700; font-size:1.3rem;">Score: ${l2.predicted_scoreline}</div>
      </div>
      <div style="margin-top:14px; padding-top:12px; border-top:1px solid var(--border-glass); display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px">
        <span class="badge-pill pill-purple">★ 2-LEG AGGREGATE WINNER</span>
        <strong style="color:var(--primary-cyan); font-size:1.2rem">${agg.winner} (${agg.aggregate_scoreline})</strong>
      </div>
    `;
  }
}

function updateMatchUI(pctHome, pctDraw, pctAway, hXG, aXG, hPoss, aPoss, scoreline) {
  document.getElementById('homeWinProbVal').textContent = `${pctHome}%`;
  document.getElementById('drawProbVal').textContent = `${pctDraw}%`;
  document.getElementById('awayWinProbVal').textContent = `${pctAway}%`;
  
  document.getElementById('homeWinProbBar').style.width = `${pctHome}%`;
  document.getElementById('drawProbBar').style.width = `${pctDraw}%`;
  document.getElementById('awayWinProbBar').style.width = `${pctAway}%`;
  
  document.getElementById('homeXGVal').textContent = hXG;
  document.getElementById('awayXGVal').textContent = aXG;
  
  document.getElementById('homePossVal').textContent = `${hPoss}%`;
  document.getElementById('awayPossVal').textContent = `${aPoss}%`;
  
  document.getElementById('predictedScoreline').textContent = scoreline;
}

function setupSquadTeamSelect() {
  const squadSelect = document.getElementById('squadTeamSelect');
  if (!squadSelect || !uiData) return;
  
  squadSelect.innerHTML = '<option value="" disabled selected>-- Select Team --</option>';
  uiData.teams.forEach(team => {
    const opt = document.createElement('option');
    opt.value = team;
    opt.textContent = team;
    squadSelect.appendChild(opt);
  });
  
  squadSelect.onchange = (e) => {
    renderTeamSquadAndPitch(e.target.value);
  };
}

function renderTeamSquadAndPitch(teamName) {
  const tData = uiData.team_squads ? uiData.team_squads[teamName] : null;
  if (!tData) return;
  
  const bestBox = document.getElementById('bestPlayerBox');
  if (bestBox && tData.best_player) {
    const bp = tData.best_player;
    bestBox.innerHTML = `
      <div class="key-badge">${bp.fifa_ovr}</div>
      <div class="best-player-details">
        <span class="badge-pill pill-gold">🌟 KEY MAN / TEAM MVP</span>
        <h3 style="margin-top:4px">${bp.web_name}</h3>
        <p>${teamName} • ${bp.position} • Form: ${bp.form} • Expected Goals: ${bp.expected_goals} xG</p>
      </div>
    `;
  }
  
  const pitchContainer = document.getElementById('tacticalPitchContainer');
  if (pitchContainer && tData.tactical_formation_11) {
    pitchContainer.innerHTML = `
      <div class="pitch-center-line"></div>
      <div class="pitch-center-circle"></div>
      <div class="pitch-penalty-box-top"></div>
      <div class="pitch-penalty-box-bottom"></div>
    `;
    
    tData.tactical_formation_11.forEach(player => {
      const card = document.createElement('div');
      card.className = 'fut-pitch-card';
      card.style.left = `${player.x}%`;
      card.style.top = `${player.y}%`;
      
      card.innerHTML = `
        <div class="fut-card-frame">
          <div class="fut-ovr-badge">${player.fifa_ovr}</div>
          <div class="fut-role-badge">${player.role}</div>
        </div>
        <div class="fut-player-name-tag">${player.web_name}</div>
      `;
      pitchContainer.appendChild(card);
    });
  }
  
  const tbody = document.getElementById('squadTableBody');
  if (tbody && tData.squad) {
    tbody.innerHTML = '';
    tData.squad.forEach((p, idx) => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td><span class="badge-pill pill-purple">#${idx + 1}</span></td>
        <td><strong>${p.web_name}</strong></td>
        <td>${p.position}</td>
        <td><span class="badge-pill pill-gold">${p.fifa_ovr} OVR</span></td>
        <td>£${p.price_m}M</td>
        <td>${p.expected_goals}</td>
        <td>${p.expected_assists}</td>
        <td><span class="badge-pill pill-cyan">${p.form}</span></td>
      `;
      tbody.appendChild(tr);
    });
  }
}

async function renderImprovisationSection() {
  const container = document.getElementById('improvisationContainer');
  if (!container) return;
  
  try {
    const res = await fetch('/api/improvisation');
    if (res.ok) {
      const data = await res.json();
      container.innerHTML = `
        <div style="display:flex; gap:20px; align-items:center; margin-bottom:20px">
          <div class="stat-badge" style="background:rgba(0,242,254,0.1); border-color:var(--primary-cyan)">
            <div class="val" style="color:var(--primary-cyan)">+${data.precision_gain_pct}%</div>
            <div class="lbl">Precision Gain</div>
          </div>
          <div class="stat-badge" style="background:rgba(255,215,0,0.1); border-color:var(--accent-gold)">
            <div class="val" style="color:var(--accent-gold)">${data.improvisation_score_pct}%</div>
            <div class="lbl">Improvisation Score</div>
          </div>
        </div>
        <h4 style="color:#fff; margin-bottom:12px">Implemented AI System Upgrades:</h4>
        <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(280px, 1fr)); gap:14px">
          ${data.recommendations.map(r => `
            <div style="background:rgba(255,255,255,0.03); border:1px solid var(--border-glass); border-radius:10px; padding:14px">
              <div style="display:flex; justify-content:space-between; margin-bottom:6px">
                <strong style="color:var(--primary-cyan)">${r.title}</strong>
                <span class="badge-pill pill-green">${r.impact}</span>
              </div>
              <p style="font-size:0.85rem; color:var(--text-muted)">${r.details}</p>
            </div>
          `).join('')}
        </div>
      `;
    }
  } catch (e) {
    console.warn("Improvisation fetch error:", e);
  }
}

function poissonPMF(k, lambda) {
  return (Math.pow(lambda, k) * Math.exp(-lambda)) / factorial(k);
}

function factorial(n) {
  if (n <= 1) return 1;
  let res = 1;
  for (let i = 2; i <= n; i++) res *= i;
  return res;
}

function renderStandingsTable() {
  const tbody = document.getElementById('standingsTableBody');
  if (!tbody || !uiData) return;
  
  tbody.innerHTML = '';
  uiData.standings.forEach((row, idx) => {
    const tr = document.createElement('tr');
    const rank = idx + 1;
    
    let rankBadge = `<span class="badge-pill pill-cyan">#${rank}</span>`;
    if (rank === 1) rankBadge = `<span class="badge-pill pill-gold">🏆 #${rank}</span>`;
    else if (rank <= 4) rankBadge = `<span class="badge-pill pill-purple">#${rank}</span>`;
    else if (rank >= 18) rankBadge = `<span class="badge-pill pill-red">#${rank}</span>`;
    
    tr.innerHTML = `
      <td>${rankBadge}</td>
      <td><strong>${row.team}</strong></td>
      <td><strong>${row.title_win_prob_%}%</strong></td>
      <td>${row.top4_prob_%}%</td>
      <td>${row.relegation_prob_%}%</td>
      <td><strong>${row.avg_projected_points} pts</strong></td>
      <td>${uiData.team_stats[row.team]?.elo || 1600} Elo</td>
    `;
    tbody.appendChild(tr);
  });
}

function renderPotsTable() {
  const tbody = document.getElementById('potsTableBody');
  if (!tbody || !uiData) return;
  tbody.innerHTML = '';
  
  uiData.pots.forEach((row, idx) => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td><span class="badge-pill pill-purple">#${idx + 1}</span></td>
      <td><strong>${row.web_name}</strong></td>
      <td>${row.team_name}</td>
      <td>${row.position}</td>
      <td><span class="badge-pill pill-gold">${row.fifa_ovr} OVR</span></td>
      <td><strong>${row.pots_score.toFixed(3)}</strong></td>
      <td>${row.expected_goals}</td>
      <td>${row.expected_assists}</td>
      <td><span class="badge-pill pill-cyan">${row.form}</span></td>
    `;
    tbody.appendChild(tr);
  });
}

function renderGoldenBootTable() {
  const tbody = document.getElementById('goldenBootTableBody');
  if (!tbody || !uiData) return;
  tbody.innerHTML = '';
  
  uiData.golden_boot.forEach((row, idx) => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td><span class="badge-pill pill-gold">#${idx + 1}</span></td>
      <td><strong>${row.web_name}</strong></td>
      <td>${row.team_name}</td>
      <td>${row.position}</td>
      <td><strong>${row.goals_scored} goals</strong></td>
      <td>${row.expected_goals} xG</td>
      <td><span class="badge-pill pill-gold">${row.golden_boot_score.toFixed(3)}</span></td>
    `;
    tbody.appendChild(tr);
  });
}

function renderDarkhorsesTable() {
  const tbody = document.getElementById('darkhorsesTableBody');
  if (!tbody || !uiData) return;
  tbody.innerHTML = '';
  
  uiData.darkhorses.forEach((row, idx) => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td><span class="badge-pill pill-cyan">#${idx + 1}</span></td>
      <td><strong>${row.web_name}</strong></td>
      <td>${row.team_name}</td>
      <td>${row.position}</td>
      <td>£${row.price_m}M</td>
      <td><span class="badge-pill pill-green">${row.darkhorse_potential_score}</span></td>
    `;
    tbody.appendChild(tr);
  });
}

function renderTransfersTable() {
  const tbody = document.getElementById('transfersTableBody');
  if (!tbody || !uiData) return;
  tbody.innerHTML = '';
  
  uiData.transfers.forEach((row, idx) => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td><span class="badge-pill pill-purple">#${idx + 1}</span></td>
      <td><strong>${row.web_name}</strong></td>
      <td>${row.team_name}</td>
      <td>${row.position}</td>
      <td><strong style="color:var(--accent-gold)">€${row.predicted_market_value_eur_m}M</strong></td>
      <td><span class="badge-pill pill-cyan">£${row.predicted_weekly_salary_k}k/wk</span></td>
    `;
    tbody.appendChild(tr);
  });
}

function renderOwnersGrid() {
  const container = document.getElementById('ownersGridContainer');
  if (!container || !uiData) return;
  container.innerHTML = '';
  
  uiData.owners.forEach(row => {
    const card = document.createElement('div');
    card.className = 'owner-card';
    card.innerHTML = `
      <div class="team-name">${row.team_name}</div>
      <div class="owner-grp">Owner: <strong>${row.owner_group}</strong></div>
      <div class="archetype">Archetype: ${row.investment_archetype}</div>
      <div style="font-size:0.85rem; color:var(--primary-cyan); margin-bottom:8px">Avg Budget: <strong>${row.avg_window_budget_m}</strong></div>
      <div class="action-text">${row.predictive_action_summary}</div>
    `;
    container.appendChild(card);
  });
}

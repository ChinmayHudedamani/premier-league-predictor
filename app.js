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
    renderStandingsTable();
    renderPotsTable();
    renderGoldenBootTable();
    renderDarkhorsesTable();
    renderTransfersTable();
    renderOwnersGrid();
    
    // Initial Match Calculation (Arsenal vs Manchester City)
    calculateMatchPrediction();
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
      document.getElementById(targetId).classList.add('active');
    });
  });
}

function setupPredictorDropdowns() {
  const homeSelect = document.getElementById('homeTeamSelect');
  const awaySelect = document.getElementById('awayTeamSelect');
  
  if (!homeSelect || !awaySelect || !uiData) return;
  
  homeSelect.innerHTML = '';
  awaySelect.innerHTML = '';
  
  uiData.teams.forEach(team => {
    const optH = document.createElement('option');
    optH.value = team;
    optH.textContent = team;
    if (team === 'Arsenal') optH.selected = true;
    homeSelect.appendChild(optH);
    
    const optA = document.createElement('option');
    optA.value = team;
    optA.textContent = team;
    if (team === 'Manchester City') optA.selected = true;
    awaySelect.appendChild(optA);
  });
  
  homeSelect.addEventListener('change', calculateMatchPrediction);
  awaySelect.addEventListener('change', calculateMatchPrediction);
}

function calculateMatchPrediction() {
  const homeTeam = document.getElementById('homeTeamSelect').value;
  const awayTeam = document.getElementById('awayTeamSelect').value;
  
  if (homeTeam === awayTeam) {
    document.getElementById('predictedScoreline').textContent = 'Invalid Match';
    return;
  }
  
  const homeStats = uiData.team_stats[homeTeam] || { elo: 1600, attack_rating: 1.0, defence_rating: 1.0 };
  const awayStats = uiData.team_stats[awayTeam] || { elo: 1600, attack_rating: 1.0, defence_rating: 1.0 };
  
  // Dixon-Coles Poisson Lambda Expected Goals
  const lambdaHome = Math.max(0.2, homeStats.attack_rating * awayStats.defence_rating * uiData.home_advantage);
  const lambdaAway = Math.max(0.2, awayStats.attack_rating * homeStats.defence_rating * 1.05);
  
  // Poisson PMF calculation (0..7 goals)
  const maxGoals = 7;
  const homeProbs = [];
  const awayProbs = [];
  
  for (let g = 0; g < maxGoals; g++) {
    homeProbs[g] = poissonPMF(g, lambdaHome);
    awayProbs[g] = poissonPMF(g, lambdaAway);
  }
  
  let pHomeWin = 0;
  let pDraw = 0;
  let pAwayWin = 0;
  
  let maxProb = -1;
  let likelyHomeG = 0;
  let likelyAwayG = 0;
  
  for (let h = 0; h < maxGoals; h++) {
    for (let a = 0; a < maxGoals; a++) {
      const p = homeProbs[h] * awayProbs[a];
      if (h > a) pHomeWin += p;
      else if (h === a) pDraw += p;
      else pAwayWin += p;
      
      if (p > maxProb) {
        maxProb = p;
        likelyHomeG = h;
        likelyAwayG = a;
      }
    }
  }
  
  const sumP = pHomeWin + pDraw + pAwayWin;
  const pctHome = ((pHomeWin / sumP) * 100).toFixed(1);
  const pctDraw = ((pDraw / sumP) * 100).toFixed(1);
  const pctAway = ((pAwayWin / sumP) * 100).toFixed(1);
  
  // Possession Split
  const eloHomePow = Math.pow(homeStats.elo, 1.25);
  const eloAwayPow = Math.pow(awayStats.elo, 1.25);
  const homePoss = Math.round((eloHomePow / (eloHomePow + eloAwayPow)) * 100);
  const awayPoss = 100 - homePoss;
  
  // UI Updates
  document.getElementById('homeWinProbVal').textContent = `${pctHome}%`;
  document.getElementById('drawProbVal').textContent = `${pctDraw}%`;
  document.getElementById('awayWinProbVal').textContent = `${pctAway}%`;
  
  document.getElementById('homeWinProbBar').style.width = `${pctHome}%`;
  document.getElementById('drawProbBar').style.width = `${pctDraw}%`;
  document.getElementById('awayWinProbBar').style.width = `${pctAway}%`;
  
  document.getElementById('homeXGVal').textContent = lambdaHome.toFixed(2);
  document.getElementById('awayXGVal').textContent = lambdaAway.toFixed(2);
  
  document.getElementById('homePossVal').textContent = `${homePoss}%`;
  document.getElementById('awayPossVal').textContent = `${awayPoss}%`;
  
  document.getElementById('predictedScoreline').textContent = `${likelyHomeG} - ${likelyAwayG}`;
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

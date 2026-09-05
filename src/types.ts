export interface TeamStats {
  elo: number;
  attack_rating: number;
  defence_rating: number;
}

export interface TacticalPlayer {
  web_name: string;
  position: string;
  fifa_ovr: number;
  role: string;
  x: number;
  y: number;
}

export interface SquadPlayer {
  web_name: string;
  position: string;
  fifa_ovr: number;
  price_m: number;
  expected_goals: number;
  expected_assists: number;
  form: number | string;
}

export interface TeamSquadData {
  best_player?: SquadPlayer;
  tactical_formation_11?: TacticalPlayer[];
  squad?: SquadPlayer[];
}

export interface StandingsRow {
  team: string;
  "title_win_prob_%"?: number;
  title_win_prob?: number;
  "top4_prob_%"?: number;
  top4_prob?: number;
  "relegation_prob_%"?: number;
  relegation_prob?: number;
  avg_projected_points: number;
}

export interface PotsPlayer {
  web_name: string;
  team_name: string;
  position: string;
  fifa_ovr: number;
  pots_score: number;
  expected_goals: number;
  expected_assists: number;
  form: number | string;
}

export interface GoldenBootPlayer {
  web_name: string;
  team_name: string;
  position: string;
  goals_scored: number;
  expected_goals: number;
  golden_boot_score: number;
}

export interface DarkhorsePlayer {
  web_name: string;
  team_name: string;
  position: string;
  price_m: number;
  darkhorse_potential_score: number;
}

export interface TransferPlayer {
  web_name: string;
  team_name: string;
  position: string;
  predicted_market_value_eur_m: number;
  predicted_weekly_salary_k: number;
}

export interface OwnerProfile {
  team_name: string;
  owner_group: string;
  investment_archetype: string;
  avg_window_budget_m: string;
  predictive_action_summary: string;
}

export interface UIData {
  teams: string[];
  home_advantage: number;
  team_stats: Record<string, TeamStats>;
  team_squads: Record<string, TeamSquadData>;
  standings: StandingsRow[];
  pots: PotsPlayer[];
  golden_boot: GoldenBootPlayer[];
  darkhorses: DarkhorsePlayer[];
  transfers: TransferPlayer[];
  owners: OwnerProfile[];
}

export interface MatchLegPrediction {
  venue: string;
  home_win_pct: string;
  draw_pct: string;
  away_win_pct: string;
  home_xg: string;
  away_xg: string;
  home_poss: number;
  away_poss: number;
  predicted_scoreline: string;
}

export interface AggregatePrediction {
  winner: string;
  aggregate_scoreline: string;
}

export interface TwoLegPrediction {
  home_team: string;
  away_team: string;
  leg1_home: MatchLegPrediction;
  leg2_away: MatchLegPrediction;
  aggregate_2leg: AggregatePrediction;
}

export interface ImprovisationRecommendation {
  title: string;
  impact: string;
  details: string;
}

export interface ImprovisationData {
  precision_gain_pct: number;
  improvisation_score_pct: number;
  recommendations: ImprovisationRecommendation[];
}

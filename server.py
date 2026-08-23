import os
import sys
import json
import urllib.parse
from http.server import HTTPServer, SimpleHTTPRequestHandler

from src.database import PredictionDatabase
from src.improvisation_engine import ImprovisationEngine

db = PredictionDatabase()
improv_engine = ImprovisationEngine(db)

class PredictorAPIHandler(SimpleHTTPRequestHandler):
    """
    Custom HTTP Request Handler serving static web files and REST API endpoints.
    """
    protocol_version = "HTTP/1.1"

    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        query = urllib.parse.parse_qs(parsed_path.query)

        if path == "/api/predict":
            home_team = query.get("home", ["Arsenal"])[0]
            away_team = query.get("away", ["Manchester City"])[0]

            pred = db.get_2leg_prediction(home_team, away_team)
            if not pred:
                self.send_json({"error": f"No prediction found for {home_team} vs {away_team}"}, status=404)
                return

            response_payload = {
                "home_team": home_team,
                "away_team": away_team,
                "leg1_home": {
                    "venue": f"{home_team} Stadium (Home)",
                    "home_win_pct": pred["leg1_home_win_pct"],
                    "draw_pct": pred["leg1_draw_pct"],
                    "away_win_pct": pred["leg1_away_win_pct"],
                    "home_xg": pred["leg1_home_xg"],
                    "away_xg": pred["leg1_away_xg"],
                    "home_poss": pred["leg1_home_poss"],
                    "away_poss": pred["leg1_away_poss"],
                    "predicted_scoreline": pred["leg1_scoreline"]
                },
                "leg2_away": {
                    "venue": f"{away_team} Stadium (Home)",
                    "home_win_pct": pred["leg2_home_win_pct"],
                    "draw_pct": pred["leg2_draw_pct"],
                    "away_win_pct": pred["leg2_away_win_pct"],
                    "home_xg": pred["leg2_home_xg"],
                    "away_xg": pred["leg2_away_xg"],
                    "home_poss": pred["leg2_home_poss"],
                    "away_poss": pred["leg2_away_poss"],
                    "predicted_scoreline": pred["leg2_scoreline"]
                },
                "aggregate_2leg": {
                    "winner": pred["aggregate_winner"],
                    "aggregate_scoreline": pred["aggregate_scoreline"]
                }
            }
            self.send_json(response_payload)
            return

        elif path == "/api/standings":
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM team_standings ORDER BY rank ASC")
                rows = [dict(r) for r in cursor.fetchall()]
            self.send_json({"standings": rows})
            return

        elif path == "/api/improvisation":
            metrics = improv_engine.compute_improvisation_metrics()
            self.send_json(metrics)
            return

        elif path == "/api/squad":
            team = query.get("team", ["Arsenal"])[0]
            ui_json_path = "data/ui_data.json"
            if os.path.exists(ui_json_path):
                with open(ui_json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                t_squad = data.get("team_squads", {}).get(team)
                if t_squad:
                    self.send_json(t_squad)
                    return
            self.send_json({"error": f"Squad data not found for {team}"}, status=404)
            return

        return super().do_GET()

    def send_json(self, data, status=200):
        content = json.dumps(data, indent=2, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Connection", "close")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(content)

if __name__ == "__main__":
    server = HTTPServer(('127.0.0.1', 8000), PredictorAPIHandler)
    print("[OK] Premier League Predictor REST API running on http://127.0.0.1:8000", flush=True)
    server.serve_forever()

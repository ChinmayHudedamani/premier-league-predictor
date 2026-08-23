import os
import pandas as pd
import numpy as np
import json
import glob
import io
from typing import Dict, Tuple, List, Optional

# Standard team name mapping across historical seasons (1993 - present)
TEAM_NAME_MAP = {
    'Man United': 'Manchester United',
    'Man City': 'Manchester City',
    'Newcastle': 'Newcastle United',
    'Blackburn': 'Blackburn Rovers',
    'Bolton': 'Bolton Wanderers',
    'Wolverhampton': 'Wolverhampton Wanderers',
    'Wolves': 'Wolverhampton Wanderers',
    'West Ham': 'West Ham United',
    'West Brom': 'West Bromwich Albion',
    'Tottenham': 'Tottenham Hotspur',
    'Spurs': 'Tottenham Hotspur',
    'Sheffield Weds': 'Sheffield Wednesday',
    'Coventry': 'Coventry City',
    'Leicester': 'Leicester City',
    'Leeds': 'Leeds United',
    'Norwich': 'Norwich City',
    'Ipswich': 'Ipswich Town',
    'Oldham': 'Oldham Athletic',
    'Swindon': 'Swindon Town',
    'QPR': 'Queens Park Rangers',
    'Charlton': 'Charlton Athletic',
    'Derby': 'Derby County',
    'Bradford': 'Bradford City',
    'Wigan': 'Wigan Athletic',
    'Stoke': 'Stoke City',
    'Hull': 'Hull City',
    'Swansea': 'Swansea City',
    'Cardiff': 'Cardiff City',
    'Huddersfield': 'Huddersfield Town',
    'Brighton': 'Brighton & Hove Albion',
    'Bournemouth': 'AFC Bournemouth',
    'Nott\'m Forest': 'Nottingham Forest',
    'Middlesbrough': 'Middlesbrough',
}

COLUMN_ALIASES = {
    'date': ['Date', 'match_date', 'MatchDate', 'date'],
    'home_team': ['HomeTeam', 'Home', 'home_team', 'Home_Team', 'HT'],
    'away_team': ['AwayTeam', 'Away', 'away_team', 'Away_Team', 'AT'],
    'home_goals': ['FTHG', 'HG', 'HomeGoals', 'home_score', 'home_goals', 'FTH_Goals'],
    'away_goals': ['FTAG', 'AG', 'AwayGoals', 'away_score', 'away_goals', 'FTA_Goals'],
    'result': ['FTR', 'Result', 'ftr', 'full_time_result', 'result'],
    'season': ['Season', 'season', 'Year', 'season_year']
}

def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Standardizes heterogeneous column names to a canonical schema."""
    renames = {}
    for canonical, aliases in COLUMN_ALIASES.items():
        for alias in aliases:
            if alias in df.columns and canonical not in renames.values():
                renames[alias] = canonical
                break
    return df.rename(columns=renames)

def clean_team_names(series: pd.Series) -> pd.Series:
    """Standardizes team names across multiple data providers and eras."""
    return series.astype(str).str.strip().replace(TEAM_NAME_MAP)

def parse_dates_robustly(date_series: pd.Series) -> pd.Series:
    """Parses mixed date formats (e.g., DD/MM/YY vs DD/MM/YYYY vs YYYY-MM-DD)."""
    parsed = pd.to_datetime(date_series, format='%d/%m/%y', errors='coerce')
    missing_mask = parsed.isna()
    if missing_mask.any():
        parsed[missing_mask] = pd.to_datetime(date_series[missing_mask], format='%d/%m/%Y', errors='coerce')
    missing_mask = parsed.isna()
    if missing_mask.any():
        parsed[missing_mask] = pd.to_datetime(date_series[missing_mask], dayfirst=True, errors='coerce')
    return parsed

def safe_read_csv(filepath: str) -> pd.DataFrame:
    """Reads CSV safely handling trailing commas or inconsistent column counts."""
    with open(filepath, 'r', encoding='latin1') as f:
        lines = f.readlines()
        
    cleaned_lines = []
    header_col_count = len(lines[0].split(',')) if len(lines) > 0 else 0
    
    for line in lines:
        parts = line.rstrip('\r\n').split(',')
        # Truncate trailing empty fields if line exceeds header length
        if len(parts) > header_col_count:
            parts = parts[:header_col_count]
        cleaned_lines.append(','.join(parts))
        
    csv_data = '\n'.join(cleaned_lines)
    return pd.read_csv(io.StringIO(csv_data), low_memory=False)

def load_all_matches(source_path: str) -> pd.DataFrame:
    """Loads a single CSV file or combines multiple CSV files from a directory."""
    if os.path.isfile(source_path):
        print(f"Reading single file: {source_path}")
        return safe_read_csv(source_path)
    elif os.path.isdir(source_path):
        csv_files = sorted(glob.glob(os.path.join(source_path, "*.csv")))
        # Exclude E1.csv (Championship) if E0 files are present
        e0_files = [f for f in csv_files if "E0" in os.path.basename(f)]
        target_files = e0_files if e0_files else csv_files
        
        print(f"Processing {len(target_files)} match CSV files in '{source_path}'...")
        dfs = []
        for f in target_files:
            try:
                filename = os.path.basename(f)
                temp_df = safe_read_csv(f)
                temp_df['source_file'] = filename
                dfs.append(temp_df)
            except Exception as e:
                print(f"Warning: Could not read {f}: {e}")
        if not dfs:
            raise ValueError(f"No valid CSV files found in {source_path}")
        return pd.concat(dfs, ignore_index=True)
    else:
        raise FileNotFoundError(f"Path not found: {source_path}")

def process_and_clean_matches(source_path: str) -> Tuple[pd.DataFrame, Dict]:
    """
    Main function to ingest, deduplicate, validate, and summarize match dataset.
    """
    df = load_all_matches(source_path)
    initial_row_count = len(df)
    
    # 1. Standardize columns
    df = standardize_columns(df)
    
    # Drop rows without teams or goals
    required_cols = ['home_team', 'away_team', 'home_goals', 'away_goals']
    existing_req = [c for c in required_cols if c in df.columns]
    df = df.dropna(subset=existing_req).copy()
    
    # Ensure goal counts are integer
    df['home_goals'] = pd.to_numeric(df['home_goals'], errors='coerce').fillna(0).astype(int)
    df['away_goals'] = pd.to_numeric(df['away_goals'], errors='coerce').fillna(0).astype(int)
    
    # Infer FTR if missing
    if 'result' not in df.columns or df['result'].isna().any():
        df['result'] = np.where(df['home_goals'] > df['away_goals'], 'H',
                       np.where(df['home_goals'] < df['away_goals'], 'A', 'D'))
    
    # Parse Dates
    if 'date' in df.columns:
        df['parsed_date'] = parse_dates_robustly(df['date'])

    # Clean team names
    if 'home_team' in df.columns:
        df['home_team'] = clean_team_names(df['home_team'])
    if 'away_team' in df.columns:
        df['away_team'] = clean_team_names(df['away_team'])
        
    # Deduplicate logic: Keep single instance of (Date, HomeTeam, AwayTeam) or (HomeTeam, AwayTeam, Goals)
    dup_cols = ['parsed_date', 'home_team', 'away_team'] if 'parsed_date' in df.columns else ['home_team', 'away_team', 'home_goals', 'away_goals']
    
    exact_duplicates = df.duplicated().sum()
    df_single = df.drop_duplicates(subset=dup_cols, keep='first').copy()
    logical_duplicates = len(df) - len(df_single)
    
    # Chronological sort
    if 'parsed_date' in df_single.columns:
        df_single = df_single.sort_values('parsed_date').reset_index(drop=True)
        
    # Infer season accurately from match date
    if 'parsed_date' in df_single.columns:
        def calc_season(dt):
            if pd.isna(dt):
                return np.nan
            year = dt.year
            month = dt.month
            # Special COVID 2019-20 season handling (June/July 2020 belonged to 2019-20)
            if (year == 2020 and month in [6, 7]) or (year == 2020 and month == 8 and dt.day <= 5):
                return "2019-2020"
            if month >= 8:
                return f"{year}-{year+1}"
            else:
                return f"{year-1}-{year}"
        df_single['season'] = df_single['parsed_date'].apply(calc_season)

    final_row_count = len(df_single)
    
    # Integrity Analysis
    missing_analysis = {col: int(count) for col, count in df_single.isnull().sum().items() if count > 0}
    
    season_counts = {}
    season_anomaly = {}
    if 'season' in df_single.columns:
        season_counts = {str(k): int(v) for k, v in df_single['season'].value_counts().items()}
        for season_str, count in season_counts.items():
            expected = 462 if season_str in ['1993-1994', '1994-1995'] else 380
            if count != expected:
                season_anomaly[season_str] = {
                    'found': count,
                    'expected': expected,
                    'missing_matches': expected - count
                }

    report = {
        'initial_rows': initial_row_count,
        'exact_duplicates_removed': int(exact_duplicates),
        'logical_match_duplicates_removed': int(logical_duplicates),
        'final_clean_rows': final_row_count,
        'missing_values_by_column': missing_analysis,
        'seasons_covered_count': len(season_counts),
        'season_match_counts': season_counts,
        'season_anomalies_or_missing': season_anomaly
    }
    
    return df_single, report

if __name__ == "__main__":
    import sys
    source_dir = r"C:\data\premier league" if os.path.exists(r"C:\data\premier league") else "data"
    output_clean_path = os.path.join("data", "cleaned_matches.csv")
    report_path = os.path.join("data", "data_health_report.json")
    
    os.makedirs("data", exist_ok=True)
    
    print(f"Processing Premier League match files from: {source_dir}")
    cleaned_df, health_report = process_and_clean_matches(source_dir)
    
    cleaned_df.to_csv(output_clean_path, index=False)
    with open(report_path, 'w') as f:
        json.dump(health_report, f, indent=4)
        
    print("\n=== DATA CLEANING & HEALTH REPORT SUMMARY ===")
    print(f"Initial Total Match Rows Loaded: {health_report['initial_rows']}")
    print(f"Exact Duplicates Removed: {health_report['exact_duplicates_removed']}")
    print(f"Logical Duplicates Removed (Keeping Single Instance): {health_report['logical_match_duplicates_removed']}")
    print(f"Cleaned Unique Match Records: {health_report['final_clean_rows']}")
    print(f"Seasons Covered: {health_report['seasons_covered_count']}")
    
    if health_report['season_anomalies_or_missing']:
        print("\n[!] Missing Match Report per Season:")
        for s, info in sorted(health_report['season_anomalies_or_missing'].items()):
            diff_text = f"Missing: {info['missing_matches']}" if info['missing_matches'] > 0 else f"Extra: {-info['missing_matches']}"
            print(f"  - Season {s}: Found {info['found']}/{info['expected']} matches ({diff_text})")
    else:
        print("\n[OK] All seasons have 100% complete match counts!")

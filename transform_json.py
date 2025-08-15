import os
import json
import argparse
import pandas as pd
from pathlib import Path

def parse_match(json_obj):
    info = json_obj.get("info", {})
    match_id = str(info.get("match_id") or info.get("event", {}).get("match_number") or info.get("dates", ["unknown"])[0]) + "_" + "-".join(info.get("teams", ["T1","T2"]))
    match_type = info.get("match_type")
    date = str(info.get("dates", [""])[0])
    city = info.get("city")
    venue = info.get("venue")
    teams = info.get("teams", [None, None])
    team1 = teams[0] if len(teams) > 0 else None
    team2 = teams[1] if len(teams) > 1 else None
    toss = info.get("toss", {})
    toss_winner = toss.get("winner")
    toss_decision = toss.get("decision")
    result = info.get("outcome", {})
    winner = result.get("winner")
    by = result.get("by", {})
    margin = None
    if isinstance(by, dict) and by:
        k = list(by.keys())[0]
        margin = f"{by.get(k)} {k}"
    pom = None
    if "player_of_match" in info:
        pom = info["player_of_match"][0] if isinstance(info["player_of_match"], list) and info["player_of_match"] else info["player_of_match"]
    gender = info.get("gender")
    competition = info.get("competition")
    return {
        "match_id": match_id,
        "match_type": match_type,
        "date": date,
        "city": city,
        "venue": venue,
        "team1": team1,
        "team2": team2,
        "toss_winner": toss_winner,
        "toss_decision": toss_decision,
        "result": None,
        "winner": winner,
        "margin": margin,
        "player_of_match": pom,
        "gender": gender,
        "competition": competition,
    }

def flatten_deliveries(json_obj, match_id):
    rows = []
    innings_list = json_obj.get("innings", [])
    for inn_idx, inn in enumerate(innings_list, start=1):
        team = inn.get("team")
        overs = inn.get("overs", [])
        for ov in overs:
            over_no = ov.get("over")
            deliveries = ov.get("deliveries", [])
            for d in deliveries:
                batsman = d.get("batter") or d.get("batsman")
                non_striker = d.get("non_striker")
                bowler = d.get("bowler")
                runs = d.get("runs", {})
                runs_batsman = runs.get("batter") or runs.get("batsman") or 0
                runs_extras = runs.get("extras", 0)
                runs_total = runs.get("total", runs_batsman + runs_extras)
                wicket = d.get("wickets") or []
                wicket_kind = None
                wicket_player_out = None
                if isinstance(wicket, list) and wicket:
                    wk = wicket[0]
                    wicket_kind = wk.get("kind")
                    wicket_player_out = wk.get("player_out")
                extras_type = None
                extras = d.get("extras") or {}
                if extras:
                    extras_type = list(extras.keys())[0]

                ball_no = d.get("ball") or len(rows) % 10 + 1  # fallback

                rows.append({
                    "match_id": match_id,
                    "innings_number": inn_idx,
                    "over": over_no,
                    "ball": ball_no,
                    "batsman": batsman,
                    "non_striker": non_striker,
                    "bowler": bowler,
                    "runs_batsman": runs_batsman,
                    "runs_extras": runs_extras,
                    "runs_total": runs_total,
                    "wicket_kind": wicket_kind,
                    "wicket_player_out": wicket_player_out,
                    "extras_type": extras_type,
                })
    return pd.DataFrame(rows)

def flatten_innings(json_obj, match_id):
    rows = []
    innings_list = json_obj.get("innings", [])
    for inn_idx, inn in enumerate(innings_list, start=1):
        batting_team = inn.get("team")
        total_runs = 0
        wickets = 0
        overs_ct = 0.0
        for ov in inn.get("overs", []):
            overs_ct = max(overs_ct, float(ov.get("over", 0))+1.0)
            for d in ov.get("deliveries", []):
                r = d.get("runs", {})
                total_runs += r.get("total", 0)
                if d.get("wickets"):
                    wickets += len(d.get("wickets"))
        rows.append({
            "match_id": match_id,
            "innings_number": inn_idx,
            "batting_team": batting_team,
            "bowling_team": None,
            "total_runs": total_runs,
            "wickets": wickets,
            "overs": overs_ct
        })
    return pd.DataFrame(rows)

def main():
    parser = argparse.ArgumentParser(description="Transform Cricsheet JSON into flat tables and Parquet.")
    parser.add_argument("--input-dir", required=True)
    parser.add_argument("--output", default="data/processed/flattened.parquet")
    parser.add_argument("--also-csv", action="store_true")
    args = parser.parse_args()

    matches_rows = []
    innings_dfs = []
    deliveries_dfs = []

    for p in Path(args.input_dir).glob("*.json"):
        try:
            with open(p, "r", encoding="utf-8") as f:
                obj = json.load(f)
            match_row = parse_match(obj)
            match_id = match_row["match_id"]
            matches_rows.append(match_row)

            inn_df = flatten_innings(obj, match_id)
            del_df = flatten_deliveries(obj, match_id)
            innings_dfs.append(inn_df)
            deliveries_dfs.append(del_df)
        except Exception as e:
            print(f"Failed to parse {p}: {e}")

    matches_df = pd.DataFrame(matches_rows).drop_duplicates(subset=["match_id"])
    innings_df = pd.concat(innings_dfs, ignore_index=True) if innings_dfs else pd.DataFrame()
    deliveries_df = pd.concat(deliveries_dfs, ignore_index=True) if deliveries_dfs else pd.DataFrame()

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    matches_df.to_parquet(args.output.replace("flattened", "matches"), index=False)
    innings_df.to_parquet(args.output.replace("flattened", "innings"), index=False)
    deliveries_df.to_parquet(args.output.replace("flattened", "deliveries"), index=False)

    if args.also_csv:
        matches_df.to_csv(args.output.replace(".parquet","_matches.csv"), index=False)
        innings_df.to_csv(args.output.replace(".parquet","_innings.csv"), index=False)
        deliveries_df.to_csv(args.output.replace(".parquet","_deliveries.csv"), index=False)

    print("Saved:")
    print(" -", args.output.replace("flattened", "matches"))
    print(" -", args.output.replace("flattened", "innings"))
    print(" -", args.output.replace("flattened", "deliveries"))

if __name__ == "__main__":
    main()

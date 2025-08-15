
-- 1. Top 10 batsmen by total runs (all formats)
SELECT batsman, SUM(runs_batsman) AS total_runs
FROM deliveries
GROUP BY batsman
ORDER BY total_runs DESC
LIMIT 10;

-- 2. Leading wicket-takers (dismissals counted)
SELECT bowler, COUNT(*) AS wickets
FROM deliveries
WHERE wicket_kind IS NOT NULL AND wicket_kind NOT IN ('run out', 'retired hurt', 'obstructing the field')
GROUP BY bowler
ORDER BY wickets DESC
LIMIT 10;

-- 3. Team with highest win count
SELECT winner AS team, COUNT(*) AS wins
FROM matches
WHERE winner IS NOT NULL AND winner <> ''
GROUP BY winner
ORDER BY wins DESC
LIMIT 10;

-- 4. Narrowest margin (by runs)
SELECT match_id, winner, margin
FROM matches
WHERE margin LIKE '%run%'
ORDER BY CAST(REPLACE(margin, ' runs', '') AS INTEGER) ASC
LIMIT 10;

-- 5. Most sixes by batsman
SELECT batsman, COUNT(*) AS sixes
FROM deliveries
WHERE runs_batsman = 6
GROUP BY batsman
ORDER BY sixes DESC
LIMIT 10;

-- 6. Most economical bowlers (min 300 balls)
WITH balls AS (
  SELECT bowler, COUNT(*) AS balls_bowled, SUM(runs_total) AS runs_conceded
  FROM deliveries
  GROUP BY bowler
)
SELECT bowler, runs_conceded*1.0/balls_bowled AS economy
FROM balls
WHERE balls_bowled >= 300
ORDER BY economy ASC
LIMIT 15;

-- 7. Best batting strike rate (min 500 balls)
WITH faced AS (
  SELECT batsman, COUNT(*) AS balls_faced, SUM(runs_batsman) AS runs
  FROM deliveries
  GROUP BY batsman
)
SELECT batsman, runs*100.0/balls_faced AS strike_rate, balls_faced
FROM faced
WHERE balls_faced >= 500
ORDER BY strike_rate DESC
LIMIT 15;

-- 8. Top 20 innings totals
SELECT match_id, innings_number, SUM(runs_total) AS total
FROM deliveries
GROUP BY match_id, innings_number
ORDER BY total DESC
LIMIT 20;

-- 9. Average runs per ball by phase (PP/MIDDLE/DEATH)
WITH phase AS (
  SELECT CASE
           WHEN over BETWEEN 0 AND 5 THEN 'PP'
           WHEN over BETWEEN 6 AND 15 THEN 'MIDDLE'
           ELSE 'DEATH'
         END AS phase,
         runs_total
  FROM deliveries
)
SELECT phase, AVG(runs_total) AS avg_runs_per_ball
FROM phase
GROUP BY phase;

-- 10. Dismissal types distribution
SELECT wicket_kind, COUNT(*) AS dismissals
FROM deliveries
WHERE wicket_kind IS NOT NULL AND wicket_kind <> ''
GROUP BY wicket_kind
ORDER BY dismissals DESC;

-- 11. Runs in an over (top 30)
SELECT match_id, innings_number, over, SUM(runs_total) AS runs_in_over
FROM deliveries
GROUP BY match_id, innings_number, over
ORDER BY runs_in_over DESC
LIMIT 30;

-- 12. Bowler dot ball percentage (min 300 balls)
WITH balls AS (
  SELECT bowler, COUNT(*) AS balls_bowled,
         SUM(CASE WHEN runs_total=0 THEN 1 ELSE 0 END) AS dot_balls
  FROM deliveries
  GROUP BY bowler
)
SELECT bowler, dot_balls*100.0/balls_bowled AS dot_pct, balls_bowled
FROM balls
WHERE balls_bowled >= 300
ORDER BY dot_pct DESC
LIMIT 15;

-- 13. Boundary % for batsmen (min 300 balls)
WITH bf AS (
  SELECT batsman, COUNT(*) AS balls_faced,
         SUM(CASE WHEN runs_batsman IN (4,6) THEN 1 ELSE 0 END) AS boundaries
  FROM deliveries
  GROUP BY batsman
)
SELECT batsman, boundaries*100.0/balls_faced AS boundary_pct, balls_faced
FROM bf
WHERE balls_faced >= 300
ORDER BY boundary_pct DESC
LIMIT 15;

-- 14. Extras by type
SELECT extras_type, SUM(runs_extras) AS extras
FROM deliveries
WHERE extras_type IS NOT NULL AND extras_type <> ''
GROUP BY extras_type
ORDER BY extras DESC;

-- 15. Highest over totals
SELECT match_id, innings_number, over, SUM(runs_total) AS over_runs
FROM deliveries
GROUP BY match_id, innings_number, over
ORDER BY over_runs DESC
LIMIT 20;

-- 16. Runs in first over by batsman
SELECT batsman, SUM(runs_batsman) AS runs_in_first_over
FROM deliveries
WHERE over = 0
GROUP BY batsman
ORDER BY runs_in_first_over DESC
LIMIT 15;

-- 17. Maidens by bowler (heuristic)
WITH by_over AS (
  SELECT match_id, innings_number, over, bowler, SUM(runs_total) AS over_runs
  FROM deliveries
  GROUP BY match_id, innings_number, over, bowler
)
SELECT bowler, COUNT(*) AS maidens
FROM by_over
WHERE over_runs = 0
GROUP BY bowler
ORDER BY maidens DESC
LIMIT 15;

-- 18. Runs conceded per ball (min 300 balls)
WITH sums AS (
  SELECT bowler, COUNT(*) AS balls, SUM(runs_total) AS runs
  FROM deliveries
  GROUP BY bowler
)
SELECT bowler, runs*1.0/balls AS runs_per_ball, balls
FROM sums
WHERE balls >= 300
ORDER BY runs_per_ball ASC
LIMIT 20;

-- 19. Win% by team
WITH totals AS (
  SELECT team1 AS team FROM matches
  UNION ALL
  SELECT team2 AS team FROM matches
),
agg AS (
  SELECT t.team,
         SUM(CASE WHEN m.winner = t.team THEN 1 ELSE 0 END) AS wins,
         COUNT(*) AS played
  FROM totals t
  LEFT JOIN matches m ON (m.team1 = t.team OR m.team2 = t.team)
  GROUP BY t.team
)
SELECT team, wins*100.0/played AS win_pct, played
FROM agg
WHERE played >= 10
ORDER BY win_pct DESC;

-- 20. Player of the match leaders
SELECT player_of_match, COUNT(*) AS awards
FROM matches
WHERE player_of_match IS NOT NULL AND player_of_match <> ''
GROUP BY player_of_match
ORDER BY awards DESC
LIMIT 20;

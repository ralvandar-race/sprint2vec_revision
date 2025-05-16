-- Sprint Performance Analysis
SELECT 
    repository,
    COUNT(*) as total_sprints,
    AVG(plan_duration) as avg_duration,
    AVG(no_issue) as avg_issues,
    AVG(no_teammember) as avg_team_size,
    AVG(productivity) as avg_productivity,
    AVG(quality_impact) as avg_quality
FROM sprints
GROUP BY repository
ORDER BY avg_productivity DESC;

-- Correlation between team size and performance
SELECT 
    repository,
    ROUND(CORR(no_teammember, productivity), 3) as team_prod_corr,
    ROUND(CORR(no_teammember, quality_impact), 3) as team_qual_corr
FROM sprints
GROUP BY repository;

-- High performing sprints analysis
SELECT 
    repository,
    plan_duration,
    no_teammember,
    productivity,
    quality_impact
FROM sprints
WHERE productivity > (SELECT AVG(productivity) FROM sprints)
  AND quality_impact > (SELECT AVG(quality_impact) FROM sprints)
ORDER BY productivity DESC
LIMIT 10;
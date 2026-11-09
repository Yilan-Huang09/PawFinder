-- Report-ready PawFinder queries

USE pawfinder;

-- 1. Active lost-pet overview (view + joins + aggregate subqueries)
SELECT *
  FROM v_active_case_summary
 ORDER BY lost_time DESC;

-- 2. Ranked candidate clues for a case (window function view)
SELECT case_id, pet_name, match_rank, sighting_id, total_score,
       distance_km, review_status, match_reason
  FROM v_case_match_rankings
 WHERE case_id = 1
 ORDER BY match_rank;

-- 3. Number of cases and average match score by pet species
SELECT p.species,
       COUNT(DISTINCT lc.case_id) AS case_count,
       COUNT(csm.match_id) AS candidate_count,
       ROUND(AVG(csm.total_score), 2) AS average_match_score
  FROM pets AS p
  JOIN lost_cases AS lc ON lc.pet_id = p.pet_id
  LEFT JOIN case_sighting_matches AS csm ON csm.case_id = lc.case_id
 GROUP BY p.species
 ORDER BY case_count DESC, p.species;

-- 4. Users who have participated as both witnesses and volunteers
SELECT u.user_id, u.username,
       COUNT(DISTINCT s.sighting_id) AS sighting_count,
       COUNT(DISTINCT st.task_id) AS task_count
  FROM users AS u
  JOIN sightings AS s ON s.reporter_id = u.user_id
  JOIN search_tasks AS st ON st.volunteer_id = u.user_id
 GROUP BY u.user_id, u.username
 ORDER BY sighting_count + task_count DESC;

-- 5. Cases whose best candidate score is above the global average
SELECT lc.case_id, p.name AS pet_name, MAX(csm.total_score) AS best_score
  FROM lost_cases AS lc
  JOIN pets AS p ON p.pet_id = lc.pet_id
  JOIN case_sighting_matches AS csm ON csm.case_id = lc.case_id
 GROUP BY lc.case_id, p.name
HAVING MAX(csm.total_score) > (
  SELECT AVG(total_score) FROM case_sighting_matches
)
 ORDER BY best_score DESC;

-- 6. Search-task progress grouped by case
SELECT lc.case_id, p.name AS pet_name,
       COUNT(st.task_id) AS total_tasks,
       SUM(st.status = 'AVAILABLE') AS available_tasks,
       SUM(st.status IN ('CLAIMED', 'IN_PROGRESS')) AS active_tasks,
       SUM(st.status = 'COMPLETED') AS completed_tasks
  FROM lost_cases AS lc
  JOIN pets AS p ON p.pet_id = lc.pet_id
  LEFT JOIN search_areas AS sa ON sa.case_id = lc.case_id
  LEFT JOIN search_tasks AS st ON st.area_id = sa.area_id
 GROUP BY lc.case_id, p.name
 ORDER BY lc.case_id;

-- 7. Unread message center query
SELECT n.notification_id, n.type, n.title, n.content, n.created_at
  FROM notifications AS n
 WHERE n.user_id = 2
   AND n.is_read = FALSE
 ORDER BY n.created_at DESC;

-- 8. Reunion statistics and average search duration in hours
SELECT COUNT(*) AS reunion_count,
       ROUND(AVG(TIMESTAMPDIFF(MINUTE, lc.lost_time, rr.reunion_time)) / 60, 2)
         AS average_search_hours
  FROM reunion_records AS rr
  JOIN lost_cases AS lc ON lc.case_id = rr.case_id;

-- 9. Explain the active-case index path
EXPLAIN
SELECT case_id, pet_id, lost_time, address
  FROM lost_cases
 WHERE status = 'SEARCHING'
 ORDER BY lost_time DESC
 LIMIT 20;

-- 10. Explain the match-ranking index path
EXPLAIN
SELECT match_id, sighting_id, total_score, review_status
  FROM case_sighting_matches
 WHERE case_id = 1
   AND review_status = 'PENDING'
 ORDER BY total_score DESC;

-- Verifies deterministic seed data.
-- Run after schema.sql, objects.sql, and seed.sql.

USE pawfinder;

DELIMITER $$

DROP PROCEDURE IF EXISTS test_seed_expectations$$

CREATE PROCEDURE test_seed_expectations()
BEGIN
  DECLARE actual_count INT DEFAULT 0;
  DECLARE expected_count INT DEFAULT 0;
  DECLARE inconsistent_count INT DEFAULT 0;

  SELECT COUNT(*) INTO actual_count FROM users;
  IF actual_count <> 9 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Seed test failed: expected 9 users';
  END IF;

  SELECT COUNT(*) INTO actual_count FROM pets;
  IF actual_count <> 12 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Seed test failed: expected 12 pets';
  END IF;

  SELECT COUNT(*) INTO actual_count FROM lost_cases;
  IF actual_count <> 6 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Seed test failed: expected 6 lost cases';
  END IF;

  SELECT COUNT(*) INTO actual_count FROM sightings;
  IF actual_count <> 15 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Seed test failed: expected 15 sightings';
  END IF;

  SELECT COUNT(*) INTO actual_count FROM case_sighting_matches;
  IF actual_count <> 12 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Seed test failed: expected 12 matches';
  END IF;

  SELECT COUNT(*) INTO actual_count FROM search_areas;
  IF actual_count <> 8 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Seed test failed: expected 8 search areas';
  END IF;

  SELECT COUNT(*) INTO actual_count FROM search_tasks;
  IF actual_count <> 8 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Seed test failed: expected 8 search tasks';
  END IF;

  SELECT COUNT(*) INTO actual_count FROM reunion_records;
  IF actual_count <> 1 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Seed test failed: expected one reunion record';
  END IF;

  SELECT COUNT(*) INTO actual_count
    FROM lost_cases
   WHERE status = 'SEARCHING';
  IF actual_count <> 4 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Seed test failed: expected four searching cases';
  END IF;

  SELECT COUNT(*) INTO expected_count
    FROM case_sighting_matches
   WHERE total_score >= 75;
  SELECT COUNT(*) INTO actual_count
    FROM notifications
   WHERE type = 'HIGH_MATCH';
  IF actual_count <> expected_count THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Seed test failed: high-match notifications do not match high scores';
  END IF;

  SELECT COUNT(*) INTO inconsistent_count
    FROM case_sighting_matches
   WHERE ABS(total_score - (
     appearance_score * 0.50 + distance_score * 0.30 + time_score * 0.20
   )) > 0.01;
  IF inconsistent_count <> 0 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Seed test failed: weighted match totals are inconsistent';
  END IF;

  SELECT COUNT(*) INTO actual_count FROM v_active_case_summary;
  IF actual_count <> 4 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Seed test failed: active-case view count is incorrect';
  END IF;

  SELECT COUNT(*) INTO actual_count
    FROM v_case_match_rankings
   WHERE match_rank = 1;
  IF actual_count <> 6 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Seed test failed: each case should have a top-ranked match';
  END IF;

  SELECT COUNT(*) INTO actual_count
    FROM users
   WHERE username = 'admin'
     AND role = 'ADMIN'
     AND status = 'ACTIVE';
  IF actual_count <> 1 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Seed test failed: admin account missing';
  END IF;

  SELECT 'PASS: seed data expectations verified' AS result;
END$$

DELIMITER ;

CALL test_seed_expectations();
DROP PROCEDURE test_seed_expectations;

-- Verifies PawFinder functions, views, and triggers.
-- Run after schema.sql and objects.sql.

USE pawfinder;

DELIMITER $$

DROP PROCEDURE IF EXISTS test_database_objects$$

CREATE PROCEDURE test_database_objects()
BEGIN
  DECLARE actual_count INT DEFAULT 0;
  DECLARE rejected BOOLEAN DEFAULT FALSE;
  DECLARE distance_value DECIMAL(10, 3);
  DECLARE owner_id BIGINT UNSIGNED;
  DECLARE reporter_id BIGINT UNSIGNED;
  DECLARE pet_id_value BIGINT UNSIGNED;
  DECLARE case_id_value BIGINT UNSIGNED;
  DECLARE sighting_id_value BIGINT UNSIGNED;
  DECLARE cover_value BOOLEAN;
  DECLARE notification_count INT DEFAULT 0;
  DECLARE view_count INT DEFAULT 0;
  DECLARE closed_value DATETIME;

  DECLARE EXIT HANDLER FOR SQLEXCEPTION
  BEGIN
    ROLLBACK;
    RESIGNAL;
  END;

  SELECT COUNT(*) INTO actual_count
    FROM information_schema.views
   WHERE table_schema = DATABASE()
     AND table_name IN (
       'v_active_case_summary',
       'v_case_match_rankings',
       'v_search_task_progress'
     );
  IF actual_count <> 3 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Object test failed: expected three views';
  END IF;

  SELECT COUNT(*) INTO actual_count
    FROM information_schema.routines
   WHERE routine_schema = DATABASE()
     AND routine_name IN ('fn_distance_km', 'sp_confirm_reunion');
  IF actual_count <> 2 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Object test failed: expected function and procedure';
  END IF;

  SELECT COUNT(*) INTO actual_count
    FROM information_schema.triggers
   WHERE trigger_schema = DATABASE();
  IF actual_count < 17 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Object test failed: expected validation and business triggers';
  END IF;

  SET distance_value = fn_distance_km(30.2741000, 120.1551000, 30.2741000, 120.1551000);
  IF distance_value <> 0.000 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Object test failed: identical points must have zero distance';
  END IF;

  START TRANSACTION;

  INSERT INTO users (username, password_hash, phone)
  VALUES
    ('__objects_owner__', 'test-hash', '19800000001'),
    ('__objects_reporter__', 'test-hash', '19800000002');
  SELECT user_id INTO owner_id FROM users WHERE username = '__objects_owner__';
  SELECT user_id INTO reporter_id FROM users WHERE username = '__objects_reporter__';

  SET rejected = FALSE;
  BEGIN
    DECLARE CONTINUE HANDLER FOR SQLEXCEPTION SET rejected = TRUE;
    INSERT INTO users (username, password_hash, role)
    VALUES ('__objects_invalid_role__', 'test-hash', 'OWNER');
  END;
  IF rejected = FALSE THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Object test failed: invalid role was accepted';
  END IF;

  INSERT INTO pets (
    owner_id, name, species, breed, primary_color, gender, size
  ) VALUES (
    owner_id, '对象测试宠物', 'DOG', 'Border Collie', 'BLACK', 'FEMALE', 'MEDIUM'
  );
  SET pet_id_value = LAST_INSERT_ID();

  INSERT INTO pet_photos (pet_id, photo_url, is_cover)
  VALUES (pet_id_value, 'objects/pet-first.jpg', FALSE);
  SELECT is_cover INTO cover_value
    FROM pet_photos
   WHERE pet_id = pet_id_value
   ORDER BY photo_id
   LIMIT 1;
  IF cover_value <> TRUE THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Object test failed: first pet photo was not set as cover';
  END IF;

  INSERT INTO lost_cases (
    pet_id, publisher_id, lost_time, latitude, longitude, address, description
  ) VALUES (
    pet_id_value, owner_id, '2026-11-01 08:00:00', 30.2741000, 120.1551000,
    '对象测试地址', '对象测试走失事件'
  );
  SET case_id_value = LAST_INSERT_ID();

  SET rejected = FALSE;
  BEGIN
    DECLARE CONTINUE HANDLER FOR SQLEXCEPTION SET rejected = TRUE;
    INSERT INTO sightings (
      reporter_id, species, primary_color, seen_time,
      latitude, longitude, address, confidence
    ) VALUES (
      reporter_id, 'DOG', 'BLACK', '2099-01-01 00:00:00',
      30.2741000, 120.1551000, '未来目击地址', 3
    );
  END;
  IF rejected = FALSE THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Object test failed: future sighting was accepted';
  END IF;

  INSERT INTO sightings (
    reporter_id, species, breed_guess, primary_color, gender_guess, size_guess,
    seen_time, latitude, longitude, address, confidence, description
  ) VALUES (
    reporter_id, 'DOG', 'Border Collie', 'BLACK', 'FEMALE', 'MEDIUM',
    '2026-11-01 09:00:00', 30.2750000, 120.1560000,
    '对象测试目击地址', 5, '对象测试线索'
  );
  SET sighting_id_value = LAST_INSERT_ID();

  SET rejected = FALSE;
  BEGIN
    DECLARE CONTINUE HANDLER FOR SQLEXCEPTION SET rejected = TRUE;
    INSERT INTO case_sighting_matches (
      case_id, sighting_id, appearance_score, distance_score, time_score,
      total_score, distance_km, match_reason
    ) VALUES (
      case_id_value, sighting_id_value, 101, 80, 80, 90, 0.200, '非法分数'
    );
  END;
  IF rejected = FALSE THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Object test failed: invalid match score was accepted';
  END IF;

  INSERT INTO case_sighting_matches (
    case_id, sighting_id, appearance_score, distance_score, time_score,
    total_score, distance_km, match_reason
  ) VALUES (
    case_id_value, sighting_id_value, 95, 95, 90, 94.00, 0.200, '高匹配对象测试'
  );

  SELECT COUNT(*) INTO notification_count
    FROM notifications
   WHERE user_id = owner_id
     AND related_case_id = case_id_value
     AND type = 'HIGH_MATCH';
  IF notification_count <> 1 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Object test failed: high match notification missing';
  END IF;

  SELECT COUNT(*) INTO view_count
    FROM v_case_match_rankings
   WHERE case_id = case_id_value
     AND match_rank = 1;
  IF view_count <> 1 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Object test failed: match ranking view missing data';
  END IF;

  UPDATE lost_cases SET status = 'CLOSED' WHERE case_id = case_id_value;
  SELECT closed_at INTO closed_value FROM lost_cases WHERE case_id = case_id_value;
  IF closed_value IS NULL THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Object test failed: closed_at was not populated';
  END IF;

  ROLLBACK;

  SELECT 'PASS: database objects verified' AS result;
END$$

DELIMITER ;

CALL test_database_objects();
DROP PROCEDURE test_database_objects;

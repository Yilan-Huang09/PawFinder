-- Verifies PawFinder table structure and cross-version constraints.
-- Run after database/schema.sql.

USE pawfinder;

DELIMITER $$

DROP PROCEDURE IF EXISTS test_schema_constraints$$

CREATE PROCEDURE test_schema_constraints()
BEGIN
  DECLARE actual_count INT DEFAULT 0;
  DECLARE actual_fk_count INT DEFAULT 0;
  DECLARE rejected BOOLEAN DEFAULT FALSE;
  DECLARE owner_id BIGINT UNSIGNED;
  DECLARE reporter_id BIGINT UNSIGNED;
  DECLARE volunteer_id BIGINT UNSIGNED;
  DECLARE pet_id_value BIGINT UNSIGNED;
  DECLARE case_id_value BIGINT UNSIGNED;
  DECLARE sighting_id_value BIGINT UNSIGNED;
  DECLARE area_id_value BIGINT UNSIGNED;

  DECLARE EXIT HANDLER FOR SQLEXCEPTION
  BEGIN
    ROLLBACK;
    RESIGNAL;
  END;

  SELECT COUNT(*)
    INTO actual_count
    FROM information_schema.tables
   WHERE table_schema = DATABASE()
     AND table_type = 'BASE TABLE'
     AND table_name IN (
       'users', 'pets', 'pet_photos', 'lost_cases', 'sightings',
       'sighting_photos', 'case_sighting_matches', 'search_areas',
       'search_tasks', 'reunion_records', 'notifications'
     );

  IF actual_count <> 11 THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Schema test failed: expected 11 core tables';
  END IF;

  SELECT COUNT(*)
    INTO actual_fk_count
    FROM information_schema.table_constraints
   WHERE constraint_schema = DATABASE()
     AND constraint_type = 'FOREIGN KEY';

  IF actual_fk_count < 20 THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Schema test failed: expected at least 20 foreign keys';
  END IF;

  START TRANSACTION;

  INSERT INTO users (username, password_hash, phone, email)
  VALUES
    ('__schema_owner__', 'test-hash', '19900000001', 'schema-owner@example.test'),
    ('__schema_reporter__', 'test-hash', '19900000002', 'schema-reporter@example.test'),
    ('__schema_volunteer__', 'test-hash', '19900000003', 'schema-volunteer@example.test');

  SELECT user_id INTO owner_id FROM users WHERE username = '__schema_owner__';
  SELECT user_id INTO reporter_id FROM users WHERE username = '__schema_reporter__';
  SELECT user_id INTO volunteer_id FROM users WHERE username = '__schema_volunteer__';

  SET rejected = FALSE;
  BEGIN
    DECLARE CONTINUE HANDLER FOR SQLEXCEPTION SET rejected = TRUE;
    INSERT INTO users (username, password_hash)
    VALUES ('__schema_owner__', 'test-hash');
  END;
  IF rejected = FALSE THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Schema test failed: duplicate username was accepted';
  END IF;

  INSERT INTO pets (
    owner_id, name, species, breed, primary_color, gender, size, distinctive_features
  ) VALUES (
    owner_id, '结构测试宠物', 'DOG', 'Border Collie', 'BLACK', 'FEMALE', 'MEDIUM', '胸口白毛'
  );
  SET pet_id_value = LAST_INSERT_ID();

  INSERT INTO lost_cases (
    pet_id, publisher_id, lost_time, latitude, longitude, address, description
  ) VALUES (
    pet_id_value, owner_id, '2026-11-01 08:00:00', 30.2741000, 120.1551000,
    '结构测试地址', '结构测试事件'
  );
  SET case_id_value = LAST_INSERT_ID();

  INSERT INTO sightings (
    reporter_id, species, breed_guess, primary_color, gender_guess, size_guess,
    seen_time, latitude, longitude, address, confidence, description
  ) VALUES (
    reporter_id, 'DOG', 'Border Collie', 'BLACK', 'FEMALE', 'MEDIUM',
    '2026-11-01 10:00:00', 30.2760000, 120.1570000,
    '结构测试目击地址', 4, '结构测试线索'
  );
  SET sighting_id_value = LAST_INSERT_ID();

  INSERT INTO case_sighting_matches (
    case_id, sighting_id, appearance_score, distance_score, time_score,
    total_score, distance_km, match_reason
  ) VALUES (
    case_id_value, sighting_id_value, 90, 95, 90, 91.50, 0.300, '结构测试匹配'
  );

  SET rejected = FALSE;
  BEGIN
    DECLARE CONTINUE HANDLER FOR SQLEXCEPTION SET rejected = TRUE;
    INSERT INTO case_sighting_matches (
      case_id, sighting_id, appearance_score, distance_score, time_score,
      total_score, distance_km, match_reason
    ) VALUES (
      case_id_value, sighting_id_value, 80, 80, 80, 80, 0.300, '重复匹配'
    );
  END;
  IF rejected = FALSE THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Schema test failed: duplicate case-sighting match was accepted';
  END IF;

  INSERT INTO search_areas (
    case_id, created_by, area_name, center_latitude, center_longitude, radius_meters
  ) VALUES (
    case_id_value, owner_id, '结构测试区域', 30.2750000, 120.1560000, 1000
  );
  SET area_id_value = LAST_INSERT_ID();

  INSERT INTO search_tasks (area_id, volunteer_id, status, accepted_at)
  VALUES (area_id_value, volunteer_id, 'CLAIMED', CURRENT_TIMESTAMP);

  SET rejected = FALSE;
  BEGIN
    DECLARE CONTINUE HANDLER FOR SQLEXCEPTION SET rejected = TRUE;
    INSERT INTO search_tasks (area_id, status)
    VALUES (area_id_value, 'AVAILABLE');
  END;
  IF rejected = FALSE THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Schema test failed: duplicate area task was accepted';
  END IF;

  INSERT INTO reunion_records (
    case_id, finder_id, confirmed_by, reunion_time, latitude, longitude, address
  ) VALUES (
    case_id_value, reporter_id, owner_id, '2026-11-01 18:00:00',
    30.2780000, 120.1600000, '结构测试寻回地址'
  );

  SET rejected = FALSE;
  BEGIN
    DECLARE CONTINUE HANDLER FOR SQLEXCEPTION SET rejected = TRUE;
    INSERT INTO reunion_records (
      case_id, finder_id, confirmed_by, reunion_time, address
    ) VALUES (
      case_id_value, reporter_id, owner_id, '2026-11-01 19:00:00', '重复寻回地址'
    );
  END;
  IF rejected = FALSE THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Schema test failed: duplicate reunion was accepted';
  END IF;

  ROLLBACK;

  SELECT 'PASS: core schema constraints verified' AS result;
END$$

DELIMITER ;

CALL test_schema_constraints();
DROP PROCEDURE test_schema_constraints;

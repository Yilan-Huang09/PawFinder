-- Verifies sp_confirm_reunion success, authorization, and duplicate protection.
-- This test creates committed fixtures because the procedure owns its transaction,
-- then removes them in dependency order.

USE pawfinder;

DELIMITER $$

DROP PROCEDURE IF EXISTS test_reunion_transaction$$

CREATE PROCEDURE test_reunion_transaction()
BEGIN
  DECLARE rejected BOOLEAN DEFAULT FALSE;
  DECLARE owner_id BIGINT UNSIGNED;
  DECLARE finder_id BIGINT UNSIGNED;
  DECLARE stranger_id BIGINT UNSIGNED;
  DECLARE pet_id_value BIGINT UNSIGNED;
  DECLARE case_id_value BIGINT UNSIGNED;
  DECLARE second_case_id BIGINT UNSIGNED;
  DECLARE area_id_value BIGINT UNSIGNED;
  DECLARE second_area_id BIGINT UNSIGNED;
  DECLARE actual_count INT DEFAULT 0;
  DECLARE actual_status VARCHAR(20);
  DECLARE actual_closed DATETIME;

  INSERT INTO users (username, password_hash, phone)
  VALUES
    ('__reunion_owner__', 'test-hash', '19700000001'),
    ('__reunion_finder__', 'test-hash', '19700000002'),
    ('__reunion_stranger__', 'test-hash', '19700000003');

  SELECT user_id INTO owner_id FROM users WHERE username = '__reunion_owner__';
  SELECT user_id INTO finder_id FROM users WHERE username = '__reunion_finder__';
  SELECT user_id INTO stranger_id FROM users WHERE username = '__reunion_stranger__';

  INSERT INTO pets (owner_id, name, species, primary_color, gender, size)
  VALUES (owner_id, '事务测试宠物', 'CAT', 'ORANGE', 'MALE', 'MEDIUM');
  SET pet_id_value = LAST_INSERT_ID();

  INSERT INTO lost_cases (
    pet_id, publisher_id, lost_time, latitude, longitude, address
  ) VALUES
    (pet_id_value, owner_id, '2026-11-01 08:00:00', 30.2741000, 120.1551000, '事务测试地址一'),
    (pet_id_value, owner_id, '2026-11-02 08:00:00', 30.2841000, 120.1651000, '事务测试地址二');

  SELECT MIN(case_id), MAX(case_id)
    INTO case_id_value, second_case_id
    FROM lost_cases
   WHERE pet_id = pet_id_value;

  INSERT INTO search_areas (
    case_id, created_by, area_name, center_latitude, center_longitude, radius_meters
  ) VALUES
    (case_id_value, owner_id, '事务区域一', 30.2750000, 120.1560000, 800),
    (second_case_id, owner_id, '事务区域二', 30.2850000, 120.1660000, 900);

  SELECT MIN(area_id), MAX(area_id)
    INTO area_id_value, second_area_id
    FROM search_areas
   WHERE case_id IN (case_id_value, second_case_id);

  INSERT INTO search_tasks (area_id, volunteer_id, status, accepted_at)
  VALUES
    (area_id_value, finder_id, 'IN_PROGRESS', CURRENT_TIMESTAMP),
    (second_area_id, NULL, 'AVAILABLE', NULL);

  CALL sp_confirm_reunion(
    case_id_value,
    finder_id,
    owner_id,
    '2026-11-03 18:00:00',
    30.2780000,
    120.1600000,
    '事务测试寻回地址',
    '志愿者发现',
    '状态良好'
  );

  SELECT status, closed_at
    INTO actual_status, actual_closed
    FROM lost_cases
   WHERE case_id = case_id_value;
  IF actual_status <> 'REUNITED' OR actual_closed IS NULL THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Reunion test failed: case was not archived';
  END IF;

  SELECT status INTO actual_status FROM search_tasks WHERE area_id = area_id_value;
  IF actual_status <> 'CANCELLED' THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Reunion test failed: active task was not cancelled';
  END IF;

  SELECT COUNT(*) INTO actual_count
    FROM notifications
   WHERE user_id = owner_id
     AND related_case_id = case_id_value
     AND type = 'REUNION';
  IF actual_count <> 1 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Reunion test failed: reunion notification missing';
  END IF;

  SET rejected = FALSE;
  BEGIN
    DECLARE CONTINUE HANDLER FOR SQLEXCEPTION SET rejected = TRUE;
    CALL sp_confirm_reunion(
      case_id_value, finder_id, owner_id, '2026-11-03 19:00:00',
      NULL, NULL, '重复寻回地址', '重复调用', NULL
    );
  END;
  IF rejected = FALSE THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Reunion test failed: duplicate confirmation was accepted';
  END IF;

  SELECT COUNT(*) INTO actual_count
    FROM reunion_records
   WHERE case_id = case_id_value;
  IF actual_count <> 1 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Reunion test failed: duplicate call changed reunion count';
  END IF;

  SET rejected = FALSE;
  BEGIN
    DECLARE CONTINUE HANDLER FOR SQLEXCEPTION SET rejected = TRUE;
    CALL sp_confirm_reunion(
      second_case_id, finder_id, stranger_id, '2026-11-03 19:30:00',
      NULL, NULL, '越权寻回地址', '越权调用', NULL
    );
  END;
  IF rejected = FALSE THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Reunion test failed: unauthorized confirmation was accepted';
  END IF;

  SELECT COUNT(*) INTO actual_count
    FROM reunion_records
   WHERE case_id = second_case_id;
  IF actual_count <> 0 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Reunion test failed: unauthorized call wrote a record';
  END IF;

  DELETE FROM notifications WHERE related_case_id IN (case_id_value, second_case_id);
  DELETE FROM reunion_records WHERE case_id IN (case_id_value, second_case_id);
  DELETE FROM search_tasks WHERE area_id IN (area_id_value, second_area_id);
  DELETE FROM search_areas WHERE area_id IN (area_id_value, second_area_id);
  DELETE FROM lost_cases WHERE case_id IN (case_id_value, second_case_id);
  DELETE FROM pets WHERE pet_id = pet_id_value;
  DELETE FROM users WHERE user_id IN (owner_id, finder_id, stranger_id);

  SELECT 'PASS: reunion transaction verified' AS result;
END$$

DELIMITER ;

CALL test_reunion_transaction();
DROP PROCEDURE test_reunion_transaction;

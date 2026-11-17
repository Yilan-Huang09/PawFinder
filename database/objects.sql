-- PawFinder database-side objects
-- Run after schema.sql.

USE pawfinder;

SET NAMES utf8mb4;

DROP VIEW IF EXISTS v_search_task_progress;
DROP VIEW IF EXISTS v_case_match_rankings;
DROP VIEW IF EXISTS v_active_case_summary;

DROP TRIGGER IF EXISTS trg_notifications_validate_bu;
DROP TRIGGER IF EXISTS trg_notifications_validate_bi;
DROP TRIGGER IF EXISTS trg_reunion_records_validate_bi;
DROP TRIGGER IF EXISTS trg_search_tasks_validate_bu;
DROP TRIGGER IF EXISTS trg_search_tasks_validate_bi;
DROP TRIGGER IF EXISTS trg_search_areas_validate_bu;
DROP TRIGGER IF EXISTS trg_search_areas_validate_bi;
DROP TRIGGER IF EXISTS trg_match_high_score_notify;
DROP TRIGGER IF EXISTS trg_matches_validate_bu;
DROP TRIGGER IF EXISTS trg_matches_validate_bi;
DROP TRIGGER IF EXISTS trg_sightings_validate_bu;
DROP TRIGGER IF EXISTS trg_sightings_validate_bi;
DROP TRIGGER IF EXISTS trg_case_closed_at;
DROP TRIGGER IF EXISTS trg_lost_cases_validate_bi;
DROP TRIGGER IF EXISTS trg_pet_photo_first_cover;
DROP TRIGGER IF EXISTS trg_users_validate_bu;
DROP TRIGGER IF EXISTS trg_users_validate_bi;

DROP PROCEDURE IF EXISTS sp_confirm_reunion;
DROP FUNCTION IF EXISTS fn_distance_km;

DELIMITER $$

CREATE FUNCTION fn_distance_km(
  p_latitude_1 DECIMAL(10, 7),
  p_longitude_1 DECIMAL(10, 7),
  p_latitude_2 DECIMAL(10, 7),
  p_longitude_2 DECIMAL(10, 7)
)
RETURNS DECIMAL(10, 3)
DETERMINISTIC
NO SQL
BEGIN
  DECLARE v_haversine DOUBLE;

  IF p_latitude_1 IS NULL OR p_longitude_1 IS NULL
     OR p_latitude_2 IS NULL OR p_longitude_2 IS NULL THEN
    RETURN NULL;
  END IF;

  SET v_haversine =
    POWER(SIN(RADIANS(p_latitude_2 - p_latitude_1) / 2), 2)
    + COS(RADIANS(p_latitude_1))
    * COS(RADIANS(p_latitude_2))
    * POWER(SIN(RADIANS(p_longitude_2 - p_longitude_1) / 2), 2);

  SET v_haversine = LEAST(1, GREATEST(0, v_haversine));

  RETURN ROUND(6371.0088 * 2 * ASIN(SQRT(v_haversine)), 3);
END$$

CREATE TRIGGER trg_users_validate_bi
BEFORE INSERT ON users
FOR EACH ROW
BEGIN
  IF NEW.role NOT IN ('USER', 'ADMIN') THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid user role';
  END IF;
  IF NEW.status NOT IN ('ACTIVE', 'DISABLED') THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid user status';
  END IF;
END$$

CREATE TRIGGER trg_users_validate_bu
BEFORE UPDATE ON users
FOR EACH ROW
BEGIN
  IF NEW.role NOT IN ('USER', 'ADMIN') THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid user role';
  END IF;
  IF NEW.status NOT IN ('ACTIVE', 'DISABLED') THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid user status';
  END IF;
END$$

CREATE TRIGGER trg_pet_photo_first_cover
BEFORE INSERT ON pet_photos
FOR EACH ROW
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pet_photos WHERE pet_id = NEW.pet_id LIMIT 1
  ) THEN
    SET NEW.is_cover = TRUE;
  END IF;
END$$

CREATE TRIGGER trg_lost_cases_validate_bi
BEFORE INSERT ON lost_cases
FOR EACH ROW
BEGIN
  IF NEW.latitude NOT BETWEEN -90 AND 90
     OR NEW.longitude NOT BETWEEN -180 AND 180 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid lost-case coordinates';
  END IF;
  IF NEW.status NOT IN ('SEARCHING', 'REUNITED', 'CLOSED') THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid lost-case status';
  END IF;
  IF NEW.lost_time > CURRENT_TIMESTAMP THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Lost time cannot be in the future';
  END IF;
  IF NEW.status <> 'SEARCHING' AND NEW.closed_at IS NULL THEN
    SET NEW.closed_at = CURRENT_TIMESTAMP;
  END IF;
END$$

CREATE TRIGGER trg_case_closed_at
BEFORE UPDATE ON lost_cases
FOR EACH ROW
BEGIN
  IF NEW.latitude NOT BETWEEN -90 AND 90
     OR NEW.longitude NOT BETWEEN -180 AND 180 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid lost-case coordinates';
  END IF;
  IF NEW.status NOT IN ('SEARCHING', 'REUNITED', 'CLOSED') THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid lost-case status';
  END IF;
  IF NEW.lost_time > CURRENT_TIMESTAMP THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Lost time cannot be in the future';
  END IF;
  IF OLD.status = 'SEARCHING' AND NEW.status <> 'SEARCHING' THEN
    SET NEW.closed_at = COALESCE(NEW.closed_at, CURRENT_TIMESTAMP);
  ELSEIF OLD.status <> 'SEARCHING' AND NEW.status = 'SEARCHING' THEN
    SET NEW.closed_at = NULL;
  END IF;
END$$

CREATE TRIGGER trg_sightings_validate_bi
BEFORE INSERT ON sightings
FOR EACH ROW
BEGIN
  IF NEW.latitude NOT BETWEEN -90 AND 90
     OR NEW.longitude NOT BETWEEN -180 AND 180 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid sighting coordinates';
  END IF;
  IF NEW.confidence NOT BETWEEN 1 AND 5 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Sighting confidence must be between 1 and 5';
  END IF;
  IF NEW.status NOT IN ('ACTIVE', 'HIDDEN', 'INVALID') THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid sighting status';
  END IF;
  IF NEW.seen_time > CURRENT_TIMESTAMP THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Seen time cannot be in the future';
  END IF;
END$$

CREATE TRIGGER trg_sightings_validate_bu
BEFORE UPDATE ON sightings
FOR EACH ROW
BEGIN
  IF NEW.latitude NOT BETWEEN -90 AND 90
     OR NEW.longitude NOT BETWEEN -180 AND 180 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid sighting coordinates';
  END IF;
  IF NEW.confidence NOT BETWEEN 1 AND 5 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Sighting confidence must be between 1 and 5';
  END IF;
  IF NEW.status NOT IN ('ACTIVE', 'HIDDEN', 'INVALID') THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid sighting status';
  END IF;
  IF NEW.seen_time > CURRENT_TIMESTAMP THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Seen time cannot be in the future';
  END IF;
END$$

CREATE TRIGGER trg_matches_validate_bi
BEFORE INSERT ON case_sighting_matches
FOR EACH ROW
BEGIN
  IF NEW.appearance_score NOT BETWEEN 0 AND 100
     OR NEW.distance_score NOT BETWEEN 0 AND 100
     OR NEW.time_score NOT BETWEEN 0 AND 100
     OR NEW.total_score NOT BETWEEN 0 AND 100
     OR NEW.distance_km < 0 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid match score or distance';
  END IF;
  IF NEW.review_status NOT IN ('PENDING', 'CONFIRMED', 'REJECTED') THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid match review status';
  END IF;
END$$

CREATE TRIGGER trg_matches_validate_bu
BEFORE UPDATE ON case_sighting_matches
FOR EACH ROW
BEGIN
  IF NEW.appearance_score NOT BETWEEN 0 AND 100
     OR NEW.distance_score NOT BETWEEN 0 AND 100
     OR NEW.time_score NOT BETWEEN 0 AND 100
     OR NEW.total_score NOT BETWEEN 0 AND 100
     OR NEW.distance_km < 0 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid match score or distance';
  END IF;
  IF NEW.review_status NOT IN ('PENDING', 'CONFIRMED', 'REJECTED') THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid match review status';
  END IF;
END$$

CREATE TRIGGER trg_match_high_score_notify
AFTER INSERT ON case_sighting_matches
FOR EACH ROW
BEGIN
  DECLARE v_owner_id BIGINT UNSIGNED;
  DECLARE v_pet_name VARCHAR(80);

  IF NEW.total_score >= 75 THEN
    SELECT p.owner_id, p.name
      INTO v_owner_id, v_pet_name
      FROM lost_cases AS lc
      JOIN pets AS p ON p.pet_id = lc.pet_id
     WHERE lc.case_id = NEW.case_id;

    INSERT INTO notifications (
      user_id, type, title, content, related_case_id, related_match_id
    ) VALUES (
      v_owner_id,
      'HIGH_MATCH',
      '发现高匹配线索',
      CONCAT('宠物“', v_pet_name, '”出现一条 ', FORMAT(NEW.total_score, 1), ' 分的候选线索。'),
      NEW.case_id,
      NEW.match_id
    );
  END IF;
END$$

CREATE TRIGGER trg_search_areas_validate_bi
BEFORE INSERT ON search_areas
FOR EACH ROW
BEGIN
  IF NEW.center_latitude NOT BETWEEN -90 AND 90
     OR NEW.center_longitude NOT BETWEEN -180 AND 180 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid search-area coordinates';
  END IF;
  IF NEW.radius_meters NOT BETWEEN 1 AND 20000 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Search-area radius must be between 1 and 20000 meters';
  END IF;
  IF NEW.status NOT IN ('OPEN', 'CLOSED') THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid search-area status';
  END IF;
END$$

CREATE TRIGGER trg_search_areas_validate_bu
BEFORE UPDATE ON search_areas
FOR EACH ROW
BEGIN
  IF NEW.center_latitude NOT BETWEEN -90 AND 90
     OR NEW.center_longitude NOT BETWEEN -180 AND 180 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid search-area coordinates';
  END IF;
  IF NEW.radius_meters NOT BETWEEN 1 AND 20000 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Search-area radius must be between 1 and 20000 meters';
  END IF;
  IF NEW.status NOT IN ('OPEN', 'CLOSED') THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid search-area status';
  END IF;
END$$

CREATE TRIGGER trg_search_tasks_validate_bi
BEFORE INSERT ON search_tasks
FOR EACH ROW
BEGIN
  IF NEW.status NOT IN ('AVAILABLE', 'CLAIMED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED') THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid search-task status';
  END IF;
  IF NEW.status = 'AVAILABLE' AND NEW.volunteer_id IS NOT NULL THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Available task cannot have a volunteer';
  END IF;
  IF NEW.status IN ('CLAIMED', 'IN_PROGRESS', 'COMPLETED') AND NEW.volunteer_id IS NULL THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Assigned task requires a volunteer';
  END IF;
END$$

CREATE TRIGGER trg_search_tasks_validate_bu
BEFORE UPDATE ON search_tasks
FOR EACH ROW
BEGIN
  IF NEW.status NOT IN ('AVAILABLE', 'CLAIMED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED') THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid search-task status';
  END IF;
  IF NEW.status = 'AVAILABLE' AND NEW.volunteer_id IS NOT NULL THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Available task cannot have a volunteer';
  END IF;
  IF NEW.status IN ('CLAIMED', 'IN_PROGRESS', 'COMPLETED') AND NEW.volunteer_id IS NULL THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Assigned task requires a volunteer';
  END IF;
END$$

CREATE TRIGGER trg_reunion_records_validate_bi
BEFORE INSERT ON reunion_records
FOR EACH ROW
BEGIN
  IF NEW.latitude IS NOT NULL AND NEW.latitude NOT BETWEEN -90 AND 90 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid reunion latitude';
  END IF;
  IF NEW.longitude IS NOT NULL AND NEW.longitude NOT BETWEEN -180 AND 180 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid reunion longitude';
  END IF;
  IF NEW.reunion_time > CURRENT_TIMESTAMP THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Reunion time cannot be in the future';
  END IF;
END$$

CREATE TRIGGER trg_notifications_validate_bi
BEFORE INSERT ON notifications
FOR EACH ROW
BEGIN
  IF NEW.type NOT IN ('HIGH_MATCH', 'TASK_STATUS', 'REUNION', 'SYSTEM') THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid notification type';
  END IF;
  IF (NEW.is_read = FALSE AND NEW.read_at IS NOT NULL)
     OR (NEW.is_read = TRUE AND NEW.read_at IS NULL) THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Notification read state is inconsistent';
  END IF;
END$$

CREATE TRIGGER trg_notifications_validate_bu
BEFORE UPDATE ON notifications
FOR EACH ROW
BEGIN
  IF NEW.type NOT IN ('HIGH_MATCH', 'TASK_STATUS', 'REUNION', 'SYSTEM') THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid notification type';
  END IF;
  IF (NEW.is_read = FALSE AND NEW.read_at IS NOT NULL)
     OR (NEW.is_read = TRUE AND NEW.read_at IS NULL) THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Notification read state is inconsistent';
  END IF;
END$$

CREATE PROCEDURE sp_confirm_reunion(
  IN p_case_id BIGINT UNSIGNED,
  IN p_finder_id BIGINT UNSIGNED,
  IN p_confirmed_by BIGINT UNSIGNED,
  IN p_reunion_time DATETIME,
  IN p_latitude DECIMAL(10, 7),
  IN p_longitude DECIMAL(10, 7),
  IN p_address VARCHAR(255),
  IN p_method VARCHAR(100),
  IN p_note TEXT
)
SQL SECURITY INVOKER
BEGIN
  DECLARE v_status VARCHAR(20);
  DECLARE v_owner_id BIGINT UNSIGNED;
  DECLARE v_publisher_id BIGINT UNSIGNED;
  DECLARE v_pet_name VARCHAR(80);

  DECLARE EXIT HANDLER FOR SQLEXCEPTION
  BEGIN
    ROLLBACK;
    RESIGNAL;
  END;

  IF p_address IS NULL OR CHAR_LENGTH(TRIM(p_address)) = 0 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Reunion address is required';
  END IF;

  START TRANSACTION;

  SELECT lc.status, p.owner_id, lc.publisher_id, p.name
    INTO v_status, v_owner_id, v_publisher_id, v_pet_name
    FROM lost_cases AS lc
    JOIN pets AS p ON p.pet_id = lc.pet_id
   WHERE lc.case_id = p_case_id
   FOR UPDATE;

  IF v_status <> 'SEARCHING' THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Only searching cases can be reunited';
  END IF;

  IF p_confirmed_by <> v_owner_id AND p_confirmed_by <> v_publisher_id THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Only the owner or publisher can confirm reunion';
  END IF;

  INSERT INTO reunion_records (
    case_id, finder_id, confirmed_by, reunion_time,
    latitude, longitude, address, method, note
  ) VALUES (
    p_case_id, p_finder_id, p_confirmed_by, p_reunion_time,
    p_latitude, p_longitude, TRIM(p_address), p_method, p_note
  );

  UPDATE lost_cases
     SET status = 'REUNITED'
   WHERE case_id = p_case_id;

  UPDATE search_tasks AS st
  JOIN search_areas AS sa ON sa.area_id = st.area_id
     SET st.status = CASE
       WHEN st.status = 'COMPLETED' THEN 'COMPLETED'
       ELSE 'CANCELLED'
     END,
         st.updated_at = CURRENT_TIMESTAMP
   WHERE sa.case_id = p_case_id
     AND st.status <> 'COMPLETED';

  UPDATE search_areas
     SET status = 'CLOSED'
   WHERE case_id = p_case_id;

  INSERT INTO notifications (
    user_id, type, title, content, related_case_id
  ) VALUES (
    v_owner_id,
    'REUNION',
    '宠物已确认寻回',
    CONCAT('宠物“', v_pet_name, '”已确认安全回家，相关搜寻任务已归档。'),
    p_case_id
  );

  COMMIT;

  SELECT reunion_id, case_id, reunion_time, address
    FROM reunion_records
   WHERE case_id = p_case_id;
END$$

DELIMITER ;

CREATE VIEW v_active_case_summary AS
SELECT
  lc.case_id,
  lc.pet_id,
  p.owner_id,
  lc.publisher_id,
  p.name AS pet_name,
  p.species,
  p.breed,
  p.primary_color,
  lc.lost_time,
  lc.latitude,
  lc.longitude,
  lc.address,
  lc.status,
  (
    SELECT pp.photo_url
      FROM pet_photos AS pp
     WHERE pp.pet_id = p.pet_id
     ORDER BY pp.is_cover DESC, pp.sort_order ASC, pp.photo_id ASC
     LIMIT 1
  ) AS cover_photo_url,
  (
    SELECT COUNT(*)
      FROM case_sighting_matches AS csm
     WHERE csm.case_id = lc.case_id
  ) AS match_count,
  (
    SELECT COUNT(*)
      FROM case_sighting_matches AS csm
     WHERE csm.case_id = lc.case_id
       AND csm.total_score >= 75
  ) AS high_match_count,
  (
    SELECT COUNT(*)
      FROM search_areas AS sa
      JOIN search_tasks AS st ON st.area_id = sa.area_id
     WHERE sa.case_id = lc.case_id
       AND st.status IN ('CLAIMED', 'IN_PROGRESS')
  ) AS active_task_count
FROM lost_cases AS lc
JOIN pets AS p ON p.pet_id = lc.pet_id
WHERE lc.status = 'SEARCHING';

CREATE VIEW v_case_match_rankings AS
SELECT
  csm.match_id,
  csm.case_id,
  csm.sighting_id,
  p.name AS pet_name,
  s.seen_time,
  s.address AS sighting_address,
  csm.appearance_score,
  csm.distance_score,
  csm.time_score,
  csm.total_score,
  csm.distance_km,
  csm.match_reason,
  csm.algorithm_version,
  csm.review_status,
  ROW_NUMBER() OVER (
    PARTITION BY csm.case_id
    ORDER BY csm.total_score DESC, csm.generated_at DESC, csm.match_id ASC
  ) AS match_rank
FROM case_sighting_matches AS csm
JOIN lost_cases AS lc ON lc.case_id = csm.case_id
JOIN pets AS p ON p.pet_id = lc.pet_id
JOIN sightings AS s ON s.sighting_id = csm.sighting_id;

CREATE VIEW v_search_task_progress AS
SELECT
  lc.case_id,
  p.name AS pet_name,
  sa.area_id,
  sa.area_name,
  sa.status AS area_status,
  st.task_id,
  st.status AS task_status,
  st.volunteer_id,
  u.username AS volunteer_username,
  st.accepted_at,
  st.started_at,
  st.completed_at,
  st.report,
  st.updated_at
FROM search_areas AS sa
JOIN lost_cases AS lc ON lc.case_id = sa.case_id
JOIN pets AS p ON p.pet_id = lc.pet_id
LEFT JOIN search_tasks AS st ON st.area_id = sa.area_id
LEFT JOIN users AS u ON u.user_id = st.volunteer_id;

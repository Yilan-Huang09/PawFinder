-- PawFinder core schema
-- Target: MySQL 8.0.16+ (critical checks are reinforced by objects.sql)

CREATE DATABASE IF NOT EXISTS pawfinder
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_0900_ai_ci;

USE pawfinder;

SET NAMES utf8mb4;
SET time_zone = '+08:00';

CREATE TABLE IF NOT EXISTS users (
  user_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '用户ID',
  username VARCHAR(50) NOT NULL COMMENT '登录用户名',
  password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希',
  phone VARCHAR(20) NULL COMMENT '手机号',
  email VARCHAR(120) NULL COMMENT '邮箱',
  avatar_url VARCHAR(500) NULL COMMENT '头像相对路径',
  role VARCHAR(20) NOT NULL DEFAULT 'USER' COMMENT '权限角色',
  status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE' COMMENT '账号状态',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (user_id),
  CONSTRAINT uq_users_username UNIQUE (username),
  CONSTRAINT uq_users_phone UNIQUE (phone),
  CONSTRAINT uq_users_email UNIQUE (email),
  CONSTRAINT chk_users_role CHECK (role IN ('USER', 'ADMIN')),
  CONSTRAINT chk_users_status CHECK (status IN ('ACTIVE', 'DISABLED'))
) ENGINE=InnoDB COMMENT='用户账号';

CREATE TABLE IF NOT EXISTS pets (
  pet_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '宠物ID',
  owner_id BIGINT UNSIGNED NOT NULL COMMENT '主人用户ID',
  name VARCHAR(80) NOT NULL COMMENT '宠物昵称',
  species VARCHAR(30) NOT NULL COMMENT '物种',
  breed VARCHAR(80) NULL COMMENT '品种',
  primary_color VARCHAR(50) NOT NULL COMMENT '主要毛色',
  secondary_color VARCHAR(50) NULL COMMENT '次要毛色',
  gender VARCHAR(20) NOT NULL DEFAULT 'UNKNOWN' COMMENT '性别',
  size VARCHAR(20) NOT NULL DEFAULT 'UNKNOWN' COMMENT '体型',
  birth_date DATE NULL COMMENT '出生日期或估计日期',
  distinctive_features TEXT NULL COMMENT '显著特征',
  status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE' COMMENT '档案状态',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (pet_id),
  KEY idx_pets_owner_status (owner_id, status),
  CONSTRAINT fk_pets_owner FOREIGN KEY (owner_id) REFERENCES users (user_id)
    ON UPDATE RESTRICT ON DELETE RESTRICT,
  CONSTRAINT chk_pets_gender CHECK (gender IN ('MALE', 'FEMALE', 'UNKNOWN')),
  CONSTRAINT chk_pets_size CHECK (size IN ('SMALL', 'MEDIUM', 'LARGE', 'UNKNOWN')),
  CONSTRAINT chk_pets_status CHECK (status IN ('ACTIVE', 'INACTIVE'))
) ENGINE=InnoDB COMMENT='宠物档案';

CREATE TABLE IF NOT EXISTS pet_photos (
  photo_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '照片ID',
  pet_id BIGINT UNSIGNED NOT NULL COMMENT '宠物ID',
  photo_url VARCHAR(500) NOT NULL COMMENT '照片相对路径',
  is_cover BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否封面',
  sort_order SMALLINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '展示顺序',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (photo_id),
  KEY idx_pet_photos_pet_order (pet_id, is_cover, sort_order),
  CONSTRAINT fk_pet_photos_pet FOREIGN KEY (pet_id) REFERENCES pets (pet_id)
    ON UPDATE RESTRICT ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='宠物照片';

CREATE TABLE IF NOT EXISTS lost_cases (
  case_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '走失事件ID',
  pet_id BIGINT UNSIGNED NOT NULL COMMENT '宠物ID',
  publisher_id BIGINT UNSIGNED NOT NULL COMMENT '实际发布者ID',
  lost_time DATETIME NOT NULL COMMENT '走失时间',
  latitude DECIMAL(10, 7) NOT NULL COMMENT '走失纬度',
  longitude DECIMAL(10, 7) NOT NULL COMMENT '走失经度',
  address VARCHAR(255) NOT NULL COMMENT '走失地址',
  description TEXT NULL COMMENT '事件描述',
  contact_phone VARCHAR(20) NULL COMMENT '本事件联系电话',
  status VARCHAR(20) NOT NULL DEFAULT 'SEARCHING' COMMENT '事件状态',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  closed_at DATETIME NULL COMMENT '关闭或寻回时间',
  PRIMARY KEY (case_id),
  KEY idx_lost_cases_pet (pet_id),
  KEY idx_lost_cases_publisher (publisher_id),
  KEY idx_lost_cases_status_time (status, lost_time),
  KEY idx_lost_cases_coordinates (latitude, longitude),
  CONSTRAINT fk_lost_cases_pet FOREIGN KEY (pet_id) REFERENCES pets (pet_id)
    ON UPDATE RESTRICT ON DELETE RESTRICT,
  CONSTRAINT fk_lost_cases_publisher FOREIGN KEY (publisher_id) REFERENCES users (user_id)
    ON UPDATE RESTRICT ON DELETE RESTRICT,
  CONSTRAINT chk_lost_cases_latitude CHECK (latitude BETWEEN -90 AND 90),
  CONSTRAINT chk_lost_cases_longitude CHECK (longitude BETWEEN -180 AND 180),
  CONSTRAINT chk_lost_cases_status CHECK (status IN ('SEARCHING', 'REUNITED', 'CLOSED'))
) ENGINE=InnoDB COMMENT='宠物走失事件';

CREATE TABLE IF NOT EXISTS sightings (
  sighting_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '目击线索ID',
  reporter_id BIGINT UNSIGNED NOT NULL COMMENT '报告者ID',
  species VARCHAR(30) NOT NULL COMMENT '推测物种',
  breed_guess VARCHAR(80) NULL COMMENT '推测品种',
  primary_color VARCHAR(50) NOT NULL COMMENT '主要毛色',
  secondary_color VARCHAR(50) NULL COMMENT '次要毛色',
  gender_guess VARCHAR(20) NOT NULL DEFAULT 'UNKNOWN' COMMENT '推测性别',
  size_guess VARCHAR(20) NOT NULL DEFAULT 'UNKNOWN' COMMENT '推测体型',
  seen_time DATETIME NOT NULL COMMENT '目击时间',
  latitude DECIMAL(10, 7) NOT NULL COMMENT '目击纬度',
  longitude DECIMAL(10, 7) NOT NULL COMMENT '目击经度',
  address VARCHAR(255) NOT NULL COMMENT '目击地址',
  direction VARCHAR(80) NULL COMMENT '移动方向',
  confidence TINYINT UNSIGNED NOT NULL DEFAULT 3 COMMENT '报告者自评可信度1至5',
  description TEXT NULL COMMENT '线索描述',
  status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE' COMMENT '线索状态',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (sighting_id),
  KEY idx_sightings_reporter (reporter_id),
  KEY idx_sightings_status_time (status, seen_time),
  KEY idx_sightings_species_time (species, seen_time),
  KEY idx_sightings_coordinates (latitude, longitude),
  CONSTRAINT fk_sightings_reporter FOREIGN KEY (reporter_id) REFERENCES users (user_id)
    ON UPDATE RESTRICT ON DELETE RESTRICT,
  CONSTRAINT chk_sightings_gender CHECK (gender_guess IN ('MALE', 'FEMALE', 'UNKNOWN')),
  CONSTRAINT chk_sightings_size CHECK (size_guess IN ('SMALL', 'MEDIUM', 'LARGE', 'UNKNOWN')),
  CONSTRAINT chk_sightings_latitude CHECK (latitude BETWEEN -90 AND 90),
  CONSTRAINT chk_sightings_longitude CHECK (longitude BETWEEN -180 AND 180),
  CONSTRAINT chk_sightings_confidence CHECK (confidence BETWEEN 1 AND 5),
  CONSTRAINT chk_sightings_status CHECK (status IN ('ACTIVE', 'HIDDEN', 'INVALID'))
) ENGINE=InnoDB COMMENT='独立目击线索';

CREATE TABLE IF NOT EXISTS sighting_photos (
  photo_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '照片ID',
  sighting_id BIGINT UNSIGNED NOT NULL COMMENT '目击线索ID',
  photo_url VARCHAR(500) NOT NULL COMMENT '照片相对路径',
  sort_order SMALLINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '展示顺序',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (photo_id),
  KEY idx_sighting_photos_sighting_order (sighting_id, sort_order),
  CONSTRAINT fk_sighting_photos_sighting FOREIGN KEY (sighting_id) REFERENCES sightings (sighting_id)
    ON UPDATE RESTRICT ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='目击线索照片';

CREATE TABLE IF NOT EXISTS case_sighting_matches (
  match_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '匹配ID',
  case_id BIGINT UNSIGNED NOT NULL COMMENT '走失事件ID',
  sighting_id BIGINT UNSIGNED NOT NULL COMMENT '目击线索ID',
  appearance_score DECIMAL(5, 2) NOT NULL COMMENT '外观得分',
  distance_score DECIMAL(5, 2) NOT NULL COMMENT '距离得分',
  time_score DECIMAL(5, 2) NOT NULL COMMENT '时间得分',
  total_score DECIMAL(5, 2) NOT NULL COMMENT '总得分',
  distance_km DECIMAL(10, 3) NOT NULL COMMENT '实际距离千米',
  match_reason TEXT NOT NULL COMMENT '可解释匹配依据',
  algorithm_version VARCHAR(30) NOT NULL DEFAULT 'rule-v1' COMMENT '算法版本',
  review_status VARCHAR(20) NOT NULL DEFAULT 'PENDING' COMMENT '人工核实状态',
  reviewed_by BIGINT UNSIGNED NULL COMMENT '核实用户ID',
  generated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  reviewed_at DATETIME NULL,
  PRIMARY KEY (match_id),
  CONSTRAINT uq_matches_case_sighting UNIQUE (case_id, sighting_id),
  KEY idx_matches_case_review_score (case_id, review_status, total_score),
  KEY idx_matches_sighting_score (sighting_id, total_score),
  KEY idx_matches_reviewer (reviewed_by),
  CONSTRAINT fk_matches_case FOREIGN KEY (case_id) REFERENCES lost_cases (case_id)
    ON UPDATE RESTRICT ON DELETE CASCADE,
  CONSTRAINT fk_matches_sighting FOREIGN KEY (sighting_id) REFERENCES sightings (sighting_id)
    ON UPDATE RESTRICT ON DELETE CASCADE,
  CONSTRAINT fk_matches_reviewer FOREIGN KEY (reviewed_by) REFERENCES users (user_id)
    ON UPDATE RESTRICT ON DELETE SET NULL,
  CONSTRAINT chk_matches_appearance_score CHECK (appearance_score BETWEEN 0 AND 100),
  CONSTRAINT chk_matches_distance_score CHECK (distance_score BETWEEN 0 AND 100),
  CONSTRAINT chk_matches_time_score CHECK (time_score BETWEEN 0 AND 100),
  CONSTRAINT chk_matches_total_score CHECK (total_score BETWEEN 0 AND 100),
  CONSTRAINT chk_matches_distance_km CHECK (distance_km >= 0),
  CONSTRAINT chk_matches_review_status CHECK (review_status IN ('PENDING', 'CONFIRMED', 'REJECTED'))
) ENGINE=InnoDB COMMENT='走失事件与线索匹配结果';

CREATE TABLE IF NOT EXISTS search_areas (
  area_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '搜寻区域ID',
  case_id BIGINT UNSIGNED NOT NULL COMMENT '走失事件ID',
  created_by BIGINT UNSIGNED NOT NULL COMMENT '创建者ID',
  area_name VARCHAR(100) NOT NULL COMMENT '区域名称',
  center_latitude DECIMAL(10, 7) NOT NULL COMMENT '中心纬度',
  center_longitude DECIMAL(10, 7) NOT NULL COMMENT '中心经度',
  radius_meters INT UNSIGNED NOT NULL COMMENT '半径米',
  description VARCHAR(500) NULL COMMENT '搜寻说明',
  status VARCHAR(20) NOT NULL DEFAULT 'OPEN' COMMENT '区域状态',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (area_id),
  KEY idx_search_areas_case_status (case_id, status),
  KEY idx_search_areas_creator (created_by),
  KEY idx_search_areas_coordinates (center_latitude, center_longitude),
  CONSTRAINT fk_search_areas_case FOREIGN KEY (case_id) REFERENCES lost_cases (case_id)
    ON UPDATE RESTRICT ON DELETE RESTRICT,
  CONSTRAINT fk_search_areas_creator FOREIGN KEY (created_by) REFERENCES users (user_id)
    ON UPDATE RESTRICT ON DELETE RESTRICT,
  CONSTRAINT chk_search_areas_latitude CHECK (center_latitude BETWEEN -90 AND 90),
  CONSTRAINT chk_search_areas_longitude CHECK (center_longitude BETWEEN -180 AND 180),
  CONSTRAINT chk_search_areas_radius CHECK (radius_meters BETWEEN 1 AND 20000),
  CONSTRAINT chk_search_areas_status CHECK (status IN ('OPEN', 'CLOSED'))
) ENGINE=InnoDB COMMENT='圆形搜寻区域';

CREATE TABLE IF NOT EXISTS search_tasks (
  task_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '搜寻任务ID',
  area_id BIGINT UNSIGNED NOT NULL COMMENT '搜寻区域ID',
  volunteer_id BIGINT UNSIGNED NULL COMMENT '当前志愿者ID',
  status VARCHAR(20) NOT NULL DEFAULT 'AVAILABLE' COMMENT '任务状态',
  accepted_at DATETIME NULL COMMENT '认领时间',
  started_at DATETIME NULL COMMENT '开始时间',
  completed_at DATETIME NULL COMMENT '完成时间',
  report TEXT NULL COMMENT '搜寻反馈',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (task_id),
  CONSTRAINT uq_search_tasks_area UNIQUE (area_id),
  KEY idx_search_tasks_status_volunteer (status, volunteer_id),
  KEY idx_search_tasks_volunteer (volunteer_id),
  CONSTRAINT fk_search_tasks_area FOREIGN KEY (area_id) REFERENCES search_areas (area_id)
    ON UPDATE RESTRICT ON DELETE CASCADE,
  CONSTRAINT fk_search_tasks_volunteer FOREIGN KEY (volunteer_id) REFERENCES users (user_id)
    ON UPDATE RESTRICT ON DELETE SET NULL,
  CONSTRAINT chk_search_tasks_status CHECK (status IN ('AVAILABLE', 'CLAIMED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED')),
  CONSTRAINT chk_search_tasks_claim CHECK (
    (status = 'AVAILABLE' AND volunteer_id IS NULL)
    OR status <> 'AVAILABLE'
  )
) ENGINE=InnoDB COMMENT='志愿者搜寻任务';

CREATE TABLE IF NOT EXISTS reunion_records (
  reunion_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '寻回记录ID',
  case_id BIGINT UNSIGNED NOT NULL COMMENT '走失事件ID',
  finder_id BIGINT UNSIGNED NULL COMMENT '发现者用户ID',
  confirmed_by BIGINT UNSIGNED NOT NULL COMMENT '确认人用户ID',
  reunion_time DATETIME NOT NULL COMMENT '寻回时间',
  latitude DECIMAL(10, 7) NULL COMMENT '寻回纬度',
  longitude DECIMAL(10, 7) NULL COMMENT '寻回经度',
  address VARCHAR(255) NOT NULL COMMENT '寻回地址',
  method VARCHAR(100) NULL COMMENT '寻回方式',
  note TEXT NULL COMMENT '备注',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (reunion_id),
  CONSTRAINT uq_reunion_records_case UNIQUE (case_id),
  KEY idx_reunion_records_finder (finder_id),
  KEY idx_reunion_records_confirmer (confirmed_by),
  KEY idx_reunion_records_time (reunion_time),
  CONSTRAINT fk_reunion_records_case FOREIGN KEY (case_id) REFERENCES lost_cases (case_id)
    ON UPDATE RESTRICT ON DELETE RESTRICT,
  CONSTRAINT fk_reunion_records_finder FOREIGN KEY (finder_id) REFERENCES users (user_id)
    ON UPDATE RESTRICT ON DELETE SET NULL,
  CONSTRAINT fk_reunion_records_confirmer FOREIGN KEY (confirmed_by) REFERENCES users (user_id)
    ON UPDATE RESTRICT ON DELETE RESTRICT,
  CONSTRAINT chk_reunion_records_latitude CHECK (latitude IS NULL OR latitude BETWEEN -90 AND 90),
  CONSTRAINT chk_reunion_records_longitude CHECK (longitude IS NULL OR longitude BETWEEN -180 AND 180)
) ENGINE=InnoDB COMMENT='宠物寻回记录';

CREATE TABLE IF NOT EXISTS notifications (
  notification_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '通知ID',
  user_id BIGINT UNSIGNED NOT NULL COMMENT '接收用户ID',
  type VARCHAR(30) NOT NULL COMMENT '通知类型',
  title VARCHAR(120) NOT NULL COMMENT '通知标题',
  content VARCHAR(500) NOT NULL COMMENT '通知内容',
  related_case_id BIGINT UNSIGNED NULL COMMENT '相关走失事件ID',
  related_match_id BIGINT UNSIGNED NULL COMMENT '相关匹配ID',
  related_task_id BIGINT UNSIGNED NULL COMMENT '相关任务ID',
  is_read BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否已读',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  read_at DATETIME NULL,
  PRIMARY KEY (notification_id),
  KEY idx_notifications_user_read_time (user_id, is_read, created_at),
  KEY idx_notifications_case (related_case_id),
  KEY idx_notifications_match (related_match_id),
  KEY idx_notifications_task (related_task_id),
  CONSTRAINT fk_notifications_user FOREIGN KEY (user_id) REFERENCES users (user_id)
    ON UPDATE RESTRICT ON DELETE CASCADE,
  CONSTRAINT fk_notifications_case FOREIGN KEY (related_case_id) REFERENCES lost_cases (case_id)
    ON UPDATE RESTRICT ON DELETE SET NULL,
  CONSTRAINT fk_notifications_match FOREIGN KEY (related_match_id) REFERENCES case_sighting_matches (match_id)
    ON UPDATE RESTRICT ON DELETE SET NULL,
  CONSTRAINT fk_notifications_task FOREIGN KEY (related_task_id) REFERENCES search_tasks (task_id)
    ON UPDATE RESTRICT ON DELETE SET NULL,
  CONSTRAINT chk_notifications_type CHECK (type IN ('HIGH_MATCH', 'TASK_STATUS', 'REUNION', 'SYSTEM')),
  CONSTRAINT chk_notifications_read_time CHECK (
    (is_read = FALSE AND read_at IS NULL)
    OR (is_read = TRUE AND read_at IS NOT NULL)
  )
) ENGINE=InnoDB COMMENT='站内通知';

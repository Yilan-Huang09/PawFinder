-- PawFinder deterministic demonstration data
-- Demo password for every seeded account: PawFinder123!
-- Run only after schema.sql and objects.sql on a clean database.

USE pawfinder;

SET NAMES utf8mb4;

START TRANSACTION;

INSERT INTO users (
  user_id, username, password_hash, phone, email, avatar_url, role, status
) VALUES
  (1, 'admin', 'pbkdf2:sha256:600000$9jVzpJITXzJSIPUb$3196c35b80d42ec573672e0f2f04b654e5eae6fbb70bc362b7248a1f3b6f9f99', '13800000001', 'admin@pawfinder.local', NULL, 'ADMIN', 'ACTIVE'),
  (2, 'linyu', 'pbkdf2:sha256:600000$9jVzpJITXzJSIPUb$3196c35b80d42ec573672e0f2f04b654e5eae6fbb70bc362b7248a1f3b6f9f99', '13800000002', 'linyu@pawfinder.local', NULL, 'USER', 'ACTIVE'),
  (3, 'chenxi', 'pbkdf2:sha256:600000$9jVzpJITXzJSIPUb$3196c35b80d42ec573672e0f2f04b654e5eae6fbb70bc362b7248a1f3b6f9f99', '13800000003', 'chenxi@pawfinder.local', NULL, 'USER', 'ACTIVE'),
  (4, 'wangran', 'pbkdf2:sha256:600000$9jVzpJITXzJSIPUb$3196c35b80d42ec573672e0f2f04b654e5eae6fbb70bc362b7248a1f3b6f9f99', '13800000004', 'wangran@pawfinder.local', NULL, 'USER', 'ACTIVE'),
  (5, 'zhaomin', 'pbkdf2:sha256:600000$9jVzpJITXzJSIPUb$3196c35b80d42ec573672e0f2f04b654e5eae6fbb70bc362b7248a1f3b6f9f99', '13800000005', 'zhaomin@pawfinder.local', NULL, 'USER', 'ACTIVE'),
  (6, 'lihao', 'pbkdf2:sha256:600000$9jVzpJITXzJSIPUb$3196c35b80d42ec573672e0f2f04b654e5eae6fbb70bc362b7248a1f3b6f9f99', '13800000006', 'lihao@pawfinder.local', NULL, 'USER', 'ACTIVE'),
  (7, 'sunyue', 'pbkdf2:sha256:600000$9jVzpJITXzJSIPUb$3196c35b80d42ec573672e0f2f04b654e5eae6fbb70bc362b7248a1f3b6f9f99', '13800000007', 'sunyue@pawfinder.local', NULL, 'USER', 'ACTIVE'),
  (8, 'zhouming', 'pbkdf2:sha256:600000$9jVzpJITXzJSIPUb$3196c35b80d42ec573672e0f2f04b654e5eae6fbb70bc362b7248a1f3b6f9f99', '13800000008', 'zhouming@pawfinder.local', NULL, 'USER', 'ACTIVE'),
  (9, 'witness', 'pbkdf2:sha256:600000$9jVzpJITXzJSIPUb$3196c35b80d42ec573672e0f2f04b654e5eae6fbb70bc362b7248a1f3b6f9f99', '13800000009', 'witness@pawfinder.local', NULL, 'USER', 'ACTIVE');

INSERT INTO pets (
  pet_id, owner_id, name, species, breed, primary_color, secondary_color,
  gender, size, birth_date, distinctive_features, status
) VALUES
  (1, 2, '豆包', 'DOG', 'Border Collie', 'BLACK', 'WHITE', 'FEMALE', 'MEDIUM', '2022-05-12', '胸口白色心形毛，红色项圈', 'ACTIVE'),
  (2, 3, '橘子', 'CAT', 'Domestic Shorthair', 'ORANGE', 'WHITE', 'MALE', 'MEDIUM', '2021-08-20', '左耳有小缺口，白色前爪', 'ACTIVE'),
  (3, 2, '年糕', 'CAT', 'British Shorthair', 'GRAY', NULL, 'FEMALE', 'MEDIUM', '2023-01-15', '圆脸，绿色眼睛', 'ACTIVE'),
  (4, 4, '麦麦', 'DOG', 'Golden Retriever', 'GOLDEN', NULL, 'MALE', 'LARGE', '2020-10-03', '蓝色胸背，尾巴末端颜色较浅', 'ACTIVE'),
  (5, 5, '雪球', 'DOG', 'Bichon Frise', 'WHITE', NULL, 'FEMALE', 'SMALL', '2022-12-11', '右后腿毛较短，粉色项圈', 'ACTIVE'),
  (6, 6, '布丁', 'CAT', 'Ragdoll', 'CREAM', 'BROWN', 'MALE', 'LARGE', '2021-04-09', '蓝眼睛，脸部深色花纹', 'ACTIVE'),
  (7, 7, '可乐', 'DOG', 'Labrador Retriever', 'BLACK', NULL, 'MALE', 'LARGE', '2019-06-18', '下巴有少量白毛', 'ACTIVE'),
  (8, 8, '七七', 'DOG', 'Corgi', 'BROWN', 'WHITE', 'FEMALE', 'SMALL', '2023-02-02', '左侧鼻梁有黑点', 'ACTIVE'),
  (9, 3, '小满', 'CAT', 'Calico', 'CALICO', 'WHITE', 'FEMALE', 'SMALL', '2024-03-10', '三花纹，尾巴较短', 'ACTIVE'),
  (10, 6, '阿福', 'DOG', 'Shiba Inu', 'BROWN', 'CREAM', 'MALE', 'MEDIUM', '2021-09-21', '绿色项圈，右耳尖颜色深', 'ACTIVE'),
  (11, 4, '露露', 'CAT', 'Siamese', 'CREAM', 'BROWN', 'FEMALE', 'MEDIUM', '2020-07-07', '蓝眼睛，深色面罩', 'ACTIVE'),
  (12, 7, '泡泡', 'DOG', 'Poodle', 'BROWN', NULL, 'FEMALE', 'SMALL', '2022-11-23', '黄色铃铛项圈', 'ACTIVE');

INSERT INTO pet_photos (photo_id, pet_id, photo_url, is_cover, sort_order) VALUES
  (1, 1, 'demo/pets/doubao-cover.jpg', TRUE, 0),
  (2, 1, 'demo/pets/doubao-side.jpg', FALSE, 1),
  (3, 2, 'demo/pets/juzi-cover.jpg', TRUE, 0),
  (4, 3, 'demo/pets/niangao-cover.jpg', TRUE, 0),
  (5, 4, 'demo/pets/maimai-cover.jpg', TRUE, 0),
  (6, 5, 'demo/pets/xueqiu-cover.jpg', TRUE, 0),
  (7, 6, 'demo/pets/buding-cover.jpg', TRUE, 0),
  (8, 7, 'demo/pets/kele-cover.jpg', TRUE, 0),
  (9, 8, 'demo/pets/qiqi-cover.jpg', TRUE, 0),
  (10, 9, 'demo/pets/xiaoman-cover.jpg', TRUE, 0),
  (11, 10, 'demo/pets/afu-cover.jpg', TRUE, 0),
  (12, 11, 'demo/pets/lulu-cover.jpg', TRUE, 0),
  (13, 12, 'demo/pets/paopao-cover.jpg', TRUE, 0);

INSERT INTO lost_cases (
  case_id, pet_id, publisher_id, lost_time, latitude, longitude,
  address, description, contact_phone, status, closed_at
) VALUES
  (1, 1, 2, '2026-11-08 07:40:00', 29.8269000, 106.4253000, '西南大学北门天生路附近', '晨间散步时挣脱牵引绳，可能沿天生路向东。', '13800000002', 'SEARCHING', NULL),
  (2, 2, 3, '2026-11-07 20:15:00', 29.8214000, 106.4308000, '西南大学二号门天生丽街', '开门取快递时跑出，怕生但会被猫条吸引。', '13800000003', 'SEARCHING', NULL),
  (3, 4, 4, '2026-11-06 16:30:00', 29.8160000, 106.4189000, '西南大学南区樟树林', '穿蓝色胸背，性格温顺，可能沿校园绿道移动。', '13800000004', 'SEARCHING', NULL),
  (4, 5, 5, '2026-11-03 18:10:00', 29.8105000, 106.3948000, '北碚万达广场附近', '白色比熊，粉色项圈，已由志愿者协助寻回。', '13800000005', 'REUNITED', '2026-11-04 09:20:00'),
  (5, 8, 8, '2026-10-25 11:00:00', 29.8350000, 106.4360000, '北碚公园南门', '短腿柯基，事件由主人主动关闭。', '13800000008', 'CLOSED', '2026-10-30 12:00:00'),
  (6, 10, 6, '2026-11-08 21:05:00', 29.8330000, 106.4070000, '缙云广场附近', '柴犬，绿色项圈，可能向健身步道移动。', '13800000006', 'SEARCHING', NULL);

INSERT INTO sightings (
  sighting_id, reporter_id, species, breed_guess, primary_color, secondary_color,
  gender_guess, size_guess, seen_time, latitude, longitude, address,
  direction, confidence, description, status
) VALUES
  (1, 9, 'DOG', 'Border Collie', 'BLACK', 'WHITE', 'FEMALE', 'MEDIUM', '2026-11-08 09:05:00', 29.8278000, 106.4278000, '西南大学北门公交站', '向东', 5, '黑白边牧，胸口有白毛，戴红色项圈。', 'ACTIVE'),
  (2, 7, 'DOG', 'Border Collie', 'BLACK', 'WHITE', 'UNKNOWN', 'MEDIUM', '2026-11-08 15:30:00', 29.8320000, 106.4330000, '天生路社区运动场附近', '向北', 3, '远处看到黑白中型犬，项圈颜色不确定。', 'ACTIVE'),
  (3, 6, 'DOG', 'Mixed', 'BLACK', 'BROWN', 'MALE', 'MEDIUM', '2026-11-09 08:15:00', 29.8500000, 106.4500000, '北碚滨江休闲带', NULL, 2, '黑色犬只，体型相近但没有明显白毛。', 'ACTIVE'),
  (4, 9, 'CAT', 'Domestic Shorthair', 'ORANGE', 'WHITE', 'MALE', 'MEDIUM', '2026-11-07 22:20:00', 29.8219000, 106.4315000, '天生丽街停车场入口', '向地库内', 5, '橘白猫，左耳似乎有缺口。', 'ACTIVE'),
  (5, 5, 'CAT', 'Domestic Shorthair', 'ORANGE', NULL, 'UNKNOWN', 'MEDIUM', '2026-11-08 10:40:00', 29.8250000, 106.4360000, '西南大学五号门家属区', NULL, 3, '看到一只橘猫躲在汽车底部。', 'ACTIVE'),
  (6, 8, 'CAT', 'British Shorthair', 'GRAY', NULL, 'FEMALE', 'MEDIUM', '2026-11-08 17:00:00', 29.8150000, 106.4280000, '西南大学南区杏园', NULL, 3, '灰色圆脸猫，疑似英短。', 'ACTIVE'),
  (7, 9, 'DOG', 'Golden Retriever', 'GOLDEN', NULL, 'MALE', 'LARGE', '2026-11-06 18:00:00', 29.8170000, 106.4200000, '西南大学南区樟树林东侧', '向运动场', 5, '金毛，穿蓝色胸背，性格亲人。', 'ACTIVE'),
  (8, 2, 'DOG', 'Golden Retriever', 'GOLDEN', NULL, 'UNKNOWN', 'LARGE', '2026-11-07 09:30:00', 29.8300000, 106.4480000, '北碚滨江路绿道', '向西', 4, '大型金色犬只，没有看清胸背颜色。', 'ACTIVE'),
  (9, 3, 'DOG', 'Bichon Frise', 'WHITE', NULL, 'FEMALE', 'SMALL', '2026-11-03 21:00:00', 29.8115000, 106.3955000, '北碚万达停车场', NULL, 5, '白色小型犬，粉色项圈。', 'ACTIVE'),
  (10, 7, 'DOG', 'Corgi', 'BROWN', 'WHITE', 'FEMALE', 'SMALL', '2026-10-25 13:20:00', 29.8360000, 106.4370000, '北碚公园北门', '向北', 4, '棕白柯基，左侧鼻梁似有黑点。', 'ACTIVE'),
  (11, 9, 'DOG', 'Shiba Inu', 'BROWN', 'CREAM', 'MALE', 'MEDIUM', '2026-11-08 22:10:00', 29.8340000, 106.4090000, '缙云广场东侧', '向步道', 5, '柴犬，绿色项圈，右耳尖颜色较深。', 'ACTIVE'),
  (12, 4, 'DOG', 'Shiba Inu', 'BROWN', 'CREAM', 'UNKNOWN', 'MEDIUM', '2026-11-09 07:30:00', 29.8420000, 106.4170000, '缙云山健身步道', '向西', 4, '棕色柴犬，奔跑速度较快。', 'ACTIVE'),
  (13, 6, 'DOG', 'Poodle', 'BROWN', NULL, 'FEMALE', 'SMALL', '2026-11-08 12:20:00', 29.8240000, 106.4250000, '西南大学中心体育场', NULL, 2, '棕色小型卷毛犬。', 'ACTIVE'),
  (14, 8, 'CAT', 'Siamese', 'CREAM', 'BROWN', 'FEMALE', 'MEDIUM', '2026-11-07 14:10:00', 29.8290000, 106.4120000, '西师街道家属区', NULL, 3, '暹罗猫，蓝眼睛。', 'ACTIVE'),
  (15, 1, 'DOG', 'Unknown', 'WHITE', NULL, 'UNKNOWN', 'SMALL', '2026-11-09 10:00:00', 29.8450000, 106.3980000, '嘉陵风情步行街', NULL, 1, '线索信息不足，管理员已隐藏。', 'HIDDEN');

INSERT INTO sighting_photos (photo_id, sighting_id, photo_url, sort_order) VALUES
  (1, 1, 'demo/sightings/sighting-01.jpg', 0),
  (2, 4, 'demo/sightings/sighting-04.jpg', 0),
  (3, 7, 'demo/sightings/sighting-07.jpg', 0),
  (4, 9, 'demo/sightings/sighting-09.jpg', 0),
  (5, 10, 'demo/sightings/sighting-10.jpg', 0),
  (6, 11, 'demo/sightings/sighting-11.jpg', 0),
  (7, 12, 'demo/sightings/sighting-12.jpg', 0),
  (8, 14, 'demo/sightings/sighting-14.jpg', 0);

INSERT INTO case_sighting_matches (
  match_id, case_id, sighting_id, appearance_score, distance_score, time_score,
  total_score, distance_km, match_reason, algorithm_version, review_status,
  reviewed_by, reviewed_at
) VALUES
  (1, 1, 1, 90.00, 95.00, 85.00, 90.50, 0.302, '品种、毛色、性别及红色项圈吻合，时间和位置高度合理。', 'rule-v1', 'CONFIRMED', 2, '2026-11-08 10:00:00'),
  (2, 1, 2, 75.00, 70.00, 60.00, 70.50, 3.210, '外观基本相符，但距离和目击时间间隔较大。', 'rule-v1', 'PENDING', NULL, NULL),
  (3, 1, 3, 50.00, 45.00, 45.00, 47.50, 7.850, '物种和体型相近，毛色特征及距离吻合度较低。', 'rule-v1', 'REJECTED', 2, '2026-11-09 09:00:00'),
  (4, 2, 4, 92.00, 98.00, 90.00, 93.40, 0.101, '橘白毛色、左耳缺口、性别和位置高度吻合。', 'rule-v1', 'CONFIRMED', 3, '2026-11-08 08:00:00'),
  (5, 2, 5, 68.00, 78.00, 70.00, 71.40, 1.550, '毛色和体型相符，缺少耳部特征证据。', 'rule-v1', 'PENDING', NULL, NULL),
  (6, 3, 7, 96.00, 94.00, 92.00, 94.60, 0.268, '金毛、蓝色胸背、体型、方向和时间均高度吻合。', 'rule-v1', 'CONFIRMED', 4, '2026-11-06 19:00:00'),
  (7, 3, 8, 80.00, 65.00, 75.00, 74.50, 2.890, '外观相符，未观察到蓝色胸背且距离较远。', 'rule-v1', 'PENDING', NULL, NULL),
  (8, 4, 9, 98.00, 96.00, 95.00, 96.80, 0.145, '白色比熊、粉色项圈、性别、时间和位置均吻合。', 'rule-v1', 'CONFIRMED', 5, '2026-11-04 08:30:00'),
  (9, 5, 10, 90.00, 94.00, 90.00, 91.20, 0.160, '柯基外观及鼻梁黑点吻合，位置接近。', 'rule-v1', 'CONFIRMED', 8, '2026-10-25 15:00:00'),
  (10, 6, 11, 97.00, 96.00, 95.00, 96.30, 0.218, '柴犬、绿色项圈、耳尖特征、方向和位置高度吻合。', 'rule-v1', 'CONFIRMED', 6, '2026-11-08 23:00:00'),
  (11, 6, 12, 82.00, 75.00, 76.00, 78.70, 1.820, '外观相符且移动方向合理，距离较第一条线索更远。', 'rule-v1', 'PENDING', NULL, NULL),
  (12, 2, 6, 42.00, 60.00, 55.00, 50.00, 2.300, '物种和体型接近，但毛色和品种差异明显。', 'rule-v1', 'REJECTED', 3, '2026-11-09 08:00:00');

INSERT INTO search_areas (
  area_id, case_id, created_by, area_name, center_latitude, center_longitude,
  radius_meters, description, status
) VALUES
  (1, 1, 2, '天生路东段', 29.8278000, 106.4285000, 900, '重点查看沿街商铺后巷。', 'OPEN'),
  (2, 1, 2, '西大北门家属区', 29.8300000, 106.4230000, 700, '询问小区保安并查看地下车库。', 'OPEN'),
  (3, 1, 2, '西南大学中心体育场', 29.8240000, 106.4250000, 1100, '沿绿化带和体育场外围巡查。', 'OPEN'),
  (4, 2, 3, '天生丽街地库', 29.8219000, 106.4315000, 500, '携带猫条，保持安静。', 'OPEN'),
  (5, 2, 3, '西大五号门家属区', 29.8250000, 106.4360000, 650, '查看车辆底部和楼道。', 'OPEN'),
  (6, 3, 4, '南区樟树林东区', 29.8170000, 106.4200000, 1200, '沿校园绿道和运动场出口巡查。', 'OPEN'),
  (7, 6, 6, '缙云广场片区', 29.8340000, 106.4090000, 800, '询问广场夜间工作人员。', 'OPEN'),
  (8, 6, 6, '缙云山健身步道', 29.8420000, 106.4170000, 1500, '骑行巡查并留意绿色项圈。', 'OPEN');

INSERT INTO search_tasks (
  task_id, area_id, volunteer_id, status, accepted_at, started_at,
  completed_at, report
) VALUES
  (1, 1, 5, 'IN_PROGRESS', '2026-11-08 10:10:00', '2026-11-08 10:30:00', NULL, '已询问两家便利店，继续向东巡查。'),
  (2, 2, NULL, 'AVAILABLE', NULL, NULL, NULL, NULL),
  (3, 3, 7, 'COMPLETED', '2026-11-08 11:00:00', '2026-11-08 11:20:00', '2026-11-08 13:10:00', '未发现目标，已张贴寻宠海报。'),
  (4, 4, 9, 'CLAIMED', '2026-11-08 08:20:00', NULL, NULL, NULL),
  (5, 5, NULL, 'AVAILABLE', NULL, NULL, NULL, NULL),
  (6, 6, 2, 'IN_PROGRESS', '2026-11-06 19:10:00', '2026-11-06 19:20:00', NULL, '已沿江巡查约两公里。'),
  (7, 7, 4, 'CLAIMED', '2026-11-08 23:20:00', NULL, NULL, NULL),
  (8, 8, NULL, 'AVAILABLE', NULL, NULL, NULL, NULL);

INSERT INTO reunion_records (
  reunion_id, case_id, finder_id, confirmed_by, reunion_time,
  latitude, longitude, address, method, note
) VALUES (
  1, 4, 3, 5, '2026-11-04 09:20:00', 29.8120000, 106.3960000,
  '北碚万达北侧停车场', '目击者联系主人后现场确认', '轻微脏污，健康状况良好。'
);

INSERT INTO notifications (
  notification_id, user_id, type, title, content,
  related_case_id, related_task_id, is_read, read_at, created_at
) VALUES
  (100, 5, 'REUNION', '宠物已确认寻回', '宠物“雪球”已安全回家。', 4, NULL, TRUE, '2026-11-04 09:25:00', '2026-11-04 09:21:00'),
  (101, 5, 'TASK_STATUS', '搜寻任务有新进展', '志愿者已开始巡查天生路东段。', 1, 1, FALSE, NULL, '2026-11-08 10:30:00'),
  (102, 3, 'TASK_STATUS', '搜寻区域已被认领', '天生丽街地库搜寻任务已被认领。', 2, 4, FALSE, NULL, '2026-11-08 08:20:00'),
  (103, 1, 'SYSTEM', '演示数据已初始化', 'PawFinder 课程设计演示数据初始化成功。', NULL, NULL, FALSE, NULL, '2026-11-09 09:00:00');

COMMIT;

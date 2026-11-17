# PawFinder 数据字典

| 表 | 主键 | 主要外键 | 用途 |
| --- | --- | --- | --- |
| `users` | `user_id` | — | 账号、角色、状态与联系方式 |
| `pets` | `pet_id` | `owner_id` | 宠物稳定特征 |
| `pet_photos` | `photo_id` | `pet_id` | 照片、封面与排序 |
| `lost_cases` | `case_id` | 宠物、发布者 | 走失事实 |
| `sightings` | `sighting_id` | 报告者 | 独立目击 |
| `sighting_photos` | `photo_id` | 目击 | 目击照片 |
| `case_sighting_matches` | `match_id` | 事件、目击、审核者 | 分数和审核 |
| `search_areas` | `area_id` | 事件、创建者 | 圆形搜寻区 |
| `search_tasks` | `task_id` | 区域、志愿者 | 认领和反馈 |
| `reunion_records` | `reunion_id` | 事件、发现者、确认者 | 一案一条寻回事实 |
| `notifications` | `notification_id` | 用户及业务对象 | 用户消息 |

核心状态：事件 `SEARCHING/REUNITED/CLOSED`；线索 `ACTIVE/HIDDEN/INVALID`；匹配 `PENDING/CONFIRMED/REJECTED`；任务 `AVAILABLE/CLAIMED/IN_PROGRESS/COMPLETED/CANCELLED`。完整字段、类型、约束和索引以 `database/schema.sql` 为准。

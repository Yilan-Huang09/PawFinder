# PawFinder 数据库课程设计系统设计说明

- 项目名称：基于时空线索匹配的宠物走失协同搜寻系统
- 设计日期：2026-11-09
- 提交截止日期：2026-11-30
- 开发方式：个人项目

## 1. 项目背景与目标

PawFinder 是面向宠物主人、目击者和志愿者的协同寻宠网站。系统用独立的走失事件和目击线索保存事实，再通过匹配关联表生成候选关系，避免将一条目击线索错误绑定到单一事件。

项目首先满足数据库课程设计要求，再用时空匹配、地图时间轴和志愿者任务体现创新。最终成果必须能够在本地完整运行，并具备可重复的数据库初始化、演示数据、自动测试、课程报告素材和答辩演示流程。

课程评分重点为数据库设计与对象 40 分、文档 30 分、界面 20 分、分析总结 10 分。因此系统追求完整、规范、稳定和可解释，不以功能数量作为主要目标。

## 2. 成功标准

项目完成时应满足以下条件：

1. MySQL 8 可以通过脚本创建全部表、约束、索引、视图、函数、存储过程和触发器。
2. Vue 前端、Flask 后端与 MySQL 能在本地正常连接并完成核心业务闭环。
3. 用户能够发布走失事件和独立目击线索，系统能够生成可解释的候选匹配。
4. 主人能够核实匹配、创建搜寻区域并通过事务确认寻回。
5. 地图不可用或大模型未配置时，核心功能仍然可用。
6. 自动测试覆盖数据库约束、权限、匹配边界、任务认领和寻回事务。
7. 初始化数据能够稳定重现课程答辩演示故事。

## 3. 范围

### 3.1 必须完成

- 用户注册、登录、退出、个人资料和密码修改。
- 宠物档案及多图管理。
- 走失事件发布、编辑、浏览、关闭和寻回确认。
- 独立目击线索及多图管理。
- 规则式外观、距离和时间匹配。
- 候选匹配排序、解释和人工核实。
- 地图标记、线索时间筛选和圆形搜寻区域。
- 志愿者任务认领、进度和反馈。
- 站内通知。
- 精简管理员控制台。
- 可降级的大模型描述优化和线索摘要。

### 3.2 不在范围内

- 宠物图像识别和人脸式识别模型。
- 实时定位、GPS 设备接入和轨迹预测。
- 即时聊天、短信、付费和悬赏交易。
- 多级组织审批、复杂举报工单和内容推荐算法。
- 生产级云部署、跨区域容灾和大规模并发优化。

## 4. 用户与权限

系统只有两个权限角色：`USER` 和 `ADMIN`。主人、目击者和志愿者是用户在不同业务记录中的身份，不是互斥账号角色。

- 游客可以浏览公开的寻找中事件和脱敏信息。
- 普通用户可以管理自己的宠物，发布事件和线索，认领任务。
- 宠物主人或事件发布者可以编辑事件、核实匹配、创建搜寻区域和确认寻回。
- 志愿者只能更新自己认领的任务。
- 管理员可以停用账号、隐藏无效事件或线索、查看汇总统计，但不能冒充用户修改业务事实。

所有写操作均在后端重新校验身份和资源所有权，前端路由保护只用于改善体验，不作为安全边界。

## 5. 总体架构

系统采用前后端分离的三层架构：

```text
Vue 3 + Vite + Pinia + Vue Router + Element Plus
                         |
                   REST API / JWT
                         |
Flask + SQLAlchemy + Pydantic 2 validation
                         |
                      MySQL 8
```

- 前端负责页面、表单、地图交互和用户状态。
- Flask 路由层负责 HTTP 协议、鉴权和输入输出。
- 服务层负责匹配、任务、寻回事务、通知和大模型降级。
- 数据访问层以 SQLAlchemy 完成普通业务，以原生 SQL 调用课程要求的视图、函数和存储过程。
- 图片存放在 `backend/uploads`，数据库只保存相对路径和元数据。
- 地图使用高德地图 JavaScript API，密钥从环境变量读取。
- 大模型使用可配置的 OpenAI 兼容接口；未配置时调用本地模板服务。

## 6. 后端模块边界

| 模块 | 职责 |
|---|---|
| `auth` | 注册、登录、JWT、密码修改和账号状态检查 |
| `users` | 个人资料和管理员用户管理 |
| `pets` | 宠物档案、照片和封面管理 |
| `cases` | 走失事件、状态和所有权校验 |
| `sightings` | 独立线索、照片和有效性状态 |
| `matching` | 候选筛选、评分、解释、重算和人工核实 |
| `search` | 搜寻区域、任务认领、进度和反馈 |
| `reunions` | 寻回确认存储过程和结果查询 |
| `notifications` | 高匹配、任务及寻回通知 |
| `ai_assist` | 描述优化、线索摘要、超时和本地降级 |
| `admin` | 汇总统计与内容状态管理 |

模块通过服务接口协作，不允许路由层直接拼接复杂 SQL 或跨模块修改多张表。

## 7. 核心业务流程

### 7.1 发布与匹配

1. 用户创建宠物档案并上传照片。
2. 用户发布走失事件，填写时间、地址、坐标和描述。
3. 其他用户独立提交目击线索，不选择具体走失事件。
4. 新事件或新线索触发候选筛选与规则评分。
5. 分数达到 40 的结果写入匹配表，75 分以上生成通知。
6. 主人查看分项得分、距离和解释，并确认或排除候选。

### 7.2 协作搜寻

1. 事件主人以中心坐标和半径创建搜寻区域。
2. 系统为每个区域建立一个可认领任务。
3. 志愿者认领任务并更新为进行中。
4. 志愿者提交搜寻反馈并完成任务；放弃后任务恢复为可认领。
5. 同一区域同一时刻只能有一个认领者。

### 7.3 确认寻回

1. 主人提交寻回时间、地点、发现者、方式和备注。
2. 存储过程锁定走失事件并验证其仍处于寻找中。
3. 写入唯一的寻回记录。
4. 更新事件为已寻回，关闭未完成搜寻区域和任务。
5. 生成寻回通知。
6. 任一步失败时整个事务回滚。

## 8. 数据模型

### 8.1 `users`

保存账号与权限。主要字段为 `user_id`、`username`、`password_hash`、`phone`、`email`、`avatar_url`、`role`、`status`、`created_at`、`updated_at`。

- `username` 唯一且非空。
- `phone`、`email` 在填写时分别唯一。
- `role` 只能为 `USER` 或 `ADMIN`。
- `status` 只能为 `ACTIVE` 或 `DISABLED`。
- 密码只保存强哈希，不保存明文或可逆密文。

### 8.2 `pets`

保存宠物档案。主要字段为 `pet_id`、`owner_id`、`name`、`species`、`breed`、`primary_color`、`secondary_color`、`gender`、`size`、`birth_date`、`distinctive_features`、`status` 和时间戳。

- `owner_id` 外键关联用户。
- `species`、颜色、性别和体型采用结构化字段，特征描述保留自由文本。
- 有历史走失事件的宠物不物理删除，只修改状态。

### 8.3 `pet_photos`

字段为 `photo_id`、`pet_id`、`photo_url`、`is_cover`、`sort_order`、`created_at`。照片删除随宠物受限处理；首张照片由触发器自动设置为封面，应用服务保证每只宠物最多一个封面。

### 8.4 `lost_cases`

字段为 `case_id`、`pet_id`、`publisher_id`、`lost_time`、`latitude`、`longitude`、`address`、`description`、`contact_phone`、`status`、`created_at`、`updated_at`、`closed_at`。

- 宠物主人通过 `pets.owner_id` 获取，`publisher_id` 仅记录实际创建事件的账号。
- 纬度使用 `DECIMAL(10,7)`，经度使用 `DECIMAL(10,7)`，并检查合法范围。
- `status` 为 `SEARCHING`、`REUNITED` 或 `CLOSED`。

### 8.5 `sightings`

字段为 `sighting_id`、`reporter_id`、`species`、`breed_guess`、`primary_color`、`secondary_color`、`gender_guess`、`size_guess`、`seen_time`、`latitude`、`longitude`、`address`、`direction`、`confidence`、`description`、`status` 和时间戳。

- 本表没有 `case_id`。
- `confidence` 为 1 至 5 的自评等级，不直接等同于匹配概率。
- `status` 为 `ACTIVE`、`HIDDEN` 或 `INVALID`。
- 目击时间不能晚于当前时间。

### 8.6 `sighting_photos`

字段为 `photo_id`、`sighting_id`、`photo_url`、`sort_order`、`created_at`。删除线索时由外键级联删除其照片元数据，磁盘文件由服务层同步清理。

### 8.7 `case_sighting_matches`

字段为 `match_id`、`case_id`、`sighting_id`、`appearance_score`、`distance_score`、`time_score`、`total_score`、`distance_km`、`match_reason`、`algorithm_version`、`review_status`、`reviewed_by`、`generated_at`、`reviewed_at`。

- `(case_id, sighting_id)` 唯一。
- 四个得分范围均为 0 至 100。
- `review_status` 为 `PENDING`、`CONFIRMED` 或 `REJECTED`。
- 本表实现走失事件与目击线索的多对多关系。

### 8.8 `search_areas`

字段为 `area_id`、`case_id`、`created_by`、`area_name`、`center_latitude`、`center_longitude`、`radius_meters`、`description`、`status`、`created_at`、`updated_at`。

- 搜寻区域采用圆形表示，半径必须为正数且不超过 20 千米。
- `status` 为 `OPEN` 或 `CLOSED`。

### 8.9 `search_tasks`

字段为 `task_id`、`area_id`、`volunteer_id`、`status`、`accepted_at`、`started_at`、`completed_at`、`report`、`updated_at`。

- `area_id` 唯一，每个区域对应一个可重复释放和认领的当前任务。
- `volunteer_id` 在任务可认领时为空。
- `status` 为 `AVAILABLE`、`CLAIMED`、`IN_PROGRESS`、`COMPLETED` 或 `CANCELLED`。
- 认领时通过行锁和条件更新保证并发安全。

### 8.10 `reunion_records`

字段为 `reunion_id`、`case_id`、`finder_id`、`confirmed_by`、`reunion_time`、`latitude`、`longitude`、`address`、`method`、`note`、`created_at`。

- `case_id` 唯一，保证一个事件只有一条正式寻回记录。
- `finder_id` 可为空，以支持发现者不是注册用户的情况。

### 8.11 `notifications`

字段为 `notification_id`、`user_id`、`type`、`title`、`content`、`related_case_id`、`related_match_id`、`related_task_id`、`is_read`、`created_at`、`read_at`。

- 三个关联字段均可为空，并分别设置外键。
- 通知类型包括高匹配、任务状态和寻回结果。

## 9. 关系与删除策略

- 用户一对多拥有宠物、发布事件、提交线索和认领任务。
- 宠物一对多拥有照片和走失事件。
- 走失事件与目击线索通过匹配表形成多对多关系。
- 走失事件一对多拥有搜寻区域。
- 搜寻区域与当前任务为一对一关系。
- 走失事件与寻回记录为零或一对一关系。

用户、宠物和事件存在历史业务记录时采用状态停用，不做级联物理删除。纯从属照片和通知允许在父记录删除时级联处理。关键业务外键默认使用 `RESTRICT`，避免误删历史事实。

## 10. 数据库对象

### 10.1 视图

- `v_active_case_summary`：寻找中事件、宠物、封面照片、线索数量和任务进度。
- `v_case_match_rankings`：为每个事件按总分和时间排列候选线索。
- `v_search_task_progress`：事件、区域、志愿者和任务状态汇总。

### 10.2 函数

- `fn_distance_km(lat1, lon1, lat2, lon2)`：使用 Haversine 公式计算两点距离。

### 10.3 存储过程

- `sp_confirm_reunion(...)`：锁定事件、验证权限所需状态、插入寻回记录、更新事件、关闭任务并生成通知。过程使用显式事务和异常回滚处理。

### 10.4 触发器

- `trg_match_high_score_notify`：新匹配达到 75 分时生成主人通知。
- `trg_pet_photo_first_cover`：宠物首次上传照片时自动设置封面。
- `trg_case_closed_at`：事件离开寻找中状态时自动填写关闭时间。

### 10.5 索引

- 所有外键建立普通索引。
- `lost_cases(status, lost_time)` 支持公开列表。
- `sightings(status, seen_time)` 支持有效线索筛选。
- 走失和目击表分别建立坐标组合索引，用于候选范围预筛选。
- `case_sighting_matches(case_id, review_status, total_score)` 支持候选排名。
- `search_tasks(status, volunteer_id)` 支持可认领和个人任务查询。
- `notifications(user_id, is_read, created_at)` 支持消息中心。

最终通过 `EXPLAIN` 对关键查询记录索引使用情况，并在报告中保存结果。

## 11. 匹配算法

### 11.1 候选过滤

候选必须满足：事件为 `SEARCHING`、线索为 `ACTIVE`、物种一致、目击时间不早于走失时间、距离不超过候选上限。

### 11.2 分项评分

```text
total_score = appearance_score * 0.50
            + distance_score   * 0.30
            + time_score       * 0.20
```

- 外观得分比较品种、主次毛色、性别、体型和特征关键词。
- 距离得分由 `fn_distance_km` 的结果分段计算。
- 时间得分根据走失至目击的时间间隔分段计算。
- 规则和分段常量集中保存在匹配服务配置中，算法版本初始为 `rule-v1`。

分数达到 75 为高匹配，55 至 74.99 为中匹配，40 至 54.99 为低匹配，低于 40 不落库。分数只用于候选排序，不表示真实概率，也不自动认定宠物身份。

大模型不参与数值评分，只把结构化结果转换为易读摘要，避免不可复现的判断影响核心业务。

## 12. API 设计

API 使用 `/api/v1` 前缀，主要资源如下：

- `/auth/register`、`/auth/login`、`/auth/me`
- `/pets`、`/pets/{id}`、`/pets/{id}/photos`
- `/cases`、`/cases/{id}`、`/cases/{id}/matches`
- `/sightings`、`/sightings/{id}`、`/sightings/{id}/photos`
- `/matches/{id}/review`、`/cases/{id}/recalculate`
- `/cases/{id}/areas`、`/tasks`、`/tasks/{id}/claim`、`/tasks/{id}/progress`
- `/cases/{id}/reunion`
- `/notifications`、`/notifications/{id}/read`
- `/ai/optimize-description`、`/ai/summarize-case`
- `/admin/statistics`、`/admin/users/{id}/status`、`/admin/content/{type}/{id}/status`

列表接口统一支持分页；公开查询只返回允许公开的字段。创建返回 201，参数错误返回 422，未登录返回 401，无权限返回 403，资源不存在返回 404，并发冲突返回 409。

## 13. 前端信息架构与视觉设计

主要页面为：首页、登录注册、走失列表、走失详情、宠物档案、发布走失、提交目击、候选匹配中心、地图协作搜寻、消息中心、个人中心和管理员控制台。

视觉方向采用“温暖公益”：

- 主色为珊瑚橙，背景使用奶油白，辅助色使用浅绿色。
- 圆角卡片、柔和阴影和清晰留白营造友好感。
- 首页采用“行动优先”布局：情感化标题后立即提供发布走失、提交目击和参与搜寻三个入口。
- 首页依次展示附近事件、地图预览、平台数据和简短重逢信息。
- 走失详情页将宠物资料和核心操作置于首屏，匹配、时间轴、地图和任务采用分区展示。
- 桌面端是答辩主要目标，同时保证手机宽度下表单和卡片正常单列显示。

视觉原型会保留在本地 brainstorming 会话中，但 `.superpowers` 不纳入正式代码仓库。

## 14. 异常处理与降级

统一错误响应格式为：

```json
{
  "code": "TASK_ALREADY_CLAIMED",
  "message": "该搜寻区域已被其他志愿者认领",
  "details": {}
}
```

- 前端即时校验，后端执行最终校验。
- 图片限制 MIME 类型、扩展名、单张大小、数量和随机文件名。
- 数据库异常转为稳定的业务错误，不向客户端暴露 SQL 和调用栈。
- 任务并发冲突返回 409；关键事务失败全部回滚。
- 地图加载失败后显示地址、坐标和时间列表。
- 大模型未配置、超时或返回非法内容时使用本地模板。
- 服务端日志记录请求标识、错误类别和必要上下文，不记录密码和令牌。

## 15. 安全与隐私

- 密码使用 Werkzeug 或 bcrypt 的强哈希。
- JWT 密钥、数据库密码、地图密钥和模型密钥只从环境变量读取。
- 上传目录不执行脚本，并对文件名和访问路径做限制。
- 联系方式仅对登录用户显示，公开列表进行脱敏。
- ORM 参数绑定或参数化 SQL 防止注入。
- 管理员接口和资源所有权在后端逐项检查。
- 正式提交包提供 `.env.example`，不包含真实密钥。

## 16. 测试设计

### 16.1 数据库测试

验证主外键、唯一约束、检查约束、删除策略、索引、视图、函数、触发器、存储过程、事务成功和事务回滚。

### 16.2 后端测试

使用 `pytest` 覆盖认证、资源所有权、CRUD、匹配分段边界、人工核实、并发认领、重复寻回、上传限制和降级服务。

### 16.3 前端测试

使用 Vitest 覆盖关键表单、状态组件、路由保护和错误提示。使用 Playwright 执行一条完整演示流程。

### 16.4 初始化数据

`seed.sql` 提供 8 个普通用户、1 个管理员、12 个宠物、6 个走失事件、15 条目击线索、多组高、中、低匹配、8 个搜寻区域、不同状态的任务、寻回案例和通知记录。演示账号和密码写入 README，密码以哈希形式进入数据库。

## 17. 目录结构

```text
PawFinder/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── models/
│   │   ├── services/
│   │   ├── extensions.py
│   │   └── create_app.py
│   ├── tests/
│   ├── uploads/
│   ├── requirements.txt
│   └── run.py
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   ├── layouts/
│   │   ├── router/
│   │   ├── stores/
│   │   ├── styles/
│   │   └── views/
│   └── package.json
├── database/
│   ├── schema.sql
│   ├── seed.sql
│   ├── objects.sql
│   ├── queries.sql
│   └── tests.sql
├── docs/
│   ├── requirements.md
│   ├── er-diagram.drawio
│   ├── test-cases.md
│   └── superpowers/specs/
├── .env.example
├── .gitignore
└── README.md
```

## 18. 验收演示

固定演示故事如下：

1. 主人登录并查看宠物档案。
2. 主人发布宠物走失事件。
3. 另一账号提交独立目击线索。
4. 系统生成高分匹配并通知主人。
5. 主人在匹配中心查看分项得分、地图和时间轴，确认候选。
6. 主人创建搜寻区域，志愿者认领并提交反馈。
7. 主人确认寻回，数据库事务更新所有相关状态。
8. 管理员控制台显示新的统计结果。
9. 答辩时补充演示约束失败、事务回滚和 `EXPLAIN` 索引结果。

## 19. 交付物

- 可运行的前端、后端与 MySQL 数据库。
- 建表、对象、测试数据、典型查询和数据库测试 SQL。
- 完整 E-R 图和数据字典。
- 后端、前端和端到端测试。
- 环境配置示例与启动说明。
- 课程设计报告正文素材、测试记录和系统截图。
- 答辩 PPT 内容、演示脚本与系统视频录制清单。

本设计是后续实现计划的唯一范围基线。新增功能必须先判断是否影响截止日期、数据库规范和演示稳定性。

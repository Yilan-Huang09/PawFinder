# PawFinder 寻爪计划

PawFinder 是一个基于时空线索匹配的宠物走失协同搜寻系统，也是可完整运行、可重复部署的数据库课程设计。系统连接主人、目击者与志愿者，通过结构化外观、时间和距离生成可解释匹配，并用事务保证任务认领与寻回的一致性。演示数据以重庆市北碚区、西南大学周边为背景。

## 已实现功能

- 宠物档案、照片、走失事件与独立目击线索
- 外观 45% + 距离 30% + 时间 25% 的 `rule-v1` 可解释匹配
- 搜寻区域、原子认领、进度、释放与完成反馈
- `sp_confirm_reunion` 一次完成寻回、事件关闭和任务归档
- 通知、个人中心、管理员统计和内容治理
- 无密钥开放街图、可选高德地图与本地 AI 模板降级

## 技术架构

```text
Vue 3 + TypeScript + Element Plus
              ↓ REST API / JWT
Flask + SQLAlchemy + Pydantic
              ↓
MySQL 8（11 张 3NF 业务表 + 视图/函数/触发器/存储过程）
```

## 方式一：Docker 一键运行（推荐验收）

安装 Docker Desktop 后，在项目根目录执行：

```powershell
Copy-Item .env.example .env
docker compose up --build -d
docker compose ps
```

首次启动会自动创建数据库对象并导入固定演示数据。浏览器访问 `http://127.0.0.1:8080`，统一健康检查地址为 `http://127.0.0.1:8080/api/v1/health`。

停止服务：

```powershell
docker compose down
```

如需彻底清空 Docker 中的数据库并重新导入种子数据，执行以下命令。该命令只删除本项目的 Docker 数据卷，但其中数据不可恢复：

```powershell
docker compose down -v
docker compose up --build -d
```

容器组成、端口和故障排查见 [Docker 部署说明](docs/docker-deployment.md)。

## 方式二：Windows 本地运行

要求 MySQL 8.0.16+、Python 3.11+、Node.js 20+。复制 `.env.example` 为 `.env` 并修改连接和密钥，然后运行：

```powershell
./scripts/setup.ps1 -Seed
./scripts/start-dev.ps1
```

`-Seed` 只应对空数据库使用；默认初始化不会删除已有数据。访问 `http://127.0.0.1:5173`，API 健康检查为 `http://127.0.0.1:5000/api/v1/health`。

数据库也提供统一入口 `database/bootstrap.sql`。从项目根目录执行下面的命令，可按 `schema.sql → objects.sql → seed.sql` 完整重建一个空数据库：

```powershell
mysql --host=127.0.0.1 --user=root --password --default-character-set=utf8mb4 --execute="source database/bootstrap.sql"
```

## 演示账号

种子账号统一密码为 `PawFinder123!`。主人账号 `linyu`，管理员账号 `admin`；仅用于本地课程演示。

## 测试

```powershell
./.venv/Scripts/python.exe -m pytest backend/tests -q
npm test --prefix frontend
npm run build --prefix frontend
npm run test:e2e
```

提交或录屏前可运行统一自检：

```powershell
./scripts/preflight.ps1
```

系统含 11 张第三范式业务表、3 个视图、距离函数、完整性触发器和寻回事务存储过程。建库顺序为 `schema.sql` → `objects.sql` → `seed.sql`。

## 地图说明

- 未配置密钥时，首页和事件详情直接显示 OpenStreetMap 真实地图，同时保留地址与坐标列表。
- 配置 `VITE_AMAP_JS_KEY` 后，事件详情优先加载高德地图并显示事件、目击与搜寻区域。
- 外部地图加载失败时自动回退到开放街图和坐标列表，不影响核心业务。

## 文档

- [需求说明](docs/requirements.md)
- [数据字典](docs/data-dictionary.md)
- [E-R 图](docs/er-diagram.drawio)
- [报告提纲](docs/report-outline.md)
- [答辩提纲](docs/presentation-outline.md)
- [演示脚本](docs/demo-script.md)
- [录屏清单](docs/video-checklist.md)
- [测试用例](docs/test-cases.md)
- [Docker 部署说明](docs/docker-deployment.md)
- [最终提交清单](docs/submission-checklist.md)

仓库不提交 `.env`、真实密钥、上传文件或构建产物。公开联系方式自动脱敏，资源所有权和管理员权限均由后端校验。

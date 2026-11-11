# PawFinder 寻爪计划

PawFinder 是一个基于时空线索匹配的宠物走失协同搜寻系统，也是可完整运行的数据库课程设计。系统连接主人、目击者与志愿者，通过结构化外观、时间和距离生成可解释匹配，并用事务保证任务认领与寻回的一致性。

## 已实现功能

- 宠物档案、照片、走失事件与独立目击线索
- 外观 45% + 距离 30% + 时间 25% 的 `rule-v1` 可解释匹配
- 搜寻区域、原子认领、进度、释放与完成反馈
- `sp_confirm_reunion` 一次完成寻回、事件关闭和任务归档
- 通知、个人中心、管理员统计和内容治理
- 无地图密钥坐标列表与本地 AI 模板降级

## 快速开始

要求 MySQL 8.0.16+、Python 3.11+、Node.js 20+。复制 `.env.example` 为 `.env` 并修改连接和密钥，然后运行：

```powershell
./scripts/setup.ps1 -Seed
./scripts/start-dev.ps1
```

`-Seed` 只应对空数据库使用；默认初始化不会删除已有数据。访问 `http://127.0.0.1:5173`，API 健康检查为 `http://127.0.0.1:5000/api/v1/health`。

## 演示账号

种子账号统一密码为 `PawFinder123!`。主人账号 `linyu`，管理员账号 `admin`；仅用于本地课程演示。

## 测试

```powershell
./.venv/Scripts/python.exe -m pytest backend/tests -q
npm test --prefix frontend
npm run build --prefix frontend
npm run test:e2e
```

系统含 11 张第三范式业务表、3 个视图、距离函数、完整性触发器和寻回事务存储过程。建库顺序为 `schema.sql` → `objects.sql` → `seed.sql`。

## 文档

- [需求说明](docs/requirements.md)
- [数据字典](docs/data-dictionary.md)
- [E-R 图](docs/er-diagram.drawio)
- [报告提纲](docs/report-outline.md)
- [答辩提纲](docs/presentation-outline.md)
- [演示脚本](docs/demo-script.md)
- [录屏清单](docs/video-checklist.md)
- [测试用例](docs/test-cases.md)

仓库不提交 `.env`、真实密钥、上传文件或构建产物。公开联系方式自动脱敏，资源所有权和管理员权限均由后端校验。

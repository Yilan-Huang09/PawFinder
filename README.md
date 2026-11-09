# PawFinder 寻爪计划

PawFinder 是一个面向宠物主人、目击者和志愿者的协同寻宠数据库课程设计项目。系统通过结构化外观信息、时间和地理距离生成可解释的候选线索，并支持地图搜寻任务与事务化寻回确认。

## 技术栈

- MySQL 8.0.16+（推荐 8.0.36 或更新的 8.0 版本）
- Python 3.11+
- Flask 3、SQLAlchemy 2、Pydantic 2
- Node.js 20+、Vue 3、Vite、TypeScript

当前开发环境已检测到 Python 3.11.9、Node.js 24.12.0、npm 11.19.1 和 MySQL 客户端 8.0.11。MySQL 8.0.11 不执行 `CHECK` 约束，因此本项目会同时使用数据库触发器与后端校验保证兼容；正式演示仍推荐升级到 MySQL 8.0.16 以上。

## 项目状态

项目正在按以下设计与实施计划开发：

- [系统设计](docs/superpowers/specs/2026-11-09-pawfinder-design.md)
- [实施计划](docs/superpowers/plans/2026-11-09-pawfinder-implementation.md)

## 目录

```text
backend/    Flask API 与测试
frontend/   Vue 3 前端
database/   MySQL 建表、对象、测试数据与验证 SQL
docs/       需求、设计、测试与答辩材料
```

## 环境配置

复制 `.env.example` 为 `.env`，填写本机数据库账号和密钥。不要把 `.env` 提交到 Git。

```powershell
Copy-Item .env.example .env
```

数据库、后端和前端的完整安装与启动步骤会随对应模块完成后补充到本文件。

## 安全说明

- 仓库不包含真实数据库密码、JWT 密钥、地图密钥或模型密钥。
- 地图和大模型未配置时，系统使用坐标列表与本地文本模板降级运行。
- 演示账号只用于本地课程环境。

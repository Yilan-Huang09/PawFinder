# PawFinder Docker 部署说明

## 1. 服务组成

| 服务 | 镜像/构建 | 容器端口 | 本机端口 | 职责 |
|---|---|---:|---:|---|
| `web` | Vue 构建产物 + Nginx | 80 | 8080 | 静态页面、SPA 路由、反向代理 API |
| `backend` | Python 3.12 + Gunicorn | 5000 | 不直接暴露 | Flask REST API、鉴权与业务服务 |
| `mysql` | MySQL 8.4 | 3306 | 3307 | 业务数据、视图、函数、触发器和存储过程 |

浏览器只需访问 `http://127.0.0.1:8080`。Nginx 将 `/api/` 请求转发给 Flask，因此前后端保持同源，不需要在浏览器中暴露数据库或后端容器端口。

## 2. 首次启动

```powershell
Copy-Item .env.example .env
docker compose up --build -d
docker compose ps
```

MySQL 健康后，Compose 才会启动后端；后端健康后，才会启动 Web 服务。首次创建数据卷时，MySQL 按以下顺序执行：

1. `database/schema.sql`
2. `database/objects.sql`
3. `database/seed.sql`

## 3. 验证

```powershell
Invoke-RestMethod http://127.0.0.1:8080/api/v1/health
docker compose ps
docker compose logs --tail 80 backend
```

预期健康接口返回 `status: ok`，三个服务均为 `healthy`。

## 4. 常用配置

`.env` 中与 Docker 相关的变量：

- `WEB_PORT`：网站端口，默认 `8080`。
- `MYSQL_PORT`：本机访问容器 MySQL 的端口，默认 `3307`，避免与本地 MySQL 的 `3306` 冲突。
- `MYSQL_ROOT_PASSWORD`、`MYSQL_PASSWORD`：仅用于本地课程演示，提交公开仓库前应改为随机值。
- `JWT_SECRET_KEY`：登录令牌签名密钥。
- `VITE_AMAP_JS_KEY`：可选；留空时使用 OpenStreetMap。

若密码包含 `@`、`:`、`/` 等 URL 特殊字符，需要先进行 URL 编码，或保持课程演示默认密码。

## 5. 停止与重建

保留数据库停止：

```powershell
docker compose down
```

重新构建应用镜像：

```powershell
docker compose up --build -d
```

彻底重置数据库：

```powershell
docker compose down -v
docker compose up --build -d
```

`down -v` 会删除 `pawfinder_mysql_data` 数据卷，仅应在确认不需要保留容器数据库时使用。

## 6. 常见问题

- `8080` 被占用：在 `.env` 将 `WEB_PORT` 改为 `8081`，再重新启动。
- `3307` 被占用：修改 `MYSQL_PORT`；容器内部连接不受影响。
- 修改 SQL 后没有重新导入：初始化脚本只在空数据卷执行，请先 `docker compose down -v`。
- 页面可开但接口失败：执行 `docker compose logs backend mysql` 查看数据库连接与初始化日志。
- 地图空白：先检查网络；事件地址和坐标列表仍可用于演示核心流程。

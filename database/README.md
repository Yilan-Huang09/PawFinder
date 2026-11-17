# PawFinder 数据库脚本

## 版本

推荐 MySQL 8.0.16 以上，字符集统一使用 `utf8mb4`。MySQL 8.0.11 至 8.0.15 会解析但不执行 `CHECK` 约束；项目的触发器和后端校验会覆盖关键范围规则，但课程演示应优先使用较新版本。

所有业务 `DATETIME` 均按 `Asia/Shanghai`（UTC+8）本地时间保存。应用连接建立时执行 `SET time_zone = '+08:00'`，前端 `datetime-local` 值不转换为 UTC。

## 计划执行顺序

```text
schema.sql
objects.sql
seed.sql
tests/01_schema_constraints.sql
tests/02_database_objects.sql
tests/03_reunion_transaction.sql
tests/04_seed_expectations.sql
queries.sql
```

从项目根目录可通过统一入口完成前三步：

```powershell
mysql --host=127.0.0.1 --user=root --password --default-character-set=utf8mb4 --execute="source database/bootstrap.sql"
```

`bootstrap.sql` 包含演示数据，只能用于空数据库。Docker Compose 首次创建数据卷时也会自动按前三步初始化。

`schema.sql` 不会删除数据库。重置开发数据库必须使用明确的独立命令，防止误删其他数据。

`seed.sql` 只应在空的 PawFinder 数据库中执行。它会创建 9 个账号、12 个宠物、6 个走失事件、15 条线索、12 个匹配结果和 8 个搜寻任务。

所有演示账号的本地密码均为 `PawFinder123!`。常用账号：

- 管理员：`admin`
- 宠物主人：`linyu`
- 目击者：`witness`
- 志愿者：`zhaomin`

密码以 Werkzeug PBKDF2 哈希写入数据库，不保存明文。

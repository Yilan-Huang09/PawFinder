# PawFinder 数据库脚本

## 版本

推荐 MySQL 8.0.16 以上，字符集统一使用 `utf8mb4`。MySQL 8.0.11 至 8.0.15 会解析但不执行 `CHECK` 约束；项目的触发器和后端校验会覆盖关键范围规则，但课程演示应优先使用较新版本。

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

`schema.sql` 不会删除数据库。重置开发数据库必须使用明确的独立命令，防止误删其他数据。

数据库脚本完成后，本文件会补充创建账号、执行命令、验证结果和故障排查说明。

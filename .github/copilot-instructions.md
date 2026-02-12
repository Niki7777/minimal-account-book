# Copilot 使用说明（针对 minimal-account-book）

目的：帮助 AI 编码代理快速上手本仓库，掌握架构、运行、约定与常用修改点。

概要架构
- 后端：基于 Flask（`app.py`），负责页面渲染与 JSON API（`/api/*`）。
- 数据层：使用 PyMySQL（封装在 `database.py`），返回字典游标（DictCursor）。
- 工具函数：放在 `utils/tools.py`（如 `calculate_min_unit_price`、`validate_date_format`）。
- 模板：Jinja2 模板位于 `templates/`（`index.html`, `list.html`, `manage.html`, `pending.html`, `price.html`）。
- 静态：`static/js/script.js` 与 `static/css/style.css`。前端通过 `API_BASE` 指向 `http://localhost:3000/api`。

运行与调试
- 依赖：参见 `requirements.txt`（Flask, PyMySQL, flask-cors 等）。
- 启动：在已配置好 MySQL 的情况下，运行：

```bash
python app.py
```

- 默认端口：`3000`（可在 `app.py` 中修改 `PORT`）。确保 `config.py` 中 `DB_CONFIG` 指向正确的 MySQL 实例和库名 `minimal_account_book`。

数据与重要表（可在 DB 中验证）
- 主要表：`consumption`（消费记录），同时有 `channels`, `main_types`, `sub_types` 用作管理表。
- `database.py` 中包含插入/删除/查询与管理类函数（例如 `add_channel`, `get_all_main_types` 等）。

项目约定（很重要，AI 请遵守）
- API 响应格式：统一返回 JSON，成功或失败用 `{'success': True/False, 'message': ..., 'data': ...}`。请勿改变该约定。
- 日期格式：统一为 `YYYY-MM-DD`（使用 `utils/tools.py` 中 `get_current_date` 与 `validate_date_format`）。
- 货币/价格值：以浮点数为准，前端/后端均保持两位小数（`round(..., 2)`）。
- DB 连接：使用 `get_db_connection()` 并在使用后关闭 cursor 与 connection。
- 错误处理：后端多处捕获 `pymysql.Error`（或通用 Exception），返回友好错误消息。

常用修改点与示例
- 批量添加接口（示例）：

  POST `/api/consumption/batch` 接收 JSON：
  ```json
  { "list": [ {"content":"...","quantity":1,"totalPrice":9.9,"channel":"..","mainType":"..","subType":"..","unitCoefficient":1,"receiveStatus":"已收货"} ] }
  ```

- 价格查询：GET `/api/consumption/type/<sub_type>` 返回近30天记录，字段含 `min_unit_price`。
- 管理页相关：`/api/channel`, `/api/main-type`, `/api/sub-type`（增删改查已在 `app.py`/`database.py` 对接）。

前端交互要点
- `static/js/script.js` 将 `API_BASE` 指向 `http://localhost:3000/api`，AI 修改后端路由时请同时更新此常量或使用相对路径。
- 模板变量常用：`pending_count`, `channels`, `main_types`, `sub_types`。

安全与运维提示（可发现的现状）
- 当前 `config.py` 中包含明文 DB 配置（用于本地开发）。部署到生产前请改为环境变量或机密管理。
- 未包含认证/权限，适合局域网或本地使用；如需要上线，请加鉴权与 CSRF 防护。

当你作为 AI 编码代理要做什么
- 优先阅读 `app.py` 和 `database.py` 来理解路由与数据流。修改 API 时同时更新 `templates/` 或 `static/js/` 中的调用。 
- 保持 API 响应结构与日期/金额约定一致。若添加新字段，确保前后端模版/JS 都同步。 
- 若要添加 DB 表，先在 `database.py` 增加封装函数，再在 `app.py` 增加路由，并在 `manage.html`/`list.html` 增加前端交互。

我已草拟此文件；如需我把示例变为更详细的“变更模板”或补充数据库建表语句，请回复说明具体需求。

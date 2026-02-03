
# 解决MySQL连接依赖导入问题，适配虚拟环境
try:
    import pymysql
    from pymysql.cursors import DictCursor  # 适配字典格式返回（和config.py一致）
    from pymysql import Error  # MySQL错误捕获
except ImportError as e:
    print(f"⚠️ 导入MySQL依赖失败：{e}")
    print(f"🔧 请在虚拟环境中执行安装命令：pip install pymysql")
    raise SystemExit(1)

from config import MYSQL_CONFIG  # 从根目录config.py导入MySQL配置（无需重复定义）

def get_db_connection():
    """
    获取MySQL数据库连接（核心函数，所有数据库操作都依赖此连接）
    返回：数据库连接对象（成功）/ None（失败）
    """
    connection = None
    try:
        # 连接MySQL（参数完全来自config.py，确保配置一致）
        connection = pymysql.connect(
            host=MYSQL_CONFIG['host'],
            user=MYSQL_CONFIG['user'],
            password=MYSQL_CONFIG['password'],
            database=MYSQL_CONFIG['database'],
            port=MYSQL_CONFIG['port'],
            charset=MYSQL_CONFIG['charset'],
            cursorclass=DictCursor  # 查询结果返回字典格式，Python操作更顺手
        )
        # 验证连接成功
        if connection.open:
            print("✅ MySQL数据库连接成功（数据库：{}）".format(MYSQL_CONFIG['database']))
            return connection
    except Error as err:
        print(f"❌ MySQL连接失败：{err}")
        return None

def init_db():
    """
    初始化MySQL数据库，创建消费项表（第一次运行执行，仅需运行一次）
    表结构完全匹配项目需求，适配MySQL语法（和SQLite区分）
    """
    connection = get_db_connection()
    if not connection:
        print("❌ 数据库连接失败，无法初始化表结构")
        return False

    try:
        cursor = connection.cursor()
        # 创建消费项表（MySQL语法：AUTO_INCREMENT、ENGINE=InnoDB等）
        create_table_sql = '''
        CREATE TABLE IF NOT EXISTS consumption (
            id INT PRIMARY KEY AUTO_INCREMENT COMMENT '消费项唯一ID（自动递增）',
            content VARCHAR(255) NOT NULL COMMENT '消费内容（例：2包抽纸）',
            quantity DECIMAL(10,1) NOT NULL COMMENT '数量（支持小数，例：1.5）',
            total_price DECIMAL(10,2) NOT NULL COMMENT '总价（元，支持小数）',
            channel VARCHAR(50) NOT NULL COMMENT '购买渠道（例：超市、淘宝）',
            main_type VARCHAR(50) NOT NULL COMMENT '账单大类（饮食、日用品等）',
            sub_type VARCHAR(50) NOT NULL COMMENT '细分类型（纸巾、洗发水等）',
            unit_coefficient DECIMAL(10,1) NOT NULL DEFAULT 1.0 COMMENT '最小单位换算系数（默认1）',
            receive_status VARCHAR(20) NOT NULL DEFAULT '已收货' COMMENT '收货状态（已收货/待收货）',
            create_time DATE NOT NULL COMMENT '购买时间（格式：YYYY-MM-DD）',
            statistical_status VARCHAR(20) NOT NULL DEFAULT '计入' COMMENT '统计状态（计入/不计入账单）',
            min_unit_price DECIMAL(10,2) DEFAULT 0.0 COMMENT '最小单位单价（自动计算）',
            tag VARCHAR(20) DEFAULT '' COMMENT '打标（回购/踩雷/待定）',
            evaluate TEXT  COMMENT '文字评价（可选）',
            start_use_time DATE NULL COMMENT '开始使用时间（格式：YYYY-MM-DD，可选）',
            end_use_time DATE NULL COMMENT '结束使用时间（格式：YYYY-MM-DD，可选）',
            daily_average_price DECIMAL(10,2) DEFAULT 0.0 COMMENT '日均价（自动计算）'
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='消费项记录表';
        '''
        # 执行创建表语句（MySQL语法兼容）
        cursor.execute(create_table_sql)
        connection.commit()  # 提交事务（MySQL必须提交才生效）
        print("✅ MySQL表初始化成功！已创建consumption消费项表")
        return True
    except Error as err:
        print(f"❌ 创建表失败：{err}")
        connection.rollback()  # 出错回滚事务
        return False
    finally:
        # 关闭游标和连接（避免资源泄露）
        if connection and connection.open:
            cursor.close()
            connection.close()

# 以下为核心数据操作函数（适配MySQL，供app.py调用）
def delete_consumption(id):
    """删除指定ID的消费项（适配前端删除功能）"""
    connection = get_db_connection()
    if not connection:
        return False
    try:
        cursor = connection.cursor()
        # MySQL删除语法（参数化查询，避免SQL注入）
        cursor.execute('DELETE FROM consumption WHERE id = %s', (id,))
        connection.commit()
        return cursor.rowcount > 0  # 返回是否删除成功（影响行数>0为成功）
    except Error as err:
        print(f"❌ 删除消费项失败：{err}")
        connection.rollback()
        return False
    finally:
        if connection and connection.open:
            cursor.close()
            connection.close()

def get_pending_count():
    """获取待收货消费项数量（适配导航栏计数）"""
    connection = get_db_connection()
    if not connection:
        return 0
    try:
        cursor = connection.cursor()
        cursor.execute('SELECT COUNT(*) AS count FROM consumption WHERE receive_status = %s', ('待收货',))
        result = cursor.fetchone()
        return result['count'] if result else 0
    except Error as err:
        print(f"❌ 查询待收货数量失败：{err}")
        return 0
    finally:
        if connection and connection.open:
            cursor.close()
            connection.close()

def get_tagged_consumption(tag):
    """查询指定打标的消费项（回购/踩雷清单功能）"""
    connection = get_db_connection()
    if not connection:
        return []
    try:
        cursor = connection.cursor()
        cursor.execute(
            'SELECT * FROM consumption WHERE tag = %s AND receive_status = %s ORDER BY create_time DESC',
            (tag, '已收货')
        )
        return cursor.fetchall()  # 返回字典列表，前端直接使用
    except Error as err:
        print(f"❌ 查询{tag}清单失败：{err}")
        return []
    finally:
        if connection and connection.open:
            cursor.close()
            connection.close()

def get_sub_types():
    """获取所有细分类型（适配前端价格查询下拉框）"""
    connection = get_db_connection()
    if not connection:
        return []
    try:
        cursor = connection.cursor()
        cursor.execute('SELECT DISTINCT sub_type FROM consumption ORDER BY sub_type')
        # 提取细分类型列表（适配前端下拉选择）
        return [item['sub_type'] for item in cursor.fetchall()]
    except Error as err:
        print(f"❌ 查询细分类型失败：{err}")
        return []
    finally:
        if connection and connection.open:
            cursor.close()
            connection.close()

# database.py 新增函数
def get_all_consumption():
    """查询所有消费项（供列表页渲染）"""
    connection = get_db_connection()
    if not connection:
        return []
    try:
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM consumption ORDER BY create_time DESC')
        return cursor.fetchall()
    except Error as err:
        print(f"❌ 查询所有消费项失败：{err}")
        return []
    finally:
        if connection and connection.open:
            cursor.close()
            connection.close()

# 测试入口（第一次运行验证连接和表初始化）
if __name__ == '__main__':
    print("🔍 开始验证MySQL连接和表初始化...")
    get_db_connection()
    init_db()
    print("✅ 验证完成，database.py可正常使用！")

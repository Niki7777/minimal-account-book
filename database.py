import pymysql

from config import DB_CONFIG  # 确保config.py有数据库配置

def get_db_connection():
    """获取数据库连接"""
    try:
        connection = pymysql.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database'],
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except pymysql.Error as e:
        print(f"数据库连接失败：{e}")
        return None

# ------------------- 原有函数（保留） -------------------
def delete_consumption(id):
    connection = get_db_connection()
    if not connection:
        return False
    try:
        cursor = connection.cursor()
        cursor.execute('DELETE FROM consumption WHERE id = %s', (id,))
        connection.commit()
        return cursor.rowcount > 0
    except pymysql.Error as e:
        print(f"删除失败：{e}")
        return False
    finally:
        cursor.close()
        connection.close()

def get_pending_count():
    connection = get_db_connection()
    if not connection:
        return 0
    try:
        cursor = connection.cursor()
        cursor.execute('SELECT COUNT(*) as count FROM consumption WHERE receive_status = %s', ('待收货',))
        result = cursor.fetchone()
        return result['count'] if result else 0
    except pymysql.Error as e:
        print(f"查询待收货数量失败：{e}")
        return 0
    finally:
        cursor.close()
        connection.close()

def get_tagged_consumption(tag):
    connection = get_db_connection()
    if not connection:
        return []
    try:
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM consumption WHERE tag = %s ORDER BY create_time DESC', (tag,))
        return cursor.fetchall()
    except pymysql.Error as e:
        print(f"查询标签数据失败：{e}")
        return []
    finally:
        cursor.close()
        connection.close()

def get_sub_types():
    connection = get_db_connection()
    if not connection:
        return []
    try:
        cursor = connection.cursor()
        cursor.execute('SELECT DISTINCT sub_type FROM consumption ORDER BY sub_type')
        result = cursor.fetchall()
        return [item['sub_type'] for item in result]
    except pymysql.Error as e:
        print(f"查询细分类型失败：{e}")
        return []
    finally:
        cursor.close()
        connection.close()

# ------------------- 新增管理函数 -------------------
# 渠道管理
def get_all_channels():
    connection = get_db_connection()
    if not connection:
        return []
    try:
        cursor = connection.cursor()
        cursor.execute('SELECT id, name FROM channels ORDER BY id')
        return cursor.fetchall()
    except pymysql.Error as e:
        print(f"查询渠道失败：{e}")
        return []
    finally:
        cursor.close()
        connection.close()

def add_channel(name):
    connection = get_db_connection()
    if not connection:
        raise Exception("数据库连接失败")
    try:
        cursor = connection.cursor()
        cursor.execute('INSERT INTO channels (name) VALUES (%s)', (name,))
        connection.commit()
    except pymysql.Error as e:
        connection.rollback()
        raise Exception(f"添加渠道失败：{e}")
    finally:
        cursor.close()
        connection.close()

def update_channel(id, name):
    connection = get_db_connection()
    if not connection:
        raise Exception("数据库连接失败")
    try:
        cursor = connection.cursor()
        cursor.execute('UPDATE channels SET name = %s WHERE id = %s', (name, id))
        connection.commit()
        if cursor.rowcount == 0:
            raise Exception("渠道不存在")
    except pymysql.Error as e:
        connection.rollback()
        raise Exception(f"更新渠道失败：{e}")
    finally:
        cursor.close()
        connection.close()

def delete_channel(id):
    connection = get_db_connection()
    if not connection:
        raise Exception("数据库连接失败")
    try:
        cursor = connection.cursor()
        # 检查是否被消费项关联
        cursor.execute('SELECT COUNT(*) as count FROM consumption WHERE channel = (SELECT name FROM channels WHERE id = %s)', (id,))
        if cursor.fetchone()['count'] > 0:
            raise Exception("该渠道已关联消费项，无法删除")
        cursor.execute('DELETE FROM channels WHERE id = %s', (id,))
        connection.commit()
        if cursor.rowcount == 0:
            raise Exception("渠道不存在")
    except pymysql.Error as e:
        connection.rollback()
        raise Exception(f"删除渠道失败：{e}")
    finally:
        cursor.close()
        connection.close()

# 账单大类管理
def get_all_main_types():
    connection = get_db_connection()
    if not connection:
        return []
    try:
        cursor = connection.cursor()
        cursor.execute('SELECT id, name FROM main_types ORDER BY id')
        return cursor.fetchall()
    except pymysql.Error as e:
        print(f"查询大类失败：{e}")
        return []
    finally:
        cursor.close()
        connection.close()

def add_main_type(name):
    connection = get_db_connection()
    if not connection:
        raise Exception("数据库连接失败")
    try:
        cursor = connection.cursor()
        cursor.execute('INSERT INTO main_types (name) VALUES (%s)', (name,))
        connection.commit()
    except pymysql.Error as e:
        connection.rollback()
        raise Exception(f"添加大类失败：{e}")
    finally:
        cursor.close()
        connection.close()

def update_main_type(id, name):
    connection = get_db_connection()
    if not connection:
        raise Exception("数据库连接失败")
    try:
        cursor = connection.cursor()
        cursor.execute('UPDATE main_types SET name = %s WHERE id = %s', (name, id))
        connection.commit()
        if cursor.rowcount == 0:
            raise Exception("大类不存在")
    except pymysql.Error as e:
        connection.rollback()
        raise Exception(f"更新大类失败：{e}")
    finally:
        cursor.close()
        connection.close()

def delete_main_type(id):
    connection = get_db_connection()
    if not connection:
        raise Exception("数据库连接失败")
    try:
        cursor = connection.cursor()
        # 检查关联
        cursor.execute('SELECT COUNT(*) as count FROM consumption WHERE main_type = (SELECT name FROM main_types WHERE id = %s)', (id,))
        if cursor.fetchone()['count'] > 0:
            raise Exception("该大类已关联消费项，无法删除")
        cursor.execute('DELETE FROM main_types WHERE id = %s', (id,))
        connection.commit()
        if cursor.rowcount == 0:
            raise Exception("大类不存在")
    except pymysql.Error as e:
        connection.rollback()
        raise Exception(f"删除大类失败：{e}")
    finally:
        cursor.close()
        connection.close()

# 细分类型管理
def get_all_sub_types():
    connection = get_db_connection()
    if not connection:
        return []
    try:
        cursor = connection.cursor()
        cursor.execute('''
        SELECT st.id, st.name, st.main_type_id, mt.name as main_type_name 
        FROM sub_types st
        LEFT JOIN main_types mt ON st.main_type_id = mt.id
        ORDER BY st.id
        ''')
        return cursor.fetchall()
    except pymysql.Error as e:
        print(f"查询细分类型失败：{e}")
        return []
    finally:
        cursor.close()
        connection.close()

def add_sub_type(name, main_type_id):
    connection = get_db_connection()
    if not connection:
        raise Exception("数据库连接失败")
    try:
        cursor = connection.cursor()
        # 检查大类是否存在
        cursor.execute('SELECT id FROM main_types WHERE id = %s', (main_type_id,))
        if not cursor.fetchone():
            raise Exception("所属大类不存在")
        cursor.execute('INSERT INTO sub_types (name, main_type_id) VALUES (%s, %s)', (name, main_type_id))
        connection.commit()
    except pymysql.Error as e:
        connection.rollback()
        raise Exception(f"添加细分类型失败：{e}")
    finally:
        cursor.close()
        connection.close()

def update_sub_type(id, name, main_type_id):
    connection = get_db_connection()
    if not connection:
        raise Exception("数据库连接失败")
    try:
        cursor = connection.cursor()
        # 检查大类是否存在
        cursor.execute('SELECT id FROM main_types WHERE id = %s', (main_type_id,))
        if not cursor.fetchone():
            raise Exception("所属大类不存在")
        cursor.execute('UPDATE sub_types SET name = %s, main_type_id = %s WHERE id = %s', (name, main_type_id, id))
        connection.commit()
        if cursor.rowcount == 0:
            raise Exception("细分类型不存在")
    except pymysql.Error as e:
        connection.rollback()
        raise Exception(f"更新细分类型失败：{e}")
    finally:
        cursor.close()
        connection.close()

def delete_sub_type(id):
    connection = get_db_connection()
    if not connection:
        raise Exception("数据库连接失败")
    try:
        cursor = connection.cursor()
        # 检查关联
        cursor.execute('SELECT COUNT(*) as count FROM consumption WHERE sub_type = (SELECT name FROM sub_types WHERE id = %s)', (id,))
        if cursor.fetchone()['count'] > 0:
            raise Exception("该细分类型已关联消费项，无法删除")
        cursor.execute('DELETE FROM sub_types WHERE id = %s', (id,))
        connection.commit()
        if cursor.rowcount == 0:
            raise Exception("细分类型不存在")
    except pymysql.Error as e:
        connection.rollback()
        raise Exception(f"删除细分类型失败：{e}")
    finally:
        cursor.close()
        connection.close()
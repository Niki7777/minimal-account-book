
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS  # 解决前端跨域问题（必须导入，否则前端无法调用接口）


# 导入自定义模块（确保路径正确，适配项目结构）
from database import (
    get_db_connection, delete_consumption, get_pending_count,
    get_tagged_consumption, get_sub_types
)
from utils.tools import (
    calculate_min_unit_price, calculate_daily_average_price,
    get_current_date, validate_date_format
)
from pymysql import Error  # 导入MySQL错误类，用于捕获异常

# 初始化Flask应用
app = Flask(__name__)
# 允许前端跨域请求（关键配置，否则前端调用接口会报跨域错误）
CORS(app)
# 后端服务端口（固定为3000，前端代码默认调用此端口，不要修改）
PORT = 3000

# ------------------- 接口1：新增消费项（前端点击「保存消费项」调用）-------------------
@app.route('/api/consumption', methods=['POST'])
def add_consumption():
    try:
        # 1. 获取前端提交的JSON数据（和前端表单字段一一对应）
        data = request.get_json()
        # 2. 提取核心字段，做基础校验（避免空值）
        content = data.get('content')
        quantity = float(data.get('quantity', 1.0))  # 默认为1.0，转换为浮点数
        total_price = float(data.get('totalPrice', 0.0))  # 默认为0.0，转换为浮点数
        channel = data.get('channel')
        main_type = data.get('mainType')  # 前端驼峰命名，后端适配
        sub_type = data.get('subType')    # 前端驼峰命名，后端适配
        unit_coefficient = float(data.get('unitCoefficient', 1.0))  # 换算系数默认1.0
        receive_status = data.get('receiveStatus', '已收货')  # 收货状态默认已收货

        # 基础校验：核心字段不能为空
        if not all([content, channel, main_type, sub_type]):
            return jsonify({
                'success': False,
                'message': '消费内容、购买渠道、账单大类、细分类型不能为空！'
            }), 400  # 400状态码：请求参数错误

        # 3. 自动计算和补充字段（无需前端传入，后端处理）
        create_time = get_current_date()  # 自动填充当前购买日期
        min_unit_price = calculate_min_unit_price(total_price, quantity, unit_coefficient)  # 计算最小单位单价
        statistical_status = '计入' if receive_status == '已收货' else '不计入'  # 统计状态关联收货状态

        # 4. 连接MySQL，插入数据（适配MySQL参数化查询语法：%s占位符）
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': '数据库连接失败，无法添加消费项！'}), 500

        cursor = connection.cursor()
        # MySQL插入SQL语句（字段和consumption表完全对应）
        insert_sql = '''
        INSERT INTO consumption 
        (content, quantity, total_price, channel, main_type, sub_type, unit_coefficient, 
         receive_status, create_time, statistical_status, min_unit_price)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        '''
        # 执行插入操作（参数顺序和SQL字段顺序严格一致）
        cursor.execute(insert_sql, (
            content, quantity, total_price, channel, main_type, sub_type, unit_coefficient,
            receive_status, create_time, statistical_status, min_unit_price
        ))
        connection.commit()  # MySQL必须提交事务才生效
        new_id = cursor.lastrowid  # 获取新增消费项的自增ID

        # 5. 查询新增的完整数据，返回给前端
        cursor.execute('SELECT * FROM consumption WHERE id = %s', (new_id,))
        new_consumption = cursor.fetchone()  # 字典格式，前端直接使用

        # 6. 关闭资源，返回成功信息
        cursor.close()
        connection.close()
        return jsonify({
            'success': True,
            'message': '消费项添加成功！',
            'data': new_consumption
        }), 200  # 200状态码：请求成功

    except Error as err:
        # 捕获MySQL相关错误
        return jsonify({
            'success': False,
            'message': f'添加消费项失败（MySQL错误）：{str(err)}',
            'error': str(err)
        }), 500
    except Exception as e:
        # 捕获其他通用错误
        return jsonify({
            'success': False,
            'message': f'添加消费项失败：{str(e)}',
            'error': str(e)
        }), 500

# ------------------- 接口2：查询所有消费项（前端加载页面、切换列表调用）-------------------
@app.route('/api/consumption', methods=['GET'])
def get_all_consumption():
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': '数据库连接失败，无法查询数据！'}), 500

        cursor = connection.cursor()
        # MySQL查询语句（按购买时间倒序，最新数据排在前面）
        cursor.execute('SELECT * FROM consumption ORDER BY create_time DESC')
        consumption_list = cursor.fetchall()  # 字典列表，前端渲染表格直接使用

        # 关闭资源，返回数据
        cursor.close()
        connection.close()
        return jsonify({
            'success': True,
            'data': consumption_list
        }), 200

    except Error as err:
        return jsonify({
            'success': False,
            'message': f'查询消费项失败（MySQL错误）：{str(err)}',
            'error': str(err)
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'查询消费项失败：{str(e)}',
            'error': str(e)
        }), 500

# ------------------- 接口3：更新消费项（修改状态、打标、评价等调用）-------------------
@app.route('/api/consumption/<int:id>', methods=['PUT'])
def update_consumption(id):
    try:
        # 1. 获取前端修改的数据和消费项ID
        data = request.get_json()
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': '数据库连接失败，无法更新数据！'}), 500

        cursor = connection.cursor()
        # 2. 先查询消费项是否存在
        cursor.execute('SELECT * FROM consumption WHERE id = %s', (id,))
        consumption = cursor.fetchone()
        if not consumption:
            return jsonify({'success': False, 'message': '要修改的消费项不存在！'}), 404

        # 3. 提取修改字段，未修改字段保留原数据
        receive_status = data.get('receiveStatus', consumption['receive_status'])
        tag = data.get('tag', consumption['tag'])
        evaluate = data.get('evaluate', consumption['evaluate'])
        content = data.get('content', consumption['content'])
        quantity = float(data.get('quantity', consumption['quantity']))
        total_price = float(data.get('totalPrice', consumption['total_price']))
        unit_coefficient = float(data.get('unitCoefficient', consumption['unit_coefficient']))
        start_use_time = data.get('startUseTime', consumption['start_use_time'])
        end_use_time = data.get('endUseTime', consumption['end_use_time'])

        # 验证时间格式（若传入时间，必须是YYYY-MM-DD）
        if start_use_time and not validate_date_format(start_use_time):
            return jsonify({'success': False, 'message': '开始使用时间格式错误，需为YYYY-MM-DD！'}), 400
        if end_use_time and not validate_date_format(end_use_time):
            return jsonify({'success': False, 'message': '结束使用时间格式错误，需为YYYY-MM-DD！'}), 400

        # 4. 重新计算相关字段
        min_unit_price = calculate_min_unit_price(total_price, quantity, unit_coefficient)
        daily_average_price = calculate_daily_average_price(
            total_price, start_use_time, end_use_time
        ) if (start_use_time and end_use_time) else consumption['daily_average_price']
        statistical_status = '计入' if receive_status == '已收货' else '不计入'

        # 5. 执行MySQL更新操作
        update_sql = '''
        UPDATE consumption 
        SET content = %s, quantity = %s, total_price = %s, unit_coefficient = %s,
            receive_status = %s, tag = %s, evaluate = %s, start_use_time = %s,
            end_use_time = %s, min_unit_price = %s, daily_average_price = %s,
            statistical_status = %s
        WHERE id = %s
        '''
        cursor.execute(update_sql, (
            content, quantity, total_price, unit_coefficient,
            receive_status, tag, evaluate, start_use_time,
            end_use_time, min_unit_price, daily_average_price,
            statistical_status, id
        ))
        connection.commit()

        # 6. 查询更新后的数据，返回给前端
        cursor.execute('SELECT * FROM consumption WHERE id = %s', (id,))
        updated_consumption = cursor.fetchone()

        # 关闭资源，返回成功信息
        cursor.close()
        connection.close()
        return jsonify({
            'success': True,
            'message': '消费项更新成功！',
            'data': updated_consumption
        }), 200

    except Error as err:
        return jsonify({
            'success': False,
            'message': f'更新消费项失败（MySQL错误）：{str(err)}',
            'error': str(err)
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'更新消费项失败：{str(e)}',
            'error': str(e)
        }), 500

# ------------------- 接口4：删除消费项（前端点击删除按钮调用）-------------------
@app.route('/api/consumption/<int:id>', methods=['DELETE'])
def delete_consumption_api(id):
    try:
        # 调用database.py中的删除函数
        delete_success = delete_consumption(id)
        if delete_success:
            return jsonify({
                'success': True,
                'message': f'消费项（ID：{id}）删除成功！'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': f'消费项（ID：{id}）不存在或删除失败！'
            }), 404
    except Error as err:
        return jsonify({
            'success': False,
            'message': f'删除消费项失败（MySQL错误）：{str(err)}',
            'error': str(err)
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'删除消费项失败：{str(e)}',
            'error': str(e)
        }), 500

# ------------------- 接口5：查询待收货消费项（前端待收货专区调用）-------------------
@app.route('/api/consumption/pending', methods=['GET'])
def get_pending_consumption():
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': '数据库连接失败，无法查询待收货数据！'}), 500

        cursor = connection.cursor()
        cursor.execute(
            'SELECT * FROM consumption WHERE receive_status = %s ORDER BY create_time DESC',
            ('待收货',)
        )
        pending_list = cursor.fetchall()

        cursor.close()
        connection.close()
        return jsonify({
            'success': True,
            'data': pending_list,
            'count': len(pending_list)  # 同时返回待收货数量
        }), 200

    except Error as err:
        return jsonify({
            'success': False,
            'message': f'查询待收货数据失败（MySQL错误）：{str(err)}',
            'error': str(err)
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'查询待收货数据失败：{str(e)}',
            'error': str(e)
        }), 500

# ------------------- 接口6：按细分类型查询历史价格（前端价格查询功能调用）-------------------
@app.route('/api/consumption/type/<sub_type>', methods=['GET'])
def get_price_by_subtype(sub_type):
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': '数据库连接失败，无法查询价格数据！'}), 500

        cursor = connection.cursor()
        # 筛选条件：同一细分类型+已收货+近30天（贴合实际价格查询需求）
        thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        query_sql = '''
        SELECT * FROM consumption 
        WHERE sub_type = %s AND receive_status = %s AND create_time >= %s
        ORDER BY create_time DESC
        '''
        cursor.execute(query_sql, (sub_type, '已收货', thirty_days_ago))
        price_list = cursor.fetchall()

        cursor.close()
        connection.close()
        return jsonify({
            'success': True,
            'data': price_list,
            'count': len(price_list)
        }), 200

    except Error as err:
        return jsonify({
            'success': False,
            'message': f'查询价格数据失败（MySQL错误）：{str(err)}',
            'error': str(err)
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'查询价格数据失败：{str(e)}',
            'error': str(e)
        }), 500

# ------------------- 接口7：查询回购/踩雷清单（前端清单功能调用）-------------------
@app.route('/api/consumption/tag/<tag>', methods=['GET'])
def get_tag_list(tag):
    try:
        # 调用database.py中的查询函数
        tag_list = get_tagged_consumption(tag)
        return jsonify({
            'success': True,
            'data': tag_list,
            'count': len(tag_list)
        }), 200
    except Error as err:
        return jsonify({
            'success': False,
            'message': f'查询{tag}清单失败（MySQL错误）：{str(err)}',
            'error': str(err)
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'查询{tag}清单失败：{str(e)}',
            'error': str(e)
        }), 500
    # app.py 顶部新增导入
from flask import render_template

# 补充页面渲染路由
@app.route('/')
def index():
    """首页（新增消费项）"""
    pending_count = get_pending_count()
    return render_template('index.html', pending_count=pending_count)

@app.route('/list')
def consumption_list():
    """消费列表页"""
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM consumption ORDER BY create_time DESC')
    consumption_list = cursor.fetchall()
    cursor.close()
    connection.close()
    pending_count = get_pending_count()
    return render_template('list.html', consumption_list=consumption_list, pending_count=pending_count)

@app.route('/pending')
def pending_list():
    """待收货列表页"""
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM consumption WHERE receive_status = %s ORDER BY create_time DESC', ('待收货',))
    pending_list = cursor.fetchall()
    cursor.close()
    connection.close()
    pending_count = get_pending_count()
    return render_template('pending.html', pending_list=pending_list, pending_count=pending_count)

@app.route('/price')
def price_query():
    """价格查询页"""
    sub_types = get_sub_types()
    pending_count = get_pending_count()
    return render_template('price.html', sub_types=sub_types, pending_count=pending_count)

# ------------------- 启动Flask服务（项目入口）-------------------
if __name__ == '__main__':
    print(f"🚀 Flask后端服务启动中... 端口：{PORT}")
    print(f"📌 前端可通过 http://localhost:{PORT} 调用接口")
    # 启动服务（debug=True：开发模式，修改代码自动重启，生产环境可改为False）
    app.run(host='0.0.0.0', port=PORT, debug=True)

from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from database import (
    get_db_connection, delete_consumption, get_pending_count,
    get_tagged_consumption, get_sub_types,
    # 新增管理相关函数（需在database.py补充，见下文）
    add_channel, get_all_channels, delete_channel, update_channel,
    add_main_type, get_all_main_types, delete_main_type, update_main_type,
    add_sub_type, get_all_sub_types, delete_sub_type, update_sub_type
)
from utils.tools import (
    calculate_min_unit_price, calculate_daily_average_price,
    get_current_date, validate_date_format
)
from pymysql import Error
import json

# 初始化Flask应用
app = Flask(__name__)
CORS(app)
PORT = 3000

# ------------------- 新增：批量添加消费项接口 -------------------
@app.route('/api/consumption/batch', methods=['POST'])
def batch_add_consumption():
    try:
        data = request.get_json()
        consumption_list = data.get('list', [])
        if not consumption_list:
            return jsonify({
                'success': False,
                'message': '批量添加的消费项列表不能为空！'
            }), 400

        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': '数据库连接失败！'}), 500
        cursor = connection.cursor()
        inserted_ids = []
        insert_sql = '''
        INSERT INTO consumption 
        (content, quantity, total_price, channel, main_type, sub_type, unit_coefficient, 
         receive_status, create_time, statistical_status, min_unit_price)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        '''

        for item in consumption_list:
            # 字段校验
            content = item.get('content')
            quantity = float(item.get('quantity', 1.0))
            total_price = float(item.get('totalPrice', 0.0))
            channel = item.get('channel')
            main_type = item.get('mainType')
            sub_type = item.get('subType')
            if not all([content, channel, main_type, sub_type]):
                connection.rollback()
                cursor.close()
                connection.close()
                return jsonify({
                    'success': False,
                    'message': f'消费项「{content}」的核心字段不能为空！'
                }), 400

            # 自动计算字段
            create_time = get_current_date()
            unit_coefficient = float(item.get('unitCoefficient', 1.0))
            receive_status = item.get('receiveStatus', '已收货')
            min_unit_price = calculate_min_unit_price(total_price, quantity, unit_coefficient)
            statistical_status = '计入' if receive_status == '已收货' else '不计入'

            # 执行插入
            cursor.execute(insert_sql, (
                content, quantity, total_price, channel, main_type, sub_type, unit_coefficient,
                receive_status, create_time, statistical_status, min_unit_price
            ))
            inserted_ids.append(cursor.lastrowid)

        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({
            'success': True,
            'message': f'批量添加{len(inserted_ids)}条消费项成功！',
            'data': inserted_ids
        }), 200

    except Error as err:
        return jsonify({'success': False, 'message': f'MySQL错误：{str(err)}'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': f'批量添加失败：{str(e)}'}), 500

# ------------------- 新增：饼图统计接口 -------------------
@app.route('/api/consumption/statistics', methods=['GET'])
def get_consumption_statistics():
    try:
        # 获取前端筛选的时间范围
        start_date = request.args.get('startDate')
        end_date = request.args.get('endDate')
        
        # 默认：当月1号至今
        if not start_date:
            today = datetime.now()
            start_date = today.replace(day=1).strftime('%Y-%m-%d')
        if not end_date:
            end_date = get_current_date()

        # 验证日期格式
        if not validate_date_format(start_date) or not validate_date_format(end_date):
            return jsonify({'success': False, 'message': '日期格式错误，需为YYYY-MM-DD！'}), 400

        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': '数据库连接失败！'}), 500

        cursor = connection.cursor()
        # 按账单大类统计金额（仅计入已收货）
        query_sql = '''
        SELECT main_type, SUM(total_price) as total_amount 
        FROM consumption 
        WHERE create_time BETWEEN %s AND %s 
        AND receive_status = '已收货' 
        GROUP BY main_type
        '''
        cursor.execute(query_sql, (start_date, end_date))
        statistics = cursor.fetchall()

        # 格式化数据（适配ECharts饼图）
        pie_data = {
            'categories': [item['main_type'] for item in statistics],
            'values': [round(item['total_amount'], 2) for item in statistics]
        }

        cursor.close()
        connection.close()
        return jsonify({
            'success': True,
            'data': pie_data,
            'filter': {'startDate': start_date, 'endDate': end_date}
        }), 200

    except Error as err:
        return jsonify({'success': False, 'message': f'MySQL错误：{str(err)}'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': f'统计失败：{str(e)}'}), 500

# ------------------- 渠道管理接口 -------------------
@app.route('/api/channel', methods=['GET'])
def get_channels():
    try:
        channels = get_all_channels()
        return jsonify({'success': True, 'data': channels}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/channel', methods=['POST'])
def add_channel_api():
    try:
        data = request.get_json()
        name = data.get('name')
        if not name:
            return jsonify({'success': False, 'message': '渠道名称不能为空！'}), 400
        add_channel(name)
        return jsonify({'success': True, 'message': '渠道添加成功！'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/channel/<int:id>', methods=['PUT'])
def update_channel_api(id):
    try:
        data = request.get_json()
        name = data.get('name')
        if not name:
            return jsonify({'success': False, 'message': '渠道名称不能为空！'}), 400
        update_channel(id, name)
        return jsonify({'success': True, 'message': '渠道更新成功！'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/channel/<int:id>', methods=['DELETE'])
def delete_channel_api(id):
    try:
        delete_channel(id)
        return jsonify({'success': True, 'message': '渠道删除成功！'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ------------------- 账单大类管理接口 -------------------
@app.route('/api/main-type', methods=['GET'])
def get_main_types():
    try:
        types = get_all_main_types()
        return jsonify({'success': True, 'data': types}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/main-type', methods=['POST'])
def add_main_type_api():
    try:
        data = request.get_json()
        name = data.get('name')
        if not name:
            return jsonify({'success': False, 'message': '大类名称不能为空！'}), 400
        add_main_type(name)
        return jsonify({'success': True, 'message': '大类添加成功！'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/main-type/<int:id>', methods=['PUT'])
def update_main_type_api(id):
    try:
        data = request.get_json()
        name = data.get('name')
        if not name:
            return jsonify({'success': False, 'message': '大类名称不能为空！'}), 400
        update_main_type(id, name)
        return jsonify({'success': True, 'message': '大类更新成功！'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/main-type/<int:id>', methods=['DELETE'])
def delete_main_type_api(id):
    try:
        delete_main_type(id)
        return jsonify({'success': True, 'message': '大类删除成功！'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ------------------- 细分类型管理接口 -------------------
@app.route('/api/sub-type', methods=['GET'])
def get_sub_types_api():
    try:
        types = get_all_sub_types()
        return jsonify({'success': True, 'data': types}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/sub-type', methods=['POST'])
def add_sub_type_api():
    try:
        data = request.get_json()
        name = data.get('name')
        main_type_id = data.get('mainTypeId')
        if not name or not main_type_id:
            return jsonify({'success': False, 'message': '名称和所属大类不能为空！'}), 400
        add_sub_type(name, main_type_id)
        return jsonify({'success': True, 'message': '细分类型添加成功！'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/sub-type/<int:id>', methods=['PUT'])
def update_sub_type_api(id):
    try:
        data = request.get_json()
        name = data.get('name')
        main_type_id = data.get('mainTypeId')
        if not name or not main_type_id:
            return jsonify({'success': False, 'message': '名称和所属大类不能为空！'}), 400
        update_sub_type(id, name, main_type_id)
        return jsonify({'success': True, 'message': '细分类型更新成功！'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/sub-type/<int:id>', methods=['DELETE'])
def delete_sub_type_api(id):
    try:
        delete_sub_type(id)
        return jsonify({'success': True, 'message': '细分类型删除成功！'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ------------------- 原有接口（保留） -------------------
@app.route('/api/consumption', methods=['POST'])
def add_consumption():
    try:
        data = request.get_json()
        content = data.get('content')
        quantity = float(data.get('quantity', 1.0))
        total_price = float(data.get('totalPrice', 0.0))
        channel = data.get('channel')
        main_type = data.get('mainType')
        sub_type = data.get('subType')
        unit_coefficient = float(data.get('unitCoefficient', 1.0))
        receive_status = data.get('receiveStatus', '已收货')

        if not all([content, channel, main_type, sub_type]):
            return jsonify({'success': False, 'message': '核心字段不能为空！'}), 400

        create_time = get_current_date()
        min_unit_price = calculate_min_unit_price(total_price, quantity, unit_coefficient)
        statistical_status = '计入' if receive_status == '已收货' else '不计入'

        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': '数据库连接失败！'}), 500

        cursor = connection.cursor()
        insert_sql = '''
        INSERT INTO consumption 
        (content, quantity, total_price, channel, main_type, sub_type, unit_coefficient, 
         receive_status, create_time, statistical_status, min_unit_price)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        '''
        cursor.execute(insert_sql, (
            content, quantity, total_price, channel, main_type, sub_type, unit_coefficient,
            receive_status, create_time, statistical_status, min_unit_price
        ))
        connection.commit()
        new_id = cursor.lastrowid

        cursor.execute('SELECT * FROM consumption WHERE id = %s', (new_id,))
        new_consumption = cursor.fetchone()

        cursor.close()
        connection.close()
        return jsonify({
            'success': True,
            'message': '添加成功！',
            'data': new_consumption
        }), 200

    except Error as err:
        return jsonify({'success': False, 'message': f'MySQL错误：{str(err)}'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/consumption', methods=['GET'])
def get_all_consumption():
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': '数据库连接失败！'}), 500

        cursor = connection.cursor()
        cursor.execute('SELECT * FROM consumption ORDER BY create_time DESC')
        consumption_list = cursor.fetchall()

        cursor.close()
        connection.close()
        return jsonify({'success': True, 'data': consumption_list}), 200

    except Error as err:
        return jsonify({'success': False, 'message': f'MySQL错误：{str(err)}'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/consumption/<int:id>', methods=['PUT'])
def update_consumption(id):
    try:
        data = request.get_json()
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': '数据库连接失败！'}), 500

        cursor = connection.cursor()
        cursor.execute('SELECT * FROM consumption WHERE id = %s', (id,))
        consumption = cursor.fetchone()
        if not consumption:
            return jsonify({'success': False, 'message': '消费项不存在！'}), 404

        receive_status = data.get('receiveStatus', consumption['receive_status'])
        tag = data.get('tag', consumption['tag'])
        evaluate = data.get('evaluate', consumption['evaluate'])
        content = data.get('content', consumption['content'])
        quantity = float(data.get('quantity', consumption['quantity']))
        total_price = float(data.get('totalPrice', consumption['total_price']))
        unit_coefficient = float(data.get('unitCoefficient', consumption['unit_coefficient']))
        start_use_time = data.get('startUseTime', consumption['start_use_time'])
        end_use_time = data.get('endUseTime', consumption['end_use_time'])

        if start_use_time and not validate_date_format(start_use_time):
            return jsonify({'success': False, 'message': '开始时间格式错误！'}), 400
        if end_use_time and not validate_date_format(end_use_time):
            return jsonify({'success': False, 'message': '结束时间格式错误！'}), 400

        min_unit_price = calculate_min_unit_price(total_price, quantity, unit_coefficient)
        daily_average_price = calculate_daily_average_price(
            total_price, start_use_time, end_use_time
        ) if (start_use_time and end_use_time) else consumption['daily_average_price']
        statistical_status = '计入' if receive_status == '已收货' else '不计入'

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

        cursor.execute('SELECT * FROM consumption WHERE id = %s', (id,))
        updated_consumption = cursor.fetchone()

        cursor.close()
        connection.close()
        return jsonify({
            'success': True,
            'message': '更新成功！',
            'data': updated_consumption
        }), 200

    except Error as err:
        return jsonify({'success': False, 'message': f'MySQL错误：{str(err)}'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/consumption/<int:id>', methods=['DELETE'])
def delete_consumption_api(id):
    try:
        delete_success = delete_consumption(id)
        if delete_success:
            return jsonify({'success': True, 'message': f'删除成功！'}), 200
        else:
            return jsonify({'success': False, 'message': '消费项不存在！'}), 404
    except Error as err:
        return jsonify({'success': False, 'message': f'MySQL错误：{str(err)}'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/consumption/pending', methods=['GET'])
def get_pending_consumption():
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': '数据库连接失败！'}), 500

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
            'count': len(pending_list)
        }), 200

    except Error as err:
        return jsonify({'success': False, 'message': f'MySQL错误：{str(err)}'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/consumption/type/<sub_type>', methods=['GET'])
def get_price_by_subtype(sub_type):
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': '数据库连接失败！'}), 500

        cursor = connection.cursor()
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
        return jsonify({'success': False, 'message': f'MySQL错误：{str(err)}'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/consumption/tag/<tag>', methods=['GET'])
def get_tag_list(tag):
    try:
        tag_list = get_tagged_consumption(tag)
        return jsonify({
            'success': True,
            'data': tag_list,
            'count': len(tag_list)
        }), 200
    except Error as err:
        return jsonify({'success': False, 'message': f'MySQL错误：{str(err)}'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ------------------- 页面路由改造 -------------------
@app.route('/')
def index():
    """首页：改为饼图统计页面"""
    pending_count = get_pending_count()
    # 获取当月1号作为默认开始时间
    today = datetime.now()
    default_start = today.replace(day=1).strftime('%Y-%m-%d')
    default_end = get_current_date()
    return render_template('index.html', 
                           pending_count=pending_count,
                           default_start=default_start,
                           default_end=default_end)

@app.route('/list')
def consumption_list():
    """消费列表页：新增新增按钮+批量添加弹窗"""
    pending_count = get_pending_count()
    # 获取下拉框选项
    channels = get_all_channels()
    main_types = get_all_main_types()
    sub_types = get_all_sub_types()
    return render_template('list.html', 
                           pending_count=pending_count,
                           channels=channels,
                           main_types=main_types,
                           sub_types=sub_types)

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

@app.route('/manage')
def manage_page():
    """新增管理页面"""
    pending_count = get_pending_count()
    # 获取所有管理数据
    channels = get_all_channels()
    main_types = get_all_main_types()
    sub_types = get_all_sub_types()
    return render_template('manage.html', 
                           pending_count=pending_count,
                           channels=channels,
                           main_types=main_types,
                           sub_types=sub_types)

# ------------------- 启动服务 -------------------
if __name__ == '__main__':
    print(f"🚀 Flask后端服务启动中... 端口：{PORT}")
    print(f"📌 前端可通过 http://localhost:{PORT} 访问")
    app.run(host='0.0.0.0', port=PORT, debug=True)
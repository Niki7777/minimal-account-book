from app.api import api_bp
from flask import request, jsonify
from app.models import Consumption
from app.schemas import ConsumptionCreate, ConsumptionUpdate
from app import db
from datetime import datetime, date
import math
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def parse_purchase_time(time_str):
    """解析购买时间，支持多种格式"""
    if not time_str:
        return None
    
    formats = [
        '%Y-%m-%dT%H:%M',  # ISO格式: 2026-02-18T12:15
        '%Y-%m-%d %H:%M',  # 带空格格式: 2026-02-18 12:15
        '%Y-%m-%d %H:%M:%S',  # 带秒格式: 2026-02-18 12:15:00
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(time_str, fmt)
        except ValueError:
            continue
    
    # 如果所有格式都失败，抛出异常
    raise ValueError(f"时间格式错误: {time_str}，支持的格式: YYYY-MM-DDTHH:MM 或 YYYY-MM-DD HH:MM")

@api_bp.route('/consumption', methods=['GET'])
def get_consumption():
    """获取消费项列表"""
    try:
        logger.info('开始获取消费项列表')
        
        # 获取查询参数
        start_date = request.args.get('startDate')
        end_date = request.args.get('endDate')
        
        # 构建查询
        query = Consumption.query.filter_by(is_deleted=False)
        
        # 添加日期过滤条件
        if start_date:
            from datetime import datetime
            try:
                start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
                query = query.filter(Consumption.create_time >= start_datetime)
                logger.info(f'添加开始日期过滤：{start_date}')
            except ValueError:
                logger.warning(f'开始日期格式错误：{start_date}')
        
        if end_date:
            from datetime import datetime, timedelta
            try:
                # 结束日期设置为当天的23:59:59
                end_datetime = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1) - timedelta(seconds=1)
                query = query.filter(Consumption.create_time <= end_datetime)
                logger.info(f'添加结束日期过滤：{end_date}')
            except ValueError:
                logger.warning(f'结束日期格式错误：{end_date}')
        
        # 执行查询
        consumptions = query.order_by(Consumption.create_time.desc()).all()
        logger.info(f'数据库查询完成，获取到 {len(consumptions)} 条消费项')
        
        # 转换为字典列表
        data = [item.to_dict() for item in consumptions]
        logger.info(f'数据转换完成，准备返回 {len(data)} 条记录')
        
        response = {
            'success': True,
            'data': data
        }
        logger.info('返回消费项列表成功')
        return jsonify(response), 200
    except Exception as e:
        logger.error(f'获取消费项列表失败：{str(e)}', exc_info=True)
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@api_bp.route('/consumption', methods=['POST'])
def create_consumption():
    """创建消费项"""
    try:
        logger.info('开始创建消费项')
        data = request.get_json()
        logger.info(f'接收到的请求数据: {data}')
        
        schema = ConsumptionCreate(**data)
        logger.info(f'数据验证通过，准备创建消费项: {schema.content}')
        
        # 计算最小单位单价
        min_unit_price = schema.total_price / (schema.quantity * schema.unit_coefficient)
        logger.info(f'计算最小单位单价: {min_unit_price}')
        
        # 计算使用天数和日均价格
        daily_average_price = 0.0
        if schema.start_use_time and schema.end_use_time:
            start_date = datetime.strptime(schema.start_use_time, '%Y-%m-%d').date()
            end_date = datetime.strptime(schema.end_use_time, '%Y-%m-%d').date()
            days = (end_date - start_date).days + 1
            if days > 0:
                daily_average_price = schema.total_price / days
                logger.info(f'计算日均价格: {daily_average_price} (使用天数: {days})')
        
        # 处理购买时间
        create_time = datetime.now()
        if schema.purchase_time:
            create_time = parse_purchase_time(schema.purchase_time)
            logger.info(f'使用指定的购买时间: {create_time}')
        else:
            logger.info(f'使用当前时间作为购买时间: {create_time}')
        
        # 创建消费项
        consumption = Consumption(
            content=schema.content,
            quantity=schema.quantity,
            total_price=schema.total_price,
            channel=schema.channel,
            main_type=schema.main_type,
            sub_type=schema.sub_type,
            unit_coefficient=schema.unit_coefficient,
            receive_status=schema.receive_status,
            create_time=create_time,
            statistical_status='计入' if schema.receive_status == '已收货' else '不计入',
            min_unit_price=min_unit_price,
            tag=schema.tag,
            evaluate=schema.evaluate,
            start_use_time=datetime.strptime(schema.start_use_time, '%Y-%m-%d').date() if schema.start_use_time else None,
            end_use_time=datetime.strptime(schema.end_use_time, '%Y-%m-%d').date() if schema.end_use_time else None,
            daily_average_price=daily_average_price
        )
        
        db.session.add(consumption)
        logger.info('准备提交数据库')
        db.session.commit()
        logger.info(f'消费项创建成功，ID: {consumption.id}')
        
        response = {
            'success': True,
            'message': '创建成功！',
            'data': consumption.to_dict()
        }
        logger.info(f'返回创建结果: {response}')
        return jsonify(response), 201
    except Exception as e:
        logger.error(f'创建消费项失败: {str(e)}', exc_info=True)
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@api_bp.route('/consumption/<int:id>', methods=['GET'])
def get_consumption_by_id(id):
    """获取单个消费项"""
    try:
        logger.info(f'开始获取ID为 {id} 的消费项')
        
        # 执行数据库查询
        consumption = Consumption.query.filter_by(id=id, is_deleted=False).first()
        logger.info(f'数据库查询完成，结果: {consumption}')
        
        if not consumption:
            logger.warning(f'消费项不存在，ID: {id}')
            return jsonify({
                'success': False,
                'message': '消费项不存在！'
            }), 404
        
        response_data = consumption.to_dict()
        logger.info(f'获取消费项成功，ID: {id}, 数据: {response_data}')
        
        return jsonify({
            'success': True,
            'data': response_data
        }), 200
    except Exception as e:
        logger.error(f'获取单个消费项失败，ID: {id}, 错误: {str(e)}', exc_info=True)
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@api_bp.route('/consumption/<int:id>', methods=['PUT'])
def update_consumption(id):
    """更新消费项"""
    try:
        logger.info(f'开始更新ID为 {id} 的消费项')
        
        # 执行数据库查询
        consumption = Consumption.query.filter_by(id=id, is_deleted=False).first()
        logger.info(f'数据库查询完成，结果: {consumption}')
        
        if not consumption:
            logger.warning(f'消费项不存在，ID: {id}')
            return jsonify({
                'success': False,
                'message': '消费项不存在！'
            }), 404
        
        data = request.get_json()
        logger.info(f'接收到的更新数据: {data}')
        
        schema = ConsumptionUpdate(**data)
        logger.info('数据验证通过，准备更新字段')
        
        # 更新字段
        if schema.content is not None:
            logger.info(f'更新content: {schema.content}')
            consumption.content = schema.content
        if schema.quantity is not None:
            logger.info(f'更新quantity: {schema.quantity}')
            consumption.quantity = schema.quantity
        if schema.total_price is not None:
            logger.info(f'更新total_price: {schema.total_price}')
            consumption.total_price = schema.total_price
        if schema.channel is not None:
            logger.info(f'更新channel: {schema.channel}')
            consumption.channel = schema.channel
        if schema.main_type is not None:
            logger.info(f'更新main_type: {schema.main_type}')
            consumption.main_type = schema.main_type
        if schema.sub_type is not None:
            logger.info(f'更新sub_type: {schema.sub_type}')
            consumption.sub_type = schema.sub_type
        if schema.unit_coefficient is not None:
            logger.info(f'更新unit_coefficient: {schema.unit_coefficient}')
            consumption.unit_coefficient = schema.unit_coefficient
        if schema.receive_status is not None:
            logger.info(f'更新receive_status: {schema.receive_status}')
            consumption.receive_status = schema.receive_status
            consumption.statistical_status = '计入' if schema.receive_status == '已收货' else '不计入'
        if schema.purchase_time is not None:
            logger.info(f'更新purchase_time: {schema.purchase_time}')
            consumption.create_time = parse_purchase_time(schema.purchase_time)
        if schema.tag is not None:
            logger.info(f'更新tag: {schema.tag}')
            consumption.tag = schema.tag
        if schema.evaluate is not None:
            logger.info(f'更新evaluate: {schema.evaluate}')
            consumption.evaluate = schema.evaluate
        if schema.start_use_time is not None:
            logger.info(f'更新start_use_time: {schema.start_use_time}')
            consumption.start_use_time = datetime.strptime(schema.start_use_time, '%Y-%m-%d').date()
        if schema.end_use_time is not None:
            logger.info(f'更新end_use_time: {schema.end_use_time}')
            consumption.end_use_time = datetime.strptime(schema.end_use_time, '%Y-%m-%d').date()
        if schema.pickup_code is not None:
            logger.info(f'更新pickup_code: {schema.pickup_code}')
            consumption.pickup_code = schema.pickup_code
        
        # 重新计算最小单位单价
        consumption.min_unit_price = consumption.total_price / (consumption.quantity * consumption.unit_coefficient)
        logger.info(f'重新计算最小单位单价: {consumption.min_unit_price}')
        
        # 重新计算日均价格
        if consumption.start_use_time and consumption.end_use_time:
            days = (consumption.end_use_time - consumption.start_use_time).days + 1
            if days > 0:
                consumption.daily_average_price = consumption.total_price / days
                logger.info(f'重新计算日均价格: {consumption.daily_average_price} (使用天数: {days})')
        
        logger.info('准备提交数据库更新')
        db.session.commit()
        logger.info(f'消费项更新成功，ID: {id}')
        
        response_data = consumption.to_dict()
        response = {
            'success': True,
            'message': '更新成功！',
            'data': response_data
        }
        logger.info(f'返回更新结果: {response}')
        return jsonify(response), 200
    except Exception as e:
        logger.error(f'更新消费项失败，ID: {id}, 错误: {str(e)}', exc_info=True)
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@api_bp.route('/consumption/<int:id>', methods=['DELETE'])
def delete_consumption(id):
    """删除消费项（逻辑删除）"""
    try:
        logger.info(f'开始删除ID为 {id} 的消费项')
        
        # 执行数据库查询
        consumption = Consumption.query.filter_by(id=id, is_deleted=False).first()
        logger.info(f'数据库查询完成，结果: {consumption}')
        
        if not consumption:
            logger.warning(f'消费项不存在，ID: {id}')
            return jsonify({
                'success': False,
                'message': '消费项不存在！'
            }), 404
        
        logger.info(f'准备标记消费项为已删除，ID: {id}')
        consumption.is_deleted = True
        
        logger.info('准备提交数据库更新')
        db.session.commit()
        logger.info(f'消费项删除成功，ID: {id}')
        
        response = {
            'success': True,
            'message': '删除成功！'
        }
        logger.info(f'返回删除结果: {response}')
        return jsonify(response), 200
    except Exception as e:
        logger.error(f'删除消费项失败，ID: {id}, 错误: {str(e)}', exc_info=True)
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@api_bp.route('/consumption/pending', methods=['GET'])
def get_pending_consumption():
    """获取待收货列表"""
    try:
        logger.info('开始获取待收货列表')
        
        # 构建查询
        query = Consumption.query.filter_by(
            receive_status='待收货',
            is_deleted=False
        ).order_by(Consumption.create_time.desc())
        logger.info('执行数据库查询')
        
        consumptions = query.all()
        logger.info(f'数据库查询完成，获取到 {len(consumptions)} 条待收货记录')
        
        # 转换为字典列表
        data = [item.to_dict() for item in consumptions]
        logger.info(f'数据转换完成，准备返回 {len(data)} 条记录')
        
        response = {
            'success': True,
            'data': data
        }
        logger.info(f'返回待收货列表成功，共 {len(data)} 条记录')
        return jsonify(response), 200
    except Exception as e:
        logger.error(f'获取待收货列表失败: {str(e)}', exc_info=True)
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@api_bp.route('/consumption/type/<sub_type>', methods=['GET'])
def get_consumption_by_type(sub_type):
    """获取指定统计类型的消费项"""
    try:
        logger.info(f'开始获取统计类型为 {sub_type} 的消费项')
        from datetime import timedelta
        
        # 获取查询参数中的时间范围
        start_date = request.args.get('startDate')
        end_date = request.args.get('endDate')
        logger.info(f'接收到的时间范围参数: startDate={start_date}, endDate={end_date}')
        
        # 构建查询
        query = Consumption.query.filter(
            Consumption.sub_type == sub_type,
            Consumption.receive_status == '已收货',
            Consumption.is_deleted == False
        )
        logger.info('构建基础查询完成')
        
        # 添加时间范围过滤
        if start_date:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.filter(Consumption.create_time >= start_date_obj)
            logger.info(f'添加开始日期过滤: {start_date}')
        
        if end_date:
            # 结束日期需要包含当天的所有时间
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
            end_date_obj = end_date_obj.replace(hour=23, minute=59, second=59)
            query = query.filter(Consumption.create_time <= end_date_obj)
            logger.info(f'添加结束日期过滤: {end_date}')
        
        # 默认查询近30天
        else:
            thirty_days_ago = datetime.now() - timedelta(days=30)
            query = query.filter(Consumption.create_time >= thirty_days_ago)
            logger.info(f'未指定时间范围，默认查询近30天: {thirty_days_ago}')
        
        # 执行查询
        logger.info('执行数据库查询')
        consumptions = query.order_by(Consumption.create_time.desc()).all()
        logger.info(f'数据库查询完成，获取到 {len(consumptions)} 条记录')
        
        # 转换为字典列表
        data = [item.to_dict() for item in consumptions]
        logger.info(f'数据转换完成，准备返回 {len(data)} 条记录')
        
        response = {
            'success': True,
            'data': data,
            'count': len(consumptions)
        }
        logger.info(f'返回统计类型 {sub_type} 的消费项成功，共 {len(data)} 条记录')
        return jsonify(response), 200
    except Exception as e:
        logger.error(f'获取指定统计类型的消费项失败，类型: {sub_type}, 错误: {str(e)}', exc_info=True)
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

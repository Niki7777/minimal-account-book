from app.api import api_bp
from flask import request, jsonify
from app.models import SubType
from app.schemas import SubTypeCreate, SubTypeUpdate
from app import db
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@api_bp.route('/sub-type', methods=['GET'])
def get_sub_types():
    """获取统计类型列表"""
    try:
        logger.info('开始获取统计类型列表')
        
        # 使用get_all_sub_types函数获取所有统计类型（包括consumption表中使用的）
        from app.models.sub_type import get_all_sub_types
        sub_types = get_all_sub_types()
        logger.info(f'数据库查询完成，获取到 {len(sub_types)} 个统计类型')
        
        # 转换为字典列表
        data = [item.to_dict() for item in sub_types]
        logger.info(f'数据转换完成，准备返回 {len(data)} 条记录')
        
        response = {
            'success': True,
            'data': data
        }
        logger.info(f'返回统计类型列表成功，共 {len(data)} 条记录')
        return jsonify(response), 200
    except Exception as e:
        logger.error(f'获取统计类型列表失败: {str(e)}', exc_info=True)
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@api_bp.route('/sub-type', methods=['POST'])
def create_sub_type():
    """创建统计类型"""
    try:
        logger.info('开始创建统计类型')
        data = request.get_json()
        logger.info(f'接收到的请求数据: {data}')
        
        schema = SubTypeCreate(**data)
        logger.info(f'数据验证通过，准备创建统计类型: {schema.name}')
        
        # 检查是否已存在
        existing = SubType.query.filter_by(name=schema.name).first()
        logger.info(f'检查统计类型是否已存在，结果: {existing}')
        
        if existing:
            logger.warning(f'统计类型已存在: {schema.name}')
            return jsonify({
                'success': False,
                'message': '统计类型已存在！'
            }), 400
        
        # 创建统计类型
        sub_type = SubType(name=schema.name)
        db.session.add(sub_type)
        logger.info('准备提交数据库')
        db.session.commit()
        logger.info(f'统计类型创建成功，ID: {sub_type.id}, 名称: {sub_type.name}')
        
        response = {
            'success': True,
            'message': '统计类型添加成功！',
            'data': sub_type.to_dict()
        }
        logger.info(f'返回创建结果: {response}')
        return jsonify(response), 201
    except Exception as e:
        logger.error(f'创建统计类型失败: {str(e)}', exc_info=True)
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@api_bp.route('/sub-type/<int:id>', methods=['PUT'])
def update_sub_type(id):
    """更新统计类型"""
    try:
        logger.info(f'开始更新ID为 {id} 的统计类型')
        
        # 执行数据库查询
        sub_type = SubType.query.get(id)
        logger.info(f'数据库查询完成，结果: {sub_type}')
        
        if not sub_type:
            logger.warning(f'统计类型不存在，ID: {id}')
            return jsonify({
                'success': False,
                'message': '统计类型不存在！'
            }), 404
        
        data = request.get_json()
        logger.info(f'接收到的更新数据: {data}')
        
        schema = SubTypeUpdate(**data)
        logger.info(f'数据验证通过，准备更新统计类型名称为: {schema.name}')
        
        # 检查是否已存在
        existing = SubType.query.filter(SubType.name == schema.name, SubType.id != id).first()
        logger.info(f'检查统计类型名称是否已存在，结果: {existing}')
        
        if existing:
            logger.warning(f'统计类型名称已存在: {schema.name}')
            return jsonify({
                'success': False,
                'message': '统计类型已存在！'
            }), 400
        
        sub_type.name = schema.name
        logger.info('准备提交数据库更新')
        db.session.commit()
        logger.info(f'统计类型更新成功，ID: {id}, 新名称: {sub_type.name}')
        
        response = {
            'success': True,
            'message': '统计类型更新成功！',
            'data': sub_type.to_dict()
        }
        logger.info(f'返回更新结果: {response}')
        return jsonify(response), 200
    except Exception as e:
        logger.error(f'更新统计类型失败，ID: {id}, 错误: {str(e)}', exc_info=True)
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@api_bp.route('/sub-type/<int:id>', methods=['DELETE'])
def delete_sub_type(id):
    """删除统计类型"""
    try:
        logger.info(f'开始删除ID为 {id} 的统计类型')
        
        # 执行数据库查询
        sub_type = SubType.query.get(id)
        logger.info(f'数据库查询完成，结果: {sub_type}')
        
        if not sub_type:
            logger.warning(f'统计类型不存在，ID: {id}')
            return jsonify({
                'success': False,
                'message': '统计类型不存在！'
            }), 404
        
        logger.info(f'准备删除统计类型: {sub_type.name}')
        db.session.delete(sub_type)
        logger.info('准备提交数据库更新')
        db.session.commit()
        logger.info(f'统计类型删除成功，ID: {id}, 名称: {sub_type.name}')
        
        response = {
            'success': True,
            'message': '统计类型删除成功！'
        }
        logger.info(f'返回删除结果: {response}')
        return jsonify(response), 200
    except Exception as e:
        logger.error(f'删除统计类型失败，ID: {id}, 错误: {str(e)}', exc_info=True)
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

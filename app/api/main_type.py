from app.api import api_bp
from flask import request, jsonify
from app.models import MainType
from app.schemas import MainTypeCreate, MainTypeUpdate
from app import db
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@api_bp.route('/main-type', methods=['GET'])
def get_main_types():
    """获取账单类型列表"""
    try:
        logger.info('开始获取账单类型列表')
        
        # 执行数据库查询
        main_types = MainType.query.all()
        logger.info(f'数据库查询完成，获取到 {len(main_types)} 个账单类型')
        
        # 转换为字典列表
        data = [item.to_dict() for item in main_types]
        logger.info(f'数据转换完成，准备返回 {len(data)} 条记录')
        
        response = {
            'success': True,
            'data': data
        }
        logger.info(f'返回账单类型列表成功，共 {len(data)} 条记录')
        return jsonify(response), 200
    except Exception as e:
        logger.error(f'获取账单类型列表失败: {str(e)}', exc_info=True)
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@api_bp.route('/main-type', methods=['POST'])
def create_main_type():
    """创建账单类型"""
    try:
        logger.info('开始创建账单类型')
        data = request.get_json()
        logger.info(f'接收到的请求数据: {data}')
        
        schema = MainTypeCreate(**data)
        logger.info(f'数据验证通过，准备创建账单类型: {schema.name}')
        
        # 检查是否已存在
        existing = MainType.query.filter_by(name=schema.name).first()
        logger.info(f'检查账单类型是否已存在，结果: {existing}')
        
        if existing:
            logger.warning(f'账单类型已存在: {schema.name}')
            return jsonify({
                'success': False,
                'message': '账单类型已存在！'
            }), 400
        
        # 创建账单类型
        main_type = MainType(name=schema.name)
        db.session.add(main_type)
        logger.info('准备提交数据库')
        db.session.commit()
        logger.info(f'账单类型创建成功，ID: {main_type.id}, 名称: {main_type.name}')
        
        response = {
            'success': True,
            'message': '账单类型添加成功！',
            'data': main_type.to_dict()
        }
        logger.info(f'返回创建结果: {response}')
        return jsonify(response), 201
    except Exception as e:
        logger.error(f'创建账单类型失败: {str(e)}', exc_info=True)
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@api_bp.route('/main-type/<int:id>', methods=['PUT'])
def update_main_type(id):
    """更新账单类型"""
    try:
        logger.info(f'开始更新ID为 {id} 的账单类型')
        
        # 执行数据库查询
        main_type = MainType.query.get(id)
        logger.info(f'数据库查询完成，结果: {main_type}')
        
        if not main_type:
            logger.warning(f'账单类型不存在，ID: {id}')
            return jsonify({
                'success': False,
                'message': '账单类型不存在！'
            }), 404
        
        data = request.get_json()
        logger.info(f'接收到的更新数据: {data}')
        
        schema = MainTypeUpdate(**data)
        logger.info(f'数据验证通过，准备更新账单类型名称为: {schema.name}')
        
        # 检查是否已存在
        existing = MainType.query.filter(MainType.name == schema.name, MainType.id != id).first()
        logger.info(f'检查账单类型名称是否已存在，结果: {existing}')
        
        if existing:
            logger.warning(f'账单类型名称已存在: {schema.name}')
            return jsonify({
                'success': False,
                'message': '账单类型已存在！'
            }), 400
        
        main_type.name = schema.name
        logger.info('准备提交数据库更新')
        db.session.commit()
        logger.info(f'账单类型更新成功，ID: {id}, 新名称: {main_type.name}')
        
        response = {
            'success': True,
            'message': '账单类型更新成功！',
            'data': main_type.to_dict()
        }
        logger.info(f'返回更新结果: {response}')
        return jsonify(response), 200
    except Exception as e:
        logger.error(f'更新账单类型失败，ID: {id}, 错误: {str(e)}', exc_info=True)
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@api_bp.route('/main-type/<int:id>', methods=['DELETE'])
def delete_main_type(id):
    """删除账单类型"""
    try:
        logger.info(f'开始删除ID为 {id} 的账单类型')
        
        # 执行数据库查询
        main_type = MainType.query.get(id)
        logger.info(f'数据库查询完成，结果: {main_type}')
        
        if not main_type:
            logger.warning(f'账单类型不存在，ID: {id}')
            return jsonify({
                'success': False,
                'message': '账单类型不存在！'
            }), 404
        
        logger.info(f'准备删除账单类型: {main_type.name}')
        db.session.delete(main_type)
        logger.info('准备提交数据库更新')
        db.session.commit()
        logger.info(f'账单类型删除成功，ID: {id}, 名称: {main_type.name}')
        
        response = {
            'success': True,
            'message': '账单类型删除成功！'
        }
        logger.info(f'返回删除结果: {response}')
        return jsonify(response), 200
    except Exception as e:
        logger.error(f'删除账单类型失败，ID: {id}, 错误: {str(e)}', exc_info=True)
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

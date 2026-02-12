from app.api import api_bp
from flask import request, jsonify
from app.models import Channel
from app.schemas import ChannelCreate, ChannelUpdate
from app import db
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@api_bp.route('/channel', methods=['GET'])
def get_channels():
    """获取渠道列表"""
    try:
        logger.info('开始获取渠道列表')
        
        # 执行数据库查询
        channels = Channel.query.all()
        logger.info(f'数据库查询完成，获取到 {len(channels)} 个渠道')
        
        # 转换为字典列表
        data = [item.to_dict() for item in channels]
        logger.info(f'数据转换完成，准备返回 {len(data)} 条记录')
        
        response = {
            'success': True,
            'data': data
        }
        logger.info(f'返回渠道列表成功，共 {len(data)} 条记录')
        return jsonify(response), 200
    except Exception as e:
        logger.error(f'获取渠道列表失败: {str(e)}', exc_info=True)
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@api_bp.route('/channel', methods=['POST'])
def create_channel():
    """创建渠道"""
    try:
        logger.info('开始创建渠道')
        data = request.get_json()
        logger.info(f'接收到的请求数据: {data}')
        
        schema = ChannelCreate(**data)
        logger.info(f'数据验证通过，准备创建渠道: {schema.name}')
        
        # 检查是否已存在
        existing = Channel.query.filter_by(name=schema.name).first()
        logger.info(f'检查渠道是否已存在，结果: {existing}')
        
        if existing:
            logger.warning(f'渠道已存在: {schema.name}')
            return jsonify({
                'success': False,
                'message': '渠道已存在！'
            }), 400
        
        # 创建渠道
        channel = Channel(name=schema.name)
        db.session.add(channel)
        logger.info('准备提交数据库')
        db.session.commit()
        logger.info(f'渠道创建成功，ID: {channel.id}, 名称: {channel.name}')
        
        response = {
            'success': True,
            'message': '渠道添加成功！',
            'data': channel.to_dict()
        }
        logger.info(f'返回创建结果: {response}')
        return jsonify(response), 201
    except Exception as e:
        logger.error(f'创建渠道失败: {str(e)}', exc_info=True)
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@api_bp.route('/channel/<int:id>', methods=['PUT'])
def update_channel(id):
    """更新渠道"""
    try:
        logger.info(f'开始更新ID为 {id} 的渠道')
        
        # 执行数据库查询
        channel = Channel.query.get(id)
        logger.info(f'数据库查询完成，结果: {channel}')
        
        if not channel:
            logger.warning(f'渠道不存在，ID: {id}')
            return jsonify({
                'success': False,
                'message': '渠道不存在！'
            }), 404
        
        data = request.get_json()
        logger.info(f'接收到的更新数据: {data}')
        
        schema = ChannelUpdate(**data)
        logger.info(f'数据验证通过，准备更新渠道名称为: {schema.name}')
        
        # 检查是否已存在
        existing = Channel.query.filter(Channel.name == schema.name, Channel.id != id).first()
        logger.info(f'检查渠道名称是否已存在，结果: {existing}')
        
        if existing:
            logger.warning(f'渠道名称已存在: {schema.name}')
            return jsonify({
                'success': False,
                'message': '渠道已存在！'
            }), 400
        
        channel.name = schema.name
        logger.info('准备提交数据库更新')
        db.session.commit()
        logger.info(f'渠道更新成功，ID: {id}, 新名称: {channel.name}')
        
        response = {
            'success': True,
            'message': '渠道更新成功！',
            'data': channel.to_dict()
        }
        logger.info(f'返回更新结果: {response}')
        return jsonify(response), 200
    except Exception as e:
        logger.error(f'更新渠道失败，ID: {id}, 错误: {str(e)}', exc_info=True)
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@api_bp.route('/channel/<int:id>', methods=['DELETE'])
def delete_channel(id):
    """删除渠道"""
    try:
        logger.info(f'开始删除ID为 {id} 的渠道')
        
        # 执行数据库查询
        channel = Channel.query.get(id)
        logger.info(f'数据库查询完成，结果: {channel}')
        
        if not channel:
            logger.warning(f'渠道不存在，ID: {id}')
            return jsonify({
                'success': False,
                'message': '渠道不存在！'
            }), 404
        
        logger.info(f'准备删除渠道: {channel.name}')
        db.session.delete(channel)
        logger.info('准备提交数据库更新')
        db.session.commit()
        logger.info(f'渠道删除成功，ID: {id}, 名称: {channel.name}')
        
        response = {
            'success': True,
            'message': '渠道删除成功！'
        }
        logger.info(f'返回删除结果: {response}')
        return jsonify(response), 200
    except Exception as e:
        logger.error(f'删除渠道失败，ID: {id}, 错误: {str(e)}', exc_info=True)
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

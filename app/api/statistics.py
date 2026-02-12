from app.api import api_bp
from flask import request, jsonify
from app.models import Consumption
from app import db
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@api_bp.route('/consumption/statistics', methods=['GET'])
def get_statistics():
    """获取统计数据"""
    try:
        logger.info('开始获取统计数据')
        start_date = request.args.get('startDate')
        end_date = request.args.get('endDate')
        logger.info(f'接收到的时间范围参数: startDate={start_date}, endDate={end_date}')
        
        if not start_date or not end_date:
            logger.warning('开始日期和结束日期不能为空')
            return jsonify({
                'success': False,
                'message': '开始日期和结束日期不能为空！'
            }), 400
        
        # 转换日期格式
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        end = end.replace(hour=23, minute=59, second=59)
        logger.info(f'转换后的时间范围: start={start}, end={end}')
        
        # 查询数据
        logger.info('开始执行数据库统计查询')
        result = db.session.query(
            Consumption.main_type,
            db.func.sum(Consumption.total_price).label('total_amount')
        ).filter(
            Consumption.create_time.between(start, end),
            Consumption.receive_status == '已收货',
            Consumption.is_deleted == False
        ).group_by(
            Consumption.main_type
        ).all()
        logger.info(f'数据库查询完成，获取到 {len(result)} 条记录')
        
        # 格式化数据
        categories = []
        values = []
        for item in result:
            categories.append(item.main_type)
            values.append(float(item.total_amount))
        logger.info(f'数据格式化完成，categories={categories}, values={values}')
        
        response = {
            'success': True,
            'data': {
                'categories': categories,
                'values': values
            }
        }
        logger.info(f'返回统计数据成功，共 {len(categories)} 个类别')
        return jsonify(response), 200
    except Exception as e:
        logger.error(f'获取统计数据失败: {str(e)}', exc_info=True)
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

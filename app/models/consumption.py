from app import db
from datetime import datetime

class Consumption(db.Model):
    __tablename__ = 'consumption'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.DECIMAL(10, 1), nullable=False)
    total_price = db.Column(db.DECIMAL(10, 2), nullable=False)
    channel = db.Column(db.String(50), nullable=False)
    main_type = db.Column(db.String(50), nullable=False)
    sub_type = db.Column(db.String(50))
    unit_coefficient = db.Column(db.DECIMAL(10, 1), nullable=False, default=1.0)
    receive_status = db.Column(db.String(20), nullable=False, default='已收货')
    create_time = db.Column(db.DateTime, nullable=False, default=datetime.now)
    statistical_status = db.Column(db.String(20), nullable=False, default='计入')
    min_unit_price = db.Column(db.DECIMAL(10, 2), default=0.00)
    tag = db.Column(db.String(20))
    evaluate = db.Column(db.Text)
    start_use_time = db.Column(db.Date)
    end_use_time = db.Column(db.Date)
    daily_average_price = db.Column(db.DECIMAL(10, 2), default=0.00)
    is_deleted = db.Column(db.Boolean, default=False)
    pickup_code = db.Column(db.String(50), nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'quantity': float(self.quantity),
            'total_price': float(self.total_price),
            'channel': self.channel,
            'main_type': self.main_type,
            'sub_type': self.sub_type,
            'unit_coefficient': float(self.unit_coefficient),
            'receive_status': self.receive_status,
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            'statistical_status': self.statistical_status,
            'min_unit_price': float(self.min_unit_price),
            'tag': self.tag,
            'evaluate': self.evaluate,
            'start_use_time': self.start_use_time.strftime('%Y-%m-%d') if self.start_use_time else None,
            'end_use_time': self.end_use_time.strftime('%Y-%m-%d') if self.end_use_time else None,
            'daily_average_price': float(self.daily_average_price),
            'is_deleted': self.is_deleted,
            'pickup_code': self.pickup_code
        }

def get_pending_count():
    """获取待收货数量"""
    return Consumption.query.filter_by(receive_status='待收货', is_deleted=False).count()

def get_pending_consumption():
    """获取待收货列表"""
    return Consumption.query.filter_by(receive_status='待收货', is_deleted=False).order_by(Consumption.create_time.desc()).all()

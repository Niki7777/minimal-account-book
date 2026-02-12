from app import db

class MainType(db.Model):
    __tablename__ = 'main_types'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }

def get_all_main_types():
    """获取所有账单类型"""
    return MainType.query.order_by(MainType.id).all()

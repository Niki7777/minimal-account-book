from app import db

class SubType(db.Model):
    __tablename__ = 'sub_types'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }

def get_all_sub_types():
    """获取所有统计类型"""
    from app.models.consumption import Consumption
    
    # 从sub_types表获取所有统计类型
    db_sub_types = SubType.query.order_by(SubType.id).all()
    
    # 从consumption表获取所有实际使用的统计类型
    used_sub_types = db.session.query(Consumption.sub_type).distinct().all()
    used_sub_type_names = [item[0] for item in used_sub_types if item[0]]
    
    # 合并并去重
    all_sub_type_names = set()
    result = []
    
    # 先添加数据库中已有的统计类型
    for sub_type in db_sub_types:
        if sub_type.name not in all_sub_type_names:
            all_sub_type_names.add(sub_type.name)
            result.append(sub_type)
    
    # 再添加consumption表中使用但sub_types表中没有的统计类型
    for name in used_sub_type_names:
        if name not in all_sub_type_names:
            all_sub_type_names.add(name)
            # 创建临时SubType对象用于模板渲染
            temp_sub_type = type('SubType', (), {'id': None, 'name': name, 'to_dict': lambda self: {'id': self.id, 'name': self.name}})()
            result.append(temp_sub_type)
    
    return result

import pytest
from app import create_app
from app.models import Channel, MainType, SubType, Consumption
from app import db
from datetime import datetime

@pytest.fixture
def app():
    """创建Flask应用实例"""
    import os
    # 保存原始环境变量
    original_env = os.environ.get('DATABASE_URL')
    # 设置测试环境变量
    os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
    
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    yield app
    
    # 恢复原始环境变量
    if original_env:
        os.environ['DATABASE_URL'] = original_env
    else:
        del os.environ['DATABASE_URL']

@pytest.fixture
def client(app):
    """创建测试客户端"""
    return app.test_client()

@pytest.fixture
def init_db(app):
    """初始化数据库"""
    with app.app_context():
        db.create_all()
        # 添加测试数据
        channel1 = Channel(name='淘宝')
        channel2 = Channel(name='京东')
        main_type1 = MainType(name='食品')
        main_type2 = MainType(name='服装')
        sub_type1 = SubType(name='日常用品')
        sub_type2 = SubType(name='电子产品')
        
        db.session.add_all([channel1, channel2, main_type1, main_type2, sub_type1, sub_type2])
        db.session.commit()
        
        # 添加测试消费数据
        consumption1 = Consumption(
            content='测试商品1',
            quantity=2,
            total_price=200.0,
            channel='淘宝',
            main_type='食品',
            sub_type='日常用品',
            receive_status='已收货',
            is_deleted=False,
            create_time=datetime.now()
        )
        
        consumption2 = Consumption(
            content='测试商品2',
            quantity=1,
            total_price=50.0,
            channel='京东',
            main_type='服装',
            sub_type='电子产品',
            receive_status='已收货',
            is_deleted=False,
            create_time=datetime.now()
        )
        
        db.session.add_all([consumption1, consumption2])
        db.session.commit()
        
        yield
        
        db.drop_all()

# 渠道相关测试
def test_get_channels(client, init_db):
    """测试获取渠道列表"""
    response = client.get('/api/channel')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] == True
    assert len(data['data']) == 2

def test_create_channel(client, init_db):
    """测试创建渠道"""
    response = client.post('/api/channel', json={'name': '拼多多'})
    assert response.status_code == 201
    data = response.get_json()
    assert data['success'] == True
    assert data['message'] == '渠道添加成功！'
    assert data['data']['name'] == '拼多多'

def test_update_channel(client, init_db):
    """测试更新渠道"""
    response = client.put('/api/channel/1', json={'name': '淘宝商城'})
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] == True
    assert data['message'] == '渠道更新成功！'
    assert data['data']['name'] == '淘宝商城'

def test_delete_channel(client, init_db):
    """测试删除渠道"""
    response = client.delete('/api/channel/1')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] == True
    assert data['message'] == '渠道删除成功！'

# 账单类型相关测试
def test_get_main_types(client, init_db):
    """测试获取账单类型列表"""
    response = client.get('/api/main-type')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] == True
    assert len(data['data']) == 2

def test_create_main_type(client, init_db):
    """测试创建账单类型"""
    response = client.post('/api/main-type', json={'name': '娱乐'})
    assert response.status_code == 201
    data = response.get_json()
    assert data['success'] == True
    assert data['message'] == '账单类型添加成功！'
    assert data['data']['name'] == '娱乐'

def test_update_main_type(client, init_db):
    """测试更新账单类型"""
    response = client.put('/api/main-type/1', json={'name': '食品饮料'})
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] == True
    assert data['message'] == '账单类型更新成功！'
    assert data['data']['name'] == '食品饮料'

def test_delete_main_type(client, init_db):
    """测试删除账单类型"""
    response = client.delete('/api/main-type/1')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] == True
    assert data['message'] == '账单类型删除成功！'

# 统计类型相关测试
def test_get_sub_types(client, init_db):
    """测试获取统计类型列表"""
    response = client.get('/api/sub-type')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] == True
    assert len(data['data']) == 2

def test_create_sub_type(client, init_db):
    """测试创建统计类型"""
    response = client.post('/api/sub-type', json={'name': '家居用品'})
    assert response.status_code == 201
    data = response.get_json()
    assert data['success'] == True
    assert data['message'] == '统计类型添加成功！'
    assert data['data']['name'] == '家居用品'

def test_update_sub_type(client, init_db):
    """测试更新统计类型"""
    response = client.put('/api/sub-type/1', json={'name': '生活用品'})
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] == True
    assert data['message'] == '统计类型更新成功！'
    assert data['data']['name'] == '生活用品'

def test_delete_sub_type(client, init_db):
    """测试删除统计类型"""
    response = client.delete('/api/sub-type/1')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] == True
    assert data['message'] == '统计类型删除成功！'

# 消费相关测试
def test_get_consumptions(client, init_db):
    """测试获取消费列表"""
    response = client.get('/api/consumption')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] == True
    assert len(data['data']) == 2

def test_get_consumption_by_type(client, init_db):
    """测试按类型获取消费项"""
    response = client.get('/api/consumption/type/日常用品')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] == True
    assert len(data['data']) >= 1

# 统计数据相关测试
def test_get_statistics(client, init_db):
    """测试获取统计数据"""
    # 计算日期范围
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now().replace(day=1)).strftime('%Y-%m-%d')
    
    response = client.get(f'/api/consumption/statistics?startDate={start_date}&endDate={end_date}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] == True
    assert 'categories' in data['data']
    assert 'values' in data['data']

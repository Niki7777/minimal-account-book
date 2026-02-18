from flask import Flask, send_from_directory, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

# 创建数据库实例
db = SQLAlchemy()

# 创建Flask应用
def create_app():
    # 获取项目根目录
    basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    app = Flask(__name__, 
                template_folder=os.path.join(basedir, 'templates'),
                static_folder=os.path.join(basedir, 'static'))
    
    # 配置应用
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['STATIC_FOLDER'] = os.path.join(basedir, 'static')
    
    # 初始化扩展
    db.init_app(app)
    CORS(app)
    
    # 注册蓝图
    from app.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
    
    # 根路径返回首页模板
    @app.route('/')
    def index():
        from datetime import datetime
        from app.models.consumption import get_pending_count
        
        # 获取当月1号作为默认开始时间
        today = datetime.now()
        default_start = today.replace(day=1).strftime('%Y-%m-%d')
        default_end = today.strftime('%Y-%m-%d')
        
        try:
            pending_count = get_pending_count()
        except Exception as e:
            print(f"Error getting pending count: {e}")
            pending_count = 0
        
        return render_template('index.html', 
                               pending_count=pending_count,
                               default_start=default_start,
                               default_end=default_end)
    
    # 页面路由
    @app.route('/list')
    def consumption_list():
        """消费列表页"""
        from app.models.consumption import get_pending_count
        from app.models.channel import get_all_channels
        from app.models.main_type import get_all_main_types
        from app.models.sub_type import get_all_sub_types
        
        try:
            pending_count = get_pending_count()
            channels = get_all_channels()
            main_types = get_all_main_types()
            sub_types = get_all_sub_types()
        except Exception as e:
            print(f"Error in consumption_list: {e}")
            pending_count = 0
            channels = []
            main_types = []
            sub_types = []
        
        return render_template('list.html', 
                               pending_count=pending_count,
                               channels=channels,
                               main_types=main_types,
                               sub_types=sub_types)
    
    @app.route('/pending')
    def pending_list():
        """待收货列表页"""
        from app.models.consumption import get_pending_count, get_pending_consumption
        
        try:
            pending_count = get_pending_count()
            pending_list = get_pending_consumption()
        except Exception as e:
            print(f"Error in pending_list: {e}")
            pending_count = 0
            pending_list = []
        
        return render_template('pending.html', pending_list=pending_list, pending_count=pending_count)
    
    @app.route('/price')
    def price_query():
        """价格查询页"""
        from app.models.sub_type import get_all_sub_types
        from app.models.consumption import get_pending_count
        
        try:
            sub_types = get_all_sub_types()
            pending_count = get_pending_count()
        except Exception as e:
            print(f"Error in price_query: {e}")
            sub_types = []
            pending_count = 0
        
        return render_template('price.html', sub_types=sub_types, pending_count=pending_count)
    
    @app.route('/manage')
    def manage_page():
        """管理页面"""
        from app.models.consumption import get_pending_count
        from app.models.channel import get_all_channels
        from app.models.main_type import get_all_main_types
        from app.models.sub_type import get_all_sub_types
        
        try:
            pending_count = get_pending_count()
            channels = get_all_channels()
            main_types = get_all_main_types()
            sub_types = get_all_sub_types()
        except Exception as e:
            print(f"Error in manage_page: {e}")
            pending_count = 0
            channels = []
            main_types = []
            sub_types = []
        
        return render_template('manage.html', 
                               pending_count=pending_count,
                               channels=channels,
                               main_types=main_types,
                               sub_types=sub_types)
    
    # favicon.ico路由
    @app.route('/favicon.ico')
    def favicon():
        try:
            return send_from_directory(app.config['STATIC_FOLDER'], 'favicon.ico')
        except Exception as e:
            print(f"Error in favicon route: {e}")
            return f"Error: {e}", 500
    
    return app

# Create the app instance
app = create_app()

# Print app routes for debugging
print("\n=== Flask App Routes ===")
for rule in app.url_map.iter_rules():
    print(f"Rule: {rule}")
print("======================\n")


from datetime import datetime

def calculate_min_unit_price(total_price: float, quantity: float, unit_coefficient: float = 1.0) -> float:
    """
    计算最小单位单价（核心函数）
    参数：
        total_price: 总价（元）
        quantity: 数量
        unit_coefficient: 最小单位换算系数（默认1.0，例：1包=5抽填5）
    返回：
        最小单位单价（保留2位小数，元）
    """
    try:
        # 计算逻辑：最小单位单价 = 总价 ÷（数量 × 换算系数）
        min_unit_price = total_price / (quantity * unit_coefficient)
        return round(min_unit_price, 2)  # 保留2位小数，符合金额规范
    except ZeroDivisionError:
        # 避免除数为0（数量或换算系数不能为0）
        return 0.0

def calculate_daily_average_price(total_price: float, start_use_time: str, end_use_time: str) -> float:
    """
    计算日均价（核心函数）
    参数：
        total_price: 总价（元）
        start_use_time: 开始使用时间（格式：YYYY-MM-DD）
        end_use_time: 结束使用时间（格式：YYYY-MM-DD）
    返回：
        日均价（保留2位小数，元）
    """
    try:
        # 验证时间格式，转换为datetime对象
        start_date = datetime.strptime(start_use_time, '%Y-%m-%d')
        end_date = datetime.strptime(end_use_time, '%Y-%m-%d')
        # 计算使用天数（包含开始和结束日期，天数+1）
        days = (end_date - start_date).days + 1
        if days <= 0:
            return 0.0
        # 计算日均价
        daily_price = total_price / days
        return round(daily_price, 2)
    except (ValueError, TypeError, ZeroDivisionError):
        # 时间格式错误、缺少时间或天数为0时，返回0
        return 0.0

def get_current_date() -> str:
    """获取当前日期时间（格式：YYYY-MM-DD HH:MM:SS，用于购买时间自动填充）"""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def validate_date_format(date_str: str) -> bool:
    """验证日期格式是否为YYYY-MM-DD或YYYY-MM-DD HH:MM:SS（辅助函数，避免前端传入错误格式）"""
    try:
        # 尝试解析带时间的格式
        datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        return True
    except ValueError:
        try:
            # 尝试解析仅日期的格式
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False

def format_date_display(date_str: str) -> str:
    """格式化日期为显示格式：yyyy年mm月dd日 hh:mm:ss"""
    if not date_str:
        return ''
    try:
        # 尝试解析带时间的格式
        dt = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        return dt.strftime('%Y年%m月%d日 %H:%M:%S')
    except ValueError:
        try:
            # 尝试解析仅日期的格式
            dt = datetime.strptime(date_str, '%Y-%m-%d')
            return dt.strftime('%Y年%m月%d日 00:00:00')
        except ValueError:
            return date_str

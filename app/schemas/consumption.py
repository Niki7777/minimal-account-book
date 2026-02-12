from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime

class ConsumptionBase(BaseModel):
    content: str = Field(..., description="消费内容")
    quantity: float = Field(..., description="数量")
    total_price: float = Field(..., description="总价")
    channel: str = Field(..., description="购买渠道")
    main_type: str = Field(..., description="账单类型")
    sub_type: Optional[str] = Field(None, description="统计类型")
    unit_coefficient: float = Field(default=1.0, description="换算系数")
    receive_status: str = Field(default="已收货", description="收货状态")
    purchase_time: Optional[str] = Field(None, description="购买时间")
    tag: Optional[str] = Field(None, description="标签")
    evaluate: Optional[str] = Field(None, description="评价")
    start_use_time: Optional[str] = Field(None, description="使用开始时间")
    end_use_time: Optional[str] = Field(None, description="使用结束时间")
    pickup_code: Optional[str] = Field(None, alias="pickupCode", description="取件码")

class ConsumptionCreate(ConsumptionBase):
    pass

class ConsumptionUpdate(BaseModel):
    content: Optional[str] = Field(None, description="消费内容")
    quantity: Optional[float] = Field(None, description="数量")
    total_price: Optional[float] = Field(None, description="总价")
    channel: Optional[str] = Field(None, description="购买渠道")
    main_type: Optional[str] = Field(None, description="账单类型")
    sub_type: Optional[str] = Field(None, description="统计类型")
    unit_coefficient: Optional[float] = Field(None, description="换算系数")
    receive_status: Optional[str] = Field(None, description="收货状态")
    purchase_time: Optional[str] = Field(None, description="购买时间")
    tag: Optional[str] = Field(None, description="标签")
    evaluate: Optional[str] = Field(None, description="评价")
    start_use_time: Optional[str] = Field(None, description="使用开始时间")
    end_use_time: Optional[str] = Field(None, description="使用结束时间")
    pickup_code: Optional[str] = Field(None, alias="pickupCode", description="取件码")

class ConsumptionResponse(BaseModel):
    id: int
    content: str
    quantity: float
    total_price: float
    channel: str
    main_type: str
    sub_type: Optional[str]
    unit_coefficient: float
    receive_status: str
    create_time: str
    statistical_status: str
    min_unit_price: float
    tag: Optional[str]
    evaluate: Optional[str]
    start_use_time: Optional[str]
    end_use_time: Optional[str]
    daily_average_price: float
    is_deleted: bool
    pickup_code: Optional[str]
    
    class Config:
        from_attributes = True

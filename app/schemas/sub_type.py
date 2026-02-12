from pydantic import BaseModel, Field

class SubTypeBase(BaseModel):
    name: str = Field(..., description="统计类型名称")

class SubTypeCreate(SubTypeBase):
    pass

class SubTypeUpdate(BaseModel):
    name: str = Field(..., description="统计类型名称")

class SubTypeResponse(BaseModel):
    id: int
    name: str
    
    class Config:
        from_attributes = True

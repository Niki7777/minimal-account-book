from pydantic import BaseModel, Field

class MainTypeBase(BaseModel):
    name: str = Field(..., description="账单类型名称")

class MainTypeCreate(MainTypeBase):
    pass

class MainTypeUpdate(BaseModel):
    name: str = Field(..., description="账单类型名称")

class MainTypeResponse(BaseModel):
    id: int
    name: str
    
    class Config:
        from_attributes = True

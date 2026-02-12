from pydantic import BaseModel, Field

class ChannelBase(BaseModel):
    name: str = Field(..., description="渠道名称")

class ChannelCreate(ChannelBase):
    pass

class ChannelUpdate(BaseModel):
    name: str = Field(..., description="渠道名称")

class ChannelResponse(BaseModel):
    id: int
    name: str
    
    class Config:
        from_attributes = True

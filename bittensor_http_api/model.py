from pydantic import BaseModel, Field


class InputNetuid(BaseModel):
    netuid: int = Field(..., description='Subnet uid')


class KeyAddress(BaseModel):
    ss58_address: str = Field(..., description='SS58 address')
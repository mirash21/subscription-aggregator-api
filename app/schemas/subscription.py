from pydantic import BaseModel, Field, validator
from typing import Optional, Union
from datetime import datetime
import uuid
import re


class MMYYYYDate(str):
    """Custom type for MM-YYYY date format validation"""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not isinstance(v, str):
            raise ValueError('Date must be a string')
        
        if not re.match(r'^\d{2}-\d{4}$', v):
            raise ValueError('Date must be in MM-YYYY format')
        
        month, year = v.split('-')
        month, year = int(month), int(year)
        
        if not (1 <= month <= 12):
            raise ValueError('Month must be between 01 and 12')
            
        if year < 1900 or year > 2100:
            raise ValueError('Year must be between 1900 and 2100')
            
        return v


class SubscriptionBase(BaseModel):
    service_name: str = Field(..., min_length=1, max_length=255)
    price: int = Field(..., gt=0, description="Price in rubles")
    user_id: uuid.UUID = Field(...)
    start_date: MMYYYYDate = Field(..., description="Start date in MM-YYYY format")
    
    @validator('service_name')
    def service_name_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Service name cannot be empty')
        return v.strip()


class SubscriptionCreate(SubscriptionBase):
    end_date: Optional[MMYYYYDate] = Field(None, description="End date in MM-YYYY format")


class SubscriptionUpdate(BaseModel):
    service_name: Optional[str] = Field(None, min_length=1, max_length=255)
    price: Optional[int] = Field(None, gt=0)
    start_date: Optional[MMYYYYDate] = None
    end_date: Optional[MMYYYYDate] = None
    
    @validator('service_name')
    def service_name_must_not_be_empty(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Service name cannot be empty')
        return v.strip() if v else None


class SubscriptionResponse(SubscriptionBase):
    id: uuid.UUID
    end_date: Optional[MMYYYYDate] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True


class SubscriptionCostRequest(BaseModel):
    start_period: MMYYYYDate = Field(..., description="Start period in MM-YYYY format")
    end_period: MMYYYYDate = Field(..., description="End period in MM-YYYY format")
    user_id: Optional[uuid.UUID] = Field(None, description="Filter by user ID")
    service_name: Optional[str] = Field(None, description="Filter by service name")
    
    @validator('end_period')
    def end_period_must_be_after_start(cls, v, values):
        if 'start_period' in values:
            start_month, start_year = map(int, values['start_period'].split('-'))
            end_month, end_year = map(int, v.split('-'))
            
            start_total = start_year * 12 + start_month
            end_total = end_year * 12 + end_month
            
            if end_total < start_total:
                raise ValueError('End period must be after or equal to start period')
        return v


class SubscriptionCostResponse(BaseModel):
    total_cost: int = Field(..., description="Total cost in rubles")
    period_start: str = Field(..., description="Start period in MM-YYYY format")
    period_end: str = Field(..., description="End period in MM-YYYY format")
    count: int = Field(..., description="Number of subscriptions in calculation")
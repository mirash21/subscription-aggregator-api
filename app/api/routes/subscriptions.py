from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import uuid
import logging

from app.database import get_db
from app.models.subscription import Subscription
from app.schemas.subscription import (
    SubscriptionCreate,
    SubscriptionUpdate,
    SubscriptionResponse,
    SubscriptionCostRequest,
    SubscriptionCostResponse
)
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


def mm_yyyy_to_date(date_str: str) -> datetime:
    """Convert MM-YYYY string to datetime object"""
    month, year = map(int, date_str.split('-'))
    return datetime(year, month, 1)


def date_to_mm_yyyy(date_obj: datetime) -> str:
    """Convert datetime object to MM-YYYY string"""
    return f"{date_obj.month:02d}-{date_obj.year}"


@router.post("/", response_model=SubscriptionResponse, status_code=201)
def create_subscription(
    subscription: SubscriptionCreate,
    db: Session = Depends(get_db)
):
    """
    Создание новой подписки
    """
    logger.info(f"Creating subscription for user {subscription.user_id}")
    
    try:
        # Convert dates from MM-YYYY format
        start_date = mm_yyyy_to_date(subscription.start_date)
        end_date = mm_yyyy_to_date(subscription.end_date) if subscription.end_date else None
        
        # Create subscription object
        db_subscription = Subscription(
            service_name=subscription.service_name,
            price=subscription.price,
            user_id=subscription.user_id,
            start_date=start_date.date(),
            end_date=end_date.date() if end_date else None
        )
        
        # Save to database
        db.add(db_subscription)
        db.commit()
        db.refresh(db_subscription)
        
        logger.info(f"Subscription created successfully: {db_subscription.id}")
        
        # Convert dates back to MM-YYYY format for response
        response = SubscriptionResponse.from_orm(db_subscription)
        response.start_date = subscription.start_date
        response.end_date = subscription.end_date
        
        return response
        
    except Exception as e:
        logger.error(f"Error creating subscription: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create subscription: {str(e)}")


@router.get("/{subscription_id}", response_model=SubscriptionResponse)
def get_subscription(
    subscription_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """
    Получение подписки по ID
    """
    logger.info(f"Getting subscription {subscription_id}")
    
    subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    
    if not subscription:
        logger.warning(f"Subscription {subscription_id} not found")
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    # Convert dates to MM-YYYY format for response
    response = SubscriptionResponse.from_orm(subscription)
    response.start_date = date_to_mm_yyyy(datetime.combine(subscription.start_date, datetime.min.time()))
    if subscription.end_date:
        response.end_date = date_to_mm_yyyy(datetime.combine(subscription.end_date, datetime.min.time()))
    
    logger.info(f"Subscription {subscription_id} retrieved successfully")
    return response


@router.put("/{subscription_id}", response_model=SubscriptionResponse)
def update_subscription(
    subscription_id: uuid.UUID,
    subscription_update: SubscriptionUpdate,
    db: Session = Depends(get_db)
):
    """
    Обновление подписки
    """
    logger.info(f"Updating subscription {subscription_id}")
    
    db_subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    
    if not db_subscription:
        logger.warning(f"Subscription {subscription_id} not found")
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    try:
        # Update fields if provided
        update_data = subscription_update.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            if field == 'start_date' and value:
                setattr(db_subscription, field, mm_yyyy_to_date(value).date())
            elif field == 'end_date' and value:
                setattr(db_subscription, field, mm_yyyy_to_date(value).date())
            else:
                setattr(db_subscription, field, value)
        
        db_subscription.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(db_subscription)
        
        logger.info(f"Subscription {subscription_id} updated successfully")
        
        # Convert dates back to MM-YYYY format for response
        response = SubscriptionResponse.from_orm(db_subscription)
        response.start_date = date_to_mm_yyyy(datetime.combine(db_subscription.start_date, datetime.min.time()))
        if db_subscription.end_date:
            response.end_date = date_to_mm_yyyy(datetime.combine(db_subscription.end_date, datetime.min.time()))
        
        return response
        
    except Exception as e:
        logger.error(f"Error updating subscription {subscription_id}: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update subscription: {str(e)}")


@router.delete("/{subscription_id}", status_code=204)
def delete_subscription(
    subscription_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """
    Удаление подписки
    """
    logger.info(f"Deleting subscription {subscription_id}")
    
    subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    
    if not subscription:
        logger.warning(f"Subscription {subscription_id} not found")
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    try:
        db.delete(subscription)
        db.commit()
        logger.info(f"Subscription {subscription_id} deleted successfully")
        return None
    except Exception as e:
        logger.error(f"Error deleting subscription {subscription_id}: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete subscription: {str(e)}")


@router.get("/", response_model=List[SubscriptionResponse])
def list_subscriptions(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    user_id: Optional[uuid.UUID] = Query(None, description="Filter by user ID"),
    service_name: Optional[str] = Query(None, description="Filter by service name"),
    db: Session = Depends(get_db)
):
    """
    Получение списка подписок с фильтрацией
    """
    logger.info(f"Listing subscriptions with filters: user_id={user_id}, service_name={service_name}")
    
    query = db.query(Subscription)
    
    if user_id:
        query = query.filter(Subscription.user_id == user_id)
    
    if service_name:
        query = query.filter(Subscription.service_name.ilike(f"%{service_name}%"))
    
    subscriptions = query.offset(skip).limit(limit).all()
    
    # Convert dates to MM-YYYY format for response
    response_list = []
    for subscription in subscriptions:
        response = SubscriptionResponse.from_orm(subscription)
        response.start_date = date_to_mm_yyyy(datetime.combine(subscription.start_date, datetime.min.time()))
        if subscription.end_date:
            response.end_date = date_to_mm_yyyy(datetime.combine(subscription.end_date, datetime.min.time()))
        response_list.append(response)
    
    logger.info(f"Retrieved {len(response_list)} subscriptions")
    return response_list


@router.get("/cost/", response_model=SubscriptionCostResponse)
def calculate_subscription_cost(
    request: SubscriptionCostRequest,
    db: Session = Depends(get_db)
):
    """
    Подсчет суммарной стоимости подписок за выбранный период
    """
    logger.info(f"Calculating subscription cost for period {request.start_period} to {request.end_period}")
    
    # Convert period dates
    start_date = mm_yyyy_to_date(request.start_period)
    end_date = mm_yyyy_to_date(request.end_period)
    
    # Build query
    query = db.query(Subscription)
    
    # Apply filters
    if request.user_id:
        query = query.filter(Subscription.user_id == request.user_id)
    
    if request.service_name:
        query = query.filter(Subscription.service_name.ilike(f"%{request.service_name}%"))
    
    # Filter by date range (subscription overlaps with period)
    query = query.filter(
        Subscription.start_date <= end_date.date()
    ).filter(
        (Subscription.end_date >= start_date.date()) | (Subscription.end_date.is_(None))
    )
    
    subscriptions = query.all()
    
    # Calculate total cost
    total_cost = sum(sub.price for sub in subscriptions)
    
    logger.info(f"Calculated cost: {total_cost} rubles for {len(subscriptions)} subscriptions")
    
    return SubscriptionCostResponse(
        total_cost=total_cost,
        period_start=request.start_period,
        period_end=request.end_period,
        count=len(subscriptions)
    )
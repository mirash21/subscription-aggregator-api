from sqlalchemy import Column, Integer, String, Date, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from app.database.session import Base
import uuid


class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    service_name = Column(String(255), nullable=False, index=True)
    price = Column(Integer, nullable=False)  # Цена в рублях
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    start_date = Column(Date, nullable=False)  # Формат MM-YYYY будет преобразован в Date
    end_date = Column(Date, nullable=True)  # Опциональная дата окончания
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Индексы для оптимизации запросов
    __table_args__ = (
        Index('idx_subscriptions_user_id', 'user_id'),
        Index('idx_subscriptions_service_name', 'service_name'),
        Index('idx_subscriptions_start_date', 'start_date'),
        Index('idx_subscriptions_end_date', 'end_date'),
    )
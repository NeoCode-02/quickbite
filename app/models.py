import uuid
from datetime import datetime, timezone
from enum import Enum as PyEnum

from sqlalchemy import (
    ForeignKey, Index, Table, Column, Enum
)
from sqlalchemy import String, Integer, Float, Boolean
from geoalchemy2 import Geography
from geoalchemy2.types import Geography as GeoType
from sqlalchemy.dialects.postgresql import UUID, BIGINT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.timestamp_mixin import TimestampMixin


class UserRole(PyEnum):
    CUSTOMER = "customer"
    COURIER = "courier"
    ADMIN = "admin"

class User(Base, TimestampMixin):

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.CUSTOMER, nullable=False)
    phone: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=True)
    address: Mapped[str] = mapped_column(String, nullable=True)
    hashed_pw: Mapped[str] = mapped_column(String(128), nullable=False)
    username: Mapped[str] = mapped_column(String, index=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, server_default="false", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, server_default="true", nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, server_default="false", nullable=False)

    __table_args__ = (
        Index("ix_user_phone", "phone"),
        Index("ix_user_email", "email"),
        Index("ix_user_username", "username"),
    )

    orders_customer: Mapped[list["Order"]] = relationship(
        back_populates="customer",
        foreign_keys="Order.customer_id"
    )
    positions: Mapped[list["CourierPosition"]] = relationship(back_populates="courier")
    assignments: Mapped[list["CourierAssignment"]] = relationship(back_populates="courier")

class Restaurant(Base, TimestampMixin):

    __tablename__ = "restaurants"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    address: Mapped[str] = mapped_column(String, nullable=False)
    phone: Mapped[str] = mapped_column(String, nullable=True)
    email: Mapped[str] = mapped_column(String, nullable=True)
    geom: Mapped[GeoType] = mapped_column(Geography("POINT", 4326))
    operating_hours: Mapped[str] = mapped_column(String, nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False)
    lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    lon: Mapped[float | None] = mapped_column(Float, nullable=True)

    items: Mapped[list["Item"]] = relationship(back_populates="restaurant")
    orders: Mapped[list["Order"]] = relationship(back_populates="restaurant")

    __table_args__ = (
        Index("ix_restaurant_phone", "phone"),
        Index("ix_restaurant_address", "address"),
        Index("ix_restaurant_email", "email"),
        Index("ix_restaurants_geom", "geom", postgresql_using="gist"),
    )

class Item(Base, TimestampMixin):

    __tablename__ = "items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    price_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    restaurant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("restaurants.id"), index=True)

    restaurant: Mapped["Restaurant"] = relationship(back_populates="items")
    order_items: Mapped[list["OrderItem"]] = relationship(back_populates="item")

    __table_args__ = (
        Index("ix_items_name", "name"),
    )

class OrderItem(Base, TimestampMixin):

    __tablename__ = "order_items"

    order_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("orders.id"), primary_key=True)
    item_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("items.id"), primary_key=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    price_at_time: Mapped[int] = mapped_column(Integer, nullable=True)

    order: Mapped["Order"] = relationship(back_populates="order_items")
    item: Mapped["Item"] = relationship(back_populates="order_items")

class OrderStatus(PyEnum):
    PLACED = "placed"
    ACCEPTED = "accepted"
    READY = "ready"
    PICKED_UP = "picked_up"
    DONE = "done"
    CANCELLED = "cancelled"

class Order(Base, TimestampMixin):

    __tablename__ = "orders"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    customer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    restaurant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("restaurants.id"), index=True)
    total_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus), default=OrderStatus.PLACED, nullable=False)

    customer: Mapped["User"] = relationship(back_populates="orders_customer", foreign_keys=[customer_id])
    restaurant: Mapped["Restaurant"] = relationship(back_populates="orders")
    order_items: Mapped[list["OrderItem"]] = relationship(back_populates="order")

    assignment: Mapped["CourierAssignment | None"] = relationship(
        back_populates="order", uselist=False
    )

    __table_args__ = (
        Index("ix_order_status", "status"),
    )

class CourierPosition(Base, TimestampMixin):

    __tablename__ = "courier_positions"

    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    courier_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    geom: Mapped[GeoType] = mapped_column(Geography("POINT", 4326))

    courier: Mapped["User"] = relationship(back_populates="positions")

    __table_args__ = (
        Index("ix_courier_position_courier_id", "courier_id"),
        Index("ix_courier_position_geom", "geom", postgresql_using="gist"),
    )

class CourierAssignment(Base, TimestampMixin):

    __tablename__ = "courier_assignments"

    order_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("orders.id"), primary_key=True, index=True)
    courier_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    assigned_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    picked_up_at: Mapped[datetime | None] = mapped_column(nullable=True)
    delivered_at: Mapped[datetime | None] = mapped_column(nullable=True)

    order: Mapped["Order"] = relationship(back_populates="assignment")
    courier: Mapped["User"] = relationship(back_populates="assignments")

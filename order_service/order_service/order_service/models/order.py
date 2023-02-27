from sqlalchemy import Column, BigInteger, PrimaryKeyConstraint, Sequence
from sqlalchemy import ForeignKey, Numeric, String, DateTime
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import relationship

from order_service.db.session import Base
from order_service.mixins.base import TimestampsMixin
from order_service.models import OrderStatus

status_enum = ENUM(
    *OrderStatus.to_list(),
    name=OrderStatus.snake_case_name(),
    metadata=Base.metadata,
)


class Order(Base, TimestampsMixin):
    __tablename__ = "order"
    id = Column(BigInteger, primary_key=True)
    user_id = Column(
        BigInteger, ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    cart_id = Column(
        BigInteger,
        ForeignKey("cart.id", ondelete="CASCADE"),
        nullable=True,
        default="",
    )
    status = Column(
        status_enum,
        default=f"{OrderStatus.pending.name}::{OrderStatus.snake_case_name()}",
    )
    cost = Column(Numeric(precision=2), nullable=True, default="")
    tax = Column(Numeric(precision=2), nullable=True, default="")
    total = Column(Numeric(precision=2), nullable=True, default="")
    currency = Column(String(16), nullable=True, default="")

    users = relationship("User", cascade="all,delete", back_populates="orders")


class Cart(Base, TimestampsMixin):
    __tablename__ = "cart"
    id = Column(BigInteger, primary_key=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)

    cart_items = relationship(
        "CartItem", cascade="all,delete", back_populates="carts"
    )


class CartItem(Base):
    __tablename__ = "cart_item"

    id = Column(BigInteger, Sequence("seq_id"))
    cart_id = Column(ForeignKey("cart.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(BigInteger, nullable=True, default="")

    carts = relationship(
        "Cart", cascade="all,delete", back_populates="cart_items"
    )

    __table_args__ = (PrimaryKeyConstraint("product_id", "cart_id"),)

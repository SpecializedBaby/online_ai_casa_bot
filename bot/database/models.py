from datetime import date
from sqlalchemy import (
    BigInteger,
    Integer,
    String,
    Text,
    Float,
    Date,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.database.main import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=False  # Telegram ID
    )
    username: Mapped[str | None] = mapped_column(String, nullable=True)
    full_name: Mapped[str | None] = mapped_column(String, nullable=True)
    age: Mapped[str | None] = mapped_column(String, nullable=True)
    post_code: Mapped[str | None] = mapped_column(String, nullable=True)

    bookings: Mapped[list["Booking"]] = relationship(
        "Booking", back_populates="user", cascade="all, delete-orphan"
    )
    monthly_passes: Mapped[list["MonthlyPass"]] = relationship(
        "MonthlyPass", back_populates="user", cascade="all, delete-orphan"
    )


class Route(Base):
    __tablename__ = "routes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    departure: Mapped[str] = mapped_column(String, nullable=False)
    destination: Mapped[str] = mapped_column(String, nullable=False)
    cost: Mapped[float] = mapped_column(Float, nullable=False)

    bookings: Mapped[list["Booking"]] = relationship(
        "Booking", back_populates="route", cascade="all, delete-orphan"
    )

    __table_args__ = (UniqueConstraint("departure", "destination", name="unique_points"),)


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    payment_method: Mapped[str] = mapped_column(String, nullable=False)
    invoice_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    bookings: Mapped[list["Booking"]] = relationship(
        "Booking", back_populates="payment", cascade="all, delete-orphan"
    )
    monthly_passes: Mapped[list["MonthlyPass"]] = relationship(
        "MonthlyPass", back_populates="payment", cascade="all, delete-orphan"
    )


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    route_id: Mapped[int] = mapped_column(Integer, ForeignKey("routes.id"), nullable=False)
    payment_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("payments.id"))

    date: Mapped[str] = mapped_column(String, nullable=False)
    seat_type: Mapped[str] = mapped_column(String, default="standard", nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String, default="unpaid", nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="bookings")
    route: Mapped["Route"] = relationship("Route", back_populates="bookings")
    payment: Mapped["Payment"] = relationship("Payment", back_populates="bookings")


class RegionalOffer(Base):
    __tablename__ = "regional_offers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    advantages: Mapped[str] = mapped_column(Text, nullable=False)
    url: Mapped[str] = mapped_column(String, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)


class MonthlyPass(Base):
    __tablename__ = "monthly_passes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    payment_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("payments.id"))

    month: Mapped[date] = mapped_column(Date, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="monthly_passes")
    payment: Mapped["Payment"] = relationship("Payment", back_populates="monthly_passes")

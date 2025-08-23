from datetime import datetime
from sqlalchemy import BigInteger, String, Boolean, UniqueConstraint
from sqlalchemy import Integer, Date, ForeignKey, REAL
from sqlalchemy.orm import relationship, Mapped, mapped_column

from bot.database.main import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)  # telegram ID
    username: Mapped[str | None]
    full_name: Mapped[str | None]
    birthday: Mapped[str | None]
    address: Mapped[str | None]

    bookings: Mapped[list["Booking"]] = relationship("Booking", back_populates="user")


class Route(Base):
    __tablename__ = "routes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    departure: Mapped[str]
    destination: Mapped[str]
    cost: Mapped[float]

    bookings: Mapped[list["Booking"]] = relationship("Booking", back_populates="route")

    __table_args__ = (
        UniqueConstraint("departure", "destination", name="unique_points"),
    )


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    payment_method: Mapped[str]
    invoice_id: Mapped[int | None]

    booking: Mapped["Booking"] = relationship("Booking", back_populates="payment")


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    route_id: Mapped[int] = mapped_column(Integer, ForeignKey("routes.id"), nullable=False)
    payment_id: Mapped[int] = mapped_column(Integer, ForeignKey("payments.id"), nullable=True)

    date: Mapped[str]
    seat_type: Mapped[str] = mapped_column(String, default="standard")
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    price: Mapped[float] = mapped_column(REAL, nullable=False)
    status: Mapped[str] = mapped_column(String, default="unpaid")

    user: Mapped["User"] = relationship("User", back_populates="bookings")
    route: Mapped["Route"] = relationship("Route", back_populates="bookings")
    payment: Mapped["Payment"] = relationship("Payment", back_populates="booking")

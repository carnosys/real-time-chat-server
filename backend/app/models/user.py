from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.Base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    username: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint("length(trim(display_name)) > 0", name="display_name_not_empty"),
        CheckConstraint("length(trim(username)) > 0", name="username_not_empty"),
        CheckConstraint("length(password) >= 8", name="password_min_length"),
        CheckConstraint(
            "password ~ '^[A-Za-z0-9@$!%*?&._-]+$'",
            name="password_valid_pattern",
        ),
        CheckConstraint(
            "email ~* '^[A-Z0-9._%+-]+@[A-Z0-9.-]+\\.[A-Z]{2,}$'",
            name="email_valid_pattern",
        ),
    )

from .database import Base
from sqlalchemy import DateTime, TIMESTAMP, Column, ForeignKey, Integer, String, Boolean, text, UniqueConstraint
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, nullable=False)
    username = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'))


class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    author = Column(String, nullable=True)
    isbn = Column(String, nullable=True)
    total_copies = Column(Integer, nullable=False)
    available_copies = Column(Integer, nullable=False, default=total_copies)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'))
    updated_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'))


class Borrowing(Base):
    __tablename__ = "borrowings"

    id = Column(Integer, primary_key=True, nullable=False)

    book_id = Column(Integer, ForeignKey(
        "books.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey(
        "users.id", ondelete="CASCADE"), nullable=False)
    borrowed_at = Column(TIMESTAMP(timezone=True),
                         server_default=text('now()'))
    returned_at = Column(DateTime, nullable=True)
    due_date = Column(DateTime)
    book = relationship("Book")
    user = relationship("User")

    __table_args = (
        UniqueConstraint(
            "workspace_id",
            "user_id",
            name="uq_borrowing"
        ),
    )

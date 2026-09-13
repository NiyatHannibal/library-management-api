from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime


class UserCreate(BaseModel):
    username: str
    password: str
    email: EmailStr


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str

    model_config = ConfigDict(from_attributes=True)


class BookBase(BaseModel):
    title: str
    author: str | None = None
    isbn: str | None = None
    total_copies: int | None = None


class BookCreate(BookBase):
    pass


class BookResponse(BaseModel):
    id: int
    title: str
    author: str | None
    isbn: int | None
    total_copies: int | None
    available_copies: int | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BookCopiesUpdate(BaseModel):
    copies: int


class BorrowingResponse(BaseModel):
    id: int
    book_id: int
    user_id: int
    borrowed_at: datetime
    due_date: datetime
    returned_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: int
    role: str

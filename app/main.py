from fastapi import FastAPI
from .routers import book, borrowing, user, auth

app = FastAPI()

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(borrowing.router)
app.include_router(book.router)

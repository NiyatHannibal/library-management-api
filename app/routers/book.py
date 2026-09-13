from fastapi import HTTPException, status, Depends, APIRouter
from sqlalchemy.orm import Session
from .. import models, database, schemas, outh2
router = APIRouter(
    prefix="/books",
    tags=["Books"]
)


def verify_admin(
    current_user: models.User = Depends(outh2.get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action."
        )
    return current_user


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.BookResponse)
def create_book(body: schemas.BookCreate, db: Session = Depends(database.get_db), admin: models.User = Depends(verify_admin)):
    book = models.Book(**body.model_dump(), available_copies=body.total_copies)
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


@router.get("/", response_model=list[schemas.BookResponse])
def get_books(db: Session = Depends(database.get_db), current_user: models.User = Depends(outh2.get_current_user)):
    books = db.query(models.Book).all()
    return books


@router.get("/{book_id}", response_model=schemas.BookResponse)
def get_book(book_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(outh2.get_current_user)):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"book with ID {book_id} does not exist."
        )
    return book


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int, db: Session = Depends(database.get_db), admin: models.User = Depends(verify_admin)):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"book with ID {book_id} does not exist."
        )
    db.delete(book)
    db.commit()


@router.put("/{book_id}", response_model=schemas.BookResponse)
def update_book(body: schemas.BookBase, book_id: int, db: Session = Depends(database.get_db), admin: models.User = Depends(verify_admin)):
    book = db.query(models.Book).filter(models.Book.id == book_id)
    if book.first() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"book with ID {book_id} does not exist."
        )
    book.update(body.model_dump(), synchronize_session=False)
    db.commit()
    return book.first()


@router.post("/{book_id}/copies", response_model=schemas.BookResponse)
def add_copies(body: schemas.BookCopiesUpdate, book_id: int, db: Session = Depends(database.get_db), admin: models.User = Depends(verify_admin)):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"book with ID {book_id} does not exist."
        )
    if body.copies <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Number of copies must be greater than 0."
        )
    book.total_copies += body.copies
    book.available_copies += body.copies
    db.commit()
    db.refresh(book)
    return book


@router.delete("/{book_id}/copies", response_model=schemas.BookResponse)
def remove_copies(body: schemas.BookCopiesUpdate, book_id: int, db: Session = Depends(database.get_db), admin: models.User = Depends(verify_admin)):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"book with ID {book_id} does not exist."
        )
    if body.copies > book.available_copies:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot remove more copies than are currently available."
        )
    book.total_copies -= body.copies
    book.available_copies -= body.copies
    db.commit()
    db.refresh(book)
    return book

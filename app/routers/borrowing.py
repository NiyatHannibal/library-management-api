from fastapi import HTTPException, status, Depends, APIRouter
from sqlalchemy.orm import Session
from .. import models, database, schemas, outh2
router = APIRouter(
    prefix="/borrowings",
    tags=["Borrowings"]
)


@router.post("/{book_id}", response_model=schemas.BorrowingResponse)
def create_borrowing(book_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(outh2.get_current_user)):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"book with ID {book_id} does not exist."
        )
    if book.available_copies <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No available copies found"
        )
    existing_borrowing = db.query(models.Borrowing).filter(
        models.Borrowing.user_id == current_user.id,
        models.Borrowing.book_id == book_id,
        models.Borrowing.returned_at is_(None)
    )
    if existing_borrowing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="You have already borrowed this book. Return it before borrowing it again.")

    book.available_copies -= 1
    borrowing = models.Borrowing(
        book_id=book_id,
        user_id=current_user.id,
    )
    db.add(borrowing)
    db.commit()
    db.refresh(borrowing)
    return borrowing

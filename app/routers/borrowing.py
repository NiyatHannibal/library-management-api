from fastapi import HTTPException, status, Depends, APIRouter
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from .. import models, database, schemas, outh2
router = APIRouter(
    prefix="/borrowings",
    tags=["Borrowings"]
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


@router.post("/", response_model=schemas.BorrowingResponse)
def create_borrowing(body: schemas.BorrowingCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(outh2.get_current_user)):
    book = db.query(models.Book).filter(models.Book.id == body.book_id).first()
    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"book with ID {body.book_id} does not exist."
        )
    if book.available_copies <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No available copies found"
        )
    existing_borrowing = db.query(models.Borrowing).filter(
        models.Borrowing.user_id == current_user.id,
        models.Borrowing.book_id == body.book_id,
        models.Borrowing.returned_at == None
    ).first()
    if existing_borrowing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="You have already borrowed this book. Return it before borrowing it again.")

    borrowing = models.Borrowing(
        book_id=body.book_id,
        user_id=current_user.id,
    )

    book.available_copies -= 1
    db.add(borrowing)
    db.commit()
    db.refresh(borrowing)
    return borrowing


@router.get("/me", response_model=list[schemas.BorrowingResponse])
def get_my_borrowings(db: Session = Depends(database.get_db), current_user: models.User = Depends(outh2.get_current_user)):
    borrowing_history = db.query(models.Borrowing).filter(
        models.Borrowing.user_id == current_user.id,
    ).all()
    return borrowing_history


@router.get("/", response_model=list[schemas.BorrowingResponse])
def get_all_borrowings(db: Session = Depends(database.get_db), admin: models.User = Depends(verify_admin)):
    borrowing_history = db.query(models.Borrowing).all()
    return borrowing_history


@router.put("/{borrowing_id}/return", response_model=schemas.BorrowingResponse)
def return_borrowing(borrowing_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(outh2.get_current_user)):
    borrowing = db.query(models.Borrowing).filter(
        models.Borrowing.id == borrowing_id,
        models.Borrowing.user_id == current_user.id,
    ).first()
    if borrowing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Borrowing record not found."
        )
    if borrowing.returned_at is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This book has already been returned."
        )

    book = db.query(models.Book).filter(
        models.Book.id == borrowing.book_id).first()
    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated book not found."
        )
    borrowing.returned_at = datetime.now(timezone.utc)
    book.available_copies += 1

    db.commit()
    db.refresh(borrowing)
    return borrowing

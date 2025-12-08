from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from dependencies import get_db, get_password_hash, verify_password
from models import User, Memo
from schemas import UserCreate, UserLogin, MemoCreate, MemoUpdate
from fastapi.templating import Jinja2Templates


templates = Jinja2Templates(directory="templates")


router = APIRouter()


# 회원가입
@router.post("/signup/")
async def signup(reg_data: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == reg_data.username))
    # 먼저 username이 이미 존재하는지 확인
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed_password = get_password_hash(reg_data.password)
    db_user = User(
        username=reg_data.username,
        email=reg_data.email,
        hashed_password=hashed_password,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return {"message": "User created successfully", "user": db_user}


# 로그인
@router.post("/login/")
async def login(
    request: Request, login_data: UserLogin, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.username == login_data.username))
    db_user = result.scalars().first()
    if db_user and verify_password(login_data.password, db_user.hashed_password):
        request.session["user_id"] = db_user.id
        request.session["username"] = db_user.username
        return {"message": "Login successful", "user": db_user}
    else:
        raise HTTPException(status_code=401, detail="Invalid username or password")


# 로그아웃
@router.post("/logout/")
async def logout(request: Request):
    request.session.pop("user_id", None)
    return {"message": "Logout successful"}


# 메모 생성
@router.post("/memos/")
async def create_memo(
    request: Request, memo: MemoCreate, db: AsyncSession = Depends(get_db)
):
    # 현재 로그인된 사용자 확인
    username = request.session.get("username")
    if username is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # 사용자 존재 여부 확인
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    new_memo = Memo(user_id=user.id, title=memo.title, content=memo.content)
    db.add(new_memo)
    db.commit()
    db.refresh(new_memo)
    return new_memo


# 메모 목록 조회
@router.get("/memos/", response_model=List[MemoCreate])
async def read_memos(
    request: Request,
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
):
    # 현재 로그인된 사용자 확인
    username = request.session.get("username")
    if username is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # 사용자 존재 여부 확인
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # memos = db.query(Memo).offset(skip).limit(limit).all()
    memos = (
        (
            await db.execute(
                select(Memo).where(Memo.user_id == user.id).offset(skip).limit(limit)
            )
        )
        .scalars()
        .all()
    )
    return templates.TemplateResponse(
        "memos.html",
        {
            "request": request,
            "memos": memos,
            "username": username,
        },
    )


# 메모 수정
@router.put("/memos/{memo_id}", response_model=MemoUpdate)
async def update_memo(
    request: Request,
    memo_id: int,
    memo: MemoUpdate,
    db: AsyncSession = Depends(get_db),
):
    # 현재 로그인된 사용자 확인
    username = request.session.get("username")
    if username is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # 사용자 존재 여부 확인
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    result = await db.execute(
        select(Memo).where(Memo.user_id == user.id, Memo.id == memo_id)
    )
    db_memo = result.scalars().first()
    if db_memo is None:
        return {"error": "Memo not found"}

    if memo.title is not None:
        db_memo.title = memo.title
    if memo.content is not None:
        db_memo.content = memo.content

    db.commit()
    db.refresh(db_memo)
    return db_memo


# 메모 삭제
@router.delete("/memos/{memo_id}")
async def delete_memo(
    request: Request,
    memo_id: int,
    db: AsyncSession = Depends(get_db),
):
    # 현재 로그인된 사용자 확인
    username = request.session.get("username")
    if username is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # 사용자 존재 여부 확인
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    result = await db.execute(
        select(Memo).where(Memo.user_id == user.id, Memo.id == memo_id)
    )
    db_memo = result.scalars().first()
    if db_memo is None:
        return {"error": "Memo not found"}

    await db.delete(db_memo)
    await db.commit()
    return {"message": "Memo deleted successfully"}


@router.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse(
        "home.html",
        {"request": request},
    )


@router.get("/about")
async def about(request: Request):
    # 현재 로그인된 사용자 확인
    username = request.session.get("username")
    if username is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return {
        "message": "This is the about page.",
        "username": username,
    }

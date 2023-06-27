from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from fastapi_jwt_auth import AuthJWT

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import StaleDataError

from db_dependencies import schemas, crud

from .notice import create_follow_notice

get_db = crud.get_db

router = APIRouter(
    prefix='/user',
    tags=['user'],
)

@router.get("/listall/", response_model=list[schemas.User])
async def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@router.get("/info/{user_id}", response_model=schemas.UserInfo)
async def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=400, detail="User not found")
    
    return {
        "name": db_user.name,
        "email": db_user.email,
        "phone_number" : db_user.phone_number,
        "gender" : db_user.gender,
        "avatar_url" : db_user.avatar_url,
        "introduction" : db_user.introduction,
        "grade": db_user.grade,
        "cnt_posts": len(db_user.post),
        "cnt_followers": db_user.follower.count(),
        "cnt_followings": db_user.following.count()
    }

@router.post('/updateinfo', response_model=schemas.UserInfo)
async def update_user_info(info: schemas.UserUpdateInfo, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_user_id = Authorize.get_jwt_subject()
    current_user = crud.get_user(db, user_id=current_user_id)
    if info.name:
        crud.update_user_name(db, current_user, info.name)
    if info.email:
        try:
            crud.update_user_email(db, current_user, info.email)
        except IntegrityError:
            raise HTTPException(status_code=400, detail="Duplicate email")
    if info.phone_number:
        crud.update_user_phone_number(db, current_user, info.phone_number)
    if info.gender:
        crud.update_user_gender(db, current_user, info.gender)
    if info.avatar_url:
        crud.update_user_avatar_url(db, current_user, info.avatar_url)
    if info.introduction:
        crud.update_user_introduction(db, current_user, info.introduction)
    if info.grade:
        crud.update_user_grade(db, current_user, info.grade)

    return {
        "name": current_user.name,
        "email": current_user.email,
        "phone_number" : current_user.phone_number,
        "gender" : current_user.gender,
        "avatar_url" : current_user.avatar_url,
        "introduction" : current_user.introduction,
        "grade": current_user.grade
    }

@router.get("/getuser", response_model=schemas.BaseUser)
async def get_user(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_user = Authorize.get_jwt_subject()
    return {"id": current_user}



""" 
登录
"""
@router.post('/login', response_model=schemas.UserLoginResponse)
async def login(user: schemas.UserLogin, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    login_user = crud.get_user_by_email(db, user.email)

    if not login_user:
        raise HTTPException(status_code=400,detail="Bad email or password")
    
    if user.password + "notreallyhashed" != login_user.hashed_password:
        raise HTTPException(status_code=400,detail="Bad email or password")

    access_token = Authorize.create_access_token(subject=login_user.id)
    return {
        "access_token": access_token,
        "id": login_user.id,
        "avatar_url": login_user.avatar_url,
        "name": login_user.name
        }


""" 
注册
"""
@router.post('/register', response_model=schemas.BaseUser)
async def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        new_user = crud.create_user(db=db, user=user)
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Duplicate email")
    
    if user.name != None:
        crud.update_user_name(db, new_user, user.name)
    if user.email != None:
        try:
            crud.update_user_email(db, new_user, user.email)
        except IntegrityError:
            raise HTTPException(status_code=400, detail="Duplicate email")
    if user.phone_number != None:
        crud.update_user_phone_number(db, new_user, user.phone_number)
    if user.gender != None:
        crud.update_user_gender(db, new_user, user.gender)
    if user.avatar_url != None:
        crud.update_user_avatar_url(db, new_user, user.avatar_url)
    if user.introduction != None:
        crud.update_user_introduction(db, new_user, user.introduction)
    if user.grade != None:
        crud.update_user_grade(db, new_user, user.grade)
    
    return {'id': new_user.id}

@router.post('/updatepw', response_model=schemas.BaseUser)
async def updatepw(update: schemas.UserResetPw, db: Session = Depends(get_db)):
    """ 修改密码 """
    user = crud.get_user_by_email(db, update.email)
    if not user:
        raise HTTPException(status_code=400, detail="Bad email or password")
    if update.prev_password + "notreallyhashed" != user.hashed_password:
        raise HTTPException(status_code=400, detail="Bad email or password")
    crud.update_user_password(db, user, update.new_password)
    return {"id": user.id}

"""
关注 
"""
@router.post('/follow', response_model=schemas.BaseUser)
async def follow(user: schemas.BaseUser, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_user_id = Authorize.get_jwt_subject()
    """ current_user_id = 1 """
    current_user = crud.get_user(db, user_id=current_user_id)
    target_user = crud.get_user(db, user_id=user.id)
    if not current_user:
        raise HTTPException(status_code=400, detail="Current user not found")
    if not target_user:
        raise HTTPException(status_code=400, detail="User not found")
    try:
        crud.create_user_follow(db, current_user, target_user)
        create_follow_notice(db, target_user, current_user)
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Duplicate follow")
    return {"id": target_user.id}

@router.post('/unfollow', response_model=schemas.BaseUser)
async def unfollow(user: schemas.BaseUser, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_user_id = Authorize.get_jwt_subject()
    """ current_user_id = 1 """
    current_user = crud.get_user(db, user_id=current_user_id)
    target_user = crud.get_user(db, user_id=user.id)
    if not current_user:
        raise HTTPException(status_code=400, detail="Current user not found")
    if not target_user:
        raise HTTPException(status_code=400, detail="User not found")
    try:
        crud.remove_user_follow(db, current_user, target_user)
    except StaleDataError:
        raise HTTPException(status_code=400, detail="Unfollowing an unfollowed")
    return {"id": target_user.id}

@router.get('/follower/{user_id}', response_model=schemas.DetailUserList)
async def get_follower(user_id: int, db: Session = Depends(get_db)):
    """ 用户的粉丝 """
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    raw_res = crud.get_user_follower(db, user_id)
    res = []
    for r in raw_res:
        r_user = crud.get_user(db, r.id)
        res.append({
            'id': r_user.id,
            'name': r_user.name,
            'avatar_url': r_user.avatar_url
        })

    return {
        'users': res
    }

@router.get('/following/{user_id}', response_model=schemas.DetailUserList)
async def get_following(user_id: int, db: Session = Depends(get_db)):
    """ 用户的正在关注 """
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    raw_res = crud.get_user_following(db, user_id)
    res = []
    for r in raw_res:
        r_user = crud.get_user(db, r.id)
        res.append({
            'id': r_user.id,
            'name': r_user.name,
            'avatar_url': r_user.avatar_url
        })

    return {
        'users': res
    }


@router.post('/block', response_model=schemas.BaseUser)
async def block(user: schemas.BaseUser, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_user_id = Authorize.get_jwt_subject()
    """ current_user_id = 1 """
    current_user = crud.get_user(db, user_id=current_user_id)
    target_user = crud.get_user(db, user_id=user.id)
    if not current_user:
        raise HTTPException(status_code=400, detail="Current user not found")
    if not target_user:
        raise HTTPException(status_code=400, detail="User not found")
    try:
        crud.create_user_block(db, current_user, target_user)
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Duplicate block")
    return {"id": target_user.id}

@router.post('/unblock', response_model=schemas.BaseUser)
async def unblock(user: schemas.BaseUser, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_user_id = Authorize.get_jwt_subject()
    """ current_user_id = 1 """
    current_user = crud.get_user(db, user_id=current_user_id)
    target_user = crud.get_user(db, user_id=user.id)
    if not current_user:
        raise HTTPException(status_code=400, detail="Current user not found")
    if not target_user:
        raise HTTPException(status_code=400, detail="User not found")
    try:
        crud.remove_user_block(db, current_user, target_user)
    except StaleDataError:
        raise HTTPException(status_code=400, detail="Unblocking an unblocked")
    return {"id": target_user.id}

@router.get('/blocker/{user_id}', response_model=schemas.DetailUserList)
async def get_blocker(user_id: int, db: Session = Depends(get_db)):
    """ 用户被哪些人拉黑了 """
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    raw_res = crud.get_user_blocker(db, user_id)
    res = []
    for r in raw_res:
        r_user = crud.get_user(db, r.id)
        res.append({
            'id': r_user.id,
            'name': r_user.name,
            'avatar_url': r_user.avatar_url
        })

    return {
        'users': res
    }

@router.get('/blocking/{user_id}', response_model=schemas.DetailUserList)
async def get_blocking(user_id: int, db: Session = Depends(get_db)):
    """ 用户的黑名单 """
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    raw_res = crud.get_user_blocking(db, user_id)
    res = []
    for r in raw_res:
        r_user = crud.get_user(db, r.id)
        res.append({
            'id': r_user.id,
            'name': r_user.name,
            'avatar_url': r_user.avatar_url
        })

    return {
        'users': res
    }
from fastapi import WebSocket, APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import json
from db_dependencies import schemas, crud, models

from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException

get_db = crud.get_db

router = APIRouter(
    prefix='/notice',
    tags=['notice'],
)


def create_star_notice(notice_getter, post, post_liker, db: Session):
    crud.create_star_notice(db, notice_getter, post, post_liker)

def create_pm_notice(notice_getter: models.User, msg: models.PrivateMessage, db: Session):
    crud.create_pm_notice(db, notice_getter, msg)

def create_like_notice(notice_getter: models.User, post: models.Post, post_liker: models.User, db: Session):
    crud.create_like_notice(db, notice_getter, post, post_liker)

def create_comment_notice(db: Session, notice_getter_user: models.User, post: models.Post, post_liker: models.User, content: str):
    crud.create_comment_notice(db, notice_getter_user, post, post_liker, content)

def create_follow_notice(db: Session, notice_getter_user: models.User, follower_user: models.User):
    crud.create_follow_notice(db, notice_getter_user, follower_user)

def create_subscribe_notice(db: Session, notice_getter_user: models.User, new_post: models.Post, following_user: models.User):
    crud.create_subscribe_notice(db, notice_getter_user, new_post, following_user)

@router.get('/get/{user_id}', response_model=schemas.NoticeResponseList)
async def get_notices(user_id: int, db: Session = Depends(get_db)):
    
    notices = crud.get_notices(db, user_id)
    res = []
    for notice in notices:
        if notice.is_system:
            res.append({
                'id': 0,
                'name': '系统消息',
                'avatar_url': 'http://43.138.66.21:8006/resource/4765195297074708481.png',
                'content': notice.system_detail['event_content'].split('\n')[0],
                'last_time': notice.last_time.strftime('%Y-%m-%d %H:%M:%S'),
                'is_system': notice.is_system,
                'fresh': notice.fresh,
                'system_notice_detail' : notice.system_detail
            })
        else:
            pm = crud.get_pmessage(db, notice.pm_detail_id)
            other_id = pm.receiver_id if pm.sender_id == user_id else pm.sender_id
            other_user = crud.get_user(db, other_id)
            res.append({
                'id': other_user.id,
                'name': other_user.name,
                'avatar_url': other_user.avatar_url,
                'content': pm.content,
                'last_time': notice.last_time.strftime('%Y-%m-%d %H:%M:%S'),
                'is_system': notice.is_system,
                'fresh': notice.fresh,
                'system_notice_detail' : None
            })
    return {'notices':res}

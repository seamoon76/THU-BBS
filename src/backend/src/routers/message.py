from fastapi import WebSocket, APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import json
from db_dependencies import schemas, crud, models

from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException

from .notice import create_pm_notice

get_db = crud.get_db

router = APIRouter(
    prefix='/message',
    tags=['message'],
)

connections = {}    # 用于存储 WebSocket 连接的字典

async def send_json_to_client(client_id: int, json_content):
    websocket: WebSocket = connections.get(client_id)
    if websocket:
        await websocket.send_json(json_content)

async def send_text_to_client(client_id: int, text):
    websocket: WebSocket = connections.get(client_id)
    if websocket:
        await websocket.send_text(text)

async def send_notice_to_client(client_id: int, notice):
    websocket: WebSocket = connections.get(client_id)
    if websocket:
        await websocket.send_json(json.dumps(notice))
    else:
        # 加入消息暂存数据库
        pass



@router.post('/create', tags=['message'], response_model=schemas.Message)
async def create_message(data: schemas.CreateMessage, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_user_id = Authorize.get_jwt_subject()
    """ current_user_id = 1 """
    current_user = crud.get_user(db, current_user_id)
    if not current_user:
        raise HTTPException(status_code=400, detail='Current User not found')
    receiver = crud.get_user(db, data.receiver_id)
    if not receiver:
        raise HTTPException(status_code=400, detail='Receiver User not found')
    msg = crud.create_pmessage(db, data, current_user)
    create_pm_notice(receiver, msg, db)
    res = {
        'sender_id': msg.sender_id,
        'receiver_id': msg.receiver_id,
        'content': msg.content,
        'create_at': msg.create_at
    }
    return res

@router.get('/get/{user_id}', tags=['message'], response_model=schemas.MessageList)
async def get_message(user_id: int, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_user_id = Authorize.get_jwt_subject()
    """ current_user_id = 1 """
    current_user = crud.get_user(db, current_user_id)
    if not current_user:
        raise HTTPException(status_code=400, detail='Current User not found')
    target_user = crud.get_user(db, user_id)
    if not target_user:
        raise HTTPException(status_code=400, detail='Receiver User not found')
    res = crud.get_message_from_AB(db, current_user, target_user)
    res = [{
        'sender_id': r.sender_id,
        'receiver_id': r.receiver_id,
        'content': r.content,
        'create_at': r.create_at
    } for r in res]
    res.sort(key=lambda r: r['create_at'], reverse=False)
    return {"messages": res}
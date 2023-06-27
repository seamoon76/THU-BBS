from fastapi import Depends, FastAPI, Request, WebSocket

from db_dependencies import models, schemas
from db_dependencies.database import engine

from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException

from pydantic import BaseModel
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles

from routers import user, post, resource, message, notice

class Settings(BaseModel):
    authjwt_secret_key: str = "secret"

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(user.router)
app.include_router(post.router)
app.include_router(resource.router)
app.include_router(message.router)
app.include_router(notice.router)

#app.mount('/resource', StaticFiles(directory='./resource'))

@app.get("/")
async def root():
    return {"message": "Application"}

@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": "Validation error"}
    )

@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )

@AuthJWT.load_config
def get_config():
    return Settings()

# redis 维护 websocket 连接列表

async def create_redis_pool():
    redis = await aioredis.from_url("redis://localhost")
    return redis

@app.on_event('startup')
async def start_up_event():
    #app.state.redis = create_redis_pool()
    pass

@app.on_event('shutdown')
async def shut_down_event():
    #app.state.redis.close()
    #await app.state.redis.wait_closed()
    pass



# 消息相关

@app.websocket('/ws/{user_id}')
async def create_websocket(user_id:int, websocket: WebSocket):
    await websocket.accept()
    client_id = user_id
    message.connections[client_id] = websocket
    try:
        while True:
            data = await websocket.receive_text()
            #print(f"Received message from client {client_id}: {data}")
            #await message.send_text_to_client(1, data)
    except Exception as e:
        print(f"WebSocket error for client {client_id}: {e}")
    finally:
        
        del message.connections[client_id]
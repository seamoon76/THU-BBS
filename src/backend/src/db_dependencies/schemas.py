from pydantic import BaseModel
from datetime import datetime

class BaseUser(BaseModel):
    id: int

class DetailUser(BaseModel):
    id: int
    name: str
    avatar_url: str | None

class User(BaseUser):
    name: str
    email: str
    hashed_password: str
    phone_number : str | None
    gender : int | None
    avatar_url : str | None
    introduction : str | None
    grade : int | None

    class Config:
        orm_mode = True

class UserInfo(BaseModel):
    name: str | None
    email: str | None
    phone_number : str | None
    gender : int | None
    avatar_url : str | None
    introduction : str | None
    grade: int | None
    cnt_posts: int | None
    cnt_followers: int | None
    cnt_followings: int | None

class UserCreate(BaseModel):
    email: str
    name: str
    password: str
    avatar_url: str | None
    gender: int | None
    introduction: str | None
    grade: int | None
    phone_number: str | None


class UserLogin(BaseModel):
    email: str
    password: str

class UserLoginResponse(BaseModel):
    id: int
    name: str | None
    avatar_url: str | None
    access_token: str

class UserFollow(BaseModel):
    id: int

class JwtResponse(BaseModel):
    access_token: str

class BaseUserList(BaseModel):
    users: list[BaseUser]

class DetailUserList(BaseModel):
    users: list[DetailUser]    

class UserUpdateInfo(BaseModel):
    name: str | None
    email: str | None
    phone_number : str | None
    gender : int | None
    avatar_url : str | None
    introduction : str | None
    grade: int | None

class UserResetPw(BaseModel):
    email: str
    prev_password: str
    new_password: str

class BasePost(BaseModel):
    id : int

class Resource(BaseModel):
    url: str
    type: str

class PostCreate(BaseModel):
    title: str
    content: str
    type: str
    resources: list[Resource]
    location: str | None

class BriefPost(BaseModel):
    id: int
    username: str
    avatar_url: str | None
    title: str
    content: str
    create_at: datetime
    user_id: int
    like_num: int
    like_users: list[BaseUser]
    star_num: int
    star_users: list[BaseUser]
    comment_num: int
    type: str
    location: str | None
    resources: list[Resource]

class BriefPostResponse(BaseModel):
    posts: list[BriefPost]

class CommentCreate(BaseModel):
    content: str

class CommentResonse(BaseModel):
    content: str
    id: int
    user_id: int
    create_at: datetime
    user_name: str
    avatar_url: str

class CommentResponseList(BaseModel):
    comments: list[CommentResonse]

class DetailPost(BaseModel):
    id: int
    title: str
    content: str
    create_at: datetime
    user_id: int
    like_num: int
    star_num: int
    comment: list[CommentResonse]
    type: str
    location: str | None
    resources: list

class PostQuery(BaseModel):
    filter_by: str | None
    filter_parameter: str | None
    order_by: str | None
    order: str | None
    skip: int | None
    limit: int | None
    block: int | None

class UploadResourceResponse(BaseModel):
    url: str

class Message(BaseModel):
    sender_id: int
    receiver_id: int
    content: str
    create_at: datetime

class MessageList(BaseModel):
    messages: list[Message]

class CreateMessage(BaseModel):
    receiver_id: int
    content: str


class SystemNoticeDetail(BaseModel):
    event_executor_id: int | None
    event_executor_name: str | None
    event_executor_avatar_url: str | None
    event_content: str | None

class NoticeResponse(BaseModel):
    id: int
    name: str
    avatar_url: str | None
    content: str
    last_time: datetime
    is_system: bool
    fresh: bool | None
    system_notice_detail: SystemNoticeDetail | None

class NoticeResponseList(BaseModel):
    notices: list[NoticeResponse]

class TypeResponse(BaseModel):
    type: str
    number: int

class TypeListResponse(BaseModel):
    types: list[TypeResponse]

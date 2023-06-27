from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from . import models, schemas, database
import datetime

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_user(db: Session, user_id: int) -> models.User | None:
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> models.User | None:
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def update_user_name(db: Session, user: schemas.User, new_name: str):
    user.name = new_name
    db.commit()
    return

def update_user_email(db: Session, user: schemas.User, new_email: str):
    user.email = new_email
    db.commit()
    return

def update_user_phone_number(db: Session, user: schemas.User, new_phone_number: str):
    user.phone_number = new_phone_number
    db.commit()
    return

def update_user_gender(db: Session, user: schemas.User, new_gender: int):
    user.gender = new_gender
    db.commit()
    return

def update_user_avatar_url(db: Session, user: schemas.User, new_avatar_url: str):
    user.avatar_url = new_avatar_url
    db.commit()
    return

def update_user_introduction(db: Session, user: schemas.User, new_introduction: str):
    user.introduction = new_introduction
    db.commit()
    return

def update_user_grade(db: Session, user: schemas.User, new_grade: int):
    user.grade = new_grade
    db.commit()
    return

def update_user_password(db: Session, user: schemas.User, new_password: str):
    fake_hashed_password = new_password + "notreallyhashed"
    user.hashed_password = fake_hashed_password
    db.commit()
    return

def followtest(db: Session):
    return db.query(models.Follow).all()

def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = models.User(name=user.name, 
                            hashed_password=fake_hashed_password,
                            email=user.email)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_user_follow(db: Session, user: schemas.User, target: models.User):
    target.follower.append(user)
    db.commit()
    return

def remove_user_follow(db: Session, user: schemas.User, target: models.User):
    target.follower.remove(user)
    db.commit()
    return

def get_user_follower(db: Session, user_id: int) -> list[models.User]:
    user = get_user(db, user_id)
    followers = user.follower.all()
    return followers

def get_user_following(db: Session, user_id: int) -> list[models.User]:
    user = get_user(db, user_id)
    followings = user.following.all()
    return followings

def create_user_block(db: Session, user: schemas.User, target:models.User):
    target.blocker.append(user)
    db.commit()
    return

def remove_user_block(db: Session, user: schemas.User, target: models.User):
    target.blocker.remove(user)
    db.commit()
    return

def get_user_blocker(db: Session, user_id: int) -> list[models.User]:
    user = get_user(db, user_id)
    blockers = user.blocker.all()
    return blockers

def get_user_blocking(db: Session, user_id: int) -> list[models.User]:
    user = get_user(db, user_id)
    blockings = user.blocking.all()
    return blockings

""" post """


def get_posts(db: Session):
    return db.query(models.Post).all()

def get_post(db: Session, post_id: int) -> models.Post | None :
    return db.query(models.Post).filter(models.Post.id == post_id).first()

def del_post(db: Session, post: models.Post):
    db.delete(post)
    db.commit()
    return post.id



def create_new_post(db:Session, data: schemas.PostCreate, user: models.User) -> models.Post:
    time = datetime.datetime.now()
    db_post = models.Post(title=data.title,
                          content=data.content,
                          type=data.type,
                          location=data.location,
                          create_at=time,
                          resources=data.resources)
    db.add(db_post)
    db.commit()
    user.post.append(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

def create_post_like(db: Session, post: models.Post, user: models.User):
    user.like_post.append(post)
    db.commit()
    return

def remove_post_like(db: Session, post: models.Post, user: models.User):
    user.like_post.remove(post)
    db.commit()
    return

def create_post_star(db: Session, post: models.Post, user: models.User):
    user.star_post.append(post)
    db.commit()
    return

def remove_post_star(db: Session, post: models.Post, user: models.User):
    user.star_post.remove(post)
    db.commit()
    return

def get_like_num(db: Session, post: models.Post):
    return len(post.like_user)

def get_star_num(db: Session, post: models.Post):
    return len(post.star_user)

def get_comment_num(db: Session, post: models.Post):
    return len(db.query(models.Comment).filter(models.Comment.post_id == post.id).all())

def create_comment(db: Session, data: schemas.CommentCreate, post: models.Post, user: models.User):
    time = datetime.datetime.now()
    db_comment = models.Comment(
        create_at=time,
        content=data.content,
        user_id=user.id,
        post_id=post.id
    )
    db.add(db_comment)
    db.commit()
    return db_comment.id

def get_comment(db: Session, post: models.Post) -> list[models.Comment]:
    return db.query(models.Comment).filter(models.Comment.post_id == post.id).all()


def get_types(db: Session):
    return db.query(models.Post.type, func.count(models.Post.id)).group_by(models.Post.type).all()


# 从 uid 筛选
def get_post_by_uid_ol_time(db: Session, user_id: int, order: str = 'desc', limit: int = 10, skip: int = 0):
    if order == 'asc':
        return db.query(models.Post).filter(models.Post.user_id == user_id).order_by(models.Post.create_at).offset(skip).limit(limit).all()
    else:
        return db.query(models.Post).filter(models.Post.user_id == user_id).order_by(models.Post.create_at.desc()).offset(skip).limit(limit).all()
    
def get_post_by_uid_ol_like(db: Session, user_id: int, order: str = 'desc', limit: int = 10, skip: int = 0):
    like_num_subq = db.query(models.like_table.c.post_id, func.count(models.like_table.c.user_id).label('count')
                        ).group_by(models.like_table.c.post_id).subquery()
    if order == 'asc':
        return db.query(models.Post
                        ).outerjoin(like_num_subq, like_num_subq.c.post_id == models.Post.id
                        ).order_by(like_num_subq.c.count).filter(models.Post.user_id == user_id).offset(skip).limit(limit).all()
    else:
        return db.query(models.Post
                        ).outerjoin(like_num_subq, like_num_subq.c.post_id == models.Post.id
                        ).order_by(like_num_subq.c.count.desc()).filter(models.Post.user_id == user_id).offset(skip).limit(limit).all()
    
def get_post_by_uid_ol_star(db: Session, user_id: int, order: str = 'desc', limit: int = 10, skip: int = 0):
    star_num_subq = db.query(models.star_table.c.post_id, func.count(models.star_table.c.user_id).label('count')
                        ).group_by(models.star_table.c.post_id).subquery()
    if order == 'asc':
        return db.query(models.Post
                        ).outerjoin(star_num_subq, star_num_subq.c.post_id == models.Post.id
                        ).order_by(star_num_subq.c.count).filter(models.Post.user_id == user_id).offset(skip).limit(limit).all()
    else:
        return db.query(models.Post
                        ).outerjoin(star_num_subq, star_num_subq.c.post_id == models.Post.id
                        ).order_by(star_num_subq.c.count.desc()).filter(models.Post.user_id == user_id).offset(skip).limit(limit).all()

def get_post_by_uid_ol_comment(db: Session, user_id: int, order: str = 'desc', limit: int = 10, skip: int = 0):
    comment_num_subq = db.query(models.Comment.post_id, func.count(models.Comment.id).label('count')
                        ).group_by(models.Comment.post_id).subquery()
    if order == 'asc':
        return db.query(models.Post
                        ).outerjoin(comment_num_subq, comment_num_subq.c.post_id == models.Post.id
                        ).order_by(comment_num_subq.c.count).filter(models.Post.user_id == user_id).offset(skip).limit(limit).all()
    else:
        return db.query(models.Post
                        ).outerjoin(comment_num_subq, comment_num_subq.c.post_id == models.Post.id
                        ).order_by(comment_num_subq.c.count.desc()).filter(models.Post.user_id == user_id).offset(skip).limit(limit).all()

# 从 type 筛选
def get_post_by_type_ol_time(db: Session, type: str, order: str = 'desc', limit: int = 10, skip: int = 0):
    if order == 'asc':
        return db.query(models.Post).filter(models.Post.type == type).order_by(models.Post.create_at).offset(skip).limit(limit).all()
    else:
        return db.query(models.Post).filter(models.Post.type == type).order_by(models.Post.create_at.desc()).offset(skip).limit(limit).all()
    
def get_post_by_type_ol_like(db: Session, type: str, order: str = 'desc', limit: int = 10, skip: int = 0):
    like_num_subq = db.query(models.like_table.c.post_id, func.count(models.like_table.c.user_id).label('count')
                        ).group_by(models.like_table.c.post_id).subquery()
    if order == 'asc':
        return db.query(models.Post
                        ).outerjoin(like_num_subq, like_num_subq.c.post_id == models.Post.id
                        ).order_by(like_num_subq.c.count).filter(models.Post.type == type).offset(skip).limit(limit).all()
    else:
        return db.query(models.Post
                        ).outerjoin(like_num_subq, like_num_subq.c.post_id == models.Post.id
                        ).order_by(like_num_subq.c.count.desc()).filter(models.Post.type == type).offset(skip).limit(limit).all()
    
def get_post_by_type_ol_star(db: Session, type: str, order: str = 'desc', limit: int = 10, skip: int = 0):
    star_num_subq = db.query(models.star_table.c.post_id, func.count(models.star_table.c.user_id).label('count')
                        ).group_by(models.star_table.c.post_id).subquery()
    if order == 'asc':
        return db.query(models.Post
                        ).outerjoin(star_num_subq, star_num_subq.c.post_id == models.Post.id
                        ).order_by(star_num_subq.c.count).filter(models.Post.type == type).offset(skip).limit(limit).all()
    else:
        return db.query(models.Post
                        ).outerjoin(star_num_subq, star_num_subq.c.post_id == models.Post.id
                        ).order_by(star_num_subq.c.count.desc()).filter(models.Post.type == type).offset(skip).limit(limit).all()

def get_post_by_type_ol_comment(db: Session, type: str, order: str = 'desc', limit: int = 10, skip: int = 0):
    comment_num_subq = db.query(models.Comment.post_id, func.count(models.Comment.id).label('count')
                        ).group_by(models.Comment.post_id).subquery()
    if order == 'asc':
        return db.query(models.Post
                        ).outerjoin(comment_num_subq, comment_num_subq.c.post_id == models.Post.id
                        ).order_by(comment_num_subq.c.count).filter(models.Post.type == type).offset(skip).limit(limit).all()
    else:
        return db.query(models.Post
                        ).outerjoin(comment_num_subq, comment_num_subq.c.post_id == models.Post.id
                        ).order_by(comment_num_subq.c.count.desc()).filter(models.Post.type == type).offset(skip).limit(limit).all()
    
    
# 筛选用户收藏的帖子
def get_post_by_userstar_ol_time(db: Session, user: models.User, order: str = 'desc', limit: int = 10, skip: int = 0):
    posts: list[models.Post] = user.star_post
    if order == 'asc':
        posts.sort(key=lambda x: x.create_at, reverse=False)
        return posts[skip:skip+limit]
    else:
        posts.sort(key=lambda x: x.create_at, reverse=True)
        return posts[skip:skip+limit]


def get_post_by_userstar_ol_like(db: Session, user: models.User, order: str = 'desc', limit: int = 10, skip: int = 0):
    posts: list[models.Post] = user.star_post
    if order == 'asc':
        posts.sort(key=lambda x: len(x.like_user), reverse=False)
        return posts[skip:skip+limit]
    else:
        posts.sort(key=lambda x: len(x.like_user), reverse=True)
        return posts[skip:skip+limit]
    
def get_post_by_userstar_ol_star(db: Session, user: models.User, order: str = 'desc', limit: int = 10, skip: int = 0):
    posts: list[models.Post] = user.star_post
    if order == 'asc':
        posts.sort(key=lambda x: len(x.star_user), reverse=False)
        return posts[skip:skip+limit]
    else:
        posts.sort(key=lambda x: len(x.star_user), reverse=True)
        return posts[skip:skip+limit]

def get_post_by_userstar_ol_comment(db: Session, user: models.User, order: str = 'desc', limit: int = 10, skip: int = 0):
    posts: list[models.Post] = user.star_post
    if order == 'asc':
        posts.sort(key=lambda x: get_comment_num(db, x), reverse=False)
        return posts[skip:skip+limit]
    else:
        posts.sort(key=lambda x: get_comment_num(db, x), reverse=True)
        return posts[skip:skip+limit]

# 筛选所有帖子

def get_all_post_ol_time(db: Session, order: str = 'desc', limit: int = 10, skip: int = 0):
    if order == 'asc':
        return db.query(models.Post).order_by(models.Post.create_at).offset(skip).limit(limit).all()
    else:
        return db.query(models.Post).order_by(models.Post.create_at.desc()).offset(skip).limit(limit).all()
    

def get_all_post_ol_like(db: Session, order: str = 'desc', limit: int = 10, skip: int = 0):
    like_num_subq = db.query(models.like_table.c.post_id, func.count(models.like_table.c.user_id).label('count')
                        ).group_by(models.like_table.c.post_id).subquery()
    if order == 'asc':
        return db.query(models.Post
                        ).outerjoin(like_num_subq, like_num_subq.c.post_id == models.Post.id
                        ).order_by(like_num_subq.c.count).offset(skip).limit(limit).all()
    else:
        return db.query(models.Post
                        ).outerjoin(like_num_subq, like_num_subq.c.post_id == models.Post.id
                        ).order_by(like_num_subq.c.count.desc()).offset(skip).limit(limit).all()

def get_all_post_ol_star(db: Session, order: str = 'desc', limit: int = 10, skip: int = 0):
    star_num_subq = db.query(models.star_table.c.post_id, func.count(models.star_table.c.user_id).label('count')
                        ).group_by(models.star_table.c.post_id).subquery()
    if order == 'asc':
        return db.query(models.Post
                        ).outerjoin(star_num_subq, star_num_subq.c.post_id == models.Post.id
                        ).order_by(star_num_subq.c.count).offset(skip).limit(limit).all()
    else:
        return db.query(models.Post
                        ).outerjoin(star_num_subq, star_num_subq.c.post_id == models.Post.id
                        ).order_by(star_num_subq.c.count.desc()).offset(skip).limit(limit).all()

def get_all_post_ol_comment(db: Session, order: str = 'desc', limit: int = 10, skip: int = 0):
    comment_num_subq = db.query(models.Comment.post_id, func.count(models.Comment.id).label('count')
                        ).group_by(models.Comment.post_id).subquery()
    if order == 'asc':
        return db.query(models.Post
                        ).outerjoin(comment_num_subq, comment_num_subq.c.post_id == models.Post.id
                        ).order_by(comment_num_subq.c.count).offset(skip).limit(limit).all()
    else:
        return db.query(models.Post
                        ).outerjoin(comment_num_subq, comment_num_subq.c.post_id == models.Post.id
                        ).order_by(comment_num_subq.c.count.desc()).offset(skip).limit(limit).all()

#搜索

def search_by_content(db: Session, keyword: str):
    search_p = '%{}%'.format(keyword)
    return db.query(models.Post).filter(models.Post.content.like(search_p)).all()

def search_by_title(db: Session, keyword: str):
    search_p = '%{}%'.format(keyword)
    return db.query(models.Post).filter(models.Post.title.like(search_p)).all()

def search_by_username(db: Session, keyword: str):
    search_p = '%{}%'.format(keyword)
    return db.query(models.Post).join(models.User).filter(models.User.name.like(search_p)).all()

def search_by_type(db: Session, keyword: str):
    search_p = '%{}%'.format(keyword)
    return db.query(models.Post).filter(models.Post.type.like(search_p)).all()

""" message """

def create_pmessage(db: Session, data: schemas.CreateMessage, user: models.User) -> models.PrivateMessage:
    time = datetime.datetime.now()
    db_message = models.PrivateMessage(
        sender_id = user.id,
        receiver_id = data.receiver_id,
        content = data.content,
        create_at = time
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def get_message_from_AB(db: Session, userA: models.User, userB: models.User, limit: int = 10000):
    return db.query(models.PrivateMessage
            ).filter(or_(and_(models.PrivateMessage.sender_id == userA.id, models.PrivateMessage.receiver_id == userB.id)
                        , and_(models.PrivateMessage.sender_id == userB.id, models.PrivateMessage.receiver_id == userA.id))
            ).order_by(models.PrivateMessage.create_at.desc()).all()

def get_pmessage(db: Session, id: int) -> models.PrivateMessage:
    return db.query(models.PrivateMessage).filter(models.PrivateMessage.id == id).first()

""" Notice """

"""     
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    last_time = Column(DateTime)
    is_system = Column(Boolean)
    fresh = Column(Boolean)
    system_detail = Column(PickleType) 
    pm_detail_id = Column(Integer, ForeignKey('pmessage.id'))"""

def create_pm_notice(db: Session, notice_getter_user: models.User, pm: models.PrivateMessage):
    # 先检查是否有相同的pm
    other_user_id = pm.receiver_id if pm.sender_id == notice_getter_user.id else pm.sender_id
    old_pm_notice = db.query(models.Notice
                             ).join(models.PrivateMessage
                             ).filter(or_(
                                        and_(models.PrivateMessage.sender_id == other_user_id, models.PrivateMessage.receiver_id == notice_getter_user.id),
                                        and_(models.PrivateMessage.sender_id == notice_getter_user.id, models.PrivateMessage.receiver_id == other_user_id)
                            )).first()
                                                       
    time = datetime.datetime.now()
    db_notice = models.Notice(user_id = notice_getter_user.id,
                              last_time = time,
                              is_system = False,
                              fresh = True,
                              system_detail = None,
                              pm_detail_id = pm.id)
    
    if old_pm_notice == None:
        db.add(db_notice)
        db.commit()
    else:
        db.delete(old_pm_notice)
        db.add(db_notice)
        db.commit()


""" class SystemNoticeDetail(BaseModel):
    event_executor_id: int
    event_executor_name: str
    event_executor_avatar_url: str
    event_content: str
"""

def create_like_notice(db: Session, notice_getter_user: models.User, post: models.Post, post_liker: models.User):
    time = datetime.datetime.now()
    sys_detail = {
        'event_executor_id': post_liker.id,
        'event_executor_name': post_liker.name,
        'event_executor_avatar_url': post_liker.avatar_url,
        'event_content': "您发布的信息 《" + post.title + "》 被 " + post_liker.name + " 点赞"
    }
    db_notice = models.Notice(user_id = notice_getter_user.id,
                              last_time = time,
                              is_system = True,
                              fresh = True,
                              system_detail = sys_detail,
                              pm_detail_id = None)
    db.add(db_notice)
    db.commit()

def create_star_notice(db: Session, notice_getter_user: models.User, post: models.Post, post_liker: models.User):
    time = datetime.datetime.now()
    sys_detail = {
        'event_executor_id': post_liker.id,
        'event_executor_name': post_liker.name,
        'event_executor_avatar_url': post_liker.avatar_url,
        'event_content': "您发布的信息 《" + post.title + "》 被 " + post_liker.name + " 收藏"
    }
    db_notice = models.Notice(user_id = notice_getter_user.id,
                              last_time = time,
                              is_system = True,
                              fresh = True,
                              system_detail = sys_detail,
                              pm_detail_id = None)
    db.add(db_notice)
    db.commit()

def create_comment_notice(db: Session, notice_getter_user: models.User, post: models.Post, post_liker: models.User, content: str):
    time = datetime.datetime.now()
    sys_detail = {
        'event_executor_id': post_liker.id,
        'event_executor_name': post_liker.name,
        'event_executor_avatar_url': post_liker.avatar_url,
        'event_content': "您发布的信息 《" + post.title + "》 被 " + post_liker.name + " 评论" + '\n' + content
    }
    db_notice = models.Notice(user_id = notice_getter_user.id,
                              last_time = time,
                              is_system = True,
                              fresh = True,
                              system_detail = sys_detail,
                              pm_detail_id = None)
    db.add(db_notice)
    db.commit()

def create_follow_notice(db: Session, notice_getter_user: models.User, follower_user: models.User):
    time = datetime.datetime.now()
    sys_detail = {
        'event_executor_id': follower_user.id,
        'event_executor_name': follower_user.name,
        'event_executor_avatar_url': follower_user.avatar_url,
        'event_content': "您被 " + follower_user.name + " 关注了"
    }
    db_notice = models.Notice(user_id = notice_getter_user.id,
                              last_time = time,
                              is_system = True,
                              fresh = True,
                              system_detail = sys_detail,
                              pm_detail_id = None)
    db.add(db_notice)
    db.commit()

def create_subscribe_notice(db: Session, notice_getter_user: models.User, new_post: models.Post, following_user: models.User):
    time = datetime.datetime.now()
    sys_detail = {
        'event_executor_id': following_user.id,
        'event_executor_name': following_user.name,
        'event_executor_avatar_url': following_user.avatar_url,
        'event_content': "您关注的 " + following_user.name + " 发布了信息 《" + new_post.title + "》"
    }
    db_notice = models.Notice(user_id = notice_getter_user.id,
                              last_time = time,
                              is_system = True,
                              fresh = True,
                              system_detail = sys_detail,
                              pm_detail_id = None)
    db.add(db_notice)
    db.commit()

def get_notices(db: Session, user_id: int) -> list[models.Notice]:
    return db.query(models.Notice).filter(models.Notice.user_id == user_id).order_by(models.Notice.last_time.desc()).all()
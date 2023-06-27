from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table, UniqueConstraint, Text, Enum, DateTime, PickleType
from sqlalchemy.orm import relationship, backref

from .database import Base


class Follow(Base):
    __tablename__ = "follows"
    id = Column(Integer, primary_key=True)
    follower = Column(Integer, ForeignKey("users.id"))
    followed = Column(Integer, ForeignKey("users.id"))
    UniqueConstraint(follower, followed, name="follow_relation")

class Block(Base):
    __tablename__ = "blocks"
    id = Column(Integer, primary_key=True)
    blocker = Column(Integer, ForeignKey("users.id"))
    blocked = Column(Integer, ForeignKey("users.id"))
    UniqueConstraint(blocker, blocked, name="block_relation")

star_table = Table(
    'stars',
    Base.metadata,
    Column('user_id', ForeignKey('users.id'), primary_key=True),
    Column('post_id', ForeignKey('posts.id'), primary_key=True),

)

like_table = Table(
    'likes',
    Base.metadata,
    Column('user_id', ForeignKey('users.id'), primary_key=True),
    Column('post_id', ForeignKey('posts.id'), primary_key=True)
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(64))
    email = Column(String(128), unique=True, index=True)
    hashed_password = Column(String)
    grade = Column(Integer)
    phone_number = Column(String(64))
    gender = Column(Integer)
    avatar_url = Column(String(128))
    introduction = Column(String(512))

    follower = relationship("User", secondary="follows", 
                            backref=backref("following", lazy="dynamic"),
                            lazy="dynamic",
                            primaryjoin=(Follow.followed == id),
                            secondaryjoin=(Follow.follower == id))
    
    blocker = relationship("User", secondary="blocks", 
                            backref=backref("blocking", lazy="dynamic"),
                            lazy="dynamic",
                            primaryjoin=(Block.blocked == id),
                            secondaryjoin=(Block.blocker == id))
    
    post = relationship('Post', backref='user')

    star_post = relationship('Post', secondary=star_table,
                              back_populates="star_user")
    
    like_post = relationship('Post', secondary=like_table,
                             back_populates="like_user")
    
    def __repr__(self):
        return '<User id:{}, name:{}>'.format(self.id, self.name)


class Post(Base):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(128))
    content = Column(Text)
    create_at = Column(DateTime)
    type = Column(String(128))
    location = Column(String(256))
    resources = Column(PickleType)
    user_id = Column(Integer, ForeignKey('users.id'))

    star_user = relationship('User', secondary=star_table,
                             back_populates='star_post')
    
    like_user = relationship('User', secondary=like_table,
                             back_populates='like_post')
    
    def __repr__(self):
        return '<Post id:{}, title: {}>'.format(self.id, self.title)

class Comment(Base):
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text)
    create_at = Column(DateTime)
    user_id = Column(Integer, ForeignKey('users.id'))
    post_id = Column(Integer, ForeignKey('posts.id'))

    def __repr__(self):
        return '<Comment id:{}>'.format(self.id)

class PrivateMessage(Base):
    __tablename__ = 'pmessage'

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey('users.id'))
    receiver_id = Column(Integer, ForeignKey('users.id'))
    content = Column(Text)
    create_at = Column(DateTime)

    def __repr__(self):
        return '<PrivateMessage id:{}>'.format(self.id)
    

class Notice(Base):
    __tablename__ = 'notice'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    last_time = Column(DateTime)
    is_system = Column(Boolean)
    fresh = Column(Boolean)
    system_detail = Column(PickleType)
    pm_detail_id = Column(Integer, ForeignKey('pmessage.id'))

    def __repr__(self):
        return '<Notice id:{}, user:{}>'.format(self.id, self.user_id)
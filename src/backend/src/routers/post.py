from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from fastapi_jwt_auth import AuthJWT

from sqlalchemy.exc import IntegrityError

from db_dependencies import schemas, crud, models
from .notice import create_like_notice, create_star_notice, create_comment_notice, create_subscribe_notice

get_db = crud.get_db

router = APIRouter(
    prefix='/post',
    tags=['post'],
)

@router.get('/listall')
async def list_all_posts(db: Session = Depends(get_db)):
    return crud.get_posts(db)

@router.post('', response_model=schemas.BasePost)
async def create_post(data: schemas.PostCreate, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_user_id = Authorize.get_jwt_subject()
    """ current_user_id = 1 """
    current_user = crud.get_user(db, current_user_id)
    if not current_user:
        raise HTTPException(status_code=400, detail='User not found')
    followers = current_user.follower.all()
    post = crud.create_new_post(db, data, current_user)
    for follower in followers:
        create_subscribe_notice(db, follower, post, current_user)
    return {'id': post.id}
    
@router.get('/type', response_model=schemas.TypeListResponse)
async def get_type_list(db: Session = Depends(get_db)):
    tuples = crud.get_types(db)
    res = []
    for t in tuples:
        res.append({'type': t[0], 'number': t[1]})
    return {'types': res}


@router.get('/{post_id}', response_model=schemas.DetailPost)
async def get_post_information(post_id: int, db: Session = Depends(get_db)):
    post = crud.get_post(db, post_id)
    if not post:
        raise HTTPException(status_code=400, detail='Post not found')
    
    like_num = crud.get_like_num(db, post)
    star_num = crud.get_star_num(db, post)
    comments = crud.get_comment(db, post)

    res_comments = []
    for r in comments:
        user_id = r.user_id
        user = crud.get_user(db, user_id)
        res_comments.append({
            'content': r.content,
            'id': r.id,
            'user_id': user_id,
            'create_at': r.create_at,
            'user_name': user.name,
            'avatar_url': user.avatar_url
        })

    return {
        'id': post.id,
        'title': post.title,
        'content': post.content,
        'create_at': post.create_at,
        'user_id': post.user_id,
        'like_num': like_num,
        'star_num': star_num,
        'comment': res_comments,
        'type': post.type,
        'location': post.location,
        'resources': post.resources
    }

@router.delete('/{post_id}')
async def del_a_post(post_id: int, db: Session = Depends(get_db)):
    '''
    这里没有检查当前用户，事实上可以删除任何帖子
    '''
    post = crud.get_post(db, post_id)
    if not post:
        raise HTTPException(400, detail='Post Not Found')
    return {
        'id': crud.del_post(db, post)
    }


def get_brief_information(post: models.Post, db: Session) -> schemas.BriefPost:
    like_num = crud.get_like_num(db, post)
    star_num = crud.get_star_num(db, post)
    comment_num = crud.get_comment_num(db, post)
    user = crud.get_user(db, post.user_id)
    like_user = [{'id': user.id} for user in post.like_user]
    star_user = [{'id': user.id} for user in post.star_user]

    return {
        'id': post.id,
        'title': post.title,
        'content': post.content,
        'create_at': post.create_at,
        'user_id': post.user_id,
        'like_num': like_num,
        'like_users': like_user,
        'star_num': star_num,
        'star_users': star_user,
        'comment_num': comment_num,
        'type': post.type,
        'location': post.location,
        'resources': post.resources,
        'username': user.name,
        'avatar_url': user.avatar_url
    }

def keyword_search(keyword: str, db: Session):
    res = []
    res.extend(crud.search_by_content(db, keyword))
    res.extend(crud.search_by_username(db, keyword))
    res.extend(crud.search_by_type(db, keyword))
    res.extend(crud.search_by_title(db, keyword))
    return res


@router.post('/query', response_model=schemas.BriefPostResponse)
async def query_post(query: schemas.PostQuery, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    '''
    默认 skip = 0, limit = 10
    若没有给定排序方式，按照时间排序
    若没有给定顺序，则默认按照倒序
    但十分不建议留空，可能哪个地方的逻辑不完善就炸了

    按照时间排序:
    order_by: time

    按照点赞排序:
    order_by: like

    按照收藏排序:
    order_by: star

    按照评论数排序:
    order_by: comment

    屏蔽黑名单中的用户
    block: 1 (任意非零整数就行，不存在该字段的情况下默认不屏蔽)


    1.筛选某一用户的帖子
    filter_by: 'user'
    filter_parameter: user_id
    两个参数均不可空

    2.筛选某一话题/类别的帖子
    filter_by: 'type'
    filter_parameter: xxx
    两个参数均不可空

    3.获取用户收藏的帖子
    filter_by: 'user_star'
    filter_parameter: user_id

    4.不筛选, 所有的帖子
    filter_by: 'none'
    filter_parameter: 留空即可

    5.用户关注者的所有帖子
    filter_by: 'user_follow'
    filter_parameter: 留空即可

    6.搜索
    filter_by: 'keyword'
    filter_parameter: 字符串, 关键词以空格分隔, 返回逻辑与的结果
    '''

    Authorize.jwt_required()
    current_user_id = Authorize.get_jwt_subject()
    """ current_user_id = 1 """
    current_user = crud.get_user(db, current_user_id)
    if not current_user:
        raise HTTPException(status_code=400, detail='User not found')
    
    if query.order_by != None and (query.order != 'desc' and query.order != 'asc' and query.order != None):
        raise HTTPException(422, detail='Invalid order')
    
    posts = []
    res_posts = []

    if query.filter_by == 'user':
        if not query.filter_parameter:
            raise HTTPException(422, detail='Empty user id')
        if not query.filter_parameter.isdigit():
            raise HTTPException(422, detail='Invalid user id')
        user = crud.get_user(db, int(query.filter_parameter))
        if not user:
            raise HTTPException(400, detail='User not found')
        
        if query.order_by == 'time' or query.order_by == None:
            posts = crud.get_post_by_uid_ol_time(db, user.id, query.order, query.limit, query.skip)
        elif query.order_by == 'like':
            posts = crud.get_post_by_uid_ol_like(db, user.id, query.order, query.limit, query.skip)
        elif query.order_by == 'star':
            posts = crud.get_post_by_uid_ol_star(db, user.id, query.order, query.limit, query.skip)
        elif query.order_by == 'comment':
            posts = crud.get_post_by_uid_ol_comment(db, user.id, query.order, query.limit, query.skip)
        else:
            raise HTTPException(422, detail='Invalid order by')
        res_posts = [get_brief_information(p, db) for p in posts]

    if query.filter_by == 'type':
        if not query.filter_parameter:
            raise HTTPException(422, detail='Empty type')
        type = query.filter_parameter
        if query.order_by == 'time' or query.order_by == None:
            posts = crud.get_post_by_type_ol_time(db, type, query.order, query.limit, query.skip)
        elif query.order_by == 'like':
            posts = crud.get_post_by_type_ol_like(db, type, query.order, query.limit, query.skip)
        elif query.order_by == 'star':
            posts = crud.get_post_by_type_ol_star(db, type, query.order, query.limit, query.skip)
        elif query.order_by == 'comment':
            posts = crud.get_post_by_type_ol_comment(db, type, query.order, query.limit, query.skip)
        else:
            raise HTTPException(422, detail='Invalid order by')
        res_posts = [get_brief_information(p, db) for p in posts]

    if query.filter_by == 'user_star':
        if not query.filter_parameter:
            raise HTTPException(422, detail='Empty user id')
        if not query.filter_parameter.isdigit():
            raise HTTPException(422, detail='Invalid user id')
        user = crud.get_user(db, int(query.filter_parameter))
        if not user:
            raise HTTPException(400, detail='User not found')
        if query.order_by == 'time' or query.order_by == None:
            posts = crud.get_post_by_userstar_ol_time(db, user, query.order, query.limit, query.skip)
        elif query.order_by == 'like':
            posts = crud.get_post_by_userstar_ol_like(db, user, query.order, query.limit, query.skip)
        elif query.order_by == 'star':
            posts = crud.get_post_by_userstar_ol_star(db, user, query.order, query.limit, query.skip)
        elif query.order_by == 'comment':
            posts = crud.get_post_by_userstar_ol_comment(db, user, query.order, query.limit, query.skip)
        else:
            raise HTTPException(422, detail='Invalid order by')
        res_posts = [get_brief_information(p, db) for p in posts]
    
    if query.filter_by == 'none':
        if query.order_by == 'time' or query.order_by == None:
            posts = crud.get_all_post_ol_time(db, query.order, query.limit, query.skip)
        elif query.order_by == 'like':
            posts = crud.get_all_post_ol_like(db, query.order, query.limit, query.skip)
        elif query.order_by == 'star':
            posts = crud.get_all_post_ol_star(db, query.order, query.limit, query.skip)
        elif query.order_by == 'comment':
            posts = crud.get_all_post_ol_comment(db, query.order, query.limit, query.skip)
        else:
            raise HTTPException(422, detail='Invalid order by')
        res_posts = [get_brief_information(p, db) for p in posts]

    if query.filter_by == 'user_follow':
        for f_user in current_user.following:
            posts.extend(f_user.post)
        if query.order_by == 'time' or query.order_by == None:
            if query.order == 'desc' or query.order == None:
                posts.sort(key= lambda p: p.create_at, reverse=True)
            else:
                posts.sort(key= lambda p: p.create_at)
        elif query.order_by == 'like':
            if query.order == 'desc' or query.order == None:
                posts.sort(key= lambda p: crud.get_like_num(db, p), reverse=True)
            else:
                posts.sort(key= lambda p: crud.get_like_num(db, p))
        elif query.order_by == 'star':
            if query.order == 'desc' or query.order == None:
                posts.sort(key= lambda p: crud.get_star_num(db, p), reverse=True)
            else:
                posts.sort(key= lambda p: crud.get_star_num(db, p))
        elif query.order_by == 'comment':
            if query.order == 'desc' or query.order == None:
                posts.sort(key= lambda p: crud.get_comment_num(db, p), reverse=True)
            else:
                posts.sort(key= lambda p: crud.get_comment_num(db, p))
        else:
            raise HTTPException(422, detail='Invalid order by')
        if query.limit != None and query.skip != None:
            posts = posts[query.skip : query.skip + query.limit]
        res_posts = [get_brief_information(p, db) for p in posts]

    if query.filter_by == 'keyword':
        if query.filter_parameter == None:
            raise HTTPException(422, detail='Empty key word')
        keyword_list = query.filter_parameter.split(' ')
        resset = None
        for k in keyword_list:
            kset = set(keyword_search(k, db))
            if resset == None:
                resset = kset
            else:
                resset = resset.intersection(kset)
        posts = list(resset)
        if query.order_by == 'time' or query.order_by == None:
            if query.order == 'desc' or query.order == None:
                posts.sort(key= lambda p: p.create_at, reverse=True)
            else:
                posts.sort(key= lambda p: p.create_at)
        elif query.order_by == 'like':
            if query.order == 'desc' or query.order == None:
                posts.sort(key= lambda p: crud.get_like_num(db, p), reverse=True)
            else:
                posts.sort(key= lambda p: crud.get_like_num(db, p))
        elif query.order_by == 'star':
            if query.order == 'desc' or query.order == None:
                posts.sort(key= lambda p: crud.get_star_num(db, p), reverse=True)
            else:
                posts.sort(key= lambda p: crud.get_star_num(db, p))
        elif query.order_by == 'comment':
            if query.order == 'desc' or query.order == None:
                posts.sort(key= lambda p: crud.get_comment_num(db, p), reverse=True)
            else:
                posts.sort(key= lambda p: crud.get_comment_num(db, p))
        else:
            raise HTTPException(422, detail='Invalid order by')
        if query.limit != None and query.skip != None:
            posts = posts[query.skip : query.skip + query.limit]
        res_posts = [get_brief_information(p, db) for p in posts]

    blocking_list = [user.id for user in current_user.blocking]
    if query.block != None and query.block != 0:
        res_posts = [post for post in res_posts if post['user_id'] not in blocking_list]
        
    return {'posts': res_posts}

@router.get('/{post_id}/comment', response_model=schemas.CommentResponseList)
async def get_post_comment(post_id: int, db: Session = Depends(get_db)):
    current_post = crud.get_post(db, post_id)
    if not current_post:
        raise HTTPException(status_code=400, detail="Post not found")
    raw_res = crud.get_comment(db, current_post)
    res = []
    for r in raw_res:
        user_id = r.user_id
        user = crud.get_user(db, user_id)
        res.append({
            'content': r.content,
            'id': r.id,
            'user_id': user_id,
            'create_at': r.create_at,
            'user_name': user.name,
            'avatar_url': user.avatar_url
        })
    return {
        'comments': res
    }

@router.post('/{post_id}/comment')
async def create_post_comment(post_id: int, data: schemas.CommentCreate, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_user_id = Authorize.get_jwt_subject()
    """ current_user_id = 2 """
    current_user = crud.get_user(db, current_user_id)
    if not current_user:
        raise HTTPException(status_code=400, detail='User not found')
    current_post = crud.get_post(db, post_id)
    if not current_post:
        raise HTTPException(status_code=400, detail="Post not found")
    comment_id = crud.create_comment(db, data, current_post, current_user)
    notice_getter = crud.get_user(db, current_post.user_id)
    if notice_getter == None:
        raise HTTPException(status_code=400, detail='这个异常不应该发生，请立刻联系jyx')
    create_comment_notice(db, notice_getter, current_post, current_user, data.content)
    return {'id': comment_id}
    

@router.post('/star', response_model=schemas.BasePost)
async def star_a_post(data: schemas.BasePost, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_user_id = Authorize.get_jwt_subject()
    """ current_user_id = 1 """
    current_user = crud.get_user(db, current_user_id)
    if not current_user:
        raise HTTPException(status_code=400, detail='User not found')
    current_post = crud.get_post(db, data.id)
    if not current_post:
        raise HTTPException(status_code=400, detail="Post not found")
    try:
        crud.create_post_star(db, current_post, current_user)
        notice_getter = crud.get_user(db, current_post.user_id)
        if notice_getter == None:
            raise HTTPException(status_code=400, detail='这个异常不应该发生，请立刻联系jyx')
        create_star_notice(notice_getter, current_post, current_user, db)
    except IntegrityError:
        raise HTTPException(status_code=400, detail='Duplicate like')
    return data

@router.post('/unstar', response_model=schemas.BasePost)
async def unstar_a_post(data: schemas.BasePost, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_user_id = Authorize.get_jwt_subject()
    """ current_user_id = 1 """
    current_user = crud.get_user(db, current_user_id)
    if not current_user:
        raise HTTPException(status_code=400, detail='User not found')
    current_post = crud.get_post(db, data.id)
    if not current_post:
        raise HTTPException(status_code=400, detail="Post not found")
    try:
        crud.remove_post_star(db, current_post, current_user)
    except IntegrityError:
        raise HTTPException(status_code=400, detail='这个异常不应该发生，请立刻联系jyx')
    except ValueError:
        raise HTTPException(status_code=400, detail='Unstar an unstarred post')
    return data

@router.post('/like', response_model=schemas.BasePost)
async def like_a_post(data: schemas.BasePost, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_user_id = Authorize.get_jwt_subject()
    """ current_user_id = 2 """
    current_user = crud.get_user(db, current_user_id)
    if not current_user:
        raise HTTPException(status_code=400, detail='User not found')
    current_post = crud.get_post(db, data.id)
    if not current_post:
        raise HTTPException(status_code=400, detail="Post not found")
    try:
        crud.create_post_like(db, current_post, current_user)
        notice_getter = crud.get_user(db, current_post.user_id)
        if notice_getter == None:
            raise HTTPException(status_code=400, detail='这个异常不应该发生，请立刻联系jyx')
        create_like_notice(notice_getter, current_post, current_user, db)
    except IntegrityError:
        raise HTTPException(status_code=400, detail='Duplicate like')
    return data

@router.post('/unlike', response_model=schemas.BasePost)
async def like_a_post(data: schemas.BasePost, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_user_id = Authorize.get_jwt_subject()
    """ current_user_id = 1 """
    current_user = crud.get_user(db, current_user_id)
    if not current_user:
        raise HTTPException(status_code=400, detail='User not found')
    current_post = crud.get_post(db, data.id)
    if not current_post:
        raise HTTPException(status_code=400, detail="Post not found")
    try:
        crud.remove_post_like(db, current_post, current_user)
    except IntegrityError:
        raise HTTPException(status_code=400, detail='这个异常不应该发生，请立刻联系jyx')
    except ValueError:
        raise HTTPException(status_code=400, detail='Unlike an unliked post')
    return data


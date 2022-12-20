from datetime import datetime
from fastapi import Depends, HTTPException, status, APIRouter, Response
from pymongo.collection import ReturnDocument
from app import schemas
from app.database import Post
from app.oauth2 import require_user
from app.serializers.postSerializers import postEntity, postListEntity
from bson.objectid import ObjectId
from pymongo.errors import DuplicateKeyError

router = APIRouter()


@router.get('/')
def get_posts(limit: int = 10, page: int = 1, search: str = '', user_id: str = Depends(require_user)):
    skip = (page - 1) * limit
    pipeline = [
        {'$match': {}},
        {'$lookup': {'from': 'users', 'localField': 'user',
                     'foreignField': '_id', 'as': 'user'}},
        {'$unwind': '$user'},
        {
            '$skip': skip
        }, {
            '$limit': limit
        }
    ]
    posts = postListEntity(Post.aggregate(pipeline))
    return {'status': 'success', 'results': len(posts), 'posts': posts}


@router.post('/', status_code=status.HTTP_201_CREATED)
def create_post(post: schemas.CreatePostSchema, user_id: str = Depends(require_user)):
    post.user = ObjectId(user_id)
    post.created_at = datetime.utcnow()
    post.updated_at = post.created_at
    try:
        result = Post.insert_one(post.dict())
        pipeline = [
            {'$match': {'_id': result.inserted_id}},
            {'$lookup': {'from': 'users', 'localField': 'user',
                         'foreignField': '_id', 'as': 'user'}},
            {'$unwind': '$user'},
        ]
        new_post = postListEntity(Post.aggregate(pipeline))[0]
        return new_post
    except DuplicateKeyError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"Post with title: '{post.title}' already exists")


@router.put('/{id}')
def update_post(id: str, payload: schemas.UpdatePostSchema, user_id: str = Depends(require_user)):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Invalid id: {id}")
    updated_post = Post.find_one_and_update(
        {'_id': ObjectId(id)}, {'$set': payload.dict(exclude_none=True)}, return_document=ReturnDocument.AFTER)
    if not updated_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'No post with this id: {id} found')
    return postEntity(updated_post)


@router.get('/{id}')
def get_post(id: str, user_id: str = Depends(require_user)):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Invalid id: {id}")
    pipeline = [
        {'$match': {'_id': ObjectId(id)}},
        {'$lookup': {'from': 'users', 'localField': 'user',
                     'foreignField': '_id', 'as': 'user'}},
        {'$unwind': '$user'},
    ]
    db_cursor = Post.aggregate(pipeline)
    results = list(db_cursor)

    if len(results) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No post with this id: {id} found")

    post = postListEntity(results)[0]
    return post


@router.delete('/{id}')
def delete_post(id: str, user_id: str = Depends(require_user)):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Invalid id: {id}")
    post = Post.find_one_and_delete({'_id': ObjectId(id)})
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'No post with this id: {id} found')
    return Response(status_code=status.HTTP_204_NO_CONTENT)

from fastapi import FastAPI, Depends, status, Response, HTTPException
import schemas, models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from typing import List
from hashing import Hash


from typing import Optional
import uvicorn


# from . import schemas

app = FastAPI()


models.Base.metadata.create_all(engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get('/blog', tags=['Blogs'])
def index(response: Response, db: Session = Depends(get_db)):
    blogs = db.query(models.Blog).all()
    if not blogs:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail='No Blog found')
    return blogs



@app.get('/blog/{id}', status_code=status.HTTP_200_OK, response_model=schemas.ShowBlog, tags=['Blogs'])
def show(id: int, response: Response, db: Session = Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()
    if not blog:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f'No Blog found with id {id}')
    return blog


@app.post('/blog', status_code=status.HTTP_201_CREATED, tags=['Blogs'])
def blog(request: schemas.Blog, db: Session = Depends(get_db)):
    new_blog = models.Blog(title=request.title, body=request.body, published=request.published)
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    return new_blog


@app.delete('/blog/{id}', status_code=status.HTTP_204_NO_CONTENT, tags=['Blogs'])
def destroy(id: int, db: Session = Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()
    if not blog:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f'No Blog found with id {id}')
    db.delete(blog)
    db.commit()
    return 'Done'


@app.put('/blog/{id}', status_code=status.HTTP_202_ACCEPTED, tags=['Blogs'])
def update(id: int, request: schemas.Blog, db: Session = Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == id)
    if not blog:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f'No Blog found with id {id}')
    blog.update(request.dict())
    db.commit()
    return 'updated'



@app.post('/user', status_code=status.HTTP_201_CREATED, response_model=schemas.ShowUser, tags=['Users'])
def add_user(request: schemas.User, db:Session = Depends(get_db)):
    req_data = request.dict().copy()
    req_data['password'] = Hash.bcrypt(request.password)
    new_user = models.User(**req_data)  # unpacking dict to create new user instance using pydantic model.  # **request.dict() is used to unpack the request.dict() into keyword arguments for the User model.  # This is a feature of Python's unpacking operator (*) and the dict unpacking operator (**).  # This allows us to create a new User object directly from the request data, without needing to manually set each attribute.  # This is a more concise and efficient way to create new model instances.  # Note: If you want to use the original dict structure, you can simply use new_user = models.User(**request).  # But then you would need to manually set each attribute.  # This is a trade-off between code readability and efficiency.  # For more complex models or when you want to manually set attributes, you might want to stick with the original dict structure.  # For
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.get('/user', response_model=List[schemas.ShowUser], tags=['Users'])
def show_all_users(response: Response, db: Session =  Depends(get_db)):
    Users = db.query(models.User).all()
    if not Users:
        response.status_code = status.HTTP_404_NOT_FOUND
    return Users


@app.get('/user/{id}', response_model=schemas.ShowUser, tags=['Users'])
def show_user(id: int, response: Response, db: Session =  Depends(get_db)):
    User = db.query(models.User).filter(models.User.id == id).first()
    if not User:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f'No User found with id {id}')
    return User


@app.delete('/user/{id}', status_code=status.HTTP_204_NO_CONTENT, tags=['Users'])
def destroy(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f'No User found with id {id}')
    db.delete(user)
    db.commit()
    return 'Done'


@app.put('/user/{id}', status_code=status.HTTP_202_ACCEPTED, tags=['Users'])
def update(id: int, request: schemas.ShowUser, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f'No User found with id {id}')
    user.update(request.dict())
    db.commit()
    return 'updated'


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)


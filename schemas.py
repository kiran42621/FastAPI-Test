from pydantic import BaseModel


# Pydantic models
class Blog(BaseModel):
    title: str
    body: str
    published: bool


class ShowBlog(Blog):
    author: 'ShowUser'
    class Config:
        orm_mode = True


class User(BaseModel):
    name: str
    email: str
    password: str


class ShowUser(BaseModel):
    name: str
    email: str
    blogs: ShowBlog
    class Config:
        orm_mode = True


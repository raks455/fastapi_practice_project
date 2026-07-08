from fastapi import FastAPI,status,HTTPException,Depends
from sqlalchemy import create_engine,Column,Integer,String
from sqlalchemy.orm import sessionmaker,declarative_base,Session
from jose import jwt
from datetime import datetime,timedelta,timezone
import time
import asyncio

from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from passlib.context import CryptContext
app=FastAPI()

SECRET_KEY="mysecret"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30

#PASSWORD hashing setup
pwd_context=CryptContext(schemes=["bcrypt"],deprecated="auto")
#Oauth setup
oauth2_schema=OAuth2PasswordBearer(tokenUrl="login")
#dummy user database
fake_user_db={
    "admin":{
        "username":"admin",
        "hashed_password":pwd_context.hash("1234")
    }
    
}
#hash password
def hash_password(password:str):
    return pwd_context.hash(password)
#verify password
def verify_password(plain_password,hashed_password):
    return pwd_context.verify(plain_password,hashed_password)
#create token
def create_token(data:dict):
    to_encode=data.copy()
    expire=datetime.now(timezone.utc)+timedelta(minutes=30)
    to_encode.update({"exp":expire})
    token=jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
    return token
#token verify
def tokenVerify(token:str=Depends(oauth2_schema)):
    try:
        payload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        username:str=payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid token")
        
        return username
    except jwt.JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid token")
        
#loginapi(generate token
@app.post("/login")
def login(form_data:OAuth2PasswordRequestForm=Depends()):
    user=fake_user_db.get(form_data.username)
    if not user or not verify_password(form_data.password,user["hashed_password"]):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Invalid username or password")
    access_token=create_token({
        "sub":form_data.username
    })
    return {"access_token":access_token,"token_type":"bearer"}
        
@app.get("/secure-data")
def secure_data(user=Depends(tokenVerify)):
    return {
        "message":"secure data accessed",
        "user":user
    }
@app.get("/protected")
def protected_route(username:str=Depends(tokenVerify)):
    return {
        "message":f"hello ${username} you have access to this protected route",
        "user":username
     
    }

DATABASE_URL="sqlite:///./testt.db"
engine=create_engine(DATABASE_URL,connect_args={"check_same_thread":False})
sessionLocal=sessionmaker(bind=engine)
Base=declarative_base()
def task():
   time.sleep(3)
   return "Done"
async def task():
    await asyncio.sleep(3)
    return "Done"
class Todo(Base):
    __tablename__="todo"
    id=Column(Integer,primary_key=True,index=True)
    title=Column(String)
  
    completed=Column(Integer)

Base.metadata.create_all(bind=engine)


def get_db():
    db=sessionLocal()
    try:
        yield db
    finally:
        db.close
    
@app.get("/")
async def home(db:Session=Depends(get_db)):
    await asyncio.sleep(3)
    return {"message":"db connected successfully"}
        

@app.post("/todos")
def createTodo(title:str,completed:bool,db:Session=Depends(get_db)):
    todo=Todo(title=title,completed=completed)
    
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return {
        "message":"todo created successfully",
        "data":todo
    }

@app.get("/todos")
def showTodo(db:Session=Depends(get_db)):
    todos=db.query(Todo).all()
    return{
        "total":len(todos),
        "data":todos
    }
    
@app.get("/todos/{todo_id}")
def showTodoById(id=int,db:Session=Depends(get_db)):
    todos=db.query(Todo).filter(Todo.id==id).first()
    if not  todos:
        raise HTTPException(status_code=404,detail="todo not found")
    return todos

@app.put("/todos/{todo_id}")
def updateTodoById(id=int,title=str,db:Session=Depends(get_db)):
    todos=db.query(Todo).filter(Todo.id==id).first()
    if not todos:
        raise HTTPException(status_code=404,detail="todo not found")
    todos.title=title
    db.commit()
    db.refresh(todos)
    return {
        "message":"todo updated successfully",
        "data":todos
    }
    
@app.delete("/todos/{todo_id}")
def deleteById(id=int,db:Session=Depends(get_db)):
    todos=db.query(Todo).filter(Todo.id==id).first()
    if not todos:
        raise HTTPException(status_code=404,detail="todo not found")
    db.delete(todos)
    db.commit()
    return {
        "message":"todo deleted successfully"
    }
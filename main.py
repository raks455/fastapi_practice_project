from fastapi import FastAPI,status,HTTPException,Request,Depends,Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import create_engine,Column,Integer,String
from sqlalchemy.orm import sessionmaker,declarative_base,Session
import time
import asyncio
app=FastAPI()

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
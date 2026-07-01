from fastapi import FastAPI,status,HTTPException,Request,Depends,Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import create_engine,Column,Integer,String
from sqlalchemy.orm import sessionmaker,declarative_base,Session
app=FastAPI()
DATABASE_URL="sqlite:///./testt.db"
engine=create_engine(DATABASE_URL,connect_args={"check_same_thread":False})
sessionLocal=sessionmaker(bind=engine)
Base=declarative_base()
class Todo(Base):
    __tablename__="todo"
    id=Column(Integer,primary_key=True,index=True)
    title=Column(String)
    description=Column(String)
    completed=Column(Integer)

Base.metadata.create_all(bind=engine)


def get_db():
    db=sessionLocal()
    try:
        yield db
    finally:
        db.close
    
@app.get("/")
def home(db:Session=Depends(get_db)):
    return {"message":"db connected successfully"}
        
    
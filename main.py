from fastapi import FastAPI,status,HTTPException,Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
app=FastAPI()
todos=[]

class Todo(BaseModel):
    id:int
    name:str
    age:int
    email:str
    
class UserNotFoundException(Exception):
    def __init__(self,name:str):
       self.name=name
@app.exception_handler(UserNotFoundException)
def user_not_found_handler(request:Request,exc:UserNotFoundException):
    return JSONResponse(
        status_code=404,
        content={"status":"error",
            "message":f"user {exc.name} not found"
        })
@app.get("/user/{name}")  
def getname(name:str):
    if name!="ram":
        raise UserNotFoundException(name)
    return {"name":name}



@app.get("/users",status_code=status.HTTP_200_OK)
def main(user_id:int=1000,age:int=10):
    return {"message":user_id,"age":age,"status":"success"}
    
    
@app.post("/todos",status_code=status.HTTP_201_CREATED)
def createUser(todo:Todo):
    todos.append(todo)
    return {
        "message":"created successfully",
        
    }
@app.get("/viewtodo")
def showTodo():
    return todos

@app.get("/viewtodo/{todo_id}")
def showTodoEach(todo_id:int):
    if todo_id==1:
      raise HTTPException(status_code=404,detail="User not found")
    for index,todo in enumerate(todos):
     if todo.id==todo_id:
        return todos
     return {"error":"todo not fpund"}
 
 
@app.put("/todos/{todo_id}")
def update_todo(todo_id:int,updated_todo:Todo,notify:bool=False):
    for index,todo in enumerate(todos):
        if todo.id ==todo_id:
            todos[index]=updated_todo
            return {"message":"updated successfully","data":updated_todo,
                    "notify":notify}
    return {"error":"todo not found"}

@app.delete("/deletetodo/{todo_id}")
def deleteTodo(todo_id:int):
    for index,todo in enumerate(todos):
        if todo.id==todo_id:
            del todos[index]
            return {"message":"deleted successfully"}
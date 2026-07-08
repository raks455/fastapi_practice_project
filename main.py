from fastapi import FastAPI,UploadFile,File,HTTPException,Request
from fastapi.staticfiles import StaticFiles
import requests
import os
from bs4 import BeautifulSoup
import shutil
from config import settings
import time
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
app=FastAPI()
cache_data=[]
limiter=Limiter(key_func=get_remote_address)
app.state.limiter=limiter

last_fetch=0
url="https://example.com"
response=requests.get(url)
soup=BeautifulSoup(response.text,"html.parser")
print(soup.title.text)
app.add_middleware(CORSMiddleware,allow_origins=settings.origins,allow_credentials=True,allow_methods=["*"],allow_headers=["*"]) 
@app.exception_handler(RateLimitExceeded)
def rate_limit_handler(request:Request, exc:RateLimitExceeded):
    return JSONResponse(content={"error": "Rate limit exceeded"}, status_code=429)

@app.get("/data")
@limiter.limit("5/minute")
def getdata(request:Request):
    return {"message":"Success"}
@app.get("/news")
def get_news(page:int=1,limit:int=10):
    global cache_data,last_fetch
    start=time.time()
    if time.time()-last_fetch>60:
        print("fetching fresh data")
        url="https://news.google.com/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx1YlY4U0FtVnVHZ0pWVXlnQVAB?hl=en-US&gl=US&ceid=US%3Aen"
        response=requests.get(url)
        soup=BeautifulSoup(response.text,"html.parser")
        cache_data=[
            item.text for item in soup.find_all("a",class_="svxzne")
        ]
        
        last_fetch=time.time()

    else:
        print("fetching from cache")
    end=time.time()
    time_take=round(end-start,4)
    print("time taken",time_take)
    return {
        "time_taken":time_take,
        "page":page,
        "limit":limit,
        "total_news":len(cache_data),
        "news":cache_data[(page-1)*limit:page*limit]
    }
  
      
       

@app.get("/posts")
def get_posts(page:int=1,limit:int=10):
    url="https://jsonplaceholder.typicode.com/posts/"
    start=(page-1)*limit
    end=start+limit
    responses=requests.get(url)
    return{"page":page,"limit":limit,"total_posts":len(responses.json()),"posts":responses.json()[start:end]}
@app.get("/posts/{id}")
def get_posts(id:int):
    url=f"https://jsonplaceholder.typicode.com/posts/{id}"
    response=requests.get(url)
    if response.status_code==200:
        return response.json()
    else:
        raise HTTPException(status_code=404,detail="Post not found")
#Step -1  Ensure upload folderexist
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

#Step 2 static file setup
#Url :htttps://127.0.0.1:8000/FILES/<filename>
app.mount("/files",StaticFiles(directory=UPLOAD_DIR),name="files")
@app.get("/add")
def add(a:int,b:int):
    return {"result":a+b}
#Step 3 upload file api
@app.post("/upload")
def upload_file(file:UploadFile=File(...)):
    filename=file.filename
    file_path=os.path.join(UPLOAD_DIR,filename)
    if not filename:
        raise HTTPException(status_code=400,detail="No file selected")
    with open(file_path,"wb") as buffer:
        shutil.copyfileobj(file.file,buffer)
        return {"message":"File uploaded successfully",
                "filename":filename,
                "file_url":f"http://127.0.0.1:8000/files/{filename}"}

#step 4 get file api
@app.get("/files/{filename}")
def get_file(filename:str):
    file_path=os.path.join(UPLOAD_DIR,filename)
    if not os.path.exists :
        raise HTTPException(status_code=404,detail="File not found")
    
    return {"file_url":f"http://127.0.0.1:8000/files/{filename}"}
    
@app.get("/")
def home():
    return {
        "message":"cors enable api"
    }
from fastapi import FastAPI,UploadFile,File,HTTPException
from fastapi.staticfiles import StaticFiles
import requests
import os
from bs4 import BeautifulSoup
import shutil
from config import settings
from fastapi.middleware.cors import CORSMiddleware
app=FastAPI()
url="https://example.com"
response=requests.get(url)
soup=BeautifulSoup(response.text,"html.parser")
print(soup.title.text)
app.add_middleware(CORSMiddleware,allow_origins=settings.origins,allow_credentials=True,allow_methods=["*"],allow_headers=["*"]) 
@app.get("/news")
def get_news(page:int=1,limit:int=10):
    url="https://news.google.com/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx1YlY4U0FtVnVHZ0pWVXlnQVAB?hl=en-US&gl=US&ceid=US%3Aen"
    response=requests.get(url)
    soup=BeautifulSoup(response.text,"html.parser")
    title=[]
    for item in soup.find_all("a",class_="svxzne"):
        title.append(item.text)
        start=(page-1)*limit
        end=start+limit
        return {
            "page":page,
            "limit":limit,
            "total_news":len(title),
            "news":title[start:end]
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
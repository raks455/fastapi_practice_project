from fastapi import FastAPI,UploadFile,File,HTTPException
from fastapi.staticfiles import StaticFiles
import os
import shutil
from .env import origins as origin
from fastapi.middleware.cors import CORSMiddleware
app=FastAPI()
#allowed origin frontend url

app.add_middleware(CORSMiddleware,allow_origins=origin,allow_credentials=True,allow_methods=["*"],allow_headers=["*"])    

#Step -1  Ensure upload folderexist
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

#Step 2 static file setup
#Url :htttps://127.0.0.1:8000/FILES/<filename>
app.mount("/files",StaticFiles(directory=UPLOAD_DIR),name="files")

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
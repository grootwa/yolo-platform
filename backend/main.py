from fastapi import FastAPI, Body, UploadFile, File
from models import ProjectModel
from fastapi.encoders import jsonable_encoder
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os
from typing import List

# db details 
MONGO_DETAILS = "mongodb://localhost:27017"

# create upload folder if doesnt exist
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


app = FastAPI()


# create a client
client =  AsyncIOMotorClient(MONGO_DETAILS)

database = client.yolo_db
projects_collection = database.get_collection("projects")

@app.get("/")
def home():
    return{"message": "hello world !"}

# check db connection
@app.get("/check_db")
async def home():
    try:
        await client.admin.command('ping')
        status = "Database Connected"
    except Exception as e:
        status = f"Database connection failed : {e}"
    
    return {"db status": status}

# create a project
@app.post("/projects")
async def create_project(project: ProjectModel = Body(...)):
    
    # python object into json
    project_data = jsonable_encoder(project)

    # save into "projects" collection
    new_project = await projects_collection.insert_one(project_data)
    return {
        "id": str(new_project.inserted_id),
        "message": "project saved successfully"
    }

# get all projects
@app.get("/projects")
async def get_projects():
    projects = []
    cursor = projects_collection.find()
    
    async for document in cursor:
        document["id"] = str(document["_id"])
        del document["_id"]
        projects.append(document)

    return projects

# get project by id
@app.get("/projects/{project_id}")
async def get_project(project_id: str):
    project = await projects_collection.find_one({"_id": ObjectId(project_id)})

    if project:
        project["id"] = str(project["_id"])
        del project["_id"]
        return project
    return {"error": "project not found"}

# delete project
@app.delete("/projects/{project_id}")
async def delete_project(project_id: str):
    delete_result = await projects_collection.delete_one({"_id": ObjectId(project_id)})

    if delete_result.deleted_count == 1:
        return {"message": "Project deleted Sucessfully !"}
    return {"error": "Project Not found"}

@app.post("/projects/{project_id}/upload")
async def upload_image(project_id: str, file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_FOLDER, f"{project_id}_{file.filename}")

    # save file to disk
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    await projects_collection.update_one(
        {"_id": ObjectId(project_id)},
        {"$push": {"images": file_path}}
    )

    return {"filename": file.filename, "status": "Uploaded and linked"}


@app.post("/projects/{project_id}/upload-batch")
async def upload_batch(project_id: str, files: List[UploadFile] = File(...)):
    uploaded_paths = []
    
    # 1. Ensure the project folder exists
    project_path = os.path.join(UPLOAD_FOLDER, project_id)
    os.makedirs(project_path, exist_ok=True)
    
    for file in files:
        # 2. Save each file
        file_path = os.path.join(project_path, file.filename)
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())
        uploaded_paths.append(file_path)
    
    # 3. Update MongoDB once with the whole list (using $each)
    await projects_collection.update_one(
        {"_id": ObjectId(project_id)},
        {"$push": {"images": {"$each": uploaded_paths}}}
    )
    
    return {
        "status": "Success", 
        "count": len(uploaded_paths), 
        "message": f"Uploaded {len(uploaded_paths)} images to project {project_id}"
    }
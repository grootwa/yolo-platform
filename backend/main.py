from fastapi import FastAPI, Body
from models import ProjectModel
from fastapi.encoders import jsonable_encoder
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

app = FastAPI()

# connect db 

MONGO_DETAILS = "mongodb://db:27017"

# create a client
client =  AsyncIOMotorClient(MONGO_DETAILS)

database = client.yolo_db
projects_collection = database.get_collection("projects")

@app.get("/")
def home():
    return{"message": "hello world !"}

@app.get("/home")
async def home():
    try:
        await client.admin.command('ping')
        status = "Database Connected"
    except Exception as e:
        status = f"Database connection failed : {e}"
    
    return {"db status": status}

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

@app.get("/projects")
async def get_projects():
    projects = []
    cursor = projects_collection.find()
    
    async for document in cursor:
        document["id"] = str(document["_id"])
        del document["_id"]
        projects.append(document)

    return projects

@app.get("/projects/{project_id}")
async def get_project(project_id: str):
    project = await projects_collection.find_one({"_id": ObjectId(project_id)})

    if project:
        project["id"] = str(project["_id"])
        del project["_id"]
        return project
    return {"error": "project not found"}

@app.delete("/projects/{project_id}")
async def delete_project(project_id: str):
    delete_result = await projects_collection.delete_one({"_id": ObjectId(project_id)})

    if delete_result.deleted_count == 1:
        return {"message": "Project deleted Sucessfully !"}
    return {"error": "Project Not found"}

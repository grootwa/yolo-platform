from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient

app = FastAPI()

# connect db 

MONGO_DETAILS = "mongodb://db:27017"

# create a client
client =  AsyncIOMotorClient(MONGO_DETAILS)

database = client.yolo_db

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
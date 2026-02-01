from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from bson import ObjectId
from fastapi.middleware.cors import CORSMiddleware
from .database import collection

app = FastAPI()

# Allow frontend (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Task(BaseModel):
    title: str
    completed: bool = False   # new field

# Helper to convert MongoDB document
def task_helper(task) -> dict:
    return {
        "id": str(task["_id"]),
        "title": task["title"],
        "completed": task.get("completed", False)
    }

@app.get("/tasks")
async def get_tasks():
    tasks = []
    async for task in collection.find():
        tasks.append(task_helper(task))
    return tasks

@app.post("/tasks")
async def add_task(task: Task):
    new_task = {"title": task.title, "completed": False}
    result = await collection.insert_one(new_task)
    return {"id": str(result.inserted_id), "title": task.title, "completed": False}

@app.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    result = await collection.delete_one({"_id": ObjectId(task_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted"}

@app.put("/tasks/{task_id}")
async def mark_task(task_id: str, task: Task):
    result = await collection.update_one(
        {"_id": ObjectId(task_id)},
        {"$set": {"completed": task.completed}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task updated"}
# add
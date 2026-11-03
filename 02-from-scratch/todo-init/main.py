from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Todo")
todos = []


class Todo(BaseModel):
    title: str


@app.get("/")
def home():
    return {"message": "Todo API is running"}


@app.get("/todos")
def list_todos():
    return todos


@app.post("/todos")
def add_todo(todo: Todo):
    todos.append(todo.title)
    return {"count": len(todos)}

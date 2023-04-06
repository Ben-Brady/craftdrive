from fastapi import FastAPI, Query, Body, Response
from pydantic import BaseModel, Field
from pprint import pprint
from typing import Literal, Union
import uvicorn
import time
import random

app = FastAPI()
BLOCK_SIZE = 16


class Task(BaseModel):
    id: int = Field(default_factory=lambda: random.randint(0, 2**16), gt=0)
    computer: int
    command: Literal["read"] | Literal["write"]
    data: Union[list[int], None] = None


active_tasks: list[Task] = []
finished_reads: dict[int, list[int]] = {}


@app.get('/tasks/{computer}')
def get_tasks(computer: int) -> list[Task]:
    return [
        task for task in active_tasks
        if task.computer == computer
    ]


@app.post('/report/read')
def report_read(
        id: int = Query(),
        data: list[int] = Body(embed=True),
        ):
    task = next((task for task in active_tasks if task.id == id), None)
    if task is None:
        return Response(status_code=404)
    else:
        active_tasks.remove(task)
        finished_reads[task.id] = data
        return Response(status_code=200)


@app.post('/report/write')
def report_write(id: int = Query()):
    task = next((task for task in active_tasks if task.id == id), None)
    if task is None:
        return Response(status_code=404)
    else:
        active_tasks.remove(task)
        return Response(status_code=200)


@app.post("/write")
def endpoint_write(
        id: int = Query(),
        data: list[int] = Body(embed=True),
        ):
    store(id, data)
    pprint(active_tasks)


@app.get("/read")
def endpoint_read(id: int = Query()) -> list[int]:
    data = read(id)
    return list(data)


def read(id: int) -> list[int]:
    task = Task(
        command="read",
        computer=id,
    )
    active_tasks.append(task)
    while task.id not in finished_reads:
        time.sleep(0.001)

    return finished_reads.pop(task.id)


def store(block_id: int, data: list[int]):
    task = Task(
        command="write",
        computer=block_id,
        data=data,
    )
    active_tasks.append(task)

    while len(active_tasks) != 0:
        time.sleep(0.001)


def start_server():
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
    )


if __name__ == '__main__':
    start_server()

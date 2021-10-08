def route_todos() -> str:
    return "/todos/"


def route_todo(todo_id: int) -> str:
    return route_todos() + str(todo_id)

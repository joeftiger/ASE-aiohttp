from typing import Optional, Union, Mapping

from tinydb import TinyDB, Query, operations
from tinydb.table import Document

from todo import route_todo
from tag import route_tag

db = TinyDB("./ase.db")
db_todos = db.table("todos")    # contains the todos
db_links = db.table("links")    # contains the link (todo_id <-> tag_id)
db_tags = db.table("tags")      # contains the tags

mapping = {
    "title": "some bullshit",
    "order": 1,
}

# TODO: Performance won't be good likely, but I first want a working solution

########################################################################################################################
### TODOS                                                                                                           ####
########################################################################################################################
def db_get_todos() -> map[dict[str, Union[int, bool, str, list[dict[str, Union[str, int]]]]]]:
    def fn_map(doc: Document):
        tags = db_link_from_todo(doc["tags"])
        return {
            "id": doc.doc_id,
            "title": doc["title"],
            "completed": doc["completed"],
            "url": route_todo(doc.doc_id),
            "order": doc["order"],
            "tags": tags,
        }

    return map(fn_map, db_todos.all())
def db_post_todo(fields: dict[str, Union[int, bool, str]]) -> dict[str, Union[int, bool, str]]:
    todo = {
        "title": fields["title"],
        "completed": fields["completed"],
        "order": fields["order"],
        "tags": [],
    }
    todo_id = db_todos.insert(todo)
    return {
        "id": todo_id,
        "title": todo["title"],
        "completed": todo["completed"],
        "url": route_todo(todo_id),
        "order": todo["order"],
    }
def db_delete_todos():
    db_todos.truncate()
def db_get_todo(todo_id: int) -> Optional[dict[str, Union[int, bool, str, list[dict[str, Union[str, int]]]]]]:
    raw = db_todos.get(doc_id=todo_id)

    if raw:
        tags = db_get_tags(raw["tags"])
        todo = {
            "id": todo_id,
            "title": raw["title"],
            "completed": raw["completed"],
            "url": route_todo(todo_id),
            "order": raw["order"],
            "tags": tags,
        }

        return todo
    else:
        return None
def db_patch_todo(todo_id: int, fields: dict[str, Union[int, bool, str]]) -> dict[str, Union[int, bool, str]]:
    db_todos.update(fields, doc_ids=[todo_id])

    return {
        "id": todo_id,
        "title": fields["title"],
        "completed": fields["completed"],
        "url": route_todo(todo_id),
        "order": fields["order"]
    }
def db_get_tag(todo_id: int) -> list[dict[str, Union[str, int]]]:
    raw = db_todos.get(doc_id=todo_id)
    if raw:
        return db_get_tags(raw["tags"])
    else:
        return []
def db_post_todo_tag(todo_id: int, tag_id: int):
    db_links.insert({
        "todo": todo_id,
        "tag": tag_id,
    })
def db_delete_todo_tags(todo_id: int):
    db_links.remove(cond=Query()["todo"] == todo_id)
def db_delete_todo_tag(todo_id: int, tag_id: int):
    cond = Query()["todo"] == todo_id & Query()["tag"] == tag_id
    db_links.remove(cond=cond)


########################################################################################################################
### LINKS                                                                                                           ####
########################################################################################################################
# TODO: USE THIS
def db_link_from_todo(todo_id: int) -> list[dict[str, Union[str, int]]]:
    def get_tag(d: Document) -> dict[str, Union[str, int]]:
        tag: Document = db_tags.get(doc_id=d["tag"])
        return {
            "id": tag.doc_id,
            "title": tag["title"],
            "url": route_tag(tag.doc_id),
        }

    return list(map(
        get_tag,
        db_links.search(Query()["todo"] == todo_id)
    ))

########################################################################################################################
### TAGS                                                                                                            ####
########################################################################################################################
def db_get_tags(ids: list[int]) -> list[dict[str, Union[str, int]]]:
    tags = []
    for tag_id in ids:
        tag = db_tags.get(doc_id=tag_id)
        tags.append({
            "id": tag_id,
            "title": tag["title"],
            "url": route_tag(tag_id),
        })

    return tags
def db_post_tag(fields: dict[str, str])-> dict[str, Union[int, str]]:
    tag = {
        "title": fields["title"]
    }
    db_tags.

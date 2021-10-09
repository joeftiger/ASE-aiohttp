from typing import Optional, Union

from tinydb import TinyDB, Query
from tinydb.table import Document


class Database:
    db = TinyDB("./ase.db")
    TODOS = db.table("todos")  # contains the todos
    LINKS = db.table("links")  # contains the link (todo_id <-> tag_id)
    TAGS = db.table("tags")  # contains the tags

    def populate_if_empty(self):
        if len(self.TODOS) == 0 and len(self.LINKS) == 0 and len(self.TAGS) == 0:
            self.TODOS.insert_multiple([
                {'title': 'build an API', 'order': 1, 'completed': False},
                {'title': '?????', 'order': 2, 'completed': False},
                {'title': 'profit!', 'order': 3, 'completed': False}
            ])

    ####################################################################################################################
    # TODOS                                                                                                      TODOS #
    ####################################################################################################################
    def get_todos(self) -> list[dict[str, Union[int, bool, str, list[dict[str, Union[str, int]]]]]]:
        def fn_map(doc: Document):
            tags = self.tags_from_todo(doc.doc_id)
            return {
                "id": doc.doc_id,
                "title": doc["title"],
                "completed": doc["completed"],
                "order": doc["order"],
                "tags": tags,
            }

        return list(map(fn_map, self.TODOS.all()))

    def post_todo(self, fields: dict[str, Union[int, bool, str]]) -> dict[str, Union[int, bool, str]]:
        todo = {
            "title": fields["title"],
            "completed": fields.setdefault("completed", False),
            "order": fields.setdefault("order", 0),
        }
        todo_id = self.TODOS.insert(todo)
        return {
            "id": todo_id,
            "title": todo["title"],
            "completed": todo["completed"],
            "order": todo["order"],
        }

    def delete_todos(self):
        self.TODOS.truncate()
        self.LINKS.truncate()

    def get_todo(self, todo_id: int) -> Optional[dict[str, Union[int, bool, str, list[dict[str, Union[str, int]]]]]]:
        doc = self.TODOS.get(doc_id=todo_id)

        if doc:
            tags = self.tags_from_todo(todo_id)
            return {
                "id": todo_id,
                "title": doc["title"],
                "completed": doc["completed"],
                "order": doc["order"],
                "tags": tags,
            }
        else:
            return None

    def delete_todo(self, todo_id: int):
        if not len(self.TODOS.remove(doc_ids=[todo_id])):
            return False
        self.LINKS.remove(cond=Query().todo == todo_id)

        return True

    def patch_todo(self, todo_id: int, fields: dict[str, Union[int, bool, str]]) -> Optional[
        dict[str, Union[int, bool, str]]]:
        if not len(self.TODOS.update(fields, doc_ids=[todo_id])):
            return None

        return self.get_todo(todo_id)

    def get_todo_tags(self, todo_id: int) -> list[dict[str, Union[int, str]]]:
        doc = self.TODOS.get(doc_id=todo_id)
        if doc:
            return self.tags_from_todo(todo_id)
        else:
            return []

    def post_todo_tag(self, todo_id: int, tag_id: int):
        self.LINKS.insert({
            "todo": todo_id,
            "tag": tag_id,
        })

    def delete_todo_tags(self, todo_id: int):
        self.LINKS.remove(cond=Query().todo == todo_id)

    def delete_todo_tag(self, todo_id: int, tag_id: int):
        cond = Query().todo == todo_id & Query().tag == tag_id
        self.LINKS.remove(cond)

    ####################################################################################################################
    # LINKS                                                                                                      LINKS #
    ####################################################################################################################
    def tags_from_todo(self, todo_id: int) -> list[dict[str, Union[int, str]]]:
        """
        Returns all tags linked to a todo.

        The returned format is:
          * [{ "id": tag ID, "title": tag title}]
        :param todo_id: the document ID of the todo
        :return: list of tags
        """

        def get_tag(doc: Document) -> dict[str, Union[str, int]]:
            tag: Document = self.TAGS.get(doc_id=doc["tag"])
            return {
                "id": tag.doc_id,
                "title": tag["title"],
            }

        return list(map(
            get_tag,
            self.LINKS.search(Query().todo == todo_id)
        ))

    def todos_from_tag(self, tag_id: int) -> list[dict[str, Union[int, bool, str]]]:
        """
        Returns all todos linked to a tag.

        The returned format is:
          * [{"id": int, "title": str, "completed": bool}]
        :param tag_id:
        :return: list of todos
        """

        def get_todo(d: Document) -> dict[str, Union[int, bool, str]]:
            todo: Document = self.TODOS.get(doc_id=d["todo"])
            return {
                "id": todo.doc_id,
                "title": todo["title"],
                "completed": todo["completed"],
                "order": todo["order"],
            }

        return list(map(
            get_todo,
            self.LINKS.search(Query().tag == tag_id)
        ))

    ####################################################################################################################
    # TAGS                                                                                                        TAGS #
    ####################################################################################################################
    def get_tags(self) -> list[dict[str, Union[str, int]]]:
        def fn_map(doc: Document):
            tags = self.todos_from_tag(doc.doc_id)
            return {
                "id": doc.doc_id,
                "title": doc["title"],
                "tags": tags,
            }

        return list(map(fn_map, self.TAGS.all()))

    def post_tag(self, fields: dict[str, str]) -> dict[str, Union[int, str]]:
        tag = {
            "title": fields["title"]
        }
        tag_id = self.TAGS.insert(tag)

        return {
            "id": tag_id,
            "title": tag["title"],
        }

    def delete_tags(self):
        self.TAGS.truncate()
        self.LINKS.truncate()

    def get_tag(self, tag_id: int) -> Optional[dict[str, Union[int, bool, str, list[dict[str, Union[str, int]]]]]]:
        doc = self.TAGS.get(doc_id=tag_id)

        if doc:
            todos = self.todos_from_tag(tag_id)
            return {
                "id": tag_id,
                "title": doc["title"],
                "todos": todos,
            }
        else:
            return None

    def delete_tag(self, tag_id: int) -> bool:
        if not len(self.TAGS.remove(doc_ids=[tag_id])):
            return False
        self.LINKS.remove(cond=Query().tag == tag_id)

        return True

    def patch_tag(self, tag_id: int, fields: dict[str, str]) -> Optional[dict[str, Union[int, bool, str]]]:
        if not len(self.TAGS.update(fields=fields, doc_ids=[tag_id])):
            return None

        return self.get_tag(tag_id)

    def get_tag_todos(self, tag_id: int) -> list[dict[str, Union[int, bool, str]]]:
        doc = self.TAGS.get(doc_id=tag_id)
        if doc:
            return self.todos_from_tag(tag_id)
        else:
            return []

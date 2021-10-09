from aiohttp import web

from db import Database

db = Database()


def get_todos(request):
    return web.json_response(db.get_todos())

def delete_todos(request):
    db.

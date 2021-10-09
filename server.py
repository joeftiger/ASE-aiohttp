import logging

import aiohttp_cors as aiohttp_cors
from aiohttp import web

from db import Database

URL = "0.0"
db = Database()
db.populate_if_empty()


def get_todos(request):
    todos = db.get_todos()
    for todo in todos:
        todo["url"] = str(request.url.join(request.app.router["get_todo"].url_for(id=str(todo["id"]))))

    return web.json_response(todos, status=200)


async def post_todo(request):
    fields = await request.json()

    if "title" not in fields:
        return web.json_response({"error": "'title' is a required field"})
    if not isinstance(fields["title"], str) or not len(fields["title"]):
        return web.json_response({"error": "'title' must be a str with at least one char"})

    todo = db.post_todo(fields)
    todo["url"] = str(request.url.join(request.app.router["get_todo"].url_for(id=str(todo["id"]))))
    return web.json_response(
        todo,
        headers={'Location': todo["url"]},
        status=201,
    )


def delete_todos(request):
    db.delete_todos()
    return web.Response(status=204)


def get_todo(request):
    id = int(request.match_info["id"])

    todo = db.get_todo(id)
    if not todo:
        return web.json_response({"error": "Todo not found"}, status=404)
    todo["url"] = str(request.url.join(request.app.router["get_todo"].url_for(id=str(todo["id"]))))

    return web.json_response(todo, status=200)


def delete_todo(request):
    id = int(request.match_info["id"])

    if not db.delete_todo(id):
        return web.json_response({"error": "Todo not found"}, status=404)

    return web.Response(status=204)


async def patch_todo(request):
    id = int(request.match_info["id"])

    todo = db.patch_todo(id, await request.json())
    if not todo:
        return web.json_response({"error": "Todo not found"}, status=404)
    todo["url"] = str(request.url.join(request.app.router["get_todo"].url_for(id=str(todo["id"]))))

    return web.json_response(todo, status=200)


def get_todo_tags(request):
    id = int(request.match_info["id"])

    tags = db.get_todo_tags(id)
    for tag in tags:
        tag["url"] = str(request.url.join(request.app.router["get_tag"].url_for(id=str(tag["id"]))))

    return web.json_response(tags, status=200)


async def post_todo_tag(request):
    todo_id = int(request.match_info["id"])
    json = await request.json()
    tag_id = int(json["id"])

    db.post_todo_tag(todo_id, tag_id)

    return web.Response(status=204)


def delete_todo_tags(request):
    id = int(request.match_info["id"])

    db.delete_todo_tags(id)

    return web.Response(status=204)


async def delete_todo_tag(request):
    todo_id = int(request.match_info["id"])
    tag_id = int(request.match_info["tag_id"])

    db.delete_todo_tag(todo_id, tag_id)

    return web.Response(status=204)


def get_tags(request):
    tags = db.get_tags()
    for tag in tags:
        tag["url"] = str(request.url.join(request.app.router["get_tag"].url_for(id=str(tag["id"]))))

    return web.json_response(tags, status=200)


def delete_tags(request):
    db.delete_tags()
    return web.Response(status=204)


def get_tag(request):
    id = int(request.match_info["id"])

    tag = db.get_tag(id)
    if not tag:
        return web.json_response({"error": "Tag not found"}, status=404)
    tag["url"] = str(request.url.join(request.app.router["get_tag"].url_for(id=str(tag["id"]))))

    return web.json_response(tag, status=200)


async def post_tag(request):
    fields = await request.json()

    if "title" not in fields:
        return web.json_response({"error": "'title' is a required field"})
    if not isinstance(fields["title"], str) or not len(fields["title"]):
        return web.json_response({"error": "'title' must be a str with at least one char"})

    tag = db.post_tag(fields)
    tag["url"] = str(request.url.join(request.app.router["get_tag"].url_for(id=str(tag["id"]))))
    return web.json_response(
        tag,
        headers={'Location': tag["url"]},
        status=201,
    )


async def patch_tag(request):
    id = int(request.match_info["id"])

    tag = db.patch_tag(id, await request.json())
    if not tag:
        return web.json_response({"error": "Tag not found"}, status=404)
    tag["url"] = str(request.url.join(request.app.router["get_tag"].url_for(id=str(tag["id"]))))

    return web.json_response(tag, status=200)


def delete_tag(request):
    id = int(request.match_info["id"])

    if not db.delete_tag(id):
        return web.json_response({"error": "Tag not found"}, status=404)

    return web.Response(status=204)


def get_tag_todos(request):
    id = int(request.match_info["id"])

    todos = db.get_tag_todos(id)
    for todo in todos:
        todo["url"] = str(request.url.join(request.app.router["get_todo"].url_for(id=str(todo["id"]))))

    return web.json_response(todos, status=200)


app = web.Application()

# Configure default CORS settings.
cors = aiohttp_cors.setup(app, defaults={
    "*": aiohttp_cors.ResourceOptions(
        allow_credentials=True,
        expose_headers="*",
        allow_headers="*",
        allow_methods="*",
    )
})

cors.add(app.router.add_get('/todos/', handler=get_todos, name='get_todos'))
cors.add(app.router.add_delete('/todos/', handler=delete_todos, name='delete_todos'))
cors.add(app.router.add_post('/todos/', handler=post_todo, name='post_todo'))
cors.add(app.router.add_get('/todos/{id:\d+}', handler=get_todo, name='get_todo'))
cors.add(app.router.add_patch('/todos/{id:\d+}', handler=patch_todo, name='patch_todo'))
cors.add(app.router.add_delete('/todos/{id:\d+}', handler=delete_todo, name='delete_todo'))
cors.add(app.router.add_get('/todos/{id:\d+}/tags/', handler=get_todo_tags, name='get_todo_tags'))
cors.add(app.router.add_post('/todos/{id:\d+}/tags/', handler=post_todo_tag, name='post_todo_tag'))
cors.add(app.router.add_delete('/todos/{id:\d+}/tags/', handler=delete_todo_tags, name='delete_todo_tags'))
cors.add(app.router.add_delete('/todos/{id:\d+}/tags/{tag_id:\d+}', handler=delete_todo_tag, name='delete_todo_tag'))

cors.add(app.router.add_get('/tags/', handler=get_tags, name='get_tags'))
cors.add(app.router.add_delete('/tags/', handler=delete_tags, name='delete_tags'))
cors.add(app.router.add_post('/tags/', handler=post_tag, name='post_tag'))
cors.add(app.router.add_get('/tags/{id:\d+}', handler=get_tag, name='get_tag'))
cors.add(app.router.add_patch('/tags/{id:\d+}', handler=patch_tag, name='patch_tag'))
cors.add(app.router.add_delete('/tags/{id:\d+}', handler=delete_tag, name='delete_tag'))
cors.add(app.router.add_delete('/tags/{id:\d+}/todos/', handler=get_tag_todos, name='get_tag_todos'))

logging.basicConfig(level=logging.DEBUG)
web.run_app(app, port=8080)

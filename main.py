import json
import os
import random
import string

import aiofiles

import motor.motor_asyncio
from fastapi import FastAPI, Request, Form
from typing import Annotated
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles


app = FastAPI()

# app.mount("/static", StaticFiles(directory="static"), name="static") # maybe not need


templates = Jinja2Templates(directory="templates")

# for dz 25
client = motor.motor_asyncio.AsyncIOMotorClient(
         f'mongodb://{os.getenv("MONGO_USERNAME", "root")}:'
         f'{os.getenv("MONGO_PASSWORD", "example")}@'
         f'{os.getenv("MONGO_HOST", "localhost")}:'
         f'{os.getenv("MONGO_PORT", 27017)}/')


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse(request=request, name='index.html')


# @app.post("/") # for dz 24
# async def get_url(url: Annotated[str, Form()]):
#     short_url = ''.join(random.choice(string.ascii_uppercase+string.ascii_lowercase+string.digits)
#                     for _ in range(6))
#
#     async with aiofiles.open('filename', mode='r') as f:
#         contents = await f.read()
#
#     db_dict = json.loads(contents)  # з текстового словника робимо json
#     db_dict[short_url] = url
#     # db_dict.update({'short_url': short_url}) ключ-коротка, значення=довга урла
#
#     async with aiofiles.open('filename', mode='w') as f:
#         await f.write(json.dumps(db_dict))
#
#
#    #url_dict = {short_url: url}  # ключ-коротка, значення=довга урла
#     return {"result": short_url}

@app.post("/")  # for the 25 dz
# довга урла приходить в змінну url з форми
async def get_url(url: Annotated[str, Form()]):
    short_url = ''.join(random.choice(string.ascii_uppercase+string.ascii_lowercase+string.digits)
                    for _ in range(6))  # тут генеруємо коротку урлу
    new_doc = {"short_url": short_url, "long_url": url}
    await client["url_shortener"]["urls"].insert_one(new_doc)

    return {"result": short_url}

# @app.get("/{short_url}") # for dz 24
# async def say_hello(short_url: str):
#     async with aiofiles.open('filename', mode='r') as f:
#         contents = await f.read()
#     db_dict = json.loads(contents)
#     url = db_dict[short_url]
#     return RedirectResponse(url)


# беремо коротку урлу і робимо переадресацію на довгу урлу
@app.get("/{short_url}")  # for the 25 dz
async def say_hello(short_url: str):
    # вибираємо базу даних await client.url_shortener.urls = await client["url_shortener"]["urls"]
    # .urls or ["urls"] - це вибираємо колекцію
    url_document = await client["url_shortener"]["urls"].find_one({"short_url": short_url})  # await client.url_shortener.urls
    res_url = url_document["long_url"]

    hits_counter = url_document.get("hits_counter", 0)
    url_document["hits_counter"] = hits_counter + 1
    # url_document["hits_counter"] = url_document.get("hits_counter", 0) + 1 замість попередніх 2х строк
    await client["url_shortener"]["urls"].replace_one(
        {"_id": url_document["_id"]}, url_document)

    return RedirectResponse(res_url)




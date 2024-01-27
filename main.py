#written while reading through their docs in Jan24, listening to YT vids, and three beers deep at the time of this comment
from fastapi import FastAPI
from enum import Enum

app = FastAPI()

#smoke and mirrors for the sake of progress courtesy of FastAPI's technical writing team
#----not relevant, but when did 'foo' 'bar' become the default placeholder text in documentation as opposed to something that takes less time to type like 'asdf' or 'test'? idc if it's related/equivalent to 'FUBAR', my theory is that some douche who's already retired started doing this to dissuade or otherwise micro-shame his direct reports or stakeholders from reading his documentation so they wouldn't notice he wasn't maintaining it
fake_items_db = [{"item_name": "A"}, {"item_name": "Fukkin Uhhhhh"}, {"item_name": "Item"}]

#declaring a pydantic enum for use as a path var
#it sounds pedantic *rimshot*, but doing this is going to be almost as short as references to your own boilerplate, except this also has the benefit of handling invalid url params without requiring you to do anything else (I might actually prefer to be anal retentive about that because maybe if someone sends my server an invalid url param, I might want to block their IP or user agent on the spot. Your mileage may vary)
class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"

#minimum req for it work
@app.get('/')
async def root():
    return {'fuck':'\'er right in the pussy'}

#for style
@app.get('/healthcheck')
async def healthcheck():
    return {'test server':'is up'}

#also a path var
@app.get('/items/{item_id}')
async def read_item(item_id:int):
    return {'item_id':item_id}

#a path *trademarked, do not copy
@app.get("/users/me")
async def read_user_me():
    return {"user_id": "the current user"}

#path var
@app.get("/users/{user_id}")
async def read_user(user_id: str):
    return {"user_id": user_id}

#enumurated path
@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name is ModelName.alexnet:
        return {"model_name": model_name, "message": "The AI bubble's eventual collapse"}

    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "and its accompanying CEO tears"}

    return {"model_name": model_name, "message": "will be a neverending source of schadenfreude :)"}

#so this is the first time the FastAPI docs doesn't provide you with a local url to your server to test an endpoint, and I took that as a low key challenge to finish the method
#----not relevant, but this ran in 6ms locally ::sweating::, which is already making flask look like the wordpress of writing your own websites
@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
    text_contents = 'something is fucked'
    with open(file_path,'r') as thing:
        text_contents = ''
        for l in thing.readlines(-1):
            text_contents += f'{l} '
        thing.close()
    return {"file_path": file_path,'text_contents':text_contents}

#this example introduces both URL params and their validation
#changed the path to items2 because it conflicts with previous documentation -_-
#----not relevant, but cool usage of built-in list index functionality with this example
@app.get("/items2/")
async def read_item(skip: int = 0, limit: int = 10):
    return fake_items_db[skip : skip + limit]

#
#changed path to item3 because the docs are increasingly lazy with nomenclature
#---- ok, now this is getting out hand, surely there's another noun they can come up with instead of beating the dead 'items' horse

@app.get("/items3/{item_id}")
async def read_item(item_id: str, q: str | None = None):
    if q:
        return {"item_id": item_id, "q": q}
    return {"item_id": item_id}
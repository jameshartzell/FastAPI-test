#written while reading through their docs on Jan24, listening to YT vids, and three beers deep at the time of this comment
from typing import Annotated, Any, List, Union
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi import Body, Cookie, FastAPI, Header, Path, Response, BackgroundTasks
from enum import Enum
from pydantic import BaseModel, EmailStr, Field, HttpUrl
import time,os

#install dependencies w/ 'pip install "fastapi[all]"
#start the server w/ 'uvicorn main:app --reload'
app = FastAPI()

#smoke and mirrors for the sake of progress courtesy of FastAPI's technical writing team
#----not relevant, but when did 'foo' 'bar' become the default placeholder text in documentation as opposed to something that takes less time to type like 'asdf' or 'test'? idc if it's related/equivalent to 'FUBAR', my theory is that some douche who's already retired started doing this to dissuade or otherwise micro-shame his direct reports or stakeholders from reading his documentation so they wouldn't notice he wasn't maintaining it
fake_items_db = [{"item_name": "A"}, {"item_name": "Fukkin Uhhhhh"}, {"item_name": "Item"}]

#more smoke and mirrors for later examples
more_fake_items = {
    "foo": {"name": "Foo", "price": 50.2},
    "bar": {"name": "Bar", "description": "The Bar fighters", "price": 62, "tax": 20.2},
    "baz": {
        "name": "Baz",
        "description": "There goes my baz",
        "price": 50.2,
        "tax": 10.5,
    },
}

#declaring a pydantic enum for use as a path var
#it sounds pedantic *rimshot*, but doing this is going to be almost as short as references to your own boilerplate, except this also has the benefit of handling invalid url params without requiring you to do anything else (I might actually prefer to be anal retentive about that because maybe if someone sends my server an invalid url param, I might want to block their IP or user agent on the spot. Your mileage may vary)
class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"

#all the pyd models
class Image(BaseModel):
    url: HttpUrl
    name: str

#declaring a pydantic model for the expected body of calls to a POST method    
class Item(BaseModel):
    name: str
    description: str | None = Field(
        default=None, title="The description of the item", max_length=300
    )
    price: float = Field(gt=0, description="The price must be greater than zero")
    tax: Union[float, None] = None
#for just a regular array of strings
    #tags: list[str] = []
#for a unique array of strings
    tags: set[str] = set()
#another pyd model as a field
    #image: Image | None = None
#an array of other pyd models
    images: list[Image] | None = None
#providing sample data for the auto-generated docs
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Foo",
                    "description": "A very nice Item",
                    "price": 35.4,
                    "tax": 3.2,
                    "tags":['some','fuggin','tags'],
                    "images":[]
                }
            ]
        }
    }

#even more models    
class User(BaseModel):
    username: str
    full_name: str | None = None
    
#even more nesting
class Offer(BaseModel):
    name: str
    description: str | None = None
    price: float
    items: list[Item]
    
class UserIn(BaseModel):
    username: str
    password: str
    email: EmailStr
    full_name: str | None = None
    
class UserOut(BaseModel):
    username: str
    email: EmailStr
    full_name: str | None = None

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

#everything is still an item and bools exist weow
@app.get("/items4/{item_id}")
async def read_item(item_id: str, q: str | None = None, short: bool = False):
    item = {"item_id": item_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item

#multiple path parameters
@app.get("/users/{user_id}/items/{item_id}")
async def read_user_item(
    user_id: int, item_id: str, q: str | None = None, short: bool = False
):
    item = {"item_id": item_id, "owner_id": user_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item

#ITEMS
#query params can be made to be required by leaving out default values
@app.get("/items5/{item_id}")
async def read_user_item(item_id: str, needy: str):
    item = {"item_id": item_id, "needy": needy}
    return item

#I would certainly hope that whether a query params can be required or not is customizable
#(it is)
@app.get("/items6/{item_id}")
async def read_user_item(
    item_id: str, needy: str, skip: int = 0, limit: int | None = None
):
    item = {"item_id": item_id, "needy": needy, "skip": skip, "limit": limit}
    return item

#finally, a new section
#and finally, POST
@app.post("/items7/")
async def create_item(item: Item):
    return item

#accepting both url params and a payload
@app.put("/items8/{item_id}")
async def update_item(item_id: int, item: Item):
    return {"item_id": item_id, **item.dict()}

#url params, a payload, and query params all in the same place
@app.put("/items9/{item_id}")
async def update_item(item_id: int, item: Item, q: str | None = None):
    result = {"item_id": item_id, **item.dict()}
    if q:
        result.update({"q": q})
    return result

#skipping 'Query Parameters and String Validations' and 'Path Parameters and Numeric Validations' sections

#
@app.put("/items10/{item_id}")
async def update_item(
    item_id: Annotated[int, Path(title="The ID of the item to get", ge=0, le=1000)],
    q: str | None = None,
    item: Item | None = None,
):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    if item:
        results.update({"item": item})
    return results

#multiple body parameters (pydantic models in the payload)
#this is how fastapi handles nested dictionaries in payloads btw
@app.put("/items11/{item_id}")
async def update_item(item_id: int, item: Item, user: User):
    results = {"item_id": item_id, "item": item, "user": user}
    return results

#an individual/top level key in the payload
@app.put("/items12/{item_id}")
async def update_item(
    item_id: int, item: Item, user: User, importance: Annotated[int, Body()]
):
    results = {"item_id": item_id, "item": item, "user": user, "importance": importance}
    return results

#skipping 'Multiple body params and query' because they've already covered it

#'embed' argument to Body()
# indents the json param in the expected payload
@app.put("/items13/{item_id}")
async def update_item(item_id: int, item: Annotated[Item, Body(embed=True)]):
    results = {"item_id": item_id, "item": item}
    return results

#an endpoint with even more nesting in its expected payload
@app.post("/offers/")
async def create_offer(offer: Offer):
    return offer

#a body that's just an array of something
@app.post("/images/multiple/")
async def create_multiple_images(images: list[Image]):
    return images

#a body that's an arbitrary dict
@app.post("/index-weights/")
async def create_index_weights(weights: dict[int, float]):
    return weights

#skippping most of the providing example data section as it's pretty straightforward and also not necessary for in-house only tools

#skipping 'Extra Data Types', but it's a good idea to take a look at it
#----enough of the items shit holy fuck who wrote this documentation
@app.get("/items14/")
async def read_items(ads_id: Annotated[str | None, Cookie()] = None):
    return {"ads_id": ads_id}

#HEADERS (a little annoying that this requires an import but whatev)
#----and even more items
@app.get("/items15/")
async def read_items(user_agent: Annotated[str | None, Header()] = None):
    return {"User-Agent": user_agent}

#Headers() 'convert_underscores' arg for disabling conversion from _ to - and so forth
@app.get("/items16/")
async def read_items(
    strange_header: Annotated[str | None, Header(convert_underscores=False)] = None
):
    return {"strange_header": strange_header}

#a list header
@app.get("/items17/")
async def read_items(x_token: Annotated[list[str] | None, Header()] = None):
    return {"X-Token values": x_token}

#setting return types to validate responses w/FastAPI
@app.post("/items18/")
async def create_item(item: Item) -> Item:
    return item


@app.get("/items19/")
async def read_items() -> list[Item]:
    return [
        Item(name="Portal Gun", price=42.0),
        Item(name="Plumbus", price=32.0),
    ]
    
#setting return types to validate responses w/pyd models instead
#the 'response_model' arg to the endpoint's decorator takes priority over specifying a return type
@app.post("/items20/", response_model=Item)
async def create_item(item: Item) -> Any:
    return item


@app.get("/items21/", response_model=list[Item])
async def read_items() -> Any:
    return [
        {"name": "Portal Gun", "price": 42.0},
        {"name": "Plumbus", "price": 32.0},
    ]

#----yes, the type defined for the body can be the same as the return type    
# Don't do this in production!
#----duh
@app.post("/user/")
async def create_user(user: UserIn) -> UserIn:
    return user
#----and obv don't handle PWs in plain text

#the 'user' var here from the body can be validated/filtered as a different pyd model on the way out
@app.post("/user2/", response_model=UserOut)
async def create_user(user: UserIn) -> Any:
    return user

#redirects and raw json responses
@app.get("/portal")
async def get_portal(teleport: bool = False) -> Response:
    if teleport:
        return RedirectResponse(url="https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    return JSONResponse(content={"message": "Try teleport=true"})

#these built-in response type classes can be used as return types as well
@app.get("/teleport")
async def get_teleport() -> RedirectResponse:
    return RedirectResponse(url="https://www.youtube.com/watch?v=dQw4w9WgXcQ")

#the fastapi response model can be disabled
@app.get("/portal2", response_model=None)
async def get_portal(teleport: bool = False) -> Response | dict:
    if teleport:
        return RedirectResponse(url="https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    return {"message": "Here's your interdimensional portal."}

#skipping response_model_exclude_unset argment for endpoint decorators (it exists)

#you can include only specific fields of a pyd model or exclude specific fields of a pyd model
#with the 'response_model_include' and 'response_model_exclude' args (they take both lists and sets)
@app.get(
    "/items/{item_id}/name",
    response_model=Item,
    response_model_include={"name", "description"},
)
async def read_item_name(item_id: str):
    return more_fake_items[item_id]


@app.get("/items/{item_id}/public", response_model=Item, response_model_exclude={"tax"})
async def read_item_public_data(item_id: str):
    return more_fake_items[item_id]

#stopping at Extra Models at https://fastapi.tiangolo.com/tutorial/extra-models/

#WE INTERRUPT THIS PROGRAM TO BRING YOU AN EXPLORATION OF BACKGROUND TASKS
#(THE REASON I'M EVALUATING FASTAPI IN THE FIRST PLACE)
def log_request_in_db():
    print('bgt started')
    time.sleep(3)
    print('bgt finished')
    
@app.get('/bgt')
async def bgt(background_tasks: BackgroundTasks):
    print('endpoint called')
    background_tasks.add_task(log_request_in_db)
    print('response sent')
    return {'result':'pog'}

if __name__ == '__main__':
    try:
        app.run(debug=True, port=os.getenv("PORT", default=5000))
    except Exception as e:
        print(e)
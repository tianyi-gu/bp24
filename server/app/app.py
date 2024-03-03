from typing import Optional
from fastapi import Depends, FastAPI, File, Form, HTTPException, Request, UploadFile
import urllib.parse
import uvicorn
from mangum import Mangum
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware


# Clarifai info ---
from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
from clarifai_grpc.grpc.api import resources_pb2, service_pb2, service_pb2_grpc
from clarifai_grpc.grpc.api.status import status_code_pb2

PAT = "813aa2ce8ece4b94864d9cb01393ae88"
USER_ID = "clarifai"
APP_ID = "main"
MODEL_ID = "apparel-classification-v2"

CLAI_CLIENT = service_pb2_grpc.V2Stub(ClarifaiChannel.get_grpc_channel())
METADATA = (("authorization", "Key " + PAT),)
USERDATA = resources_pb2.UserAppIDSet(user_id=USER_ID, app_id=APP_ID)


# Amazon API (APIFY) info ---
from apify_client import ApifyClient

# TOKEN = "apify_api_SO4LvWFkmdsaSiI7io6hfEF6KDJHAN0gsfiv"
TOKEN = "apify_api_zIchgvhuSubjLQS0VCqEYAO0j7vMpf14SoHr"
ACTOR = "BG3WDrGdteHgZgbPK"
AMZN_CLIENT = ApifyClient(TOKEN)
AMZN_URL = "https://www.amazon.com/s?k={}"
AMZN_REQ = {
    # "maxItemsPerStartUrl": 5,
    "useCaptchaSolver": False,
    "scrapeProductVariantPrices": False,
    "proxyConfiguration": {
        "useApifyProxy": True,
        "apifyProxyGroups": ["RESIDENTIAL"],
    },
}

# Output config


def amzn_input(concepts: list[str], n_products: int) -> dict:
    urls = []
    for s in concepts:
        escaped = urllib.parse.quote_plus(s)
        urls.append({"url": AMZN_URL.format(escaped)})
    req = AMZN_REQ.copy()
    req["categoryOrProductUrls"] = urls
    req["maxItemsPerStartUrl"] = n_products
    return req


# Server stuff -----

app = FastAPI()
handler = Mangum(app)


@app.get("/ping")
async def ping():
    return {"message": "pong"}
    # return JSONResponse(content={"message": "pong"})


@app.get("/name")
async def greet(name: str):
    return {"message": f"Hello, {name}!"}


# {
#     "detail": [
#         {
#             "type": "missing",
#             "loc": ["query", "n_concepts"],
#             "msg": "Field required",
#             "input": null,
#             "url": "https://errors.pydantic.dev/2.6/v/missing",
#         },
#         {
#             "type": "missing",
#             "loc": ["query", "n_products"],
#             "msg": "Field required",
#             "input": null,
#             "url": "https://errors.pydantic.dev/2.6/v/missing",
#         },
#         {
#             "type": "missing",
#             "loc": ["body", "file"],
#             "msg": "Field required",
#             "input": null,
#             "url": "https://errors.pydantic.dev/2.6/v/missing",
#         },
#     ]
# }


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/image")
async def upload(
    req: Request,
):
    form = await req.form()
    n_concepts = int(form["n_concepts"])  # type: ignore
    n_products = int(form["n_products"])  # type: ignore
    file = form["image"]
    print(f"{n_concepts}, {n_products}, {file.filename}")
    # return {"hi": f"concepts: {n_concepts}, products: {n_products}"}
    if isinstance(file, str) or file.content_type != "image/png":
        return {
            "success": False,
            "error": f"Invalid image",
            "reason": "Image upload must be valid",
        }
    if n_concepts <= 0:
        return {
            "success": False,
            "error": f"Invalid number: {n_concepts}",
            "reason": "n_concepts must be greater than 0",
        }
    if n_products <= 0:
        return {
            "success": False,
            "error": f"Invalid number: {n_products}",
            "reason": "n_products must be greater than 0",
        }
    try:
        # Get file from request
        bytes = await file.read()
        # Forward to Clarifai
        resp = CLAI_CLIENT.PostModelOutputs(
            service_pb2.PostModelOutputsRequest(
                user_app_id=USERDATA,  # The userDataObject is created in the overview and is required when using a PAT
                model_id=MODEL_ID,
                inputs=[
                    resources_pb2.Input(
                        data=resources_pb2.Data(image=resources_pb2.Image(base64=bytes))
                    )
                ],
            ),
            metadata=METADATA,
        )
        if resp.status.code != status_code_pb2.SUCCESS:
            return {
                "sucess": False,
                "error": "There was an error with the Clarifai API",
                "reason": resp.status.description,
            }
        # print("got clarifai")

        # Forward to Amazon products API
        # run_input = amzn_input([c.name for c in resp.outputs[0].data.concepts][:number])
        run_input = amzn_input(
            ["".join([c.name for c in resp.outputs[0].data.concepts][:n_concepts])],
            n_products,
        )
        # print("got run input")
        # print(run_input)
        run = AMZN_CLIENT.actor(ACTOR).call(run_input=run_input)
        # print("got run")
        if run is None:
            return {
                "sucess": False,
                "error": "There was an error with the Amazon API",
                "reason": "`run` was None",
            }
        # print("amazon input")
        items = AMZN_CLIENT.dataset(run["defaultDatasetId"]).list_items()
        return {
            "sucess": True,
            "clarifai": [c.name for c in resp.outputs[0].data.concepts][:n_concepts],
            "amazon": items,
        }
    except Exception as e:
        return {"message": f"There was an error processing the image", "error": str(e)}
    finally:
        await file.close()


if __name__ == "__main__":
    uvicorn.run(app=app, host="0.0.0.0", port=8080)

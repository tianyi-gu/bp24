from fastapi import FastAPI, File, UploadFile
import urllib.parse

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

TOKEN = "apify_api_zIchgvhuSubjLQS0VCqEYAO0j7vMpf14SoHr"
ACTOR = "BG3WDrGdteHgZgbPK"
AMZN_CLIENT = ApifyClient(TOKEN)
AMZN_URL = "https://www.amazon.com/s?k={}"
AMZN_REQ = {
    "body": {
        "maxItemsPerStartUrl": 5,
        "useCaptchaSolver": False,
        "scrapeProductVariantPrices": False,
        "proxyConfiguration": {
            "useApifyProxy": True,
            "apifyProxyGroups": ["RESIDENTIAL"],
        },
    },
}


def amzn_input(concepts: list[str]) -> dict:
    urls = []
    for s in concepts:
        escaped = urllib.parse.quote_plus(s)
        urls.append({"url": AMZN_URL.format(escaped)})
    req = AMZN_REQ.copy()
    req["body"]["categoryOrProductUrls"] = urls
    return req


# Server stuff -----

app = FastAPI()


@app.post("/image")
async def upload(file: UploadFile = File(...)):
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
                "message": "There was an error with the Clarifai API",
                "error": resp.status.description,
            }

        # Forward to Amazon products API
        print(resp.outputs[0])
        print([(c.name, c.value) for c in resp.outputs[0].data.concepts])
        run_input = amzn_input([c.name for c in resp.outputs[0].data.concepts][:5])
        print(run_input)
        run = AMZN_CLIENT.actor(ACTOR).call(run_input=run_input)
        if run is None:
            return {
                "message": "There was an error with the Amazon API",
                "error": "`run` was None",
            }
        items = AMZN_CLIENT.dataset(run["defaultDatasetId"]).list_items()
        return {
            "message": "Success",
            "clarifai": [c.name for c in resp.outputs[0].data.concepts][:5],
            "amazon": items,
        }
    except Exception as e:
        return {"message": f"There was an error processing the image", "error": str(e)}
    finally:
        await file.close()

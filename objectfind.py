from fastapi import FastAPI, File, UploadFile
from PIL import Image
import json

# Clarifai info ---
PAT = "813aa2ce8ece4b94864d9cb01393ae88"
USER_ID = "clarifai"
APP_ID = "main"
MODEL_ID = "apparel-classification-v2"

from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
from clarifai_grpc.grpc.api import resources_pb2, service_pb2, service_pb2_grpc
from clarifai_grpc.grpc.api.status import status_code_pb2

channel = ClarifaiChannel.get_grpc_channel()
stub = service_pb2_grpc.V2Stub(channel)
METADATA = (("authorization", "Key " + PAT),)
USERDATA = resources_pb2.UserAppIDSet(user_id=USER_ID, app_id=APP_ID)


app = FastAPI()


@app.post("/images/test_image")
async def upload(file: UploadFile = File(...)):
    try:
        bytes = await file.read()
    except Exception as e:
        return {"message": f"There was an error uploading the image", "error": str(e)}
    finally:
        await file.close()

    try:
        resp = stub.PostModelOutputs(
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
    except Exception as e:
        return {"message": "There was an error with the Clarifai API", "error": str(e)}

    if resp.status.code != status_code_pb2.SUCCESS:
        return {
            "message": "There was an error with the Clarifai API",
            "error": resp.status.description,
        }

    img_resp = resp.outputs[0]
    out = [(concept.name, concept.value) for concept in img_resp.data.concepts]

    return {"status": "ok", "output": json.dumps(out)}
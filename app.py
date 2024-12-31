from dotenv import load_dotenv
import json
import os
from schemas import Payload
from helpers import crawler, crawler_sync
from fastapi import FastAPI
import uvicorn

load_dotenv()


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'secret_key.json'

app = FastAPI(title='NIN Validation API', 
              description='using Artificial Intelligence to validate National Identity Number.', 
              version='1.0.0'
              )


@app.get("/", tags=["health check"])
async def root():
    return {
        "message": "NIN Validation API!"
        }

@app.post("/get_validation/")
async def get_validation(payload: Payload):
    print(payload)
    output = await crawler(payload)
    return output

@app.post("/get_validation_sync/")
def get_validation_sync(payload: Payload):
    print(payload)
    output = crawler_sync(payload)
    return output

if __name__ == "__main__":
    uvicorn.run("app:app", host = "0.0.0.0", port = 300, log_level = "info", reload = True)

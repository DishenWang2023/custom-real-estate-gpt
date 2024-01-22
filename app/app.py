import os
from fastapi import FastAPI, HTTPException
from dataherald import AsyncDataherald
from dataherald.types import SqlGenerationResponse
from mangum import Mangum
import uvicorn
API_KEY = os.environ.get("DATAHERALD_API_KEY")
database_connection_id = os.environ.get("DATABASE_CONNECTION_ID")
finetuning_id = os.environ.get("FINETUNING_ID")

app = FastAPI()
handler = Mangum(app)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/questions", status_code=201)
async def answer_question(text: str):
    # use dataherald client
    dh_client = AsyncDataherald(api_key=API_KEY)
    try:
        # get generated sql query
        response: SqlGenerationResponse = await dh_client.sql_generations.create(
            prompt={"text": text, "db_connection_id": database_connection_id},
            finetuning_id=finetuning_id,
        )
        # execute query
        sql_results = await dh_client.sql_generations.execute(response.id, max_rows=10)

        return sql_results
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal Server Error") from e

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
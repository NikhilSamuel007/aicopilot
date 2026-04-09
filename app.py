import uvicorn
import uuid
import os
import shutil
from fastapi import FastAPI, Request, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.websockets import WebSocket, WebSocketDisconnect

from config import config
from src.logging.logger import logger
from src.middleware.authorize import Authorize
from src.agent import chat, refresh_agent
from src.ingestion import ingest_document
from src.database import insert_document_record, delete_document_record

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

authorize = Authorize()

@app.get("/health")
async def health():
    return {"message": "API is up and running"}

@app.post("/query")
async def query(request: Request):
    try:
        data = await request.json()
        query_text = data.get("query")
        session_id = data.get("session_id") or str(uuid.uuid4())
        
        if not query_text:
            return JSONResponse({"error": "Query is required"}, status_code=400)
            
        logger.info(f"Query received for session {session_id}: {query_text}")
        
        answer = await chat(query_text, session_id=session_id)
        
        return {"answer": answer, "session_id": session_id}
    except Exception as e:
        logger.error(f"Error in query: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)

def index_document_to_faiss(file_path: str, file_id: str):
    success = ingest_document(file_path)
    if success:
        refresh_agent()
    return success

@app.post('/upload-doc')
async def upload_and_index_doc(file: UploadFile = File(...)):
    allowed_extensions = ['pdf', 'docx']
    file_extension = os.path.splitext(file.filename)[1][1:].lower()

    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type. Allowed types are: {', '.join(allowed_extensions)}"
        )

    temp_file_path = f"temp_{file.filename}"
    
    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file_id = insert_document_record(file.filename)
        if not file_id:
            raise HTTPException(status_code=500, detail="Failed to create document record in Supabase.")

        success = index_document_to_faiss(temp_file_path, file_id)

        if success:
            return {
                "message": f"File {file.filename} has been successfully uploaded and indexed.", 
                "file_id": file_id
            }
        else:
            delete_document_record(file_id)
            raise HTTPException(status_code=500, detail=f"Failed to index {file.filename}.")
            
    except Exception as e:
        logger.error(f"Upload error: {e}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

@app.websocket("/ws")
async def websocket(websocket: WebSocket):
    await websocket.accept()
    session_id = str(uuid.uuid4())
    logger.info(f"Client connected on websocket session {session_id}")
    
    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f"WS received: {data}")
            
            answer = await chat(data, session_id=session_id)
            await websocket.send_text(answer)
    except WebSocketDisconnect:
        logger.info(f"Client disconnected from session {session_id}")
    except Exception as e:
        logger.error(f"WS Error: {e}")
        await websocket.close()

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
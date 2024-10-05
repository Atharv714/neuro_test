from fastapi import FastAPI, File, UploadFile
import shutil

app = FastAPI()

# Define an endpoint to receive the audio file
@app.post("/upload-audio")
async def upload_audio(file: UploadFile = File(...)):
    # Save the uploaded audio file
    file_location = f"uploads/{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return {"message": "File uploaded successfully", "filename": file.filename}

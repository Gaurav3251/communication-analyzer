from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from analyzer import TranscriptAnalyzer
from typing import Optional

app = FastAPI(title="Communication Skills Analyzer API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TranscriptInput(BaseModel):
    transcript: str
    duration_seconds: Optional[int] = None

class CriterionResult(BaseModel):
    criterion: str
    metric: str
    score: float
    max_score: float
    weight: float
    weighted_score: float
    feedback: str
    details: dict

class AnalysisResult(BaseModel):
    overall_score: float
    word_count: int
    sentence_count: int
    criteria_scores: list[CriterionResult]
    summary: str

# Initialize analyzer (loads models once at startup)
print("Loading analyzer models...")
analyzer = TranscriptAnalyzer()
print("Server ready!")

@app.get("/")
def root():
    return {
        "message": "Communication Skills Analyzer API",
        "status": "running",
        "endpoints": {
            "POST /analyze": "Analyze transcript from JSON",
            "POST /analyze/file": "Analyze transcript from .txt file"
        }
    }

@app.post("/analyze", response_model=AnalysisResult)
def analyze_transcript(input_data: TranscriptInput):
    """Analyze transcript from JSON input"""
    if not input_data.transcript or len(input_data.transcript.strip()) < 10:
        raise HTTPException(status_code=400, detail="Transcript too short (minimum 10 characters)")
    
    try:
        result = analyzer.analyze(
            input_data.transcript, 
            input_data.duration_seconds
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")

@app.post("/analyze/file", response_model=AnalysisResult)
async def analyze_file(
    file: UploadFile = File(...),
    duration_seconds: Optional[int] = Form(None)
):
    """Analyze transcript from uploaded .txt file"""
    
    # Validate file type
    if not file.filename.endswith('.txt'):
        raise HTTPException(status_code=400, detail="Only .txt files are supported")
    
    try:
        # Read file content
        content = await file.read()
        transcript = content.decode('utf-8')
        
        if len(transcript.strip()) < 10:
            raise HTTPException(status_code=400, detail="Transcript too short (minimum 10 characters)")
        
        # Analyze
        result = analyzer.analyze(transcript, duration_seconds)
        return result
        
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File encoding error. Please use UTF-8 encoded .txt file")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")

@app.get("/health")
def health_check():
    return {"status": "healthy", "models_loaded": True}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
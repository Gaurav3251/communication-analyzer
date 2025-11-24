# Communication Skills Analyzer

AI-powered tool to analyze and score student self-introduction transcripts using NLP and semantic similarity.

## 📊 Scoring System

The tool evaluates transcripts across 5 criteria with weighted scoring (0-100):

| Criterion | Weight | Method |
|-----------|--------|--------|
| **Content & Structure** | 40% | Rule-based + Semantic similarity (sentence-transformers) |
| - Salutation Level | 5% | Keyword matching |
| - Keyword Presence | 30% | Semantic + rule-based detection |
| - Flow/Structure | 5% | Position analysis |
| **Speech Rate** | 10% | Words per minute calculation |
| **Language & Grammar** | 20% | LanguageTool + pattern matching |
| - Grammar Score | 10% | Error detection |
| - Vocabulary (TTR) | 10% | Type-Token Ratio |
| **Clarity** | 15% | Filler word detection |
| **Engagement** | 15% | VADER sentiment analysis |

### Scoring Formula Details

**1. Content & Structure (40 points)**
- **Salutation (5pts)**: Excellent(5) / Good(4) / Normal(2) / None(0)
- **Keywords (30pts)**: Must-have topics (20pts max) + Good-to-have (10pts max)
  - Essential: name, age, school, family, hobbies (4pts each)
  - Bonus: goals, achievements, unique facts (2pts each)
  - Uses semantic similarity to detect implicit mentions
- **Flow (5pts)**: Greeting(2) + Name early(2) + Closing(1)

**2. Speech Rate (10 points)**
- Ideal (111-140 WPM): 10pts
- Fast/Slow: 6pts
- Too fast/slow: 2pts

**3. Language & Grammar (20 points)**
- **Grammar (10pts)**: Based on error rate per 100 words
  - <= 1 error: 10pts | <= 2: 8pts | <= 4: 6pts | <= 7: 4pts | > 7: 2pts
  - Uses LanguageTool for detailed grammar checking
- **Vocabulary (10pts)**: TTR = unique words / total words
  - >= 0.9: 10pts | >= 0.7: 8pts | >= 0.5: 6pts | >= 0.3: 4pts

**4. Clarity (15 points)**
- Filler word rate = (filler count / total words) × 100
- <= 3 %: 15pts | <= 6 %: 12pts | <= 9 %: 9pts | <= 12 %: 6pts | > 12 %: 3pts

**5. Engagement (15 points)**
- VADER sentiment analysis (positivity score)
- >= 0.9: 15pts | >= 0.7: 12pts | >= 0.5: 9pts | >= 0.3: 6pts

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI 
- **NLP Libraries**:
  - NLTK  (tokenization, sentiment)
  - sentence-transformers  (semantic similarity)
  - language-tool-python (grammar checking)
- **Python**: 

### Frontend
- **Framework**: React 18 + Vite 5
- **HTTP Client**: Axios
- **Styling**: Custom CSS 

## ✨ Features

1. **Semantic Keyword Detection**: Detects topics even when not explicitly mentioned
2. **Advanced Grammar Checking**: LanguageTool for detailed error detection
3. **Dual Input Methods**: Paste text OR upload .txt file
4. **Real-time Analysis**: Works with any transcript text
5. **Detailed Feedback**: Per-criterion scores with explanations
6. **JSON Output**: Structured data for programmatic use

## 📁 Project Structure

```
communication-analyzer/
├── backend/
│   ├── main.py              # FastAPI app with file upload
│   ├── analyzer.py          # Core scoring logic with NLP
│   ├── rubric.py            # Rubric definitions
│   └── requirements.txt     
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # React UI 
│   │   ├── App.css          
│   │   └── main.jsx         # Entry point
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── README.md
└── .gitignore
```

## 🚀 Local Setup

### Prerequisites
```bash
Python 3.9+
Node.js 18+
Git
Java 11+ (for LanguageTool)
```

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv myenv
source myenv/bin/activate  # Windows: myenv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('vader_lexicon'); nltk.download('punkt_tab')"

# Run server
uvicorn main:app --reload --port 8000
```

**Note**: First run downloads:
- sentence-transformers model (~90MB) - 1-2 minutes
- LanguageTool resources (~200MB) - 2-3 minutes

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Visit: http://localhost:5173

## 📡 API Endpoints

### POST /analyze
Analyze transcript from JSON input

**Request:**
```json
{
  "transcript": "Hello everyone, myself Muskan...",
  "duration_seconds": 52
}
```

**Response:**
```json
{
  "overall_score": 86.0,
  "word_count": 131,
  "sentence_count": 11,
  "criteria_scores": [
    {
      "criterion": "Content & Structure",
      "metric": "Salutation Level",
      "score": 4,
      "max_score": 5,
      "weight": 5,
      "weighted_score": 4,
      "feedback": "Salutation type: Good",
      "details": {"type_found": "Good"}
    }
    // more criterion present
  ],
  "summary": "Excellent introduction! Clear structure..."
}
```

### POST /analyze/file
Upload .txt file for analysis

**Form Data:**
- `file`: .txt file (UTF-8 encoded)
- `duration_seconds`: optional integer

### GET /health
Health check endpoint

## 📊 Sample Analysis

**Input**: 131-word self-introduction by Muskan (8th grade student)

**Output**:
- Overall Score: **86/100** (Grade A - Excellent)
- Word Count: 131 words
- Sentence Count: 11 sentences
- Speech Rate: 151 WPM (Ideal)
- Key Strengths: Clear structure, good keyword coverage, positive sentiment
- Areas for Improvement: Minor grammar refinements

## 🌐 Deployment

### Backend → Render.com
- Root Directory: `backend`
- Build: `pip install -r requirements.txt`
- Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Free tier (sleeps after 15min inactivity)

### Frontend → Vercel
- Root Directory: `frontend`
- Build: `npm run build`
- Environment: `VITE_API_URL=<backend-url>`

## 📝 Usage

1. Open the application
2. **Option 1**: Paste transcript in text area
3. **Option 2**: Upload .txt file
4. (Optional) Enter duration in seconds
5. Click "Analyze"
6. View detailed scores and feedback

## ⚙️ Configuration

### Adjusting Scoring Weights
Edit `backend/rubric.py` to modify criterion weights:
```python
RUBRIC = {
    "content_structure": {"weight": 40},
    "speech_rate": {"weight": 10},
    # ...
}
```

### Modifying Filler Words
Edit `backend/analyzer.py`:
```python
self.filler_words = ['um', 'uh', 'like', ...]
```

## 🔍 How It Works

### Semantic Similarity
Uses sentence-transformers (all-MiniLM-L6-v2 model) to:
- Encode transcript into vector embeddings
- Compare with expected topic embeddings
- Detect implicit topic mentions with cosine similarity

### Grammar Checking
LanguageTool analyzes:
- Grammar errors (subject-verb agreement, tense)
- Spelling mistakes
- Typographical errors
- Capitalization and punctuation

### Sentiment Analysis
VADER (Valence Aware Dictionary and sEntiment Reasoner):
- Analyzes text polarity (positive/negative/neutral)
- Generates compound sentiment score
- Evaluates overall engagement level

## 📈 Performance

- **Local**: 2-5 seconds per analysis
- **Deployed**: 5-10 seconds (cold start), 2-3 seconds (warm)
- **Model Loading**: First startup takes 3-5 minutes
- **Subsequent Runs**: 10-30 seconds

## 📦 Dependencies

### Backend (requirements.txt)
```
fastapi
uvicorn[standard]
nltk
sentence-transformers
language-tool-python
python-multipart
```

### Frontend (package.json)
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "axios": "^1.6.5"
  }
}
```

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 👤 Author

Gaurav Tarate

---


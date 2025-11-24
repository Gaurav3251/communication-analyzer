import re
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from sentence_transformers import SentenceTransformer, util
import language_tool_python
from collections import Counter

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)
    nltk.download('vader_lexicon', quiet=True)
    nltk.download('punkt_tab', quiet=True)

class TranscriptAnalyzer:
    def __init__(self):
        print("Initializing analyzer models...")
        self.sia = SentimentIntensityAnalyzer()
        self.model = SentenceTransformer('all-MiniLM-L6-v2')  # Lightweight model
        self.grammar_tool = language_tool_python.LanguageTool('en-US')
        self.filler_words = ['um', 'uh', 'like', 'you know', 'so', 'actually', 
                            'basically', 'right', 'i mean', 'well', 'kinda', 
                            'sort of', 'okay', 'hmm', 'ah']
        print("Analyzer ready.")
    
    def analyze(self, transcript: str, duration_sec: int = None):
        text = transcript.strip()
        
        #NLTK Tokenization
        sentences = sent_tokenize(text)
        words = word_tokenize(text.lower())
        word_count = len([w for w in words if w.isalnum()])
        
        if not duration_sec:
            duration_sec = max(30, word_count // 2)
        
        criteria_results = []
        
        #1. CONTENT & STRUCTURE (40%)
        sal_result = self._score_salutation(text)
        criteria_results.append(sal_result)
        
        kw_result = self._score_keywords_semantic(text)
        criteria_results.append(kw_result)
        
        flow_result = self._score_flow(text)
        criteria_results.append(flow_result)
        
        #2. SPEECH RATE (10%)
        wpm = (word_count / duration_sec) * 60
        sr_result = self._score_speech_rate(wpm, duration_sec)
        criteria_results.append(sr_result)
        
        #3. LANGUAGE & GRAMMAR (20%)
        gram_result = self._score_grammar_languagetool(text, word_count)
        criteria_results.append(gram_result)
        
        ttr_result = self._score_vocabulary(words)
        criteria_results.append(ttr_result)
        
        #4. CLARITY (15%)
        filler_result = self._score_filler_words(text, word_count)
        criteria_results.append(filler_result)
        
        #5. ENGAGEMENT (15%)
        sent_result = self._score_sentiment(text)
        criteria_results.append(sent_result)
        
        overall = sum(c['weighted_score'] for c in criteria_results)
        
        return {
            "overall_score": round(overall, 1),
            "word_count": word_count,
            "sentence_count": len(sentences),
            "criteria_scores": criteria_results,
            "summary": self._generate_summary(overall, criteria_results)
        }
    
    def _score_salutation(self, text):
        text_lower = text.lower()
        score = 0
        found = "None"
        
        excellent = ["i am excited to introduce", "feeling great"]
        good = ["good morning", "good afternoon", "good evening", "hello everyone"]
        normal = ["hi", "hello"]
        
        if any(s in text_lower for s in excellent):
            score, found = 5, "Excellent"
        elif any(s in text_lower for s in good):
            score, found = 4, "Good"
        elif any(s in text_lower for s in normal):
            score, found = 2, "Normal"
        
        return {
            "criterion": "Content & Structure",
            "metric": "Salutation Level",
            "score": score,
            "max_score": 5,
            "weight": 5,
            "weighted_score": score,
            "feedback": f"Salutation type: {found}",
            "details": {"type_found": found}
        }
    
    def _score_keywords_semantic(self, text):
        """Enhanced keyword detection using semantic similarity"""
        text_lower = text.lower()
        
        must_have_keywords = {
            "name": ["name", "myself", "i am", "i'm"],
            "age": ["age", "years old", "year old"],
            "school": ["school", "college", "university", "class"],
            "family": ["family", "parents", "mother", "father", "siblings"],
            "hobbies": ["hobby", "hobbies", "enjoy", "like to", "love to", "play"]
        }
        
        good_to_have = {
            "goals": ["dream", "goal", "ambition", "want to", "aspire"],
            "unique": ["fun fact", "unique", "special", "different"],
            "achievements": ["achievement", "strength", "good at"]
        }
        
        must_score = 0
        must_found = []
        
        for category, keywords in must_have_keywords.items():
            if any(kw in text_lower for kw in keywords):
                must_score += 4
                must_found.append(category)
        
        if len(must_found) < 5:
            embedding = self.model.encode(text, convert_to_tensor=True)
            
            for category in ["name", "age", "school", "family", "hobbies"]:
                if category not in must_found:
                    query = f"student's {category}"
                    query_emb = self.model.encode(query, convert_to_tensor=True)
                    similarity = util.cos_sim(embedding, query_emb).item()
                    
                    if similarity > 0.3:  #threshold for semantic match
                        must_score += 2  
                        must_found.append(f"{category}(semantic)")
        
        must_score = min(must_score, 20)
        
        good_score = 0
        good_found = []
        for category, keywords in good_to_have.items():
            if any(kw in text_lower for kw in keywords):
                good_score += 2
                good_found.append(category)
        good_score = min(good_score, 10)
        
        total = must_score + good_score
        
        return {
            "criterion": "Content & Structure",
            "metric": "Keyword Presence",
            "score": total,
            "max_score": 30,
            "weight": 30,
            "weighted_score": total,
            "feedback": f"Found {len(must_found)} essential topics, {len(good_found)} additional topics",
            "details": {"must_have_found": must_found, "good_to_have_found": good_found}
        }
    
    def _score_flow(self, text):
        text_lower = text.lower()
        order_score = 0
        
        has_greeting = any(g in text_lower[:50] for g in ["hello", "hi", "good"])
        has_name_early = any(n in text_lower[:100] for n in ["my name", "myself", "i am", "i'm"])
        has_closing = any(c in text_lower[-100:] for c in ["thank", "that's all", "that is all"])
        
        if has_greeting: order_score += 2
        if has_name_early: order_score += 2
        if has_closing: order_score += 1
        
        return {
            "criterion": "Content & Structure",
            "metric": "Flow/Structure",
            "score": order_score,
            "max_score": 5,
            "weight": 5,
            "weighted_score": order_score,
            "feedback": f"Structure: Greeting {has_greeting}, Name early {has_name_early}, Closing {has_closing}",
            "details": {"has_greeting": has_greeting, "has_name": has_name_early, "has_closing": has_closing}
        }
    
    def _score_speech_rate(self, wpm, duration):
        if wpm > 161: score = 2
        elif wpm > 140: score = 6
        elif wpm >= 111: score = 10
        elif wpm >= 81: score = 6
        else: score = 2
        
        ideal = "Ideal" if 111 <= wpm <= 140 else ("Too fast" if wpm > 140 else "Too slow")
        
        return {
            "criterion": "Speech Rate",
            "metric": "Words Per Minute",
            "score": score,
            "max_score": 10,
            "weight": 10,
            "weighted_score": score,
            "feedback": f"WPM: {wpm:.0f} ({ideal}). Ideal: 111-140 WPM",
            "details": {"wpm": round(wpm, 1), "duration_used": duration, "category": ideal}
        }
    
    def _score_grammar_languagetool(self, text, word_count):
        """Enhanced grammar checking using LanguageTool"""
        try:
            matches = self.grammar_tool.check(text)
            
            #chk available attributes and filter accordingly
            errors = []
            for m in matches:
                #tried diff attribute names for error classif
                issue_type = None
                if hasattr(m, 'ruleIssueType'):
                    issue_type = m.ruleIssueType
                elif hasattr(m, 'category'):
                    issue_type = m.category
                elif hasattr(m, 'rule'):
                    issue_type = getattr(m.rule, 'category', None)
                
                if issue_type is None or issue_type.lower() in ['grammar', 'misspelling', 'typographical', 'possible_typo', 'grammar_error']:
                    errors.append(m)
            
            if not errors:
                errors = matches[:10] 
            
            error_count = len(errors)
            
            #calc error rate per 100 words
            error_rate = (error_count / max(word_count / 100, 1))
            
            #score based on errors per 100 words
            if error_rate <= 1: score = 10
            elif error_rate <= 2: score = 8
            elif error_rate <= 4: score = 6
            elif error_rate <= 7: score = 4
            else: score = 2
            
            return {
                "criterion": "Language & Grammar",
                "metric": "Grammar Score",
                "score": score,
                "max_score": 10,
                "weight": 10,
                "weighted_score": score,
                "feedback": f"Found {error_count} potential issues ({error_rate:.1f} per 100 words)",
                "details": {
                    "error_count": error_count,
                    "error_rate": round(error_rate, 2),
                    "method": "languagetool"
                }
            }
        except Exception as e:
            #fallback to basic grammar check if LanguageTool fails
            print(f"LanguageTool error: {e}")
            return self._score_grammar_basic(text, word_count)
    
    def _score_grammar_basic(self, text, word_count):
        """Fallback basic grammar check"""
        errors = 0
        sentences = sent_tokenize(text)
        
        for sent in sentences:
            if sent and not sent[0].isupper(): errors += 1
            if sent and sent[-1] not in '.!?': errors += 1
        
        error_patterns = [r'\bi is\b', r'\bhe are\b', r'\bthey is\b', r'\bwe is\b']
        for pat in error_patterns:
            errors += len(re.findall(pat, text.lower()))
        
        error_rate = errors / max(word_count / 100, 1)
        
        if error_rate <= 1: score = 10
        elif error_rate <= 2: score = 8
        elif error_rate <= 4: score = 6
        else: score = 4
        
        return {
            "criterion": "Language & Grammar",
            "metric": "Grammar Score",
            "score": score,
            "max_score": 10,
            "weight": 10,
            "weighted_score": score,
            "feedback": f"Basic check: ~{errors} issues",
            "details": {"error_count": errors}
        }
    
    def _score_vocabulary(self, words):
        alpha_words = [w for w in words if w.isalpha()]
        if not alpha_words:
            return {
                "criterion": "Language & Grammar",
                "metric": "Vocabulary (TTR)",
                "score": 0,
                "max_score": 10,
                "weight": 10,
                "weighted_score": 0,
                "feedback": "No words found",
                "details": {}
            }
        
        ttr = len(set(alpha_words)) / len(alpha_words)
        
        if ttr >= 0.9: score = 10
        elif ttr >= 0.7: score = 8
        elif ttr >= 0.5: score = 6
        elif ttr >= 0.3: score = 4
        else: score = 2
        
        return {
            "criterion": "Language & Grammar",
            "metric": "Vocabulary Richness (TTR)",
            "score": score,
            "max_score": 10,
            "weight": 10,
            "weighted_score": score,
            "feedback": f"TTR: {ttr:.2f}. Higher = more diverse vocabulary",
            "details": {"ttr": round(ttr, 2), "unique_words": len(set(alpha_words)), "total_words": len(alpha_words)}
        }
    
    def _score_filler_words(self, text, word_count):
        text_lower = text.lower()
        filler_count = sum(text_lower.count(f' {f} ') + text_lower.count(f' {f},') for f in self.filler_words)
        filler_rate = (filler_count / max(word_count, 1)) * 100
        
        if filler_rate <= 3: score = 15
        elif filler_rate <= 6: score = 12
        elif filler_rate <= 9: score = 9
        elif filler_rate <= 12: score = 6
        else: score = 3
        
        return {
            "criterion": "Clarity",
            "metric": "Filler Word Rate",
            "score": score,
            "max_score": 15,
            "weight": 15,
            "weighted_score": score,
            "feedback": f"Filler rate: {filler_rate:.1f}%. Found {filler_count} filler words",
            "details": {"filler_count": filler_count, "filler_rate": round(filler_rate, 2)}
        }
    
    def _score_sentiment(self, text):
        scores = self.sia.polarity_scores(text)
        compound = scores['compound']
        positivity = (compound + 1) / 2
        
        if positivity >= 0.9: score = 15
        elif positivity >= 0.7: score = 12
        elif positivity >= 0.5: score = 9
        elif positivity >= 0.3: score = 6
        else: score = 3
        
        return {
            "criterion": "Engagement",
            "metric": "Sentiment/Positivity",
            "score": score,
            "max_score": 15,
            "weight": 15,
            "weighted_score": score,
            "feedback": f"Positivity: {positivity:.2f}. Compound sentiment: {compound:.2f}",
            "details": {"positivity": round(positivity, 2), "compound": compound}
        }
    
    def _generate_summary(self, overall, criteria):
        if overall >= 85:
            return "Excellent introduction! Clear structure, good content coverage, and engaging delivery."
        elif overall >= 70:
            return "Good introduction with room for improvement. Consider adding more details or improving flow."
        elif overall >= 50:
            return "Satisfactory introduction. Focus on including more key information and improving structure."
        else:
            return "Needs improvement. Include essential details (name, age, school) and follow proper introduction flow."
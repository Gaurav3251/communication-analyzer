RUBRIC = {
    "content_structure": {
        "weight": 40,
        "metrics": {
            "salutation": {
                "weight": 5,
                "levels": {
                    "excellent": {"score": 5, "keywords": ["i am excited to introduce", "feeling great"]},
                    "good": {"score": 4, "keywords": ["good morning", "good afternoon", "good evening", "hello everyone"]},
                    "normal": {"score": 2, "keywords": ["hi", "hello"]},
                    "none": {"score": 0, "keywords": []}
                }
            },
            "keywords": {
                "weight": 30,
                "must_have": {
                    "max_score": 20,
                    "per_item": 4,
                    "items": ["name", "age", "school", "class", "family", "hobbies", "interest"]
                },
                "good_to_have": {
                    "max_score": 10,
                    "per_item": 2,
                    "items": ["origin", "dream", "goal", "ambition", "fun fact", "unique", "strength", "achievement"]
                }
            },
            "flow": {
                "weight": 5,
                "order": ["salutation", "name", "basic_details", "additional_details", "closing"],
                "followed": 5,
                "not_followed": 0
            }
        }
    },
    "speech_rate": {
        "weight": 10,
        "metric": "wpm",
        "levels": {
            "too_fast": {"range": [161, 999], "score": 2},
            "fast": {"range": [141, 160], "score": 6},
            "ideal": {"range": [111, 140], "score": 10},
            "slow": {"range": [81, 110], "score": 6},
            "too_slow": {"range": [0, 80], "score": 2}
        }
    },
    "language_grammar": {
        "weight": 20,
        "metrics": {
            "grammar": {
                "weight": 10,
                "formula": "1 - min(errors_per_100_words / 10, 1)",
                "levels": {
                    ">0.9": 10, "0.7-0.89": 8, "0.5-0.69": 6, "0.3-0.49": 4, "<0.3": 2
                }
            },
            "vocabulary_ttr": {
                "weight": 10,
                "formula": "unique_words / total_words",
                "levels": {
                    "0.9-1.0": 10, "0.7-0.89": 8, "0.5-0.69": 6, "0.3-0.49": 4, "0-0.29": 2
                }
            }
        }
    },
    "clarity": {
        "weight": 15,
        "metric": "filler_word_rate",
        "formula": "(filler_count / total_words) * 100",
        "filler_words": ["um", "uh", "like", "you know", "so", "actually", "basically", 
                        "right", "i mean", "well", "kinda", "sort of", "okay", "hmm", "ah"],
        "levels": {
            "0-3": 15, "4-6": 12, "7-9": 9, "10-12": 6, "13+": 3
        }
    },
    "engagement": {
        "weight": 15,
        "metric": "sentiment",
        "method": "VADER",
        "categories": {
            "positive": ["enthusiastic", "confident", "grateful"],
            "neutral": ["factual", "calm"],
            "negative": ["disinterested", "anxious", "dull"]
        },
        "levels": {
            ">0.9": 15, "0.7-0.89": 12, "0.5-0.69": 9, "0.3-0.49": 6, "<0.3": 3
        }
    }
}

SAMPLE_EXPECTED = {
    "transcript": "Hello everyone, myself Muskan, studying in class 8th B section from Christ Public School...",
    "word_count": 131,
    "sentence_count": 11,
    "duration_sec": 52,
    "expected_score": 86
}
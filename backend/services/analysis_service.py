"""
Analysis Module

Performs sentiment analysis and keyword extraction on interview data.
"""

from typing import Dict, List, Any
import re
from collections import Counter
import nltk


class InterviewAnalysis:
    """Performs analysis on interview transcripts."""
    
    def __init__(self):
        """Initialize analysis tools."""
        self.sentiment_analyzer = self._init_sentiment_analyzer()
        self.stop_words = self._get_stop_words()
    
    def _init_sentiment_analyzer(self):
        """Initialize VADER sentiment analyzer."""
        try:
            from nltk.sentiment import SentimentIntensityAnalyzer
            # Download required data
            try:
                nltk.data.find('vader_lexicon')
            except LookupError:
                nltk.download('vader_lexicon', quiet=True)
            
            return SentimentIntensityAnalyzer()
        except ImportError:
            print("  [!] NLTK not available. Sentiment analysis disabled.")
            return None
    
    def _get_stop_words(self) -> set:
        """Get common English stop words."""
        return {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'is', 'are', 'am', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'must', 'can', 'i', 'you', 'he', 'she',
            'it', 'we', 'they', 'them', 'their', 'what', 'which', 'who', 'why',
            'how', 'that', 'this', 'these', 'those', 'as', 'if', 'not', 'no',
            'yes', 'so', 'because', 'there', 'here', 'my', 'your', 'our', 'just',
            'very', 'was', 'were', 'being', 'more', 'most', 'some', 'any', 'each',
            'every', 'both', 'all', 'while', 'when', 'where', 'about', 'out'
        }
    
    def analyze_transcript(self, interview_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform comprehensive analysis on interview transcript.
        
        Args:
            interview_data: Interview data dictionary
        
        Returns:
            Analysis results dictionary
        """
        # Extract sentiment scores
        sentiment_scores = self.extract_sentiment(interview_data)
        
        # Extract keywords and key phrases
        keywords = self.extract_keywords(interview_data)
        key_phrases = self.extract_key_phrases(interview_data)
        
        # Build analysis results
        analysis = {
            "sentiment": {
                "compound": sentiment_scores["overall"].get("average_compound", 0) if sentiment_scores.get("overall") else 0,
                "pos": sum(s.get("positive", 0) for s in sentiment_scores["answers"].values()) / max(len(sentiment_scores["answers"]), 1),
                "neu": sum(s.get("neutral", 0) for s in sentiment_scores["answers"].values()) / max(len(sentiment_scores["answers"]), 1),
                "neg": sum(s.get("negative", 0) for s in sentiment_scores["answers"].values()) / max(len(sentiment_scores["answers"]), 1),
            },
            "keywords": {
                "keywords": keywords,
                "bigrams": key_phrases
            },
            "answer_lengths": self.analyze_answer_lengths(interview_data),
            "engagement_metrics": self.calculate_engagement(interview_data)
        }
        
        return analysis
    
    def extract_sentiment(self, interview_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract sentiment scores from answers.
        
        Args:
            interview_data: Interview data dictionary
        
        Returns:
            Sentiment analysis results
        """
        if not self.sentiment_analyzer:
            return {"status": "unavailable", "reason": "NLTK not installed"}
        
        sentiment_scores = {
            "answers": {},
            "overall": {}
        }
        
        answer_sentiments = []
        
        for pair in interview_data["qa_pairs"]:
            scores = self.sentiment_analyzer.polarity_scores(pair["answer"])
            sentiment_scores["answers"][f"q{pair['number']}"] = {
                "positive": round(scores['pos'], 3),
                "negative": round(scores['neg'], 3),
                "neutral": round(scores['neu'], 3),
                "compound": round(scores['compound'], 3)
            }
            answer_sentiments.append(scores['compound'])
        
        # Calculate overall sentiment
        if answer_sentiments:
            avg_compound = sum(answer_sentiments) / len(answer_sentiments)
            sentiment_scores["overall"] = {
                "average_compound": round(avg_compound, 3),
                "overall_tone": self._classify_sentiment(avg_compound)
            }
        
        return sentiment_scores
    
    @staticmethod
    def _classify_sentiment(compound_score: float) -> str:
        """Classify sentiment based on compound score."""
        if compound_score >= 0.05:
            return "positive"
        elif compound_score <= -0.05:
            return "negative"
        else:
            return "neutral"
    
    def extract_keywords(self, interview_data: Dict[str, Any], top_n: int = 10) -> List[str]:
        """
        Extract top keywords from answers using TF-IDF concept.
        
        Args:
            interview_data: Interview data dictionary
            top_n: Number of keywords to return
        
        Returns:
            List of top keywords
        """
        # Combine all answers
        all_text = " ".join([pair["answer"] for pair in interview_data["qa_pairs"]])
        
        # Tokenize and clean
        words = self._tokenize(all_text)
        
        # Filter stop words and short words
        words = [w for w in words if w not in self.stop_words and len(w) > 3]
        
        # Get most common
        if words:
            word_freq = Counter(words)
            return [word for word, _ in word_freq.most_common(top_n)]
        
        return []
    
    def extract_key_phrases(self, interview_data: Dict[str, Any], top_n: int = 5) -> List[str]:
        """
        Extract 2-3 word phrases from answers.
        
        Args:
            interview_data: Interview data dictionary
            top_n: Number of phrases to return
        
        Returns:
            List of key phrases
        """
        all_text = " ".join([pair["answer"] for pair in interview_data["qa_pairs"]])
        words = self._tokenize(all_text)
        
        # Extract 2-grams and 3-grams
        phrases = []
        
        for n in [2, 3]:
            for i in range(len(words) - n + 1):
                phrase = " ".join(words[i:i+n])
                # Filter by stop words and length
                if not any(w in self.stop_words for w in phrase.split()):
                    phrases.append(phrase)
        
        # Get most common
        if phrases:
            phrase_freq = Counter(phrases)
            return [phrase for phrase, _ in phrase_freq.most_common(top_n)]
        
        return []
    
    @staticmethod
    def analyze_answer_lengths(interview_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze characteristics of answers.
        
        Args:
            interview_data: Interview data dictionary
        
        Returns:
            Answer length statistics
        """
        lengths = [len(pair["answer"].split()) for pair in interview_data["qa_pairs"]]
        
        if not lengths:
            return {}
        
        return {
            "average_words": round(sum(lengths) / len(lengths), 1),
            "max_words": max(lengths),
            "min_words": min(lengths),
            "total_words": sum(lengths)
        }
    
    @staticmethod
    def calculate_engagement(interview_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate engagement metrics.
        
        Args:
            interview_data: Interview data dictionary
        
        Returns:
            Engagement metrics
        """
        total_qa = len(interview_data["qa_pairs"])
        total_text = sum(len(pair["answer"]) for pair in interview_data["qa_pairs"])
        
        return {
            "total_questions": total_qa,
            "total_characters": total_text,
            "completion_rate": 1.0 if total_qa == interview_data["metadata"]["total_questions"] else round(
                total_qa / interview_data["metadata"]["total_questions"], 2
            )
        }
    
    @staticmethod
    def _tokenize(text: str) -> List[str]:
        """Simple tokenization."""
        # Convert to lowercase and remove punctuation
        text = text.lower()
        text = re.sub(r"[^\w\s]", " ", text)
        return text.split()

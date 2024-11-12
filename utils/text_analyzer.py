import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.probability import FreqDist
from collections import Counter

# Download required NLTK data
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger')

class TextAnalyzer:
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))

    def extract_key_topics(self, text):
        """Extract key topics from text using frequency analysis."""
        tokens = word_tokenize(text.lower())
        tokens = [token for token in tokens if token.isalnum() and token not in self.stop_words]
        
        # Get frequency distribution
        fdist = FreqDist(tokens)
        return dict(fdist.most_common(10))

    def compare_sections(self, section1, section2):
        """Compare two sections and identify similarities and differences."""
        # Tokenize sections
        tokens1 = set(word_tokenize(section1.lower()))
        tokens2 = set(word_tokenize(section2.lower()))
        
        # Remove stop words
        tokens1 = {t for t in tokens1 if t.isalnum() and t not in self.stop_words}
        tokens2 = {t for t in tokens2 if t.isalnum() and t not in self.stop_words}
        
        # Calculate similarities and differences
        common = tokens1.intersection(tokens2)
        unique1 = tokens1 - tokens2
        unique2 = tokens2 - tokens1
        
        return {
            'common': list(common),
            'unique_to_first': list(unique1),
            'unique_to_second': list(unique2),
            'similarity_score': len(common) / (len(tokens1.union(tokens2)) + 1e-10)
        }

    def analyze_learning_outcomes(self, text):
        """Analyze learning outcomes using verb analysis."""
        if not text:
            return []
            
        sentences = sent_tokenize(text)
        action_verbs = []
        
        for sentence in sentences:
            tokens = word_tokenize(sentence)
            pos_tags = nltk.pos_tag(tokens)
            
            # Extract verbs
            verbs = [word for word, pos in pos_tags if pos.startswith('VB')]
            action_verbs.extend(verbs)
        
        verb_counts = Counter(action_verbs).most_common(5)
        return [(verb, count) for verb, count in verb_counts]

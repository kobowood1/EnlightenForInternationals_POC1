import os
from openai import OpenAI
import json

class RecommendationEngine:
    def __init__(self):
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    def analyze_syllabus(self, sections):
        """Analyze syllabus content and extract key features."""
        prompt = f"""
        Analyze this course syllabus and extract key features:
        Course Objectives: {sections.get('course_objectives', '')}
        Learning Outcomes: {sections.get('learning_outcomes', '')}
        Course Content: {sections.get('course_content', '')}
        Prerequisites: {sections.get('prerequisites', '')}

        Return a JSON with:
        1. Main topics covered
        2. Skills developed
        3. Difficulty level (Beginner/Intermediate/Advanced)
        4. Subject area
        5. Key prerequisites
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            if content:
                return json.loads(content)
            return {}
        except (json.JSONDecodeError, AttributeError) as e:
            print(f"Error parsing response: {e}")
            return {}

    def generate_recommendations(self, syllabus_analysis, other_syllabi):
        """Generate course recommendations based on syllabus analysis."""
        recommendations = []
        
        # Convert analyses to structured format for comparison
        for syllabus in other_syllabi:
            similarity_score = self._calculate_similarity(syllabus_analysis, syllabus)
            if similarity_score > 0.5:  # Threshold for recommendations
                recommendations.append({
                    'title': syllabus.get('title', 'Unknown Course'),
                    'similarity_score': similarity_score,
                    'reasons': self._generate_similarity_reasons(syllabus_analysis, syllabus)
                })
        
        return sorted(recommendations, key=lambda x: x['similarity_score'], reverse=True)

    def _calculate_similarity(self, analysis1, analysis2):
        """Calculate similarity score between two syllabi analyses."""
        # Compare main topics
        topic_similarity = len(
            set(analysis1.get('main_topics', [])) & 
            set(analysis2.get('main_topics', []))
        ) / max(
            len(analysis1.get('main_topics', [])), 
            len(analysis2.get('main_topics', [])), 
            1
        )

        # Compare skills
        skill_similarity = len(
            set(analysis1.get('skills_developed', [])) & 
            set(analysis2.get('skills_developed', []))
        ) / max(
            len(analysis1.get('skills_developed', [])), 
            len(analysis2.get('skills_developed', [])), 
            1
        )

        # Weight and combine similarities
        return (topic_similarity * 0.6) + (skill_similarity * 0.4)

    def _generate_similarity_reasons(self, analysis1, analysis2):
        """Generate reasons for course similarity."""
        reasons = []
        
        # Compare topics
        common_topics = set(analysis1.get('main_topics', [])) & set(analysis2.get('main_topics', []))
        if common_topics:
            reasons.append(f"Shares common topics: {', '.join(list(common_topics)[:3])}")

        # Compare skills
        common_skills = set(analysis1.get('skills_developed', [])) & set(analysis2.get('skills_developed', []))
        if common_skills:
            reasons.append(f"Develops similar skills: {', '.join(list(common_skills)[:3])}")

        # Compare difficulty
        if analysis1.get('difficulty_level') == analysis2.get('difficulty_level'):
            reasons.append(f"Similar difficulty level: {analysis1.get('difficulty_level')}")

        return reasons
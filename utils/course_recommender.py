import os
from openai import OpenAI

class CourseRecommender:
    def __init__(self):
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    def generate_recommendations(self, syllabus_text, num_recommendations=3):
        """Generate course recommendations based on syllabus content."""
        if not syllabus_text:
            return '{"recommendations": []}'
            
        prompt = f"""
        Based on the following syllabus content, provide {num_recommendations} course recommendations.
        For each recommendation, include:
        - Course title
        - Brief description
        - Key topics
        - Why it's relevant
        Return the response in JSON format with the following structure:
        {{
            "recommendations": [
                {{
                    "title": "Course title",
                    "description": "Brief description",
                    "key_topics": ["topic1", "topic2", "topic3"],
                    "relevance": "Why this course is relevant"
                }}
            ]
        }}

        Syllabus content:
        {syllabus_text}
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            return response.choices[0].message.content
        except Exception as e:
            return '{"recommendations": []}'

    def analyze_similarity(self, syllabus1_text, syllabus2_text):
        """Analyze similarity between two syllabi and provide detailed insights."""
        if not syllabus1_text or not syllabus2_text:
            return '{"similarity_analysis": {"overall_similarity": "N/A", "complementary_aspects": [], "key_differences": [], "progression_path": "N/A"}}'
            
        prompt = f"""
        Compare the following two syllabi and provide detailed insights about their similarities,
        differences, and potential complementary aspects. Return the response in JSON format:
        {{
            "similarity_analysis": {{
                "overall_similarity": "Brief description of overall similarity",
                "complementary_aspects": ["aspect1", "aspect2"],
                "key_differences": ["difference1", "difference2"],
                "progression_path": "Whether these courses form a logical progression"
            }}
        }}

        Syllabus 1:
        {syllabus1_text}

        Syllabus 2:
        {syllabus2_text}
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            return response.choices[0].message.content
        except Exception as e:
            return '{"similarity_analysis": {"overall_similarity": "N/A", "complementary_aspects": [], "key_differences": [], "progression_path": "N/A"}}'

import os
import json
import logging
from openai import OpenAI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CourseRecommender:
    def __init__(self):
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    def validate_json_response(self, response_text):
        """Validate JSON response from OpenAI API."""
        try:
            data = json.loads(response_text)
            # Validate recommendations structure
            if "recommendations" in data:
                for rec in data.get("recommendations", []):
                    required_fields = ["title", "description", "key_topics", "relevance"]
                    if not all(field in rec for field in required_fields):
                        logger.error("Invalid recommendation format: missing required fields")
                        return False
            # Validate similarity analysis structure
            elif "similarity_analysis" in data:
                required_fields = ["overall_similarity", "complementary_aspects", "key_differences", "progression_path"]
                if not all(field in data["similarity_analysis"] for field in required_fields):
                    logger.error("Invalid similarity analysis format: missing required fields")
                    return False
            return True
        except json.JSONDecodeError:
            logger.error("Failed to decode JSON response")
            return False

    def generate_recommendations(self, syllabus_text, num_recommendations=3):
        """Generate course recommendations based on syllabus content."""
        if not syllabus_text:
            logger.warning("Empty syllabus text provided")
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
            logger.info("Sending recommendation request to OpenAI API")
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            response_content = response.choices[0].message.content
            
            if not self.validate_json_response(response_content):
                logger.error("Invalid JSON response format from API")
                return '{"recommendations": [], "error": "Invalid response format"}'
                
            logger.info("Successfully generated recommendations")
            return response_content
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return json.dumps({
                "recommendations": [],
                "error": f"Failed to generate recommendations: {str(e)}"
            })

    def analyze_similarity(self, syllabus1_text, syllabus2_text):
        """Analyze similarity between two syllabi and provide detailed insights."""
        if not syllabus1_text or not syllabus2_text:
            logger.warning("Empty syllabus text provided for similarity analysis")
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
            logger.info("Sending similarity analysis request to OpenAI API")
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            response_content = response.choices[0].message.content
            
            if not self.validate_json_response(response_content):
                logger.error("Invalid JSON response format from API")
                return '{"similarity_analysis": {"overall_similarity": "Error: Invalid response format", "complementary_aspects": [], "key_differences": [], "progression_path": "N/A"}}'
            
            logger.info("Successfully generated similarity analysis")
            return response_content
            
        except Exception as e:
            logger.error(f"Error analyzing similarity: {str(e)}")
            return json.dumps({
                "similarity_analysis": {
                    "overall_similarity": f"Error: {str(e)}",
                    "complementary_aspects": [],
                    "key_differences": [],
                    "progression_path": "N/A"
                }
            })
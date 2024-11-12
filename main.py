import streamlit as st
import pandas as pd
import json
import logging
from utils.pdf_processor import PDFProcessor
from utils.text_analyzer import TextAnalyzer
from utils.visualizer import Visualizer
from utils.course_recommender import CourseRecommender

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Syllabus Analyzer",
    page_icon="📚",
    layout="wide"
)

# Load custom CSS
with open('assets/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Initialize components
pdf_processor = PDFProcessor()
text_analyzer = TextAnalyzer()
visualizer = Visualizer()
course_recommender = CourseRecommender()

# Title and description
st.title("📚 Course Syllabus Analyzer")
st.markdown("""
Compare and analyze two course syllabi to identify similarities, differences, 
and key learning outcomes. Upload your PDF files below to get started.
""")

# File upload section
col1, col2 = st.columns(2)
with col1:
    st.subheader("First Syllabus")
    file1 = st.file_uploader("Upload first syllabus (PDF)", type=['pdf'])

with col2:
    st.subheader("Second Syllabus")
    file2 = st.file_uploader("Upload second syllabus (PDF)", type=['pdf'])

if file1 and file2:
    try:
        # Process PDFs
        with st.spinner("Processing syllabi..."):
            # Extract and clean text
            text1 = pdf_processor.clean_text(pdf_processor.extract_text(file1.read()))
            text2 = pdf_processor.clean_text(pdf_processor.extract_text(file2.read()))
            
            # Extract sections
            sections1 = pdf_processor.extract_sections(text1)
            sections2 = pdf_processor.extract_sections(text2)

        # Analysis tabs
        tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Detailed Comparison", "Learning Outcomes", "Course Recommendations"])
        
        # Overview Tab
        with tab1:
            st.header("Overview Analysis")
            
            # Overall similarity
            comparison = text_analyzer.compare_sections(text1, text2)
            st.plotly_chart(visualizer.create_similarity_gauge(comparison['similarity_score']))
            
            # Key topics comparison
            st.subheader("Key Topics Comparison")
            topics1 = text_analyzer.extract_key_topics(text1)
            topics2 = text_analyzer.extract_key_topics(text2)
            st.plotly_chart(visualizer.create_topic_comparison(topics1, topics2))

        # Detailed Comparison Tab
        with tab2:
            st.header("Section-by-Section Comparison")
            
            for section in sections1.keys():
                with st.expander(f"{section.replace('_', ' ').title()}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**First Syllabus**")
                        st.write(sections1[section] or "No content available")
                    with col2:
                        st.markdown("**Second Syllabus**")
                        st.write(sections2[section] or "No content available")
                    
                    # Show section-specific comparison
                    section_comparison = text_analyzer.compare_sections(
                        sections1[section] or "", sections2[section] or ""
                    )
                    
                    st.markdown("### Common Elements")
                    st.write(", ".join(section_comparison['common']) or "None found")
                    
                    st.markdown("### Unique Elements")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**First Syllabus**")
                        st.write(", ".join(section_comparison['unique_to_first']) or "None found")
                    with col2:
                        st.markdown("**Second Syllabus**")
                        st.write(", ".join(section_comparison['unique_to_second']) or "None found")

        # Learning Outcomes Tab
        with tab3:
            st.header("Learning Outcomes Analysis")
            
            # Analyze learning outcomes
            outcomes1 = text_analyzer.analyze_learning_outcomes(sections1['learning_outcomes'] or "")
            outcomes2 = text_analyzer.analyze_learning_outcomes(sections2['learning_outcomes'] or "")
            
            # Display action verbs analysis
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### First Syllabus Action Verbs")
                if outcomes1:
                    df1 = pd.DataFrame(outcomes1, columns=['Verb', 'Count'])
                    st.write(df1)
                else:
                    st.write("No learning outcomes found")
            with col2:
                st.markdown("### Second Syllabus Action Verbs")
                if outcomes2:
                    df2 = pd.DataFrame(outcomes2, columns=['Verb', 'Count'])
                    st.write(df2)
                else:
                    st.write("No learning outcomes found")
            
            # Display learning outcomes comparison chart
            st.plotly_chart(visualizer.create_learning_outcomes_chart(
                dict(outcomes1) if outcomes1 else {}, 
                dict(outcomes2) if outcomes2 else {}
            ))

        # Course Recommendations Tab
        with tab4:
            st.header("AI-Powered Course Recommendations")
            
            # Add retry button for recommendations
            if 'recommendation_retries' not in st.session_state:
                st.session_state.recommendation_retries = 0
            
            retry_col1, retry_col2 = st.columns([3, 1])
            with retry_col2:
                if st.button("🔄 Retry Analysis", key="retry_button"):
                    st.session_state.recommendation_retries += 1
                    try:
                        st.rerun()
                    except Exception as e:
                        logger.error(f"Error during rerun: {str(e)}")
                        st.error("Failed to refresh the analysis. Please try uploading the files again.")
            
            with st.spinner("Analyzing syllabi and generating recommendations..."):
                try:
                    # Get recommendations based on both syllabi
                    if not text1 or not text2:
                        st.warning("Unable to process syllabi content. Please ensure both files are properly uploaded.")
                        recommendations = {"recommendations": []}
                        similarity_analysis = {
                            "similarity_analysis": {
                                "overall_similarity": "N/A",
                                "complementary_aspects": [],
                                "key_differences": [],
                                "progression_path": "N/A"
                            }
                        }
                    else:
                        recommendations = json.loads(course_recommender.generate_recommendations(
                            text1 + "\n" + text2))
                        similarity_analysis = json.loads(course_recommender.analyze_similarity(
                            text1, text2))
                    
                    # Display similarity analysis
                    st.subheader("Course Similarity Analysis")
                    analysis = similarity_analysis.get("similarity_analysis", {})
                    
                    # Check for errors in similarity analysis
                    if "error" in analysis.get("overall_similarity", ""):
                        st.error(f"Error in similarity analysis: {analysis['overall_similarity']}")
                        st.info("Try uploading the files again or click the retry button above.")
                    else:
                        st.write(analysis.get("overall_similarity", "Analysis not available"))
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("### Complementary Aspects")
                            aspects = analysis.get("complementary_aspects", [])
                            if aspects:
                                for aspect in aspects:
                                    st.markdown(f"- {aspect}")
                            else:
                                st.info("No complementary aspects found")
                        
                        with col2:
                            st.markdown("### Key Differences")
                            differences = analysis.get("key_differences", [])
                            if differences:
                                for diff in differences:
                                    st.markdown(f"- {diff}")
                            else:
                                st.info("No key differences found")
                        
                        st.markdown("### Progression Path")
                        st.write(analysis.get("progression_path", "Analysis not available"))
                    
                    # Display recommendations with error handling
                    st.subheader("Recommended Related Courses")
                    
                    if "error" in recommendations:
                        st.error(f"Error generating recommendations: {recommendations['error']}")
                        st.info("Try uploading the files again or click the retry button above.")
                    else:
                        recs = recommendations.get("recommendations", [])
                        if not recs:
                            st.warning("No course recommendations available. Try uploading different syllabi or click the retry button.")
                        else:
                            for rec in recs:
                                with st.expander(f"📘 {rec['title']}"):
                                    st.markdown(f"**Description:** {rec['description']}")
                                    st.markdown("**Key Topics:**")
                                    for topic in rec.get('key_topics', []):
                                        st.markdown(f"- {topic}")
                                    st.markdown(f"**Why it's relevant:** {rec['relevance']}")
                
                except json.JSONDecodeError as e:
                    logger.error(f"JSON parsing error: {str(e)}")
                    st.error("Error processing API response. Please try again.")
                    st.info("If the error persists, try uploading the files again or click the retry button.")
                
                except Exception as e:
                    logger.error(f"Unexpected error in recommendations tab: {str(e)}")
                    st.error(f"An unexpected error occurred: {str(e)}")
                    st.info("Please try again or contact support if the issue persists.")

    except Exception as e:
        logger.error(f"Error processing syllabi: {str(e)}")
        st.error(f"An error occurred while processing the syllabi: {str(e)}")
else:
    st.info("Please upload both syllabi to begin the analysis.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>Built with ❤️ for educational analysis</p>
</div>
""", unsafe_allow_html=True)
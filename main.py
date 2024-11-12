import streamlit as st
import pandas as pd
import json
from utils.pdf_processor import PDFProcessor
from utils.text_analyzer import TextAnalyzer
from utils.visualizer import Visualizer
from utils.course_recommender import CourseRecommender

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
            
            with st.spinner("Generating course recommendations..."):
                try:
                    # Get recommendations based on both syllabi
                    recommendations = json.loads(course_recommender.generate_recommendations(text1 + "\n" + text2))
                    
                    # Get similarity analysis
                    similarity_analysis = json.loads(course_recommender.analyze_similarity(text1, text2))
                    
                    # Display similarity analysis
                    st.subheader("Course Similarity Analysis")
                    analysis = similarity_analysis.get("similarity_analysis", {})
                    st.write(analysis.get("overall_similarity", "Analysis not available"))
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("### Complementary Aspects")
                        for aspect in analysis.get("complementary_aspects", []):
                            st.markdown(f"- {aspect}")
                    
                    with col2:
                        st.markdown("### Key Differences")
                        for diff in analysis.get("key_differences", []):
                            st.markdown(f"- {diff}")
                    
                    st.markdown("### Progression Path")
                    st.write(analysis.get("progression_path", "Analysis not available"))
                    
                    # Display recommendations
                    st.subheader("Recommended Related Courses")
                    for rec in recommendations.get("recommendations", []):
                        with st.expander(f"📘 {rec['title']}"):
                            st.markdown(f"**Description:** {rec['description']}")
                            st.markdown("**Key Topics:**")
                            for topic in rec['key_topics']:
                                st.markdown(f"- {topic}")
                            st.markdown(f"**Why it's relevant:** {rec['relevance']}")
                except Exception as e:
                    st.error("Error generating recommendations. Please try again.")

    except Exception as e:
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

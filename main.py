import streamlit as st
import pandas as pd
from utils.pdf_processor import PDFProcessor
from utils.text_analyzer import TextAnalyzer
from utils.visualizer import Visualizer
from utils.recommendation_engine import RecommendationEngine

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
recommendation_engine = RecommendationEngine()

# Session state for storing analyzed syllabi
if 'analyzed_syllabi' not in st.session_state:
    st.session_state.analyzed_syllabi = []

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

            # Get course recommendations
            with st.spinner("Analyzing syllabi for recommendations..."):
                syllabus1_analysis = recommendation_engine.analyze_syllabus(sections1)
                syllabus2_analysis = recommendation_engine.analyze_syllabus(sections2)
                
                # Store analyses in session state
                if syllabus1_analysis not in st.session_state.analyzed_syllabi:
                    st.session_state.analyzed_syllabi.append(syllabus1_analysis)
                if syllabus2_analysis not in st.session_state.analyzed_syllabi:
                    st.session_state.analyzed_syllabi.append(syllabus2_analysis)

        # Analysis tabs
        tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Detailed Comparison", "Learning Outcomes", "Recommendations"])
        
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
                        st.write(sections1[section])
                    with col2:
                        st.markdown("**Second Syllabus**")
                        st.write(sections2[section])
                    
                    # Show section-specific comparison
                    section_comparison = text_analyzer.compare_sections(
                        sections1[section], sections2[section]
                    )
                    
                    st.markdown("### Common Elements")
                    st.write(", ".join(section_comparison['common']))
                    
                    st.markdown("### Unique Elements")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**First Syllabus**")
                        st.write(", ".join(section_comparison['unique_to_first']))
                    with col2:
                        st.markdown("**Second Syllabus**")
                        st.write(", ".join(section_comparison['unique_to_second']))

        # Learning Outcomes Tab
        with tab3:
            st.header("Learning Outcomes Analysis")
            
            # Analyze learning outcomes
            outcomes1 = text_analyzer.analyze_learning_outcomes(sections1['learning_outcomes'])
            outcomes2 = text_analyzer.analyze_learning_outcomes(sections2['learning_outcomes'])
            
            # Display action verbs analysis
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### First Syllabus Action Verbs")
                outcomes_df1 = pd.DataFrame(outcomes1, columns=['Action Verb', 'Frequency'])
                st.write(outcomes_df1)
            with col2:
                st.markdown("### Second Syllabus Action Verbs")
                outcomes_df2 = pd.DataFrame(outcomes2, columns=['Action Verb', 'Frequency'])
                st.write(outcomes_df2)
            
            # Display learning outcomes comparison chart
            st.plotly_chart(visualizer.create_learning_outcomes_chart(
                dict(outcomes1), dict(outcomes2)
            ))

        # Recommendations Tab
        with tab4:
            st.header("Course Recommendations")
            
            # Generate recommendations for both syllabi
            if len(st.session_state.analyzed_syllabi) > 0:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Based on First Syllabus")
                    recommendations1 = recommendation_engine.generate_recommendations(
                        syllabus1_analysis,
                        [s for s in st.session_state.analyzed_syllabi if s != syllabus1_analysis]
                    )
                    
                    if recommendations1:
                        for rec in recommendations1:
                            with st.expander(f"📘 {rec['title']} (Similarity: {rec['similarity_score']:.2%})"):
                                st.markdown("**Why this course?**")
                                for reason in rec['reasons']:
                                    st.markdown(f"- {reason}")
                    else:
                        st.info("No similar courses found yet. Upload more syllabi for better recommendations.")

                with col2:
                    st.subheader("Based on Second Syllabus")
                    recommendations2 = recommendation_engine.generate_recommendations(
                        syllabus2_analysis,
                        [s for s in st.session_state.analyzed_syllabi if s != syllabus2_analysis]
                    )
                    
                    if recommendations2:
                        for rec in recommendations2:
                            with st.expander(f"📘 {rec['title']} (Similarity: {rec['similarity_score']:.2%})"):
                                st.markdown("**Why this course?**")
                                for reason in rec['reasons']:
                                    st.markdown(f"- {reason}")
                    else:
                        st.info("No similar courses found yet. Upload more syllabi for better recommendations.")
            else:
                st.info("Upload syllabi to get course recommendations.")

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
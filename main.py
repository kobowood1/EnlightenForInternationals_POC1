import streamlit as st
import pandas as pd
from utils.pdf_processor import PDFProcessor
from utils.text_analyzer import TextAnalyzer
from utils.visualizer import Visualizer

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
        tab1, tab2, tab3 = st.tabs(["Overview", "Detailed Comparison", "Learning Outcomes"])
        
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
                st.write(pd.DataFrame(outcomes1, columns=['Verb', 'Count']))
            with col2:
                st.markdown("### Second Syllabus Action Verbs")
                st.write(pd.DataFrame(outcomes2, columns=['Verb', 'Count']))
            
            # Display learning outcomes comparison chart
            st.plotly_chart(visualizer.create_learning_outcomes_chart(
                dict(outcomes1), dict(outcomes2)
            ))

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

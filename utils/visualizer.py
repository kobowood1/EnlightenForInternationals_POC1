import plotly.graph_objects as go
import plotly.express as px

class Visualizer:
    @staticmethod
    def create_similarity_gauge(similarity_score):
        """Create a gauge chart showing similarity score."""
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = similarity_score * 100,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Similarity Score"},
            gauge = {
                'axis': {'range': [0, 100]},
                'bar': {'color': "#1f4068"},
                'steps': [
                    {'range': [0, 33], 'color': "#ffebee"},
                    {'range': [33, 66], 'color': "#fff3e0"},
                    {'range': [66, 100], 'color': "#e8f5e9"}
                ]
            }
        ))
        return fig

    @staticmethod
    def create_topic_comparison(topics1, topics2):
        """Create a bar chart comparing key topics."""
        all_topics = set(topics1.keys()).union(set(topics2.keys()))
        
        data = []
        for topic in all_topics:
            data.append({
                'Topic': topic,
                'Syllabus 1': topics1.get(topic, 0),
                'Syllabus 2': topics2.get(topic, 0)
            })
        
        fig = px.bar(data, x='Topic', y=['Syllabus 1', 'Syllabus 2'],
                    barmode='group',
                    color_discrete_sequence=['#1f4068', '#ff6b6b'])
        return fig

    @staticmethod
    def create_learning_outcomes_chart(outcomes1, outcomes2):
        """Create a radar chart comparing learning outcomes."""
        categories = ['Knowledge', 'Comprehension', 'Application', 
                     'Analysis', 'Synthesis', 'Evaluation']
        
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=[len(outcomes1.get(cat, [])) for cat in categories],
            theta=categories,
            fill='toself',
            name='Syllabus 1'
        ))
        fig.add_trace(go.Scatterpolar(
            r=[len(outcomes2.get(cat, [])) for cat in categories],
            theta=categories,
            fill='toself',
            name='Syllabus 2'
        ))
        
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 10])))
        return fig

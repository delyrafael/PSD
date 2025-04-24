import streamlit as st
import os
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import plotly.express as px

# Set page configuration
st.set_page_config(
    page_title="Movie Recommendation System",
    page_icon="🎬",
    layout="wide"
)

# Load environment variables
load_dotenv()

# Custom CSS for better styling
st.markdown("""
<style>
    .header-container {
        background-color: #1E1E1E;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .recommendation-card {
        background-color: #2C2C2C;
        padding: 1rem;
        border-radius: 5px;
        margin-bottom: 1rem;
        min-height: 180px;
        overflow-y: auto;
        display: flex;
        flex-direction: column;
    }
    .movie-title {
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .similarity-score {
        font-size: 14px;
        color: #4CAF50;
    }
    .movie-overview {
        font-size: 14px;
        color: #CCCCCC;
    }
    .recommendation-header {
        background-color: #333333;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# App title and description
st.markdown("""
<div class="header-container">
    <h1 style="color: #FF4B4B;">🎬 Smart Movie Recommendation System</h1>
    <p style="color: #CCCCCC;">Discover movies similar to your favorites with AI-powered recommendations and explanations.</p>
</div>
""", unsafe_allow_html=True)

# # Sidebar
# with st.sidebar:
#     st.header("About")
#     st.info("This app uses content-based filtering with NLP to recommend movies similar to your search. The system analyzes movie tags, plots, and other features to find the most similar films.")
    
#     st.header("How it works")
#     st.write("1. Enter a movie title in the search box")
#     st.write("2. View the top 5 recommended movies")
#     st.write("3. Read AI-generated explanations of why these movies match your interests")
    
#     st.header("Features")
#     st.write("✅ Content-based movie recommendations")
#     st.write("✅ Similarity scores visualization")
#     st.write("✅ Detailed explanations of recommendations")
#     st.write("✅ Movie information and overviews")

# Load data function
@st.cache_data
def load_movie_data():
    # In a real application, you'd load your actual movie data
    # For this example, let's create a sample dataframe with some movies
    
    df = pd.read_excel("newdf_for_rag.xlsx")
    return df

# Load movie data
new_df = load_movie_data()

# Set up Content-Based recommendation system
@st.cache_resource
def prepare_recommendation_system(df):
    cv = CountVectorizer(max_features=5000, stop_words='english')
    vector = cv.fit_transform(df['tags']).toarray()
    similarity = cosine_similarity(vector)
    return similarity

similarity = prepare_recommendation_system(new_df)

# Function to get content-based recommendations
def recommend_content_based(movie, df, similarity_matrix):
    if movie not in df['title'].values:
        return None
    
    index = df[df['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity_matrix[index])), reverse=True, key=lambda x: x[1])
    
    recommendations = []
    for i in distances[1:6]:
        movie_title = df.iloc[i[0]].title
        similarity_score = i[1]
        recommendations.append({
            'title': movie_title,
            'index': i[0],
            'similarity': similarity_score,
            'overview': df.iloc[i[0]].overview,
            'tags': df.iloc[i[0]].tags
        })
    
    return recommendations

# Create recommendations context
def create_recommendations_context(recommendations):
    context = "Film-film yang direkomendasikan berdasarkan kemiripan dengan query:\n\n"
    
    for idx, rec in enumerate(recommendations):
        context += f"{idx+1}. {rec['title']}\n"
        context += f"   Overview: {rec['overview']}\n"
        context += f"   Tags: {rec['tags']}\n"
        context += f"   Similarity score: {rec['similarity']*100:.2f}%\n\n"
    
    return context

# Generate reasoning for recommendations
def generate_reasoning(movie_query, recommendations_context):
    # Check if OpenAI API key is available
    if os.getenv("OPENAI_API_KEY"):
        try:
            # Template for providing reasoning
            template = """
            You are a smart movie recommendation assistant. Provide a detailed analysis of why the following movies are recommended.
            
            Original movie query: {movie_query}
            
            Here are the recommended movies based on similarity:
            {recommendations_context}
            
            Explain why these movies are recommended, especially the top ones in the list.
            Compare them with the original movie being queried. Discuss themes, genres, directors, or other elements that make them similar.
            Provide informative and in-depth explanations.
            
            Begin your explanation by mentioning the top recommended movie and why it's a particularly good match.
            """
            
            prompt = PromptTemplate(
                input_variables=["movie_query", "recommendations_context"],
                template=template
            )
            
            llm = OpenAI(temperature=0.7)
            
            reasoning_input = prompt.format(
                movie_query=movie_query,
                recommendations_context=recommendations_context
            )
            
            reasoning = llm(reasoning_input)
            return reasoning
        except Exception as e:
            return f"Could not generate AI explanation: {str(e)}\n\nThese movies were recommended based on content similarity in tags, themes, and other attributes."
    else:
        # Fallback explanation if no API key
        return """
        These movies were recommended based on content similarity analysis. The system analyzed tags, plots, directors, and themes to find movies that share similar characteristics with your search. The similarity score indicates how closely each recommendation matches your original movie.
        
        For more detailed AI-powered explanations, please configure your OpenAI API key in the .env file.
        """

# Main app layout
st.subheader("Find Movie Recommendations")

# Movie search
movie_list = new_df['title'].tolist()
selected_movie = st.selectbox("Search for a movie", [""] + movie_list)

if selected_movie:
    # Get recommendations
    recommendations = recommend_content_based(selected_movie, new_df, similarity)
    
    if recommendations:
        # Display selected movie info
        selected_movie_info = new_df[new_df['title'] == selected_movie].iloc[0]
        
        st.markdown("### 🎞 Selected Movie")
        st.markdown(f"""
        <div class="recommendation-card" style="background-color: #3D3D3D;">
            <div class="movie-title">{selected_movie}</div>
            <div class="movie-overview">{selected_movie_info['tags']}</div>
            <div class="movie-tags" style="margin-top: 10px; font-size: 12px;">
                <span style="color: #AAAAAA;">Tags:</span> {selected_movie_info['genres']}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Create two columns for recommendations and explanation
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("""
            <div class="recommendation-header">
                <h3 style="margin: 0; color: white;">Top 5 Recommendations</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Display recommendations
            for rec in recommendations:
                st.markdown(f"""
                <div class="recommendation-card">
                    <div class="movie-title">{rec['title']}</div>
                    <div class="similarity-score">Similarity Score: {rec['similarity']*100:.2f}%</div>
                    <div class="movie-overview">{rec['tags']}</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Create visualization of similarity scores
            similarity_data = pd.DataFrame(
                {'Movie': [r['title'] for r in recommendations],
                 'Similarity': [r['similarity'] * 100 for r in recommendations]}
            )
            
            fig = px.bar(
                similarity_data,
                x='Similarity',
                y='Movie',
                orientation='h',
                title='Similarity Scores',
                labels={'Similarity': 'Similarity Score (%)'},
                color='Similarity',
                color_continuous_scale='Viridis',
                range_color=[0, 100]
            )
            fig.update_xaxes(range=[0, 100])
            
            fig.update_layout(
                height=300,
                margin=dict(l=20, r=20, t=40, b=20),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                yaxis=dict(autorange="reversed")
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("""
            <div class="recommendation-header">
                <h3 style="margin: 0; color: white;">Why These Movies?</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Create context for reasoning
            recommendations_context = create_recommendations_context(recommendations)
            
            # Generate and display reasoning
            with st.spinner("Generating explanations..."):
                reasoning = generate_reasoning(selected_movie, recommendations_context)
                st.markdown(f"""
                <div class="recommendation-card" style="background-color: #2C2C2C; padding: 10px; border-radius: 5px;  overflow-wrap: break-word;">
                    <p style="color: white; margin: 0;">
                    {reasoning}
                </div>
                """, unsafe_allow_html=True)
    else:
        st.error("Sorry, couldn't find recommendations for that movie. Try another title.")
else:
    # Display sample movies when no movie is selected
    st.info("Select a movie from the dropdown to get recommendations.")
    
    st.markdown("### Sample Movies in Our Database")
    
    # Display sample movie cards in a grid
    cols = st.columns(3)
    for i, movie in enumerate(new_df['title'][:6]):
        movie_info = new_df[new_df['title'] == movie].iloc[0]
        with cols[i % 3]:
            st.markdown(f"""
            <div class="recommendation-card">
                <div class="movie-title">{movie}</div>
                <div class="movie-overview">{movie_info['tags'][:100]}...</div>
            </div>
            """, unsafe_allow_html=True)

# Add footer
st.markdown("""
<div style="text-align: center; margin-top: 50px; padding: 20px; color: #AAAAAA; font-size: 12px;">
    Movie Recommendation System | Built with Streamlit | Data Analysis & NLP
</div>
""", unsafe_allow_html=True)
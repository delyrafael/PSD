import streamlit as st
import pandas as pd
import json
import os
import plotly.express as px
import sys
from preposesing import generate_ai_summary_for_category
import pandas as pd
import re
import logging
from io import StringIO
import contextlib
from Crawling import (
    initialize_driver, search_movie_by_title, scrape_all_reviews)

from preposesing import (
    clean_text, generate_wordcloud, categorize_sentiment, extract_common_phrases)


# Set page configuration
st.set_page_config(
    page_title="IMDb Review Scraper",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Styling
st.markdown("""
<style>
.title {
    font-size: 42px !important;
    color: #F5C518;
    text-align: center;
}
.subtitle {
    font-size: 24px !important;
    color: #E2B616;
    text-align: center;
}
.stProgress > div > div > div > div {
    background-color: #F5C518;
}
.review-card {
    background-color: #f0f2f6;
    border-radius: 10px;
    padding: 20px;
    margin-bottom: 20px;
}
.review-title {
    font-weight: bold;
    font-size: 18px;
    margin-bottom: 10px;
}
.review-rating {
    color: #F5C518;
    font-weight: bold;
}
.review-text {
    font-style: italic;
    color: #333;
}
.review-author {
    text-align: right;
    font-size: 14px;
    color: #666;
}
.review-date {
    text-align: right;
    font-size: 12px;
    color: #888;
}
</style>
""", unsafe_allow_html=True)

# Title and description
st.markdown("<h1 class='title'>IMDb Review Scraper Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Search for movies and analyze their reviews</p>", unsafe_allow_html=True)


# Safe execution function to capture output
@contextlib.contextmanager
def capture_output():
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    stdout_buffer = StringIO()
    stderr_buffer = StringIO()
    sys.stdout = stdout_buffer
    sys.stderr = stderr_buffer
    try:
        yield stdout_buffer, stderr_buffer
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr

# Initialize session state
if 'search_results' not in st.session_state:
    st.session_state.search_results = None
if 'selected_movie' not in st.session_state:
    st.session_state.selected_movie = None
if 'reviews_data' not in st.session_state:
    st.session_state.reviews_data = None
if 'driver' not in st.session_state:
    st.session_state.driver = None
if 'loading' not in st.session_state:
    st.session_state.loading = False


# if api_key:
#     # Save the API key to an environment variable
#     os.environ['OPENAI_API_KEY'] = api_key
#     st.success("API Key saved successfully!")
# # Create sidebar for search and options
# if 'api_key' not in st.session_state:
#     st.session_state.api_key = ""

# if not st.session_state.api_key:
#     api_key = st.text_input("API Key", type="password")
#     if api_key:
#         st.session_state.api_key = api_key
#         st.success("API Key saved successfully!")
# else:
#     api_key = st.session_state.api_key

page = st.sidebar.selectbox("Navigate", ["API Assign","Home", "Crawling Dashboard", "Analisis Movie"])
logging.getLogger("streamlit.runtime.caching.cache_data_api.CacheDataAPI object at").setLevel(logging.ERROR)
st.cache_data.clear()
GLOBAL_API_KEY = None
if page == "API Assign":
    st.title("Masukan API Key OpenAI")
    api_key = st.text_input("API Key", type="password")
    if st.button("Enter"):
        if api_key:
            GLOBAL_API_KEY
            GLOBAL_API_KEY = api_key
            os.environ['OPENAI_API_KEY'] = api_key
            st.success("API Key saved successfully!")
            st.experimental_set_query_params(page="Home")
            st.rerun()
        else:
            st.warning("Please enter your API Key.")

elif page == "Home":
    st.title("Sentiment Analysis and Summarization using LLM")
    st.markdown("""
    sistem analisis sentimen berbasis Large Language Model (LLM) menggunakan API OpenAI, 
                dengan fokus pada ulasan film. Tujuan dari penelitian ini adalah untuk mengembangkan sistem analisis sentimen dan summarization yang efektif,
                serta mengevaluasi akurasi hasilnya. Sistem ini melalui tahapan akuisisi data, eksplorasi data awal (EDA), preprocessing, 
                dan penerapan analisis sentimen berbasis agen. Hasil dari analisis sentimen kemudian disajikan dalam bentuk ringkasan menggunakan model LLM
    
    This tool uses data IMBD, analisis sentimen, summarization, LLM, OpenAI API, , NLP.
    """)
elif page == "Crawling Dashboard":
    st.title("IMDb Review Scraper")

    with st.sidebar:
        st.header("Search Options")
        
        # Movie search
        movie_title = st.text_input("Enter movie title:")
        max_pages = st.number_input("Maximum pages to scrape (0 for all):", min_value=0, value=2)
        if max_pages == 0:
            max_pages = None
        
        # Search button
        if st.button("Search Movies"):
            if movie_title:
                st.session_state.loading = True

                # Initialize driver
                if not st.session_state.driver:
                    with st.spinner("Initializing browser..."):
                        with capture_output() as (stdout, stderr):
                            try:
                                st.session_state.driver = initialize_driver()
                            except Exception as e:
                                st.error(f"Error initializing browser: {str(e)}")
                                st.session_state.loading = False
                
                # Search for movies
                if st.session_state.driver:
                    with st.spinner(f"Searching for '{movie_title}'..."):
                        with capture_output() as (stdout, stderr):
                            try:
                                st.session_state.search_results = search_movie_by_title(movie_title, st.session_state.driver)
                            except Exception as e:
                                st.error(f"Error searching for movie: {str(e)}")
                        st.session_state.loading = False
            else:
                st.warning("Please enter a movie title")


# Display search results and let user select a movie
    if st.session_state.search_results and not st.session_state.loading:
        st.header("Search Results")
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Display movies as compact cards with smaller images
            # Use 3 cards per row
            movies_per_row = 3
            rows = [st.session_state.search_results[i:i+movies_per_row] 
                    for i in range(0, len(st.session_state.search_results), movies_per_row)]
            
            for row in rows:
                cols = st.columns(movies_per_row)
                
                for i, (col, movie) in enumerate(zip(cols, row)):
                    idx = rows.index(row) * movies_per_row + i  # Calculate global index
                    
                    with col:
                        # Display movie poster if available
                        if movie.get('image_url'):
                            st.image(movie['image_url'], width=80)
                        else:
                            # Display placeholder if no image available
                            st.markdown("📽️")
                        
                        # Add title with smaller font
                        st.markdown(f"**{movie['title']}** ({movie['year']})")
                        
                        # Streamlined ID display
                        st.caption(f"ID: {movie['imdb_id']}")
                        
                        # More compact button
                        if st.button(f"Select", key=f"select_{idx}", use_container_width=True):
                            st.session_state.selected_movie = movie
                            st.session_state.selected_index = idx
                            # Force rerun to trigger the automatic scraping
                            st.rerun()
        
        with col2:
            st.subheader("Selected Movie")
            
            # Check if selected_movie exists and is not None
            if hasattr(st.session_state, 'selected_movie') and st.session_state.selected_movie is not None:
                selected_movie = st.session_state.selected_movie
                
                # Display selected movie poster
                if selected_movie.get('image_url'):
                    st.image(selected_movie['image_url'], width=150)
                
                st.markdown(f"**{selected_movie['title']}** ({selected_movie['year']})")
                st.text(f"IMDb ID: {selected_movie['imdb_id']}")
                
                # Automatic scraping when movie is selected (happens only once per selection)
                if not hasattr(st.session_state, 'last_scraped_id') or st.session_state.last_scraped_id != selected_movie['imdb_id']:
                    st.session_state.last_scraped_id = selected_movie['imdb_id']
                    st.session_state.loading = True
                    
                    # Scrape reviews for selected movie
                    with st.spinner(f"Scraping reviews for '{selected_movie['title']}'..."):
                        try:
                            with capture_output() as (stdout, stderr):
                                imdb_id = selected_movie['imdb_id']
                                st.session_state.reviews_data = scrape_all_reviews(
                                    imdb_id, 
                                    st.session_state.driver, 
                                    max_pages
                                )
                            
                            # Save to file
                            os.makedirs("reviews", exist_ok=True)
                            sanitized_title = re.sub(r'[\\/*?:"<>|]', "", 
                                                selected_movie['title'].replace(' ', '_'))
                            filename = f"reviews/reviews_{imdb_id}_{sanitized_title}.json"
                            with open(filename, 'w', encoding='utf-8') as json_file:
                                json.dump(st.session_state.reviews_data, json_file, ensure_ascii=False, indent=4)
                            
                            # Notify user that scraping is complete
                            st.success(f"Scraped {len(st.session_state.reviews_data['reviews'])} reviews!")
                        
                        except Exception as e:
                            st.error(f"Error scraping reviews: {str(e)}")
                        
                        st.session_state.loading = False
            else:
                st.markdown("*Please select a movie from the list*")

elif page == "Analisis Movie":
    st.title("Analisis Movie Reviews")
# Display and analyze reviews if available
    if st.session_state.reviews_data and not st.session_state.loading:
        reviews = st.session_state.reviews_data['reviews']
        movie_info = st.session_state.selected_movie
        
        st.header(f"Reviews Analysis: {movie_info['title']} ({movie_info['year']})")
        st.subheader(f"Found {len(reviews)} reviews")
        
        # Create dataframe from reviews
        review_data = []
        for review in reviews:
            review_data.append({
                'short_review': review.get('short_review', 'No title'),
                'full_review': review.get('full_review', 'No content'),
                'rating': review.get('rating_value', 'Unknown'),
                'reviewer': review.get('reviewer_name', 'Anonymous'),
                'date': review.get('review_date', 'Unknown date'),
                'sentiment': categorize_sentiment(review.get('rating_value'))
            })
        
        df_reviews = pd.DataFrame(review_data)
        
        # Analytics tabs
        tab1, tab2, tab3, tab4, tab5= st.tabs(["Overview", "Review Text Analysis", "Sentiment Analysis", "Reasoning Review","Raw Data"])
        
        with tab1:
            # Overview stats
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Rating distribution
                ratings = df_reviews['rating'].dropna()
                if len(ratings) > 0:
                    try:
                        ratings = ratings.astype(float)
                        avg_rating = ratings.mean()
                        st.metric("Average Rating", f"{avg_rating:.1f}/10")
                        
                        # Rating distribution chart
                        fig_rating = px.histogram(
                            df_reviews, 
                            x='rating',
                            nbins=10,
                            title="Rating Distribution",
                            color_discrete_sequence=['#F5C518']
                        )
                        fig_rating.update_layout(
                            xaxis=dict(
                                range=[1, 10], 
                                tickvals=list(range(1, 11)),
                                tickmode='array',  # Ensures exact tick placement
                                tickformat='.0f'   # Forces integer display
                            )
                        )

                        st.plotly_chart(fig_rating, use_container_width=True)
                    except:
                        st.warning("Could not analyze ratings (possible format issues)")
                else:
                    st.warning("No rating data available")
            
            with col2:
                # Sentiment distribution
                sentiment_counts = df_reviews['sentiment'].value_counts()
                fig_sentiment = px.pie(
                    names=sentiment_counts.index,
                    values=sentiment_counts.values,
                    title="Review Sentiment Distribution",
                    color=sentiment_counts.index,
                    color_discrete_map={
                        'Positive': '#4CAF50',
                        'Negative': '#F44336',
                    }
                )
                fig_sentiment.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_sentiment, use_container_width=True)
            
            with col3:
                # Review date trend if available
                if 'date' in df_reviews.columns:
                    # Try to convert date strings to datetime
                    try:
                        # Extract year from date strings using regex
                        df_reviews['year'] = df_reviews['date'].str.extract(r'(\d{4})')
                        year_counts = df_reviews['year'].value_counts().sort_index()
                        
                        if not year_counts.empty:
                            fig_trend = px.bar(
                                x=year_counts.index,
                                y=year_counts.values,
                                title="Reviews by Year",
                                labels={'x': 'Year', 'y': 'Number of Reviews'},
                                color_discrete_sequence=['#1f77b4']
                            )
                            st.plotly_chart(fig_trend, use_container_width=True)
                    except:
                        st.warning("Could not analyze review dates")
            
            # Sample reviews
            st.subheader("Sample Reviews")
            
            # Sort by rating if available
            if 'rating' in df_reviews.columns:
                try:
                    df_sorted = df_reviews.copy()
                    df_sorted['rating_numeric'] = pd.to_numeric(df_sorted['rating'], errors='coerce')
                    df_sorted = df_sorted.sort_values('rating_numeric', ascending=False)
                    sample_reviews = df_sorted.head(5).to_dict('records')
                except:
                    sample_reviews = df_reviews.head(5).to_dict('records')
            else:
                sample_reviews = df_reviews.head(5).to_dict('records')
            
            # Display sample reviews
            for i, review in enumerate(sample_reviews):
                with st.container():
                    st.markdown(f"""
                    <div class="review-card">
                        <div class="review-title">{review['short_review']}</div>
                        <div class="review-rating">Rating: {review['rating']}/10</div>
                        <div class="review-text">{review['full_review'][:300]}{'...' if len(review['full_review']) > 300 else ''}</div>
                        <div class="review-author">By: {review['reviewer']}</div>
                        <div class="review-date">{review['date']}</div>
                    </div>
                    """, unsafe_allow_html=True)
        
        with tab2:
            # Text analysis
            st.subheader("Word Cloud from Reviews")
            
            # Combine all review text for word cloud
            all_review_text = " ".join([clean_text(review['full_review']) for review in review_data if review['full_review']])
            
            if all_review_text.strip():
                wordcloud_fig = generate_wordcloud(all_review_text)
                st.pyplot(wordcloud_fig)
            else:
                st.warning("No text available for word cloud generation")
            
            # Common phrases
            st.subheader("Most Common Phrases")
            
            common_phrases = extract_common_phrases(reviews)
            if common_phrases:
                phrases_df = pd.DataFrame(common_phrases, columns=['Phrase', 'Count'])
                
                fig_phrases = px.bar(
                    phrases_df.head(10),
                    x='Count',
                    y='Phrase',
                    orientation='h',
                    title="Most Common Phrases in Reviews",
                    color='Count',
                    color_continuous_scale='Viridis'
                )
                fig_phrases.update_layout(yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig_phrases, use_container_width=True)
            else:
                st.warning("No common phrases found")
        
        with tab3:
            # Sentiment analysis
            st.subheader("Sentiment Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Sentiment distribution
                sentiment_counts = df_reviews['sentiment'].value_counts()
                
                fig_sent_bar = px.bar(
                    x=sentiment_counts.index,
                    y=sentiment_counts.values,
                    title="Sentiment Distribution",
                    labels={'x': 'Sentiment', 'y': 'Count'},
                    color=sentiment_counts.index,
                    color_discrete_map={
                        'Positive': '#4CAF50',
                        'Negative': '#F44336',
                    }
                )
                st.plotly_chart(fig_sent_bar, use_container_width=True)
            
            with col2:
                # Average rating by sentiment
                try:
                    df_reviews['rating_numeric'] = pd.to_numeric(df_reviews['rating'], errors='coerce')
                    avg_by_sentiment = df_reviews.groupby('sentiment')['rating_numeric'].mean().reset_index()
                    
                    fig_avg_sent = px.bar(
                        avg_by_sentiment,
                        x='sentiment',
                        y='rating_numeric',
                        title="Average Rating by Sentiment",
                        labels={'rating_numeric': 'Average Rating', 'sentiment': 'Sentiment'},
                        color='sentiment',
                        color_discrete_map={
                            'Positive': '#4CAF50',
                            'Negative': '#F44336',
                        }
                    )
                    st.plotly_chart(fig_avg_sent, use_container_width=True)
                except:
                    st.warning("Could not analyze ratings by sentiment")
            
            # Reviews by sentiment
            st.subheader("Sample Reviews by Sentiment")
            
            # Create sentiment filter
            selected_sentiment = st.selectbox(
                "Filter by sentiment:",
                options=['All'] + list(df_reviews['sentiment'].unique())
            )
            
            if selected_sentiment != 'All':
                filtered_reviews = df_reviews[df_reviews['sentiment'] == selected_sentiment]
            else:
                filtered_reviews = df_reviews
            
            # Display filtered reviews
            for i, review in enumerate(filtered_reviews.head(3).to_dict('records')):
                with st.container():
                    st.markdown(f"""
                    <div class="review-card">
                        <div class="review-title">{review['short_review']}</div>
                        <div class="review-rating">Rating: {review['rating']}/10 ({review['sentiment']})</div>
                        <div class="review-text">{review['full_review'][:300]}{'...' if len(review['full_review']) > 300 else ''}</div>
                        <div class="review-author">By: {review['reviewer']}</div>
                    </div>
                    """, unsafe_allow_html=True)
        
        
        with tab4:
            st.subheader("Reasoning Summaries Review")
            
            # Create review data for analysis
            reviews_text = [review.get('full_review', '') for review in reviews]
            ratings = [review.get('rating_value', 0) for review in reviews]
            
            # Prepare data for AI summary
            analysis_data = {
                'total': len(reviews),
                'positive': len([r for r in df_reviews['sentiment'] if r == 'Positive']),
                'negative': len([r for r in df_reviews['sentiment'] if r == 'Negative']),
                'positive_pct': f"{len([r for r in df_reviews['sentiment'] if r == 'Positive'])/len(reviews)*100:.1f}",
                'negative_pct': f"{len([r for r in df_reviews['sentiment'] if r == 'Negative'])/len(reviews)*100:.1f}",
                'pos_common': extract_common_phrases([r for r, s in zip(reviews, df_reviews['sentiment']) if s == 'Positive']),
                'neg_common': extract_common_phrases([r for r, s in zip(reviews, df_reviews['sentiment']) if s == 'Negative']),
                'pos_terms': "Terms extracted from positive reviews",
                'neg_terms': "Terms extracted from negative reviews",
                'pos_avg_len': f"{df_reviews[df_reviews['sentiment'] == 'Positive']['full_review'].str.len().mean():.1f}",
                'neg_avg_len': f"{df_reviews[df_reviews['sentiment'] == 'Negative']['full_review'].str.len().mean():.1f}"
            }
            
            # Create tabs for different summaries
            summary_tab1, summary_tab2, summary_tab3 = st.tabs(["Overall Analysis", "Negative Reviews", "Positive Reviews"])
            
            with summary_tab1:
                with st.spinner("Generating overall summary..."):
                    positive_summary = generate_ai_summary_for_category(GLOBAL_API_KEY, analysis_data, "overall")
                    st.subheader("Overall Analysis")
                    st.write(positive_summary)
            
            with summary_tab2:
                with st.spinner("Generating positive reviews summary..."):
                    negative_summary = generate_ai_summary_for_category(GLOBAL_API_KEY,analysis_data, "positive")
                    st.subheader("Positive Reviews Summary")
                    st.write(negative_summary)
            
            with summary_tab3:
                with st.spinner("Generating negative reviews summary..."):
                    overall_summary = generate_ai_summary_for_category(GLOBAL_API_KEY, analysis_data, "negative")
                    st.subheader("Negative Reviews Summary")
                    st.write(overall_summary)
            
            # Display a note about OpenAI API usage
            st.info("Note: These summaries are generated using OpenAI's API. Make sure you have set your API key in the environment variables for this feature to work properly.")


        with tab5:
            # Raw data display
            st.subheader("Raw Review Data")
            st.dataframe(df_reviews, use_container_width=True)
            
            # Download button
            @st.cache_data
            def convert_df_to_csv(df):
                return df.to_csv(index=False).encode('utf-8')
            
            csv = convert_df_to_csv(df_reviews)
            st.download_button(
                "Download Data as CSV",
                csv,
                f"{movie_info['title']}_{movie_info['imdb_id']}_reviews.csv",
                "text/csv",
                key='download-csv'
            )


# Footer
st.markdown("""
---
<div style='text-align: center'>
    <p>IMDb Review Scraper Dashboard | Built with Streamlit</p>
    <p style='font-size: 12px; color: #888;'>
        This dashboard scrapes data from IMDb for analysis purposes. Please respect IMDb's terms of service.
    </p>
</div>
""", unsafe_allow_html=True)


# import streamlit as st
# import pandas as pd
# import json
# import os
# import plotly.express as px
# import sys
# from preposesing import generate_ai_summary_for_category
# import pandas as pd
# import re
# from io import StringIO
# import contextlib
# from Crawling import (
#     initialize_driver, search_movie_by_title, scrape_all_reviews,get_movie_reviews_by_title)

# from preposesing import (
#     clean_text, generate_wordcloud, categorize_sentiment, extract_common_phrases)

# # Display and analyze reviews if available
# if st.session_state.reviews_data and not st.session_state.loading:
#     reviews = st.session_state.reviews_data['reviews']
#     movie_info = st.session_state.selected_movie
    
#     st.header(f"Reviews Analysis: {movie_info['title']} ({movie_info['year']})")
#     st.subheader(f"Found {len(reviews)} reviews")
    
#     # Create dataframe from reviews
#     review_data = []
#     for review in reviews:
#         review_data.append({
#             'short_review': review.get('short_review', 'No title'),
#             'full_review': review.get('full_review', 'No content'),
#             'rating': review.get('rating_value', 'Unknown'),
#             'reviewer': review.get('reviewer_name', 'Anonymous'),
#             'date': review.get('review_date', 'Unknown date'),
#             'sentiment': categorize_sentiment(review.get('rating_value'))
#         })
    
#     df_reviews = pd.DataFrame(review_data)
    
#     # Analytics tabs
#     tab1, tab2, tab3, tab4, tab5= st.tabs(["Overview", "Review Text Analysis", "Sentiment Analysis", "Reasoning Review","Raw Data"])
    
#     with tab1:
#         # Overview stats
#         col1, col2, col3 = st.columns(3)
        
#         with col1:
#             # Rating distribution
#             ratings = df_reviews['rating'].dropna()
#             if len(ratings) > 0:
#                 try:
#                     ratings = ratings.astype(float)
#                     avg_rating = ratings.mean()
#                     st.metric("Average Rating", f"{avg_rating:.1f}/10")
                    
#                     # Rating distribution chart
#                     fig_rating = px.histogram(
#                         df_reviews, 
#                         x='rating',
#                         nbins=10,
#                         title="Rating Distribution",
#                         color_discrete_sequence=['#F5C518']
#                     )
#                     fig_rating.update_layout(
#                         xaxis=dict(
#                             range=[1, 10], 
#                             tickvals=list(range(1, 11)),
#                             tickmode='array',  # Ensures exact tick placement
#                             tickformat='.0f'   # Forces integer display
#                         )
#                     )

#                     st.plotly_chart(fig_rating, use_container_width=True)
#                 except:
#                     st.warning("Could not analyze ratings (possible format issues)")
#             else:
#                 st.warning("No rating data available")
        
#         with col2:
#             # Sentiment distribution
#             sentiment_counts = df_reviews['sentiment'].value_counts()
#             fig_sentiment = px.pie(
#                 names=sentiment_counts.index,
#                 values=sentiment_counts.values,
#                 title="Review Sentiment Distribution",
#                 color=sentiment_counts.index,
#                 color_discrete_map={
#                     'Positive': '#4CAF50',
#                     'Neutral': '#FFC107',
#                     'Negative': '#F44336',
#                 }
#             )
#             fig_sentiment.update_traces(textposition='inside', textinfo='percent+label')
#             st.plotly_chart(fig_sentiment, use_container_width=True)
        
#         with col3:
#             # Review date trend if available
#             if 'date' in df_reviews.columns:
#                 # Try to convert date strings to datetime
#                 try:
#                     # Extract year from date strings using regex
#                     df_reviews['year'] = df_reviews['date'].str.extract(r'(\d{4})')
#                     year_counts = df_reviews['year'].value_counts().sort_index()
                    
#                     if not year_counts.empty:
#                         fig_trend = px.bar(
#                             x=year_counts.index,
#                             y=year_counts.values,
#                             title="Reviews by Year",
#                             labels={'x': 'Year', 'y': 'Number of Reviews'},
#                             color_discrete_sequence=['#1f77b4']
#                         )
#                         st.plotly_chart(fig_trend, use_container_width=True)
#                 except:
#                     st.warning("Could not analyze review dates")
        
#         # Sample reviews
#         st.subheader("Sample Reviews")
        
#         # Sort by rating if available
#         if 'rating' in df_reviews.columns:
#             try:
#                 df_sorted = df_reviews.copy()
#                 df_sorted['rating_numeric'] = pd.to_numeric(df_sorted['rating'], errors='coerce')
#                 df_sorted = df_sorted.sort_values('rating_numeric', ascending=False)
#                 sample_reviews = df_sorted.head(5).to_dict('records')
#             except:
#                 sample_reviews = df_reviews.head(5).to_dict('records')
#         else:
#             sample_reviews = df_reviews.head(5).to_dict('records')
        
#         # Display sample reviews
#         for i, review in enumerate(sample_reviews):
#             with st.container():
#                 st.markdown(f"""
#                 <div class="review-card">
#                     <div class="review-title">{review['short_review']}</div>
#                     <div class="review-rating">Rating: {review['rating']}/10</div>
#                     <div class="review-text">{review['full_review'][:300]}{'...' if len(review['full_review']) > 300 else ''}</div>
#                     <div class="review-author">By: {review['reviewer']}</div>
#                     <div class="review-date">{review['date']}</div>
#                 </div>
#                 """, unsafe_allow_html=True)
    
#     with tab2:
#         # Text analysis
#         st.subheader("Word Cloud from Reviews")
        
#         # Combine all review text for word cloud
#         all_review_text = " ".join([clean_text(review['full_review']) for review in review_data if review['full_review']])
        
#         if all_review_text.strip():
#             wordcloud_fig = generate_wordcloud(all_review_text)
#             st.pyplot(wordcloud_fig)
#         else:
#             st.warning("No text available for word cloud generation")
        
#         # Common phrases
#         st.subheader("Most Common Phrases")
        
#         common_phrases = extract_common_phrases(reviews)
#         if common_phrases:
#             phrases_df = pd.DataFrame(common_phrases, columns=['Phrase', 'Count'])
            
#             fig_phrases = px.bar(
#                 phrases_df.head(10),
#                 x='Count',
#                 y='Phrase',
#                 orientation='h',
#                 title="Most Common Phrases in Reviews",
#                 color='Count',
#                 color_continuous_scale='Viridis'
#             )
#             fig_phrases.update_layout(yaxis={'categoryorder':'total ascending'})
#             st.plotly_chart(fig_phrases, use_container_width=True)
#         else:
#             st.warning("No common phrases found")
    
#     with tab3:
#         # Sentiment analysis
#         st.subheader("Sentiment Analysis")
        
#         col1, col2 = st.columns(2)
        
#         with col1:
#             # Sentiment distribution
#             sentiment_counts = df_reviews['sentiment'].value_counts()
            
#             fig_sent_bar = px.bar(
#                 x=sentiment_counts.index,
#                 y=sentiment_counts.values,
#                 title="Sentiment Distribution",
#                 labels={'x': 'Sentiment', 'y': 'Count'},
#                 color=sentiment_counts.index,
#                 color_discrete_map={
#                     'Positive': '#4CAF50',
#                     'Neutral': '#FFC107',
#                     'Negative': '#F44336',
#                 }
#             )
#             st.plotly_chart(fig_sent_bar, use_container_width=True)
        
#         with col2:
#             # Average rating by sentiment
#             try:
#                 df_reviews['rating_numeric'] = pd.to_numeric(df_reviews['rating'], errors='coerce')
#                 avg_by_sentiment = df_reviews.groupby('sentiment')['rating_numeric'].mean().reset_index()
                
#                 fig_avg_sent = px.bar(
#                     avg_by_sentiment,
#                     x='sentiment',
#                     y='rating_numeric',
#                     title="Average Rating by Sentiment",
#                     labels={'rating_numeric': 'Average Rating', 'sentiment': 'Sentiment'},
#                     color='sentiment',
#                     color_discrete_map={
#                         'Positive': '#4CAF50',
#                         'Neutral': '#FFC107',
#                         'Negative': '#F44336',
#                     }
#                 )
#                 st.plotly_chart(fig_avg_sent, use_container_width=True)
#             except:
#                 st.warning("Could not analyze ratings by sentiment")
        
#         # Reviews by sentiment
#         st.subheader("Sample Reviews by Sentiment")
        
#         # Create sentiment filter
#         selected_sentiment = st.selectbox(
#             "Filter by sentiment:",
#             options=['All'] + list(df_reviews['sentiment'].unique())
#         )
        
#         if selected_sentiment != 'All':
#             filtered_reviews = df_reviews[df_reviews['sentiment'] == selected_sentiment]
#         else:
#             filtered_reviews = df_reviews
        
#         # Display filtered reviews
#         for i, review in enumerate(filtered_reviews.head(3).to_dict('records')):
#             with st.container():
#                 st.markdown(f"""
#                 <div class="review-card">
#                     <div class="review-title">{review['short_review']}</div>
#                     <div class="review-rating">Rating: {review['rating']}/10 ({review['sentiment']})</div>
#                     <div class="review-text">{review['full_review'][:300]}{'...' if len(review['full_review']) > 300 else ''}</div>
#                     <div class="review-author">By: {review['reviewer']}</div>
#                 </div>
#                 """, unsafe_allow_html=True)
    
    
#     with tab4:
#         st.subheader("Reasoning Summaries Review")
        
#         # Create review data for analysis
#         reviews_text = [review.get('full_review', '') for review in reviews]
#         ratings = [review.get('rating_value', 0) for review in reviews]
        
#         # Prepare data for AI summary
#         analysis_data = {
#             'total': len(reviews),
#             'positive': len([r for r in df_reviews['sentiment'] if r == 'Positive']),
#             'negative': len([r for r in df_reviews['sentiment'] if r == 'Negative']),
#             'positive_pct': f"{len([r for r in df_reviews['sentiment'] if r == 'Positive'])/len(reviews)*100:.1f}",
#             'negative_pct': f"{len([r for r in df_reviews['sentiment'] if r == 'Negative'])/len(reviews)*100:.1f}",
#             'pos_common': extract_common_phrases([r for r, s in zip(reviews, df_reviews['sentiment']) if s == 'Positive']),
#             'neg_common': extract_common_phrases([r for r, s in zip(reviews, df_reviews['sentiment']) if s == 'Negative']),
#             'pos_terms': "Terms extracted from positive reviews",
#             'neg_terms': "Terms extracted from negative reviews",
#             'pos_avg_len': f"{df_reviews[df_reviews['sentiment'] == 'Positive']['full_review'].str.len().mean():.1f}",
#             'neg_avg_len': f"{df_reviews[df_reviews['sentiment'] == 'Negative']['full_review'].str.len().mean():.1f}"
#         }
        
#         # Create tabs for different summaries
#         summary_tab1, summary_tab2, summary_tab3 = st.tabs(["Overall Analysis", "Negative Reviews", "Positive Reviews"])
        
#         with summary_tab1:
#             with st.spinner("Generating overall summary..."):
#                 positive_summary = generate_ai_summary_for_category(analysis_data, "overall")
#                 st.subheader("Overall Analysis")
#                 st.write(positive_summary)
        
#         with summary_tab2:
#             with st.spinner("Generating positive reviews summary..."):
#                 negative_summary = generate_ai_summary_for_category(analysis_data, "positive")
#                 st.subheader("Positive Reviews Summary")
#                 st.write(negative_summary)
        
#         with summary_tab3:
#             with st.spinner("Generating negative reviews summary..."):
#                 overall_summary = generate_ai_summary_for_category(analysis_data, "negative")
#                 st.subheader("Negative Reviews Summary")
#                 st.write(overall_summary)
        
#         # Display a note about OpenAI API usage
#         st.info("Note: These summaries are generated using OpenAI's API. Make sure you have set your API key in the environment variables for this feature to work properly.")


#     with tab5:
#         # Raw data display
#         st.subheader("Raw Review Data")
#         st.dataframe(df_reviews, use_container_width=True)
        
#         # Download button
#         @st.cache_data
#         def convert_df_to_csv(df):
#             return df.to_csv(index=False).encode('utf-8')
        
#         csv = convert_df_to_csv(df_reviews)
#         st.download_button(
#             "Download Data as CSV",
#             csv,
#             f"{movie_info['title']}_{movie_info['imdb_id']}_reviews.csv",
#             "text/csv",
#             key='download-csv'
#         )
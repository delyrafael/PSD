import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from collections import Counter
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import re
import openai

import os
from dotenv import load_dotenv
# Function to clean text for analysis

import re
from collections import Counter
import matplotlib.pyplot as plt
from wordcloud import WordCloud


def clean_text(text):
    if not text:
        return ""
    # Remove HTML tags
    text = re.sub(r'<.*?>', '', text)
    # Remove special characters and numbers
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    # Convert to lowercase and remove extra whitespace
    text = text.lower().strip()
    return text

# Function to generate word cloud from text
def generate_wordcloud(text,title= None):
    wordcloud = WordCloud(
        width=800, 
        height=400, 
        background_color='white',
        colormap='viridis',
        max_words=100,
        contour_width=3,
        contour_color='steelblue'
    ).generate(text)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    return fig



# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Download necessary NLTK resources
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)

# Function to extract sentiments based on ratings
def categorize_sentiment(rating):
    if not rating:
        return "Negative"
    try:
        rating_value = float(rating)
        if rating_value >= 5:
            return "Positive"


        else:
            return "Negative"
    except:
        return "Negative"

# Function to analyze common phrases
def extract_common_phrases(reviews, min_phrase_length=3, max_phrase_length=5):
    all_text = " ".join([clean_text(review.get('full_review', '')) for review in reviews])
    words = all_text.split()
    phrases = []

    for i in range(len(words) - min_phrase_length + 1):
        for j in range(min_phrase_length, min(max_phrase_length + 1, len(words) - i + 1)):
            phrase = " ".join(words[i:i+j])
            if len(phrase) > 10:  # Minimum characters for a meaningful phrase
                phrases.append(phrase)

    # Count frequencies and get top phrases
    phrase_counter = Counter(phrases)
    return phrase_counter.most_common(15)

def clean_text(text):
    """Clean text by removing HTML tags, special characters, and converting to lowercase"""
    # Ensure input is always treated as string
    text = str(text)

    # Remove HTML tags
    text = re.sub(r'<.*?>', ' ', text)
    # Remove special characters and digits
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    # Convert to lowercase
    text = text.lower()
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def get_most_common_words(text_series, top_n=10):
    """Extract most common words from a series of texts"""
    # Clean and tokenize all texts
    all_words = []
    stop_words = set(stopwords.words('english'))

    for text in text_series:
        cleaned_text = clean_text(text)
        tokens = word_tokenize(cleaned_text)
        words = [word for word in tokens if word.isalpha() and word not in stop_words]
        all_words.extend(words)

    # Get most common words
    word_counts = Counter(all_words)
    return word_counts.most_common(top_n)

def extract_top_tfidf_terms(text_series, top_n=10):
    """Extract most important terms using TF-IDF"""
    # Clean texts
    cleaned_texts = [clean_text(text) for text in text_series]

    # Create TF-IDF vectorizer
    tfidf_vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
    tfidf_matrix = tfidf_vectorizer.fit_transform(cleaned_texts)

    # Get feature names
    feature_names = tfidf_vectorizer.get_feature_names_out()

    # Calculate average TF-IDF score for each term
    avg_tfidf = np.mean(tfidf_matrix.toarray(), axis=0)

    # Get top terms
    top_indices = avg_tfidf.argsort()[-top_n:][::-1]
    top_terms = [(feature_names[idx], avg_tfidf[idx]) for idx in top_indices]

    return top_terms

def generate_ai_summary_for_category( analysis_data, category):
    """Generate an AI summary using OpenAI API based on the analysis data for a specific category"""
    try:
        # Set up OpenAI API client
        openai.api_key = os.getenv("OPENAI_API_KEY")
        # openai.api_key = api_key

        # Create different prompts based on the category
        if category == "positive":
            prompt = f"""
            Based on the following analysis of POSITIVE customer reviews, generate a concise summary paragraph
            highlighting the key findings, patterns, and insights:

            Total Positive Reviews: {analysis_data['positive']} ({analysis_data['positive_pct']}%)
            
            Top terms in positive reviews (TF-IDF):
            {analysis_data['pos_terms']}

            Most common words in positive reviews:
            {analysis_data['pos_common']}
            
            Average length of positive reviews: {analysis_data['pos_avg_len']} characters
            
            Focus on what customers liked, product strengths, and positive aspects of the customer experience.
            """
            system_prompt = "You are an expert data analyst. Summarize the positive review findings into a concise, insight-driven paragraph that highlights patterns and key strengths mentioned in positive reviews."

        elif category == "negative":
            prompt = f"""
            Based on the following analysis of NEGATIVE customer reviews, generate a concise summary paragraph
            highlighting the key findings, patterns, and insights:

            Total Negative Reviews: {analysis_data['negative']} ({analysis_data['negative_pct']}%)
            
            Top terms in negative reviews (TF-IDF):
            {analysis_data['neg_terms']}

            Most common words in negative reviews:
            {analysis_data['neg_common']}
            
            Average length of negative reviews: {analysis_data['neg_avg_len']} characters
            
            Focus on pain points, areas for improvement, and critical issues mentioned by customers.
            """
            system_prompt = "You are an expert data analyst. Summarize the negative review findings into a concise, insight-driven paragraph that highlights patterns, pain points, and key issues mentioned in negative reviews."

        else:  # overall
            prompt = f"""
            Based on the following sentiment analysis of customer reviews, generate a concise summary paragraph
            highlighting the key findings, actionable insights, and overall conclusions:

            Total Reviews: {analysis_data['total']}
            Positive Reviews: {analysis_data['positive']} ({analysis_data['positive_pct']}%)
            Negative Reviews: {analysis_data['negative']} ({analysis_data['negative_pct']}%)

            Top terms in positive reviews (TF-IDF):
            {analysis_data['pos_terms']}

            Top terms in negative reviews (TF-IDF):
            {analysis_data['neg_terms']}

            Most common words in positive reviews:
            {analysis_data['pos_common']}

            Most common words in negative reviews:
            {analysis_data['neg_common']}
            
            Average length of positive reviews: {analysis_data['pos_avg_len']} characters
            Average length of negative reviews: {analysis_data['neg_avg_len']} characters
            
            Compare positive and negative review patterns and provide actionable recommendations.
            """
            system_prompt = "You are an expert data analyst. Summarize the overall sentiment analysis findings into a concise, insight-driven paragraph that highlights patterns, key differences between positive and negative reviews, and provides actionable recommendations based on the data."

        # Call OpenAI API
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            max_tokens=350,
            temperature=0.7
        )

        # Return the generated summary
        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"Error generating AI summary for {category}: {e}")
        return f"Failed to generate {category} AI summary. Please check your OpenAI API key and connection."

import streamlit as st
import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
import re
from openai import OpenAI
from dotenv import load_dotenv
import time

# Load environment variables (non-Streamlit operation)
load_dotenv()

# Initialize OpenAI client (non-Streamlit operation)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyze_sentiment(text):
    prompt = f"""
    Your role: As a sentiment analysis assistant that helps labeling message.
    Task: Answer with only one of the sentiment labels in the list (["negative", "positive"]) for the given message.
    STRICT RESTRICTION: You must answer only with either "positive" or "negative". 
    If uncertain, choose the most likely label based on the overall tone.
    Message: {text}
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a strict sentiment classifier that only outputs 'positive' or 'negative'."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.0
    )
    
    # Extract and strictly validate the sentiment
    sentiment = response.choices[0].message.content.strip().lower()
    
    # Force binary classification
    if "positive" in sentiment:
        return "positive"
    elif "negative" in sentiment:
        return "negative"
    
    # Final fallback to positive for any ambiguous cases
    return "positive"

def clean_text(text):
    """Clean text by removing HTML tags, special characters, and converting to lowercase"""
    if not isinstance(text, str):
        return ""
    text = re.sub(r'<.*?>', ' ', text)
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    text = text.lower()
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def generate_wordcloud(text_series, title):
    """Generate a word cloud from a series of texts"""
    text = ' '.join(text_series)
    text = clean_text(text)
    stop_words = set(stopwords.words('english'))
    
    wordcloud = WordCloud(width=800, height=400, 
                         background_color='white',
                         stopwords=stop_words,
                         max_words=100).generate(text)
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis("off")
    ax.set_title(title)
    plt.tight_layout(pad=0)
    return fig

def get_most_common_words(text_series, top_n=10):
    """Extract most common words from a series of texts"""
    all_words = []
    stop_words = set(stopwords.words('english'))
    
    for text in text_series:
        if not isinstance(text, str):
            continue
        cleaned_text = clean_text(text)
        tokens = word_tokenize(cleaned_text)
        words = [word for word in tokens if word.isalpha() and word not in stop_words]
        all_words.extend(words)
    
    word_counts = Counter(all_words)
    return word_counts.most_common(top_n)

def extract_top_tfidf_terms(text_series, top_n=10):
    """Extract most important terms using TF-IDF"""
    cleaned_texts = [clean_text(text) if isinstance(text, str) else "" for text in text_series]
    
    tfidf_vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
    
    if all(not text for text in cleaned_texts):
        return [("No valid text", 0.0)]
    
    tfidf_matrix = tfidf_vectorizer.fit_transform(cleaned_texts)
    feature_names = tfidf_vectorizer.get_feature_names_out()
    avg_tfidf = np.mean(tfidf_matrix.toarray(), axis=0)
    
    top_indices = avg_tfidf.argsort()[-top_n:][::-1]
    top_terms = [(feature_names[idx], avg_tfidf[idx]) for idx in top_indices]
    return top_terms

def generate_ai_summary_for_category(analysis_data, category):
    """Generate an AI summary using OpenAI API based on the analysis data"""
    try:
        if category == "positive":
            prompt = f"""
            Based on the following analysis of POSITIVE customer reviews, generate a concise summary paragraph
            highlighting the key findings:
            Total Positive Reviews: {analysis_data['positive']} ({analysis_data['positive_pct']}%)
            Top terms: {analysis_data['pos_terms']}
            Most common words: {analysis_data['pos_common']}
            Average length: {analysis_data['pos_avg_len']} characters
            """
            system_prompt = "Summarize positive review findings."
        
        elif category == "negative":
            prompt = f"""
            Based on the following analysis of NEGATIVE customer reviews, generate a concise summary paragraph
            highlighting the key findings:
            Total Negative Reviews: {analysis_data['negative']} ({analysis_data['negative_pct']}%)
            Top terms: {analysis_data['neg_terms']}
            Most common words: {analysis_data['neg_common']}
            Average length: {analysis_data['neg_avg_len']} characters
            """
            system_prompt = "Summarize negative review findings."
        
        else:
            prompt = f"""
            Based on sentiment analysis of customer reviews, generate a concise summary paragraph:
            Total Reviews: {analysis_data['total']}
            Positive: {analysis_data['positive']} ({analysis_data['positive_pct']}%)
            Negative: {analysis_data['negative']} ({analysis_data['negative_pct']}%)
            Positive terms: {analysis_data['pos_terms']}
            Negative terms: {analysis_data['neg_terms']}
            """
            system_prompt = "Summarize overall findings."
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            max_tokens=350,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        return f"Error generating summary: {str(e)}"

def generate_rag_summary(df):
    """Generate summary analysis for the dataframe"""
    if 'sentiment' not in df.columns:
        st.error("Error: 'sentiment' column not found.")
        return
    
    text_col = [col for col in df.columns if col != 'sentiment'][0]
    positive_df = df[df['sentiment'] == 'positive']
    negative_df = df[df['sentiment'] == 'negative']
    
    st.subheader("📊 Sentiment Analysis Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total reviews", len(df))
    col2.metric("Positive reviews", f"{len(positive_df)} ({len(positive_df)/len(df)*100:.1f}%)")
    col3.metric("Negative reviews", f"{len(negative_df)} ({len(negative_df)/len(df)*100:.1f}%)")
    
    st.subheader("🔤 Word Clouds")
    tab1, tab2, tab3 = st.tabs(["Positive", "Negative", "All"])
    
    with tab1:
        if len(positive_df) > 0:
            st.pyplot(generate_wordcloud(positive_df[text_col], "Positive Reviews"))
    
    with tab2:
        if len(negative_df) > 0:
            st.pyplot(generate_wordcloud(negative_df[text_col], "Negative Reviews"))
    
    with tab3:
        st.pyplot(generate_wordcloud(df[text_col], "All Reviews"))
    
    st.subheader("📝 Most Common Words")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("Positive reviews:")
        if len(positive_df) > 0:
            for word, count in get_most_common_words(positive_df[text_col], 10):
                st.write(f"- {word}: {count}")
    
    with col2:
        st.write("Negative reviews:")
        if len(negative_df) > 0:
            for word, count in get_most_common_words(negative_df[text_col], 10):
                st.write(f"- {word}: {count}")
    
    st.subheader("🤖 AI-Generated Insights")
    if len(df) > 0:
        analysis_data = {
            'total': len(df),
            'positive': len(positive_df),
            'negative': len(negative_df),
            'positive_pct': f"{len(positive_df)/len(df)*100:.1f}",
            'negative_pct': f"{len(negative_df)/len(df)*100:.1f}",
            'pos_terms': ", ".join([f"{term}" for term, _ in extract_top_tfidf_terms(positive_df[text_col], 5)]),
            'neg_terms': ", ".join([f"{term}" for term, _ in extract_top_tfidf_terms(negative_df[text_col], 5)]),
            'pos_common': ", ".join([f"{word}" for word, _ in get_most_common_words(positive_df[text_col], 5)]),
            'neg_common': ", ".join([f"{word}" for word, _ in get_most_common_words(negative_df[text_col], 5)]),
            'pos_avg_len': f"{positive_df[text_col].str.len().mean():.1f}",
            'neg_avg_len': f"{negative_df[text_col].str.len().mean():.1f}"
        }
        
        with st.spinner("Generating insights..."):
            tab1, tab2, tab3 = st.tabs(["Positive", "Negative", "Overall"])
            
            with tab1:
                st.write(generate_ai_summary_for_category(analysis_data, "positive"))
            
            with tab2:
                st.write(generate_ai_summary_for_category(analysis_data, "negative"))
            
            with tab3:
                st.write(generate_ai_summary_for_category(analysis_data, "overall"))

def process_file(uploaded_file):
    """Process uploaded CSV file"""
    df = pd.read_csv(uploaded_file)
    
    tab1, tab2 = st.tabs(["Analysis", "Insights"])
    
    with tab1:
        text_col = st.selectbox("Select text column:", df.columns)
        
        if st.button("Analyze Sentiment"):
            progress_bar = st.progress(0)
            results = []
            
            for i, row in enumerate(df.itertuples()):
                text = getattr(row, text_col)
                results.append(analyze_sentiment(text))
                progress_bar.progress((i+1)/len(df))
                time.sleep(0.1)
            
            df['sentiment'] = results
            st.session_state['sentiment_df'] = df
            st.session_state['text_col'] = text_col
            st.success("Analysis completed!")
            st.dataframe(df.head())
    
    with tab2:
        if 'sentiment_df' in st.session_state:
            generate_rag_summary(st.session_state['sentiment_df'])
        else:
            st.info("Run analysis first")

def main():
    # FIRST Streamlit command ✅
    st.set_page_config(
        page_title="Sentiment Analysis", 
        page_icon="📊", 
        layout="wide"
    )
    
    # Initialize NLTK resources (AFTER set_page_config)
    @st.cache_resource
    def download_nltk_resources():
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
    
    download_nltk_resources()
    
    # Main app
    st.title("Sentiment Analysis App")
    uploaded_file = st.file_uploader("Upload CSV", type="csv")
    
    if uploaded_file:
        process_file(uploaded_file)

if __name__ == "__main__":
    main()
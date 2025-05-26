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
from openai import OpenAI
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
api_key = st.session_state.get("api_key")
    
if not api_key:
    raise ValueError("API Key tidak ditemukan!")
# load_dotenv()
# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
client = OpenAI(api_key=api_key)
# Download necessary NLTK resources
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)

# Function to extract sentiments based on ratings
def categorize_sentiment(rating):
    if not rating:
        return "Unknown"
    try:
        rating_value = float(rating)
        if rating_value >= 8:
            return "Positive"
        elif rating_value >= 5:
            return "Neutral"
        else:
            return "Negative"
    except:
        return "Neutral"

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

# def generate_wordcloud(text_series, title= None):
#     """Generate a word cloud from a series of texts"""
#     # Convert entire series to strings first
#     # text_series = text_series.astype(str)
    
#     # Combine all text
#     text = ' '.join(text_series)
    
#     # Clean the text
#     text = clean_text(text)
    
#     # Get stopwords
#     stop_words = set(stopwords.words('english'))
    
#     # Create and generate word cloud
#     wordcloud = WordCloud(width=800, height=400, 
#                          background_color='white',
#                          stopwords=stop_words,
#                          max_words=100).generate(text)
    
#     # Create plot
#     fig, ax = plt.subplots(figsize=(10, 5))
#     ax.imshow(wordcloud, interpolation='bilinear')
#     ax.axis("off")
#     ax.set_title(title)
#     plt.tight_layout(pad=0)
    
#     return fig

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

def generate_ai_summary_for_category(analysis_data, category):
    """Generate an AI summary using OpenAI API based on the analysis data for a specific category"""
    try:
        # Set up OpenAI API client
        openai.api_key = os.getenv("OPENAI_API_KEY")
        
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

def generate_rag_summary(csv_file):
    """Generate a RAG summary for the sentiment analysis results"""
    print("Loading sentiment analysis results...")
    df = pd.read_csv(csv_file)
    
    # Ensure sentiment column exists
    if 'sentiment' not in df.columns:
        print("Error: 'sentiment' column not found in the CSV file.")
        return
    
    # Ensure review column exists
    if 'review' not in df.columns:
        print("Error: 'review' column not found in the CSV file.")
        return
    
    # Split by sentiment
    positive_df = df[df['sentiment'] == 'positive']
    negative_df = df[df['sentiment'] == 'negative']
    
    # Print basic statistics
    print("\n===== SENTIMENT ANALYSIS SUMMARY =====")
    print(f"Total reviews analyzed: {len(df)}")
    print(f"Positive reviews: {len(positive_df)} ({len(positive_df)/len(df)*100:.1f}%)")
    print(f"Negative reviews: {len(negative_df)} ({len(negative_df)/len(df)*100:.1f}%)")
    
    # Generate word clouds
    print("\nGenerating word clouds...")
    generate_wordcloud(positive_df['review'], "Positive Reviews WordCloud")
    generate_wordcloud(negative_df['review'], "Negative Reviews WordCloud")
    generate_wordcloud(df['review'], "All Reviews WordCloud")
    
    # Extract common words for each category
    print("\n===== MOST COMMON WORDS =====")
    print("\nMost common words in POSITIVE reviews:")
    pos_common = get_most_common_words(positive_df['review'])
    for word, count in pos_common:
        print(f"  - {word}: {count}")
    
    print("\nMost common words in NEGATIVE reviews:")
    neg_common = get_most_common_words(negative_df['review'])
    for word, count in neg_common:
        print(f"  - {word}: {count}")
    
    # Extract important terms using TF-IDF
    print("\n===== IMPORTANT TERMS (TF-IDF) =====")
    print("\nMost important terms in POSITIVE reviews:")
    pos_terms = extract_top_tfidf_terms(positive_df['review'])
    for term, score in pos_terms:
        print(f"  - {term}: {score:.4f}")
    
    print("\nMost important terms in NEGATIVE reviews:")
    neg_terms = extract_top_tfidf_terms(negative_df['review'])
    for term, score in neg_terms:
        print(f"  - {term}: {score:.4f}")
    
    # Calculate average review length
    pos_avg_len = positive_df['review'].apply(len).mean()
    neg_avg_len = negative_df['review'].apply(len).mean()
    
    print("\n===== REVIEW LENGTH ANALYSIS =====")
    print(f"Average length of POSITIVE reviews: {pos_avg_len:.1f} characters")
    print(f"Average length of NEGATIVE reviews: {neg_avg_len:.1f} characters")
    
    # Generate pie chart for sentiment distribution
    print("\nGenerating sentiment distribution chart...")
    plt.figure(figsize=(8, 6))
    sentiment_counts = df['sentiment'].value_counts()
    plt.pie(sentiment_counts, labels=sentiment_counts.index, autopct='%1.1f%%', 
            colors=['lightgreen', 'lightcoral'])
    plt.title('Sentiment Distribution')
    plt.axis('equal')
    plt.savefig("sentiment_distribution.png")
    plt.close()
    
    # Generate bar charts comparing word frequencies
    print("\nGenerating word frequency comparison chart...")
    pos_dict = dict(pos_common[:5])
    neg_dict = dict(neg_common[:5])
    all_words = set(list(pos_dict.keys()) + list(neg_dict.keys()))
    
    # Create DataFrame for comparison
    compare_df = pd.DataFrame(0, index=list(all_words), columns=['Positive', 'Negative'])
    for word in pos_dict:
        compare_df.loc[word, 'Positive'] = pos_dict[word]
    for word in neg_dict:
        compare_df.loc[word, 'Negative'] = neg_dict[word]
    
    # Plot
    plt.figure(figsize=(12, 6))
    compare_df.plot(kind='bar')
    plt.title('Top Words Comparison: Positive vs Negative Reviews')
    plt.ylabel('Frequency')
    plt.tight_layout()
    plt.savefig("word_frequency_comparison.png")
    plt.close()
    
    # Prepare data for AI summary
    analysis_data = {
        'total': len(df),
        'positive': len(positive_df),
        'negative': len(negative_df),
        'positive_pct': f"{len(positive_df)/len(df)*100:.1f}",
        'negative_pct': f"{len(negative_df)/len(df)*100:.1f}",
        'pos_common': ", ".join([f"{word} ({count})" for word, count in pos_common[:5]]),
        'neg_common': ", ".join([f"{word} ({count})" for word, count in neg_common[:5]]),
        'pos_terms': ", ".join([f"{term} ({score:.4f})" for term, score in pos_terms[:5]]),
        'neg_terms': ", ".join([f"{term} ({score:.4f})" for term, score in neg_terms[:5]]),
        'pos_avg_len': f"{pos_avg_len:.1f}",
        'neg_avg_len': f"{neg_avg_len:.1f}"
    }
    
    # Generate AI summaries for each category
    print("\n===== GENERATING AI SUMMARIES =====")
    
    print("\nGenerating positive reviews summary...")
    positive_summary = generate_ai_summary_for_category(analysis_data, "positive")
    print("\nPOSITIVE REVIEWS SUMMARY:")
    print(positive_summary)
    
    print("\nGenerating negative reviews summary...")
    negative_summary = generate_ai_summary_for_category(analysis_data, "negative")
    print("\nNEGATIVE REVIEWS SUMMARY:")
    print(negative_summary)
    
    print("\nGenerating overall summary...")
    overall_summary = generate_ai_summary_for_category(analysis_data, "overall")
    print("\nOVERALL SUMMARY:")
    print(overall_summary)
    
    # Generate summary text file
    print("\nGenerating summary text file...")
    with open("sentiment_analysis_summary.txt", "w") as f:
        f.write("===== SENTIMENT ANALYSIS SUMMARY =====\n")
        f.write(f"Total reviews analyzed: {len(df)}\n")
        f.write(f"Positive reviews: {len(positive_df)} ({len(positive_df)/len(df)*100:.1f}%)\n")
        f.write(f"Negative reviews: {len(negative_df)} ({len(negative_df)/len(df)*100:.1f}%)\n\n")
        
        f.write("===== MOST COMMON WORDS =====\n")
        f.write("Most common words in POSITIVE reviews:\n")
        for word, count in pos_common:
            f.write(f"  - {word}: {count}\n")
        
        f.write("\nMost common words in NEGATIVE reviews:\n")
        for word, count in neg_common:
            f.write(f"  - {word}: {count}\n")
        
        f.write("\n===== IMPORTANT TERMS (TF-IDF) =====\n")
        f.write("Most important terms in POSITIVE reviews:\n")
        for term, score in pos_terms:
            f.write(f"  - {term}: {score:.4f}\n")
        
        f.write("\nMost important terms in NEGATIVE reviews:\n")
        for term, score in neg_terms:
            f.write(f"  - {term}: {score:.4f}\n")
        
        f.write("\n===== REVIEW LENGTH ANALYSIS =====\n")
        f.write(f"Average length of POSITIVE reviews: {pos_avg_len:.1f} characters\n")
        f.write(f"Average length of NEGATIVE reviews: {neg_avg_len:.1f} characters\n")
        
        f.write("\n===== AI GENERATED SUMMARIES =====\n")
        f.write("\nPOSITIVE REVIEWS SUMMARY:\n")
        f.write(positive_summary)
        
        f.write("\n\nNEGATIVE REVIEWS SUMMARY:\n")
        f.write(negative_summary)
        
        f.write("\n\nOVERALL SUMMARY:\n")
        f.write(overall_summary)
    
    print("\nSummary generation complete. Files created:")
    print("- positive_reviews_wordcloud.png")
    print("- negative_reviews_wordcloud.png")
    print("- all_reviews_wordcloud.png")
    print("- sentiment_distribution.png")
    print("- word_frequency_comparison.png")
    print("- sentiment_analysis_summary.txt (includes all AI summaries)")


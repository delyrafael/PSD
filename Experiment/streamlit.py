
# sentiment_app.py
import streamlit as st
import pandas as pd
import os
from openai import OpenAI
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyze_sentiment(text):
    """Analyze sentiment using OpenAI API with strict binary classification"""
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
        temperature=0.1
    )
    
    sentiment = response.choices[0].message.content.strip().lower()
    return "positive" if "positive" in sentiment else "negative"

def process_file(uploaded_file):
    """Process uploaded CSV file"""
    df = pd.read_csv(uploaded_file)
    
    # Select text column
    text_col = st.selectbox("Pilih kolom teks untuk analisis:", df.columns)
    
    if st.button("Mulai Analisis Sentimen"):
        if text_col not in df.columns:
            st.error("Kolom yang dipilih tidak ada dalam file!")
            return
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        results = []
        
        total_rows = len(df)
        for i, row in enumerate(df.itertuples()):
            text = getattr(row, text_col)
            sentiment = analyze_sentiment(text)
            results.append(sentiment)
            
            # Update progress
            progress = (i + 1) / total_rows
            progress_bar.progress(progress)
            status_text.text(f"Memproses {i+1}/{total_rows} baris ({progress:.1%})")
        
        # Add results to dataframe
        df['sentiment'] = results
        
        # Show completion message
        st.success("Analisis selesai!")
        
        # Show summary stats
        st.subheader("Statistik Hasil")
        col1, col2 = st.columns(2)
        col1.metric("Total Positive", df[df['sentiment'] == 'positive'].shape[0])
        col2.metric("Total Negative", df[df['sentiment'] == 'negative'].shape[0])
        
        # Show sample data
        st.subheader("Preview Hasil")
        st.dataframe(df.head())
        
        # Download button
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Unduh Hasil Analisis",
            data=csv,
            file_name='hasil_sentimen.csv',
            mime='text/csv'
        )

def main():
    st.title("📊 Sentiment Analysis and reasoning using LLM")
    st.write("Silahkan unggah file CSV dan lakukan labeling otomatis.")
    
    uploaded_file = st.file_uploader(
        "Seret file CSV ke sini atau klik untuk memilih file",
        type="csv"
    )
    
    if uploaded_file is not None:
        try:
            process_file(uploaded_file)
        except Exception as e:
            st.error(f"Terjadi error: {str(e)}")

if __name__ == "__main__":
    main()
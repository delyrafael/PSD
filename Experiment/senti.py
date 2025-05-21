import os
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
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

def process_csv_file(df, output_path=None):
    try:
        # Read the CSV file
        
        
        # Check if the file has any data
        if df.empty:
            print("The CSV file is empty.")
            return
        
        # Ask user which column contains the text to analyze
        print("Available columns:")
        for i, col in enumerate(df.columns):
            print(f"{i+1}. {col}")
        
        col_index = int(input("Enter the number of the column containing text to analyze: ")) - 1
        text_column = df.columns[col_index]
        
        print(f"Analyzing sentiment for column: {text_column}")
        print("This may take some time depending on the number of rows...")
        
        # Add a new column for sentiment
        df['sentiment'] = df[text_column].apply(analyze_sentiment)
        
        # If no output path is specified, create one based on the input file
        if output_path is None:
            base_name = os.path.splitext(csv_path)[0]
            output_path = f"{base_name}_with_sentiment.csv"
        
        # Save the dataframe with sentiment analysis to a new CSV file
        df.to_csv(output_path, index=False)
        print(f"Sentiment analysis completed! Results saved to: {output_path}")
        
        # Print summary of results
        sentiment_counts = df['sentiment'].value_counts()
        print("\nSentiment Distribution:")
        for sentiment, count in sentiment_counts.items():
            print(f"{sentiment}: {count} ({count/len(df)*100:.1f}%)")
        
        return df
        
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
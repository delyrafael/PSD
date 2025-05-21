import json
import os
import pandas as pd

def convert_imdb_reviews_to_excel(json_file_path, excel_file_path):
    """
    Converts IMDB reviews JSON file to Excel with all information in one sheet.
    
    Args:
        json_file_path (str): Path to the JSON file containing IMDB reviews
        excel_file_path (str): Path to save the Excel file
    """
    # Read the JSON file
    with open(json_file_path, 'r', encoding='utf-8') as file:
        json_data = json.load(file)
    
    print(f"JSON file successfully read. Data type: {type(json_data)}")
    
    # Initialize data structure for Excel
    excel_data = []
    
    # Process the reviews
    try:
        # Extract movie info
        imdb_id = json_data.get("ImdbId", "Unknown")
        total_reviews = json_data.get("total_reviews", 0)
        reviews = json_data.get("reviews", [])
        
        print(f"Processing IMDB ID: {imdb_id} with {total_reviews} reviews")
        
        # Process each review
        for review in reviews:
            if not isinstance(review, dict):
                print(f"Warning: Expected dictionary but got {type(review)}: {review}")
                continue
                
            row_data = {
                "imdb_id": imdb_id,
                "reviewer_name": review.get("reviewer_name", ""),
                "reviewer_url": review.get("reviewer_url", ""),
                "review_date": review.get("review_date", ""),
                "rating_value": review.get("rating_value", ""),
                "short_review": review.get("short_review", ""),
                "full_review": review.get("full_review", "")
            }
            
            excel_data.append(row_data)
            
    except Exception as e:
        print(f"Error processing JSON data: {e}")
    
    # Create DataFrame from prepared data
    try:
        if excel_data:
            df_reviews = pd.DataFrame(excel_data)
        else:
            # Create empty DataFrame with header columns if no data
            df_reviews = pd.DataFrame(columns=["imdb_id", "reviewer_name", "reviewer_url", 
                                      "review_date", "rating_value", "short_review", 
                                      "full_review"])
        
        # Write to Excel
        with pd.ExcelWriter(excel_file_path, engine='xlsxwriter') as writer:
            print(f"Creating Excel file: {excel_file_path}")
            
            df_reviews.to_excel(writer, sheet_name='IMDB Reviews', index=False)
            print(f"Sheet 'IMDB Reviews' created with {len(df_reviews)} rows")
            
            # Format workbook
            workbook = writer.book
            worksheet = writer.sheets['IMDB Reviews']
            
            # Header format
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#D9E1F2',
                'border': 1
            })
            
            # Format for text with line breaks
            wrap_format = workbook.add_format({
                'text_wrap': True,
                'valign': 'top'
            })
            
            # Apply format to header
            for col_num, value in enumerate(df_reviews.columns.values):
                worksheet.write(0, col_num, value, header_format)
            
            # Apply wrap format to specific columns
            for row_num in range(1, len(df_reviews) + 1):
                worksheet.set_row(row_num, None, wrap_format)
            
            # Set column widths
            for i, col in enumerate(df_reviews.columns):
                max_len = 0
                # Check header length
                header_len = len(col)
                
                # Check data length in column
                column_data = df_reviews[col].astype(str)
                for data in column_data:
                    # Split text with line breaks
                    lines = data.split('\n')
                    for line in lines:
                        if len(line) > max_len:
                            max_len = len(line)
                
                # Choose longer of header or data
                column_width = max(max_len, header_len) + 2  # Add extra space
                
                # Limit maximum column width
                if column_width > 100:
                    column_width = 100
                    
                # Make full_review column wider
                if col == "full_review":
                    column_width = min(100, max(column_width, 50))
                
                worksheet.set_column(i, i, column_width)
        
        # Verify Excel file was created
        if os.path.exists(excel_file_path):
            file_size = os.path.getsize(excel_file_path)
            print(f"Excel file successfully created at {excel_file_path} with size {file_size} bytes")
            return True
        else:
            print(f"WARNING: Excel file not found at {excel_file_path}")
            return False
            
    except Exception as e:
        print(f"Error creating Excel file: {e}")
        return False

# Example usage:
convert_imdb_reviews_to_excel("reviews_tt0499549_Avatar.json", "imdb_reviews.xlsx")
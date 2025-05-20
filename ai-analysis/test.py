import csv
import google.generativeai as genai
import os
import time

# --- Configuration ---
# Update these paths if your files are located elsewhere
INPUT_CSV_FILE = 'test.csv'
OUTPUT_CSV_FILE = 'test_with_countries.csv'

# Choose your Gemini model
GEMINI_MODEL_NAME = 'gemma-3-27b-it'
GOOGLE_API_KEY = os.getenv('GAIzaSyCEnPkMFwjbNeA73XIW3rqPrQt5aRqjkVw')

def get_country_iso_from_gemini(title, shorttext, labeltop, model):
    """
    Uses the Gemini API to determine the country ISO code from article details.
    """
    prompt = f"""Analyze the following news article details and determine the primary country it pertains to. Provide the country's two-letter ISO 3166-1 alpha-2 code.

Title: {title}
Short Text: {shorttext}
Label: {labeltop}

Respond with only the ISO 3166-1 alpha-2 code (e.g., US, DE, GB, EU). If multiple countries are equally prominent, try to use the origin of the article and don’t forget refers to a supranational entity like the EU. If no specific country can be identified, respond with 'N/A'. 
ISO Code:"""

    try:
        response = model.generate_content(prompt)
        iso_code = response.text.strip()
        # Validate the response format
        if (len(iso_code) == 2 and iso_code.isalpha() and iso_code.isupper()) or iso_code == "N/A":
            return iso_code
        else:
            print(f"Warning: Unexpected response format from Gemini for title '{title[:30]}...': '{iso_code}'. Defaulting to 'ERR'.")
            return "ERR"  # Indicate an unexpected response
    except Exception as e:
        print(f"Error calling Gemini API for title '{title[:30]}...': {e}")
        return "API_ERR" # Indicate an API error

def process_csv():
    """
    Reads the input CSV, processes each row to add a country_iso,
    and writes to the output CSV.
    """
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("GOOGLE_API_KEY environment variable not found.")
        api_key_input = input("Please enter your Google API Key for Gemini: ")
        if api_key_input:
            genai.configure(api_key=api_key_input)
        else:
            print("API Key not provided. Exiting.")
            return
    else:
        genai.configure(api_key=api_key)

    try:
        model = genai.GenerativeModel(GEMINI_MODEL_NAME)
    except Exception as e:
        print(f"Error initializing Gemini model '{GEMINI_MODEL_NAME}': {e}")
        print("Please ensure your API key is correct, and you have access to the model.")
        return

    processed_rows = 0
    try:
        with open(INPUT_CSV_FILE, mode='r', encoding='utf-8', newline='') as infile, \
             open(OUTPUT_CSV_FILE, mode='w', encoding='utf-8', newline='') as outfile:

            reader = csv.DictReader(infile)
            
            if not reader.fieldnames:
                print(f"Error: Input CSV file '{INPUT_CSV_FILE}' is empty or has no header row.")
                return
            
            # Define output fieldnames, adding the new 'country_iso' column
            fieldnames = reader.fieldnames + ['country_iso']
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()

            print(f"Starting processing of {INPUT_CSV_FILE}...")
            for i, row in enumerate(reader):
                title = row.get('titel', '')
                shorttext = row.get('shorttext', '')
                labeltop = row.get('labeltop', '')

                # Skip if key text fields are missing
                if not title and not shorttext and not labeltop:
                    print(f"Skipping row {i+1} due to missing title, shorttext, and labeltop.")
                    country_iso = "N/A"
                else:
                    print(f"Processing article (row {i+2}): {title[:50]}...")
                    country_iso = get_country_iso_from_gemini(title, shorttext, labeltop, model)
                    # Optional: Add a small delay to respect API rate limits if processing a very large file
                    # time.sleep(0.5) # 0.5 second delay

                row['country_iso'] = country_iso
                writer.writerow(row)
                processed_rows += 1
                
                if processed_rows % 10 == 0:
                    print(f"--- Processed {processed_rows} articles ---")

        print(f"\nProcessing complete.")
        print(f"Total articles processed: {processed_rows}")
        print(f"Output saved to {OUTPUT_CSV_FILE}")

    except FileNotFoundError:
        print(f"Error: Input file not found at {INPUT_CSV_FILE}")
    except Exception as e:
        print(f"An unexpected error occurred during CSV processing: {e}")

if __name__ == '__main__':
    process_csv()

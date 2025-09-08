import requests
import sqlite3
import os
import json
import time
from bs4 import BeautifulSoup
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv(dotenv_path='./.env', override=True)

# --- CONFIGURATION (Added a known multi-rep ZIP code) ---
ZIP_CODES_TO_SCRAPE = ['11354', '13662', '90210'] # 90210 is split between multiple districts

# --- INITIALIZE LLM CLIENT ---
try:
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
except Exception as e:
    print("Error initializing Gemini client. Make sure your GOOGLE_API_KEY is set in your .env file.")
    exit()

# --- DATABASE AND FETCH FUNCTIONS (Unchanged) ---
def get_db_connection():
    return sqlite3.connect('civic_tracker.db')

def fetch_page_content(url):
    try:
        print(f"Fetching data from: {url}")
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup.get_text(separator=' ', strip=True)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL: {e}")
        return None

# --- AGENT STEP 2: EXTRACT WITH LLM (Now Smarter!) ---
def extract_rep_info_with_llm(content):
    """
    Uses Google Gemini to extract representative names.
    It now detects if there are multiple reps and adjusts its prompt.
    Always returns a LIST of names.
    """
    if not content:
        return []

    print("Asking Gemini LLM to extract representative information...")
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    
    # Logic to detect the page type and choose the right prompt
    if "overlaps with more than one congressional district" in content:
        print("Multi-representative page detected.")
        prompt = f'''
        From the following text, extract a list of all U.S. House Representatives' full names.
        Respond ONLY with a JSON object in this exact format: {{"names": ["Name One", "Name Two", "Name Three"]}}
        
        Text:
        ---
        {content[:12000]}
        ---
        '''
    else:
        print("Single-representative page detected.")
        prompt = f'''
        From the following text, find the full name of the U.S. House Representative.
        Respond ONLY with a JSON object in this exact format: {{"names": ["Full Name"]}}
        
        Text:
        ---
        {content[:12000]}
        ---
        '''

    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip().replace('```json', '').replace('```', '')
        print(f"LLM Response: {response_text}")
        data = json.loads(response_text)
        # Ensure we return a list, even if it's empty
        return data.get("names", [])
    except Exception as e:
        print(f"An error occurred with the Gemini API call or JSON parsing: {e}")
        return []

# --- AGENT STEP 3: STORE IN DATABASE (Updated to handle a list) ---
def add_data_to_db(rep_names_list, zip_code, conn):
    """Saves a list of representatives for a given ZIP code to the database."""
    if not rep_names_list:
        print(f"No representative names found for {zip_code}. Skipping DB update.")
        return

    cursor = conn.cursor()
    # For simplicity, we just use generic geo data for the multi-rep case
    geo_details = {
        '11354': ('Flushing', 'New York', 'NY', 'NY-6'),
        '13662': ('Massena', 'New York', 'NY', 'NY-21'),
        '90210': ('Beverly Hills', 'California', 'CA', 'CA-30/32') # Example district
    }
    city, state_name, state_abbr, district = geo_details.get(zip_code, ('Unknown', 'Unknown', 'UN', 'UN-00'))

    try:
        cursor.execute(
            "INSERT INTO geography (zip_code, city, state_name, state_abbr, congressional_district) VALUES (?, ?, ?, ?, ?)",
            (zip_code, city, state_name, state_abbr, district)
        )
        geo_id = cursor.lastrowid
        
        # Loop through each representative found and add them
        for rep_name in rep_names_list:
            cursor.execute(
                "INSERT INTO representatives (name, party, branch, title) VALUES (?, ?, ?, ?)",
                (rep_name, 'Unknown', 'Federal', 'U.S. House Rep')
            )
            rep_id = cursor.lastrowid
            cursor.execute(
                "INSERT INTO rep_geography_map (representative_id, geography_id) VALUES (?, ?)",
                (rep_id, geo_id)
            )
            print(f"Successfully inserted '{rep_name}' for ZIP code {zip_code}.")
    except Exception as e:
        print(f"Database error for {zip_code}: {e}")

# --- MAIN EXECUTION (Unchanged) ---
if __name__ == '__main__':
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print("Clearing old data from the database...")
    cursor.execute("DELETE FROM rep_geography_map")
    cursor.execute("DELETE FROM representatives")
    cursor.execute("DELETE FROM geography")
    conn.commit()

    for zip_code in ZIP_CODES_TO_SCRAPE:
        print(f"\n--- Processing ZIP Code: {zip_code} ---")
        target_url = f"https://ziplook.house.gov/htbin/findrep_house?ZIP={zip_code}"
        
        page_content = fetch_page_content(target_url)
        # This now returns a list, e.g., ["Grace Meng"] or ["Ted Lieu", "Adam Schiff"]
        representative_names = extract_rep_info_with_llm(page_content)
        
        add_data_to_db(representative_names, zip_code, conn)
        conn.commit()
        time.sleep(1) # Add a small delay to avoid overwhelming the server
    
    conn.close()
    print("\nScraping process finished for all ZIP codes.")
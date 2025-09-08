import sqlite3
from flask import Flask, request, jsonify

# Initialize the Flask application
app = Flask(__name__)

# --- Helper Function to connect to the database ---
def get_db_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect('civic_tracker.db')
    # This allows us to access columns by name (like a dictionary)
    conn.row_factory = sqlite3.Row 
    return conn

# --- API Endpoint Definition ---
@app.route('/representatives', methods=['GET'])
def get_representatives_by_zip():
    """
    API endpoint to fetch representatives for a given ZIP code.
    Usage: /representatives?zip=11354
    """
    # 1. Get the 'zip' parameter from the URL
    zip_code = request.args.get('zip', type=str)

    # 2. Validate the input
    if not zip_code:
        # Return a 400 Bad Request error if the zip is missing
        return jsonify({"error": "A 'zip' parameter is required."}), 400

    # 3. Query the database
    conn = get_db_connection()
    
    # This SQL query joins our three tables to link reps to a ZIP code.
    # The CASE statement dynamically builds the 'title' string to match the example output.
    query = """
    SELECT
        r.name,
        CASE
            WHEN r.title = 'U.S. House Rep' THEN r.title || ', ' || g.congressional_district
            WHEN r.title = 'U.S. Senator' THEN r.title || ', ' || g.state_abbr
            WHEN r.title = 'Governor' THEN r.title || ', ' || g.state_name
            ELSE r.title
        END AS full_title
    FROM representatives r
    JOIN rep_geography_map rgm ON r.id = rgm.representative_id
    JOIN geography g ON g.id = rgm.geography_id
    WHERE g.zip_code = ?
    """
    
    cursor = conn.cursor()
    results = cursor.execute(query, (zip_code,)).fetchall()
    conn.close()

    # 4. Format the output
    representatives_list = []
    for row in results:
        representatives_list.append({
            "name": row['name'],
            "title": row['full_title']
        })
    
    # Construct the final JSON response
    response_data = {
        "zip": zip_code,
        "representatives": representatives_list
    }

    # 5. Return the JSON response
    return jsonify(response_data)

# --- Run the application ---
if __name__ == '__main__':
    # debug=True allows the server to auto-reload when you save the file
    app.run(debug=True)
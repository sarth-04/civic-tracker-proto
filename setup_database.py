import sqlite3

# --- DATABASE SETUP ---
# Connect to the SQLite database. 
# If the file doesn't exist, it will be created.
conn = sqlite3.connect('civic_tracker.db')
cursor = conn.cursor()

# --- TABLE CREATION ---
# Use """ to write multi-line SQL statements for readability.

# Create the 'geography' table
cursor.execute("""
CREATE TABLE IF NOT EXISTS geography (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    zip_code TEXT NOT NULL,
    city TEXT,
    state_name TEXT,
    state_abbr TEXT,
    congressional_district TEXT
);
""")

# Create the 'representatives' table
cursor.execute("""
CREATE TABLE IF NOT EXISTS representatives (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    party TEXT,
    branch TEXT,
    title TEXT
);
""")

# Create the mapping table
cursor.execute("""
CREATE TABLE IF NOT EXISTS rep_geography_map (
    representative_id INTEGER,
    geography_id INTEGER,
    FOREIGN KEY (representative_id) REFERENCES representatives (id),
    FOREIGN KEY (geography_id) REFERENCES geography (id),
    PRIMARY KEY (representative_id, geography_id)
);
""")


# --- DATA INSERTION (for ZIP code 11354) ---
# This is our manual "mock" data for the prototype.

try:
    # 1. Insert Geography Data
    # We use a tuple to safely pass values into the SQL statement.
    cursor.execute(
        "INSERT INTO geography (zip_code, city, state_name, state_abbr, congressional_district) VALUES (?, ?, ?, ?, ?)",
        ('11354', 'Flushing', 'New York', 'NY', 'NY-6')
    )
    # Get the ID of the geography we just inserted to use it in the mapping table
    geo_id = cursor.lastrowid

    # 2. Insert Representative Data
    reps_to_insert = [
        ('Grace Meng', 'Democratic', 'Federal', 'U.S. House Rep'),
        ('Chuck Schumer', 'Democratic', 'Federal', 'U.S. Senator'),
        ('Kathy Hochul', 'Democratic', 'State', 'Governor')
    ]
    
    # Insert each representative and create the mapping
    for rep in reps_to_insert:
        cursor.execute(
            "INSERT INTO representatives (name, party, branch, title) VALUES (?, ?, ?, ?)",
            rep
        )
        rep_id = cursor.lastrowid
        
        # 3. Create the Mapping
        cursor.execute(
            "INSERT INTO rep_geography_map (representative_id, geography_id) VALUES (?, ?)",
            (rep_id, geo_id)
        )

    # Commit the changes to the database
    conn.commit()
    print("Database setup complete. Tables created and initial data inserted successfully!")

except sqlite3.IntegrityError:
    print("Data may have already been inserted. Skipping.")
except Exception as e:
    print(f"An error occurred: {e}")
    conn.rollback() # Roll back any changes if an error occurs
finally:
    # Close the connection
    conn.close()
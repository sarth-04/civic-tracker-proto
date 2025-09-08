

```markdown
# 🏛️ Civic Tracker API – U.S. Representatives by ZIP Code

This project is a **prototype API** that returns political representative details for a given **U.S. ZIP code**.  
It demonstrates database design, web scraping, API development using **Flask**, and basic **LLM integration** for data extraction.

---

## 🚀 Features

- **Database Schema** for:
  - Geography (ZIP, City, State, District)
  - Representatives (Name, Title, Party, Branch)
  - Mapping between Geography & Representatives
- **API Endpoint**:
  - Input: ZIP Code (e.g., `zip=11354`)
  - Output: JSON with Representative Details
- **Scraping + LLM Integration**:
  - Uses **Google Gemini API** + `BeautifulSoup` for representative data extraction.
- **Prototype Demo**:
  - Supports one or two ZIP codes as proof-of-concept.

---

## 🗂️ Project Structure

```

├── app.py                # Flask API for fetching representatives
├── scraper\_gemini.py      # Scraping + LLM extraction + DB insertion
├── setup\_database.py      # Creates SQLite DB & inserts initial data
├── civic\_tracker.db        # SQLite Database (auto-generated)
├── requirements.txt       # Python dependencies
└── README.md              # Project Documentation

````

---

## 📦 Setup Instructions

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/<your-username>/civic-tracker-api.git
cd civic-tracker-api
````

### 2️⃣ Create a Virtual Environment (Optional but Recommended)

```bash
python -m venv venv
source venv/bin/activate  # For Mac/Linux
venv\Scripts\activate     # For Windows
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Set Up Environment Variables

Create a `.env` file in the root directory:

```env
GOOGLE_API_KEY=your_google_gemini_api_key_here
```

### 5️⃣ Initialize the Database

```bash
python setup_database.py
```

### 6️⃣ Run the Scraper (Optional)

Fetch representative details for sample ZIP codes:

```bash
python scraper_gemini.py
```

### 7️⃣ Start the API

```bash
python app.py
```

The API will start on `http://127.0.0.1:5000`.

---

## 🔗 API Usage

### Endpoint

```
GET /representatives?zip=<ZIP_CODE>
```

### Example Request

```
GET http://127.0.0.1:5000/representatives?zip=11354
```

### Example Response

```json
{
  "zip": "11354",
  "representatives": [
    { "name": "Grace Meng", "title": "U.S. House Rep, NY-6" },
    { "name": "Chuck Schumer", "title": "U.S. Senator, NY" },
    { "name": "Kathy Hochul", "title": "Governor, New York" }
  ]
}
```

---

## 📊 Database Schema

**Tables**:

1. **geography**: Stores ZIP, City, State, District
2. **representatives**: Stores Representative Details
3. **rep\_geography\_map**: Many-to-Many Mapping Table

---

## 🎥 Demo Video

* Record a **short video** showing:

  1. Running the API
  2. Sample ZIP code query
  3. JSON Output
* Upload to **Google Drive** & share the **link** here.

---

## 🛠️ Tech Stack

* **Python** (Flask, Requests, BeautifulSoup)
* **SQLite** for lightweight storage
* **Google Gemini API** for LLM-based data extraction

---


## 👨‍💻 Author

**Your Name**
Email: [sarthakingle04@gmail.com](mailto:sarthakingle04@gmail.com)
GitHub: [@sarth-04](https://github.com/sarth-04)

---


```

---


```

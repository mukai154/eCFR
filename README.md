# ECFR Analyzer 🔍📊

Analyze historical word counts for ECFR titles over time. Built with FastAPI and React.

---

## 📘 Description

ECFR Analyzer allows users to search for federal agencies, explore the Code of Federal Regulations (CFR) titles associated with them, and analyze the historical changes in word counts of those regulations over time. Users can visualize revision trends through dynamic charts.

---

## ✨ Features

- 🔎 Search for a federal agency and view its associated CFR titles
- 🕓 Fetch and display word count of historical corrections and revisions
- 📈 Visualize word count changes over time
- ⚡ FastAPI backend and React frontend
- 📊 Dynamic Chart.js for chart visualization

---

## 🧰 Tech Stack

- **Frontend**: React (Vite), Chart.js, JSX
- **Backend**: FastAPI (Python)
- **Styling**: Dark Mode, Custom CSS

---

## 🛠️ Local Setup

### 1. Clone the Repo

```bash
git clone https://github.com/your-username/ecfr-analyzer.git
cd ecfr-analyzer
```

### 2. Start the Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate   # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
uvicorn main:app --reload
```

By default, the backend runs at `http://localhost:8000`.

### 3. Start the Frontend

```bash
cd ../frontend
npm install
npm run dev
```

The frontend runs at `http://localhost:5173`.

---

## 🚀 Potential Future Improvements

- [ ] Improved UX/UI
- [ ] Display full text of each revision that is downloadable
- [ ] Export chart data as CSV

---

## 📄 License

MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights  
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell  
copies of the Software, and to permit persons to whom the Software is  
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR  
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,  
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE  
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER  
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,  
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE  
SOFTWARE.

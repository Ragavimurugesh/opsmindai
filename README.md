# OpsMind AI 🧠🏪

> **AI-Powered Warehouse Inventory Forecasting & Decision Support System**
>
> OpsMind AI is an advanced, intelligent warehouse forecasting system designed to optimize inventory levels, forecast demand using state-of-the-art machine learning models (Prophet, XGBoost), and provide real-time decision support dashboards.

---

## 📂 Project Folder Structure

The project has been organized with a clean, decoupled frontend-backend architecture:

```text
opsmind-ai/
├── frontend/             # React + Vite frontend application
├── backend/              # FastAPI application
│   ├── routes/           # API endpoints (auth, inventory, forecasting, etc.)
│   ├── services/         # Business logic and external API integrations
│   ├── models/           # SQLAlchemy database schemas / tables
│   ├── schemas/          # Pydantic schemas for data validation
│   ├── utils/            # Shared helper functions / utility modules
│   ├── main.py           # FastAPI entry point
│   ├── database.py       # Supabase PostgreSQL configuration & session handling
│   └── requirements.txt  # Backend dependencies
├── ml/                   # Machine Learning workflows
│   └── saved_models/     # Serialized Prophet/XGBoost models (Joblib/PKL)
├── dataset/              # Data storage
│   ├── raw/              # Original, unmodified datasets (ignored by git)
│   └── processed/        # Cleaned datasets ready for training (ignored by git)
├── docs/                 # Project documentation & design sheets
├── screenshots/          # Dashboard screenshots for report submissions
├── README.md             # Project documentation (this file)
└── .gitignore            # Git ignore configurations (Python + Node.js)
```

---

## 🎨 2. Frontend Setup (React + Vite)

### Step 1: Initialize Vite React App
Run the following command from the root directory (`opsmind-ai/`):
```bash
# Initialize Vite React + TypeScript/JS project
npm create vite@latest frontend -- --template react

# Move into the frontend directory
cd frontend
```

### Step 2: Install Styling & Visualization Dependencies
Install Tailwind CSS, Axios for API communications, React Router DOM for routing, and Recharts for charts/analytics:
```bash
# Install styling and libraries
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# Install utilities, routing, and charts
npm install axios react-router-dom recharts lucide-react
```

### Step 3: Configure Tailwind CSS
Update the `tailwind.config.js` file in the `frontend/` directory to scan all files:
```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Suggested premium dark/blue aesthetic palette
        brand: {
          dark: '#0B0F19',
          card: '#161B26',
          accent: '#3B82F6',
          success: '#10B981',
        }
      }
    },
  },
  plugins: [],
}
```

Add the Tailwind directives to your `frontend/src/index.css`:
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

### Step 4: Run the Development Server
```bash
npm run dev
```
The React development server will start (usually on `http://localhost:5173`).

---

## ⚙️ 3. Backend Setup (FastAPI)

### Step 1: Create a Python Virtual Environment
Navigate to the `backend/` directory and set up a virtual environment:
```bash
# Navigate to backend
cd backend

# Create the environment (Windows)
python -m venv venv

# Activate the virtual environment
# On Windows (Command Prompt):
venv\Scripts\activate
# On Windows (PowerShell):
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 2: Install Dependencies
Install all ML, FastAPI, and Database connector dependencies listed in `requirements.txt`:
```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Run the FastAPI Server
To launch the development server with hot-reloading enabled, run:
```bash
uvicorn main:app --reload
```
The documentation will be interactively available at `http://127.0.0.1:8000/docs`.

---

## 🗄️ 4. Supabase Setup Instructions

Supabase is used as our hosted PostgreSQL database. Follow these steps to link it with FastAPI:

### Step 1: Create a Project
1. Visit [Supabase](https://supabase.com) and log in.
2. Click **New Project** and select your organization.
3. Name the project `OpsMind AI`, set a secure database password, and pick a region close to your users.
4. Click **Create Project** (it will take a few minutes to provision).

### Step 2: Obtain Connection Details
Navigate to the **Project Settings** (gear icon) -> **API** or **Database**:
- **Project URL**: Located in settings under API. (Use this for connecting frontend/backend clients).
- **Anon/Public Key**: Used in the frontend or middleware to make safe client-side queries.
- **Database Connection String**: Navigate to **Database** settings -> **Connection Strings** -> select **URI**. It looks like this:
  `postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-ID].supabase.co:5432/postgres`

### Step 3: Configure FastAPI Environment Variables
Create a file named `.env` in the `backend/` folder:
```env
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-ID].supabase.co:5432/postgres
SUPABASE_URL=https://[YOUR-PROJECT-ID].supabase.co
SUPABASE_KEY=[YOUR-ANON-PUBLIC-KEY]
```
These values are loaded by `database.py` via `python-dotenv` to configure the SQLAlchemy engine and verify connections.

---

## 🐙 5. GitHub Setup

### Step 1: Create Repository
Create a new repository on GitHub named `opsmind-ai` (keep it public or private as preferred). Do **not** initialize it with a README or gitignore there (we already have them here!).

### Step 2: Run Git Commands in Terminal
Initialize git and push to GitHub:
```bash
# Run these commands in the root "opsmind-ai/" directory
git init

# Add all files to the initial commit
git add .

# Create the initial commit
git commit -m "feat: phase 1 project setup skeleton for OpsMind AI"

# Rename default branch to main
git branch -M main

# Link to your remote repository
git remote add origin https://github.com/YOUR_USERNAME/opsmind-ai.git

# Push to your repository
git push -u origin main
```

---

## ✅ 6. Final Verification Checklist

Run through these verification checks to ensure Phase 1 is fully complete and operational:

* [ ] **Folder Structure**: Compare directory contents to the tree diagram to confirm all subfolders are present.
* [ ] **Gitignore Working**: Ensure `node_modules/`, `venv/`, and `.env` are not being tracked by git (run `git status` to verify they aren't staged).
* [ ] **React App Initialized**: Able to create Vite app and run `npm run dev` successfully.
* [ ] **FastAPI Server Running**: Run `uvicorn main:app --reload` and visit `http://127.0.0.1:8000/` to receive the welcome JSON output.
* [ ] **API Documentation Accessible**: Visit `http://127.0.0.1:8000/docs` to see the automated interactive Swagger UI.
* [ ] **Dependencies Stored**: `requirements.txt` contains all core libraries (Prophet, XGBoost, scikit-learn, SQLAlchemy, Uvicorn, FastAPI).
* [ ] **Supabase Connected**: Database URL format is configured correctly in `.env` and loaded by `database.py`.
* [ ] **GitHub Initialized**: Remote repository is set and successfully pushed to origin.

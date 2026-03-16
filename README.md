Wind Power Forecast Monitoring & Analysis System
A full-stack monitoring solution and statistical analysis of UK wind power generation, built for the REint AI Software Engineer Challenge. This project bridges the gap between raw grid data and actionable reliability insights.

🚀 Project Links
- **Live Application:** [reint-wind-challenge.vercel.app](https://reint-wind-challenge-taufeeq.vercel.app/)
- **Technical Walkthrough:** [Watch the Loom Demo](https://www.loom.com/share/38960785ebbc4cd7b3466af2a2477482)
- **Backend API:** [reint-wind-challenge.onrender.com](https://reint-wind-challenge.onrender.com)

📊 Core Analytical Insight: The Reliability Baseline
The central challenge was determining how much wind power the grid can actually rely on given forecast volatility.

Key Findings:

Accuracy Decay: My analysis of the 48-hour forecast horizon revealed a "staircase" degradation in Mean Absolute Error (MAE).

The 4,300 MW Buffer: Based on 95th-percentile forecast deviations, I recommend a conservative ~4,300 MW reliability baseline. This ensures grid stability even during periods of high forecast volatility.

🛠️ Technical Stack
Frontend: React, Vite, Recharts, Tailwind CSS.

Backend: Django, Django REST Framework, SQLite.

Data Engineering: Python (Pandas, NumPy, Requests).

Infrastructure: Vercel (Frontend), Render (Backend).

⚙️ Key Features
Resilient Ingestion: A custom data pipeline with automated retries and day-chunking to handle Elexon API rate limits.

Horizon-Based Analysis: An interactive dashboard that allows users to adjust the forecast lead time (0–48h) to visualize real-time error margins.

Statistical Rigor: Full Jupyter Notebook analysis (reint_analysis.ipynb) mapping theoretical reliability against historical actuals.

🛠️ Local Setup
Backend
Navigate to /backend

Install dependencies: pip install -r requirements.txt

Run migrations: python manage.py migrate

Ingest data: python ingest.py

Start server: python manage.py runserver

Frontend
Navigate to /frontend

Install dependencies: npm install

Start development server: npm run dev

👨‍💻 Author
Taufeeq Syed ---

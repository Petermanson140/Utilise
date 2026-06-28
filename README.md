# Utilize
### AI-Powered Personalized London Household Bill Savings Advisor

MSc Applied AI | Peter Manson | Student ID: 21764040 | September 2026

---

## What It Does
Utilize helps London households save money on electricity, gas, and water 
bills through personalised, weather-aware AI recommendations shown in 
pounds per month and per year.

## Live URL
🔗 Coming soon — will be deployed on Render

## Tech Stack
| Layer | Technology |
|---|---|
| Frontend | React + Tailwind CSS |
| Backend | FastAPI (Python) |
| LLM | Claude API (Anthropic) |
| RAG | LangChain + ChromaDB |
| Embeddings | all-MiniLM-L6-v2 |
| Weather | Open-Meteo + Met Office DataPoint |
| Forecasting | Meta Prophet |
| Evaluation | RAGAS |
| Database | PostgreSQL |
| Deployment | Docker + Render |

## Project Structure
utilize/
├── backend/          # FastAPI backend
├── frontend/         # React frontend
├── data/             # Datasets and synthetic profiles
├── rag_docs/         # UK energy guidance documents
├── dissertation/     # Dissertation chapters
└── README.md

## Research Questions
1. Does adding live weather data improve savings recommendation accuracy?
2. Which household factors best predict high energy bills?
3. Can the RAG pipeline achieve RAGAS faithfulness above 0.80?

## Supervisor
DR Barbara Villarini

## Submission Date
3 September 2026

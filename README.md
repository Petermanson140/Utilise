# Utilize
### An AI-Driven Personalised London Household Bill Savings Advisor

MSc Applied AI | Peter Kyan Win Manson | Student ID: 21764040 | September 2026

## What It Does
Utilize helps London households save money on electricity, gas, and water 
bills through personalised, weather-aware AI recommendations shown in 
pounds per month and annually.

## Live URL


## Technology Stack
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

##  3 Research Questions
1. Does integrating live weather data improve the accuracy of savings recommendations?
2. Which household factors are the best predictions for high energy bills?
3. Can the RAG pipeline achieve RAGAS confidence score of above 0.80?

## Supervisor of MSc Utilize Project
Dr. Barbara Villarini

## Official Submission Date of Utilize
3rd September 2026

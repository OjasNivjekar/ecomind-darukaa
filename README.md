🌱 EcoMind — AI Biodiversity Intelligence Advisor

«Evidence-grounded AI for understanding environmental conditions and generating actionable biodiversity interventions.»

EcoMind combines structured environmental knowledge, multi-metric ecological reasoning, retrieval-augmented generation (RAG), Llama-based synthesis, conversational memory, and curated evidence to turn environmental observations into practical, traceable recommendations.

It connects soil health, moisture, rainfall, land use, habitat quality, and biodiversity indicators to explain ecological interactions and identify interventions.

🚀 Links

- Live application: Coming soon
- API: Coming soon
- Repository: Coming soon

🎯 Problem and Solution

Environmental decisions depend on interacting variables rather than isolated measurements.

Low soil organic carbon combined with low rainfall can reduce moisture retention, increase plant stress, lower habitat quality, and reduce biodiversity support.

Generic LLMs can also produce plausible but unsupported advice. EcoMind addresses both challenges through an evidence-grounded pipeline:

1. Environmental observation
2. Input understanding
3. Structured knowledge and multi-metric reasoning
4. Scientific evidence retrieval
5. Grounded Llama synthesis
6. Actionable recommendation with metrics, timeline, confidence, and citations

✨ Features

Environmental Analysis

Users describe environmental conditions in natural language. EcoMind extracts relevant context and identifies biodiversity risks.

Multi-Metric Reasoning

The system models relationships between:

- Soil health and water availability
- Water availability and species survival
- Land use, habitat quality, and fragmentation
- Climate and soil moisture
- Soil conditions, vegetation, and pollinators

Evidence-Grounded Recommendations

A curated evidence layer supports recommendations with:

- Evidence ID
- Source title and organization
- Publication year
- URL
- Relevant excerpt

Recommendations are omitted when supporting evidence is unavailable. The synthesis layer is instructed not to invent sources, statistics, measurements, relationships, or unsupported benefits.

Structured Outputs

Each recommendation can include:

- Action: Recommended intervention
- Why it works: Ecological reasoning
- Impacted metrics: Environmental variables affected
- Time horizon: Expected implementation horizon
- Confidence: Confidence level
- Citations: Supporting evidence

Conversational Memory

Session-based conversations retain environmental context and apply follow-up constraints to updated assessments.

🏗️ Architecture

EcoMind uses the following architecture:

1. React frontend
2. FastAPI validation and session handling
3. Structured environmental knowledge
4. Multi-metric ecological reasoning
5. RAG with curated evidence and FAISS
6. Llama synthesis
7. Assessment, recommendations, metrics, confidence, and sources

EcoMind separates:

1. Environmental context interpretation
2. Structured knowledge
3. Evidence retrieval
4. Ecological reasoning
5. Natural-language synthesis

📚 Knowledge and RAG

- "environmental_knowledge.json": Predefined environmental relationships.
- "curated_evidence.json": Scientific sources used to ground recommendations.

🛠️ Technology Stack

- Frontend: React, TypeScript, Vite
- Backend: Python, FastAPI, Pydantic, Uvicorn
- AI: Llama, RAG, FAISS, structured environmental knowledge
- Deployment: Vercel frontend, Render backend, hosted Llama inference

📜 License

This project was developed for the Darukaa.Earth AI Biodiversity Intelligence Chatbot Challenge. Add an appropriate project license if required.

👥 Team

EcoMind — AI Biodiversity Intelligence Advisor

Built by:

- Ojas Nivjekar

Independent project.

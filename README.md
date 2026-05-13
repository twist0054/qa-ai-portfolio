# SergioQE — AI-Powered QA Portfolio

**Sergio Juarez | QA Manager | Banking & Fintech**

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Sergio_Juarez-blue)](https://linkedin.com/in/sergio-arturo-juarez-rodriguez-07814787/)

---

## What This Portfolio Demonstrates

An end-to-end AI-augmented Quality Engineering framework built 
specifically for regulated banking and fintech environments. 
Every scenario maps directly to real enterprise QA challenges.

> "Quality is not just about finding bugs — it is about proving compliance."

---

## Portfolio Structure

| Epic | Scenario | Tools | Status |
|------|----------|-------|--------|
| SQAI-E1 | JIRA Story → Xray Test Case Agent | Python, Claude AI, Copilot, Xray | 🔨 In Progress |
| SQAI-E2 | ETL SQL Validation Agent | Python, PostgreSQL, MongoDB, Copilot | 📋 Planned |
| SQAI-E3 | UI Automation with Playwright | Playwright, Python, pytest, Copilot | 📋 Planned |
| SQAI-E4 | API Automation Suite | Python, pytest, requests, Postman | 📋 Planned |
| SQAI-E5 | Full AI QA Orchestrator | All tools combined | 📋 Planned |

---

## Tech Stack

- **Languages:** Python 3.12
- **Testing:** pytest, pytest-html, Playwright
- **AI Tools:** GitHub Copilot, Claude AI
- **Test Management:** JIRA, Xray
- **Databases:** PostgreSQL, MongoDB
- **API Testing:** requests, Postman
- **Version Control:** Git, GitHub

---

## Epic 1 — JIRA Story → Xray Test Case Agent

### What It Does
Takes a JIRA user story as input and automatically generates:
- Structured test cases covering positive, negative, edge, and security scenarios
- All 18 Xray fields populated and ready for import
- CSV export formatted for direct JIRA Xray import
- Coverage validation confirming 100% AC coverage

### Stories Completed
- ✅ SQAI-10 — Story parser with 17 passing tests
- 🔨 SQAI-11 — Test case generator (in progress)
- 📋 SQAI-12 — Xray CSV export
- 📋 SQAI-13 — Config panel
- 📋 SQAI-14 — Xray import
- 📋 SQAI-15 — Coverage validation

### Running the Parser
```bash
# Clone the repo
git clone https://github.com/twist0054/qa-ai-portfolio.git
cd qa-ai-portfolio

# Set up environment
python -m venv .venv
.venv\Scripts\activate
pip install pytest pytest-html requests

# Run the story parser
python 01-jira-to-testcases/story_parser.py

# Run all tests
pytest 01-jira-to-testcases/ -v
```

---

## Current Test Results

Epic 1 — JIRA Story Parser
17 passed in 0.08s ✅
Baseline Tests
4 passed in 0.03s ✅
Total: 21 tests passing


---

## About This Portfolio

Built as part of a structured 10-week learning plan to demonstrate 
AI-augmented QA leadership for Sr. QE Manager roles in 
banking, fintech, and regulated industries.

**Following along?** Connect on LinkedIn for weekly updates as 
each Epic ships.

---

*SergioQE — Building the future of Quality Engineering*

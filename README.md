# SPARK — Autonomous Completion Intelligence System

> **From Intention to Action.**

SPARK is not a reminder app. It is an AI system that actively prevents missed deadlines by understanding your behavioral patterns, calculating completion probability in real time, and intervening before failure occurs.

---

## The Problem

Modern productivity tools organize work. They do not ensure work gets done.

Users miss deadlines because of activation energy, procrastination, decision paralysis, poor estimation, and cognitive overload. Existing AI assistants generate reminders and schedules. These are passive systems.

SPARK actively intervenes before failure occurs.

---

## Core Innovation

SPARK introduces a new productivity paradigm called **Completion Intelligence**.

Instead of optimizing calendars and reminders, SPARK optimizes one metric:

**Probability of Completion.**

Every decision in the system serves a single objective — maximize the chance that every important task gets completed before its deadline.

---

## Key Features

### Completion Momentum Score (CMS)
Every task receives a continuously updated score based on progress velocity, time pressure, feasibility, historical behavior, and AI behavioral adjustment. Not just a deadline countdown — a live probability engine.

### Personal Completion Genome
SPARK builds a unique behavioral intelligence model for each user. It learns peak productivity hours, focus duration, procrastination triggers, estimation accuracy, and recovery patterns. Every recommendation becomes deeply personalized over time.

### Autonomous Task Activation
The hardest part of productivity is starting. When a task is created, SPARK immediately generates a Google Doc outline, milestone checklist, and the single smallest possible first action. Users never start from a blank page.

### Point of No Return (PONR) Detection
Instead of fixed reminders, SPARK calculates the precise moment when remaining work exceeds available productive time. When this threshold approaches, the system enters intervention mode.

### Adaptive Intervention Ladder
Not every situation deserves the same response.

| Level | Type | Action |
|-------|------|--------|
| 0 | Monitoring | Passive observation |
| 1 | Suggestion | Gentle contextual nudge |
| 2 | Momentum | Break work into micro-steps |
| 3 | Collaboration | Active AI co-working |
| 4 | Critical | Calendar restructuring |
| 5 | Recovery | Damage minimization |

### Task Bankruptcy Engine
When everything cannot be completed, SPARK detects the impossible workload, prioritizes by impact, sacrifices low-value tasks, drafts extension emails, and restructures the schedule to maximize overall success.

### Memory Engine
Short-term session memory tracks what happened in the current work session. Long-term behavioral memory (the Completion Genome) evolves permanently after every task. The system becomes smarter with every interaction.

### Reflection Agent
After every completed task, SPARK analyzes what worked, what caused delays, which interventions helped, and updates the Completion Genome with precise behavioral parameter changes.

---

## Multi-Agent Architecture

SPARK is built as a true autonomous multi-agent system powered by Gemini 2.5 Flash via Vertex AI.

| Agent | Responsibility |
|-------|---------------|
| Memory Agent | Assembles behavioral context from short and long-term memory |
| Context Agent | Gathers calendar, workload, and time context |
| Planner Agent | Decomposes tasks into AI-generated milestones |
| Activation Agent | Generates starter materials and document outlines |
| Momentum Agent | Identifies the single next best action |
| Risk Agent | Calculates failure probability with AI analysis |
| Simulation Agent | Detects workload collisions across all tasks |
| Intervention Agent | Generates level-appropriate intervention messages |
| Recovery Agent | Creates damage mitigation plans with email drafts |
| Reflection Agent | Analyzes completed tasks and updates the genome |

---

## Tech Stack

### AI
- Gemini 2.5 Flash via Vertex AI
- Google Gen AI SDK

### Backend
- Python 3.13
- FastAPI
- Cloud Run
- Cloud Tasks
- Cloud Scheduler
- Pub/Sub

### Frontend
- React 18
- TypeScript
- Vite
- Tailwind CSS

### Database
- Cloud Firestore
- BigQuery

### Authentication
- Firebase Authentication (Google OAuth)

### Integrations
- Google Calendar API
- Gmail API
- Google Docs API
- Google Drive API
- Google Tasks API

### Observability
- Cloud Logging
- Cloud Monitoring

---

### API Overview
|GET  |/api/v1/health|                          Liveness probe|
|---|---|---|
|GET  |/api/v1/health/ready|                    Readiness probe|
|POST |/api/v1/tasks|                           Create task (triggers PlannerAgent)|
|GET  |/api/v1/tasks|                           List all tasks|
|GET  |/api/v1/tasks/{id}|                      Task detail|
|GET  |/api/v1/tasks/{id}/milestones|           AI-generated milestones|
|GET  |/api/v1/tasks/{id}/next-action|          MomentumAgent next best action|
|GET  |/api/v1/tasks/{id}/cms|                  Completion Momentum Score|
|POST |/api/v1/tasks/{id}/complete|             Complete task (triggers Reflection)|
|POST |/api/v1/tasks/{id}/recovery-plan|        Recovery Agent plan|
|GET  |/api/v1/genome|                          Raw genome data|
|GET  |/api/v1/genome/full|                     Complete intelligence package|
|GET  |/api/v1/genome/insights|                 AI behavioral insights|
|GET  |/api/v1/genome/productivity|             Hourly heatmap data|
|GET  |/api/v1/analytics/completion-health|     Overall health score|
|GET  |/api/v1/analytics/risk-matrix|          All tasks risk assessment|
|GET  |/api/v1/analytics/simulation|           Workload collision detection|
|GET  |/api/v1/bankruptcy/assess|              Assess workload feasibility|
|POST |/api/v1/bankruptcy/declare|             Declare task bankruptcy|
|GET  |/api/v1/agents/status|                  Registered agents list|
|GET  |/api/v1/agents/memory|                  Current memory state|
|POST |/api/v1/interventions/chat|             AI collaboration chat|
|POST |/api/v1/webhooks/cms-worker|            Manual CMS recalculation|
|POST |/api/v1/webhooks/ponr-worker|           Manual PONR scan|
---

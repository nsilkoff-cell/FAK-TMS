# FAK-TMS: Freight & Accounting Kit - Transportation Management System

A comprehensive transportation management system (TMS) that integrates with Fak (custom accounting software) to streamline load management, carrier sourcing, rate optimization, and invoicing for freight operations.

## Overview

FAK-TMS is designed to:
- **Manage loads** from creation through delivery and invoicing
- **Source carriers** intelligently using multi-factor scoring (cost, on-time %, lane experience)
- **Optimize rates** with margin-based guardrails (10-15% minimum margins)
- **Integrate with external systems**: Fak (accounting), Highway.com (carrier vetting), Teams (load parsing), Front (email automation)
- **Automate workflows** from shipper email/portal to load creation, carrier assignment, and invoice sync

## Tech Stack

- **Backend**: Python (FastAPI)
- **Database**: PostgreSQL
- **Frontend**: React
- **Integrations**: Highway.com API, Microsoft Teams Bot, Front Email Plugin
- **Deployment**: Docker + cloud (AWS/GCP)

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.9+
- Node.js 16+

### Local Development
```bash
# Clone the repo
git clone https://github.com/nsilkoff-cell/FAK-TMS.git
cd FAK-TMS

# Start the full stack (backend + database + frontend)
docker-compose up

# Backend runs on: http://localhost:8000
# Frontend runs on: http://localhost:3000
# API docs: http://localhost:8000/docs
```

See `docs/SETUP.md` for detailed setup instructions.

## Project Structure
```
FAK-TMS/
├── backend/          # Python FastAPI backend
├── frontend/         # React web dashboard
├── integrations/     # External service connectors
│   ├── highway/      # Carrier vetting platform
│   ├── teams_bot/    # Microsoft Teams bot for load parsing
│   ├── front_plugin/ # Email automation
│   └── fak/          # Accounting software sync
├── docs/             # Architecture, API specs, algorithms
└── docker-compose.yml
```

## Key Modules

| Module | Purpose |
|--------|---------|
| **Load Service** | Create, track, and manage freight loads |
| **Carrier Service** | Source carriers, calculate scores, manage assignments |
| **Rate Engine** | Validate rates against margin guardrails |
| **Fak Integration** | Sync load data and rates; pull invoicing data |
| **Highway Integration** | Real-time carrier compliance, insurance, fraud detection |
| **Teams Bot** | Auto-parse load text from Teams messages |
| **Front Plugin** | Email-to-load automation |

## Core Workflows

### 1. Load Creation
- Shipper submits load via email or web portal
- Auto-create load if shipper verified & rate meets thresholds
- Ops team reviews in dashboard

### 2. Carrier Sourcing
- Multi-factor ranking: cost, on-time %, lane experience
- Highway.com data for carrier compliance
- Suggest carriers to ops team; ops has final authority

### 3. Rate Management
- Shipper rate + carrier rate = load financials in Fak
- Margin guardrails: minimum 10-15% margin on all loads
- System suggests options; human books final rate

### 4. Invoicing
- Load completion triggers invoice workflow
- Sync data to Fak for accounting
- Highway.com used for final carrier validation

## Documentation

- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** – System design and module relationships
- **[SETUP.md](docs/SETUP.md)** – Local development setup
- **[API_SPEC.md](docs/API_SPEC.md)** – REST API documentation
- **[MODULES.md](docs/MODULES.md)** – Detailed module descriptions
- **[ALGORITHM.md](docs/ALGORITHM.md)** – Carrier scoring algorithm

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on submitting changes.

## Status

🚀 **In Development** – Repository structure initialized, ready for feature development.

---

**Questions?** Check the docs or open an issue on GitHub.
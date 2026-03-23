# FAK-TMS Architecture

## System Overview

FAK-TMS is a modular transportation management system with clear separation of concerns:
```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React)                         │
│              Dashboard, Load Management UI                   │
└────────────────────┬────────────────────────────────────────┘
                     │ REST API
┌────────────────────▼────────────────────────────────────────┐
│                 Backend (FastAPI)                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │Load Service  │  │Carrier Svc   │  │Rate Engine   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│              Integration Layer                               │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │Fak Sync  │ │Highway   │ │Teams Bot │ │Front     │       │
│  │          │ │Carrier   │ │Load      │ │Email     │       │
│  │(Acct)    │ │Vetting   │ │Parser    │ │Plugin    │       │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                 Data Layer                                   │
│            PostgreSQL Database                               │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │Loads     │ │Carriers  │ │Invoices  │ │Rates     │       │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Backend (Python FastAPI)

**Responsibilities:**
- RESTful API for load, carrier, and invoice management
- Business logic for load creation, carrier sourcing, rate validation
- Integration orchestration

**Structure:**
- `models/` – Database schemas (Load, Carrier, Invoice, Rate)
- `routes/` – API endpoints
- `services/` – Business logic layer
- `database.py` – PostgreSQL connection

### 2. Frontend (React)

**Responsibilities:**
- Dashboard for ops team to view/manage loads
- Load creation form (manual entry)
- Carrier assignment interface
- Rate approval workflow
- Invoice tracking

**Structure:**
- `components/` – Reusable UI components (LoadCard, CarrierList, etc.)
- `pages/` – Full page views (Dashboard, LoadDetail, etc.)
- `services/` – API client calls

### 3. Data Layer (PostgreSQL)

**Core Tables:**
- `loads` – Freight load details (origin, dest, weight, shipper_id, status)
- `carriers` – Carrier info (name, on_time_%, cost_per_mile, etc.)
- `rates` – Load rates (shipper_rate, carrier_rate, margin_%, load_id, carrier_id)
- `invoices` – Billing records (load_id, shipper_invoice, carrier_invoice, status)

**Relationships:**
```
Load ──┬──> Rate ──┬──> Carrier
       │           │
       └──────────> Invoice
```

### 4. Integration Layer

#### **Fak Integration**
- **Inbound**: Pull shipper rates, carrier rates, margin thresholds
- **Outbound**: Push load creation, rate updates, invoice data
- **Sync**: Two-way data flow for financial tracking

#### **Highway.com Integration**
- **Inbound**: Carrier compliance scores, insurance status, fraud detection
- **Use Case**: Real-time carrier validation before booking
- **Note**: Highway is *not* used for load creation or rate management—TMS owns those

#### **Teams Bot**
- **Function**: Auto-parse load text from Teams messages
- **Workflow**: `Paste load text → Bot extracts (origin, dest, weight) → Create load record → Ops reviews`
- **Sufficiency**: Basic info enough to create load; ops fills details later

#### **Front Email Plugin**
- **Function**: Email-to-load automation
- **Workflow**: Shipper emails load info → Plugin extracts → Auto-create load (if verified + rate threshold met) → Ops reviews
- **Gates**: Shipper verified, minimum rate thresholds

---

## Key Workflows

### Load Creation Flow
```
1. Shipper submits (email, Teams, or web portal)
   ↓
2. System extracts: origin, dest, weight, shipper_rate
   ↓
3. Check gates:
   - Is shipper verified?
   - Does shipper_rate meet min margin thresholds?
   ↓
4. If YES: Auto-create load in dashboard (ops reviews)
   If NO: Flag for ops manual review
   ↓
5. Ops adjusts details, confirms load
```

### Carrier Sourcing Flow
```
1. Load needs carrier assignment
   ↓
2. Carrier Service ranks available carriers:
   - Cost (shipper_rate - margin_% = max carrier_cost)
   - On-time % (from database)
   - Lane experience (from Highway + database)
   - Compliance score (from Highway)
   ↓
3. Rate Engine validates carrier_cost against margins:
   - Margin % = (shipper_rate - carrier_cost) / shipper_rate
   - If margin >= threshold (10-15%): OK
   - If margin < threshold: Flag or suggest alternatives
   ↓
4. System suggests ranked list to ops
   ↓
5. Ops selects carrier (ops has final authority)
   ↓
6. Book load, update rates in Fak
```

### Invoice Sync Flow
```
1. Load marked "completed"
   ↓
2. Invoice Service creates records:
   - Shipper invoice (amount owed by shipper to your company)
   - Carrier invoice (amount owed by your company to carrier)
   ↓
3. Sync to Fak accounting:
   - Push invoice records
   - Pull final margin calculation
   ↓
4. Archive load in TMS
```

---

## Data Flow

### Load Lifecycle
```
CREATED → CARRIER_ASSIGNED → IN_TRANSIT → DELIVERED → INVOICED → ARCHIVED
```

### Rate Management
```
Shipper Rate (from Fak/email)
         ↓
    Rate Engine validates margin
         ↓
    Suggests Carrier Cost = Shipper Rate - Margin
         ↓
    Highway provides Carrier Compliance Score
         ↓
    Ops approves Carrier & Rate
         ↓
    Final Rate Synced to Fak
```

---

## Module Dependencies

| Module | Depends On | Notes |
|--------|-----------|-------|
| Load Service | Database | Core CRUD operations |
| Carrier Service | Load Service, Highway Integration | Scores carriers based on load requirements |
| Rate Engine | Carrier Service, Fak Integration | Validates rates against margin guardrails |
| Fak Integration | Database | Two-way sync of rates, loads, invoices |
| Highway Integration | External API | Real-time carrier validation |
| Teams Bot | Load Service | Creates loads from parsed Teams messages |
| Front Plugin | Load Service, Fak Integration | Auto-creates loads from emails |

---

## Scalability Considerations

1. **Database**: PostgreSQL with indexing on `load_id`, `carrier_id`, `status`
2. **API**: FastAPI handles async requests; scale horizontally with multiple instances
3. **Integrations**: Async workers for Fak sync, Teams polling, Front webhooks
4. **Frontend**: React with lazy loading for large load lists

---

## Future Enhancements

- Real-time load tracking (GPS integration)
- Advanced reporting & analytics dashboard
- Machine learning for carrier performance predictions
- Multi-user role-based access control (RBAC)
- Webhook-based integrations instead of polling
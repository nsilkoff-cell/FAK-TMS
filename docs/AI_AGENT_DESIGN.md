# FAK-TMS AI Agent System Design

## Overview

An intelligent assistant integrated into the TMS dashboard that answers questions about business performance, automates operations, and escalates complex issues to the ops team.

Three user types: Internal Ops Team, Customers, and Escalation to Staff.

---

## System Architecture

### Frontend Layer
```
┌─────────────────────────────────────────────┐
│         FAK-TMS Dashboard (React)            │
├─────────────────────────────────────────────┤
│                                              │
│  [Main Dashboard Content]                    │
│                                              │
│  ┌──────────────────────────────────────┐   │
│  │  Chat Button (Bottom Right)          │   │
│  │  Red circle, like StatRabbit         │   │
│  │  Opens modal/sidebar when clicked    │   │
│  └──────────────────────────────────────┘   │
│          ↓ (on click)                       │
│  ┌──────────────────────────────────────┐   │
│  │     Chat Interface Modal             │   │
│  │  ┌────────────────────────────────┐  │   │
│  │  │ Chat History                   │  │   │
│  │  │ [previous messages]            │  │   │
│  │  └────────────────────────────────┘  │   │
│  │  ┌────────────────────────────────┐  │   │
│  │  │ Message Input                  │  │   │
│  │  │ [Type question here...] [Send] │  │   │
│  │  └────────────────────────────────┘  │   │
│  └──────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

### Backend Layer
```
┌─────────────────────────────────────────────────────────┐
│                  FastAPI Backend                        │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Chat API Endpoint: POST /api/chat/message       │  │
│  │  - Receives user message + user_id + user_type  │  │
│  │  - Validates user permissions                   │  │
│  │  - Routes to AI Agent                           │  │
│  └──────────────────────────────────────────────────┘  │
│                        ↓                               │
│  ┌──────────────────────────────────────────────────┐  │
│  │  AI Agent Processor                              │  │
│  │  - Parses user intent                            │  │
│  │  - Determines data access level                  │  │
│  │  - Calls Claude API with context                │  │
│  │  - Executes automations if needed               │  │
│  └──────────────────────────────────────────────────┘  │
│            ↓                    ↓                       │
│  ┌────────────────────┐  ┌──────────────────────────┐ │
│  │ Data Query Layer   │  │ Automation Layer        │ │
│  │ - Query loads      │  │ - Send emails           │ │
│  │ - Query carriers   │  │ - Create tasks          │ │
│  │ - Query customers  │  │ - Send Teams messages   │ │
│  │ - Analytics        │  │ - Update records        │ │
│  └────────────────────┘  └──────────────────────────┘ │
│            ↓                    ↓                       │
│  ┌─────────────────────────────────────────────────┐  │
│  │           PostgreSQL Database                    │  │
│  └─────────────────────────────────────────────────┘  │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### External Integrations
```
┌──────────────────────────────────────┐
│   Claude API (Anthropic)             │
│   - Process natural language         │
│   - Generate responses               │
│   - Make decisions                   │
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│   Microsoft Teams                    │
│   - Send escalation messages         │
│   - Teams bot for direct chat        │
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│   Email Service                      │
│   - Send escalation emails           │
│   - Send bulk carrier emails         │
└──────────────────────────────────────┘
```

---

## User Types & Permissions

### 1. Internal Ops Team

**Access Level:** Full

**Capabilities:**
- View all loads, carriers, customers, rates, invoices
- View analytics and profitability data
- Execute automations
- Escalate to themselves or others

**Example Queries:**
- "What's my margin this week?"
- "Which carriers have the best on-time performance?"
- "Show loads with margins below 10%"
- "Email all carriers in the Midwest asking for capacity"
- "Generate a daily ops report"
- "Flag any loads over 48 hours in transit"

**Automations Available:**
- Send emails (bulk carrier outreach, customer updates)
- Create tasks/reminders
- Update load status
- Generate reports

---

### 2. Customer

**Access Level:** Limited (own data only)

**Capabilities:**
- View only their own loads
- View their own shipment status and tracking
- Ask about delivery times, locations
- Request support (escalate to ops)

**Example Queries:**
- "Where is my shipment?"
- "What's the status of my pending loads?"
- "When will my delivery arrive?"
- "Can I get an update on shipment #12345?"
- "I need to speak to someone about my account"

**Automations Available:**
- None (ops team handles)

**Auth:**
- Email + password login
- Could also use SSO (Google, Microsoft)
- Session token stored in JWT

---

### 3. Escalation/Support Request

**Trigger:** When AI can't answer or customer requests support

**Flow:**
1. AI recognizes escalation needed
2. Creates support ticket in system
3. Sends Teams message to ops channel with:
   - Customer name
   - Question/issue
   - Relevant context (load ID, etc.)
4. Sends email to ops team
5. Ops team receives notification and responds

---

## Data Context for Claude API

When calling Claude, the backend provides:

### For Ops Team:
```json
{
  "user_type": "internal",
  "user_id": "op-12345",
  "user_name": "John Ops Manager",
  "context": {
    "current_date": "2024-03-23",
    "company_totals": {
      "total_loads_this_month": 250,
      "total_revenue": 125000,
      "total_cost": 100000,
      "gross_profit": 25000,
      "average_margin": 20
    },
    "recent_loads": [
      {
        "id": 1,
        "reference": "LOAD-001",
        "shipper_rate": 1500,
        "carrier_cost": 1200,
        "margin": 20,
        "status": "in_transit",
        "carrier": "ABC Trucking"
      }
    ],
    "carrier_performance": [
      {
        "name": "ABC Trucking",
        "on_time_percentage": 95,
        "loads_completed": 45,
        "average_margin": 18
      }
    ]
  },
  "message": "What's my margin this week?"
}
```

### For Customer:
```json
{
  "user_type": "customer",
  "customer_id": "cust-12345",
  "customer_name": "ABC Logistics",
  "context": {
    "current_date": "2024-03-23",
    "your_loads": [
      {
        "id": 1,
        "reference": "LOAD-001",
        "status": "in_transit",
        "pickup_location": "Denver, CO",
        "delivery_location": "Phoenix, AZ",
        "pickup_date": "2024-03-22",
        "estimated_delivery": "2024-03-24",
        "carrier": "ABC Trucking",
        "tracking_url": "https://..."
      }
    ],
    "account_info": {
      "company_name": "ABC Logistics",
      "contact": "john@abc.com",
      "payment_terms": "Net 30",
      "total_loads": 250
    }
  },
  "message": "Where is my shipment?"
}
```---

## Chat Flow Diagram

### Ops Team Flow:
```
User Types Question
    ↓
Chat Endpoint Receives Message
    ↓
Validate User (Is ops team?)
    ↓
Fetch Relevant Data from DB
    ↓
Send to Claude API with Context
    ↓
Claude Analyzes & Responds
    ↓
Does response involve automation?
    ├─ YES → Execute automation (send email, create task, etc.)
    ├─ NO → Return response
    └─ ESCALATE → Create support ticket, notify ops
    ↓
Send Response Back to Frontend
    ↓
Display in Chat Interface
```

### Customer Flow:
```
Customer Types Question
    ↓
Chat Endpoint Receives Message
    ↓
Validate User (Is customer logged in? Own data?)
    ↓
Fetch ONLY Their Loads from DB
    ↓
Send to Claude API with Limited Context
    ↓
Claude Analyzes & Responds
    ↓
Can AI answer with customer's data?
    ├─ YES → Return response
    └─ NO → Escalate to ops team
    ↓
Send Response Back to Frontend
    ↓
Display in Chat Interface
```

---

## Escalation Workflow

When AI escalates:

1. **Create Support Ticket**
```python
   ticket = SupportTicket(
       customer_id=customer_id,
       issue_type="customer_inquiry",  # or "ops_request"
       subject="Customer question: Where is my shipment?",
       description="Customer asked about shipment status for load #123",
       status="open",
       related_load_id=123,
       created_by="AI_Agent"
   )
```

2. **Send Teams Message**
```
   Channel: #ops-support (or direct to ops manager)
   
   🚨 New Support Request
   Customer: ABC Logistics
   Issue: Shipment tracking question
   Load: LOAD-001 (Phoenix → Denver)
   Message: "Where is my shipment?"
   
   [View Details] [Assign to Me]
```

3. **Send Email to Ops Team**
```
   Subject: Support Request - ABC Logistics (LOAD-001)
   
   Customer: ABC Logistics
   Contact: john@abc.com
   
   Issue: Shipment tracking question
   Load Reference: LOAD-001
   Load Status: In Transit
   
   Customer Message: "Where is my shipment?"
   
   [View in Dashboard] [Respond in Teams]
```

4. **Ops Team Responds**
   - Can respond directly in Teams
   - Response sent back to customer chat
   - Ticket marked as resolved

---

## API Endpoints

### Chat Messages
```
POST /api/chat/message
{
  "message": "What's my margin this week?",
  "user_id": "op-12345",
  "user_type": "internal",  // or "customer"
  "conversation_id": "conv-xyz"  // for chat history
}

Response:
{
  "id": "msg-12345",
  "response": "Your margin this week is 22%, up from 19% last week...",
  "executed_actions": [
    {
      "type": "email",
      "status": "sent",
      "recipients": ["carrier1@abc.com", "carrier2@xyz.com"],
      "subject": "Request for Capacity - Midwest Lanes"
    }
  ],
  "escalated": false,
  "ticket_id": null
}
```

### Chat History
```
GET /api/chat/history/{conversation_id}

Response:
{
  "conversation_id": "conv-xyz",
  "user_id": "op-12345",
  "messages": [
    {
      "id": "msg-1",
      "role": "user",
      "content": "What's my margin this week?",
      "timestamp": "2024-03-23T10:00:00Z"
    },
    {
      "id": "msg-2",
      "role": "assistant",
      "content": "Your margin this week is 22%...",
      "timestamp": "2024-03-23T10:00:05Z"
    }
  ]
}
```

### Create/Update Automations
```
POST /api/chat/automation
{
  "type": "scheduled_email",
  "schedule": "daily",
  "time": "09:00",
  "recipients": "all_carriers",
  "subject": "Daily Capacity Request",
  "body": "Asking for capacity in high-demand lanes"
}
```

---

## Database Schema Additions

### ChatConversation Table
```python
class ChatConversation(Base):
    __tablename__ = "chat_conversations"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(100), nullable=False)
    user_type = Column(String(50))  # internal, customer
    started_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
```

### ChatMessage Table
```python
class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey("chat_conversations.id"))
    role = Column(String(20))  # user, assistant
    content = Column(Text)
    executed_actions = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
```

### SupportTicket Table
```python
class SupportTicket(Base):
    __tablename__ = "support_tickets"
    
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    related_load_id = Column(Integer, ForeignKey("loads.id"), nullable=True)
    issue_type = Column(String(50))  # customer_inquiry, ops_request
    subject = Column(String(255))
    description = Column(Text)
    status = Column(String(50))  # open, in_progress, resolved
    assigned_to = Column(String(100), nullable=True)
    created_by = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
```

---

## Teams Bot Integration

Separate from dashboard chat, ops team can also:

1. **Create a Teams Channel Group Chat** with the bot
2. **Ask questions directly in Teams:**
```
   @FAK-TMS Bot what's my margin today?
```
3. **Bot responds in the channel**
4. **Can also receive notifications:**
   - New support requests
   - High-priority load issues
   - Daily operations summary

**Bot Capabilities:**
- Answer same questions as dashboard AI
- Post daily reports
- Alert on exceptions
- Receive escalations from customers

---

## Implementation Phases

### Phase 1: Core Chat Infrastructure
- [ ] Design chat UI component (modal/sidebar)
- [ ] Create chat API endpoint
- [ ] Build Claude integration
- [ ] Create ChatConversation & ChatMessage tables
- [ ] Basic chat history storage

### Phase 2: Ops Team Features
- [ ] Ops team login/auth
- [ ] Data context fetching (loads, carriers, analytics)
- [ ] Claude prompts for ops queries
- [ ] Basic analytics questions

### Phase 3: Customer Features
- [ ] Customer login/registration/auth
- [ ] Customer data isolation (only their loads)
- [ ] Customer-specific prompts
- [ ] Basic tracking queries

### Phase 4: Automations
- [ ] Email automation (send bulk emails)
- [ ] Task creation
- [ ] Load status updates
- [ ] Report generation

### Phase 5: Escalation System
- [ ] Support ticket creation
- [ ] Teams integration
- [ ] Email notifications
- [ ] Escalation workflow

### Phase 6: Teams Bot
- [ ] Teams bot setup
- [ ] Bot message handling
- [ ] Teams notification integration
- [ ] Group chat support---

## Security Considerations

1. **Authentication**
   - Ops team: Existing auth system (TBD)
   - Customers: Email + password or SSO
   - JWT tokens for API calls

2. **Authorization**
   - Ops team: Full database access in AI context
   - Customers: Only their own load data
   - Verify user_id matches requested data

3. **Data Exposure**
   - Don't expose full records to Claude
   - Only necessary fields
   - Anonymize sensitive data if possible

4. **API Rate Limiting**
   - Limit chat messages per user per hour
   - Prevent spam/abuse

5. **Audit Logging**
   - Log all chat messages
   - Log all executed automations
   - Track escalations

---

## Example Prompts for Claude

### For Ops Team Asking "What's my margin this week?"
```
You are an expert freight operations analyst for FAK-TMS, a transportation management system.

Current Context:
- Week of March 17-23, 2024
- Total loads: 50
- Total revenue: $75,000
- Total cost: $60,000
- Gross profit: $15,000
- Average margin: 20%

Top carriers by margin:
- ABC Trucking: 22%
- XYZ Logistics: 19%
- 123 Transport: 18%

Recent low-margin loads:
- LOAD-001: 8% margin (customer: ABC Corp)
- LOAD-002: 10% margin (customer: XYZ Logistics)

Answer the user's question: "What's my margin this week?"

Be concise, data-driven, and actionable.
```

### For Customer Asking "Where is my shipment?"
```
You are a friendly customer service agent for FAK-TMS.

Customer: ABC Logistics
Their loads:
- LOAD-001: Denver → Phoenix, Status: In Transit, Pickup: Mar 22, Est Delivery: Mar 24, Carrier: ABC Trucking

Answer the customer's question: "Where is my shipment?"

Be helpful, friendly, and provide specific details. If you don't have enough info, let them know and offer to escalate to the ops team.
```

---

## Next Steps

1. Review this design
2. Ask questions or request changes
3. Decide on implementation priority
4. Start Phase 1 (chat UI + backend endpoint)
5. Then integrate with database
6. Then add Claude API
7. Then add customer auth
8. Then add automations
9. Then add escalation
10. Then add Teams bot

Ready to start building?
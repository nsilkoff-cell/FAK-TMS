# FAK-TMS User Management & Audit System Design

## Overview

Multi-user authentication system with role-based access control (RBAC) and comprehensive audit logging to track all actions and identify mistakes.

---

## User Roles & Permissions

### 1. Admin
**Access Level:** Full system access + user management

**Permissions:**
- View all loads, carriers, customers, rates, invoices
- Create/edit/delete loads
- Assign carriers
- Approve rates
- Create/manage users
- View audit logs
- Access AI assistant (full)
- View all team member actions
- Generate reports

**Teams:**
- Can see all operations

---

### 2. Operations Manager
**Access Level:** Full operational access (no user management)

**Permissions:**
- View all loads, carriers, customers
- Create/edit loads
- Assign carriers
- Approve rates
- Access AI assistant (full)
- View audit logs (own actions + assigned team)
- Assign tasks to team members
- Cannot create/manage users
- Cannot delete data

**Responsibility:**
- Oversee ops team
- Review team member work
- Handle escalations

---

### 3. Operations Specialist
**Access Level:** Core operational tasks

**Permissions:**
- View all loads, carriers, customers
- Create/edit loads (own and assigned)
- Assign carriers (subject to approval by manager)
- View rates
- Cannot approve rates (manager does)
- Access AI assistant (limited - no automation execution without approval)
- View own audit logs

**Responsibility:**
- Create and manage loads
- Communicate with carriers/customers
- Execute tasks assigned by manager

---

### 4. Dispatcher
**Access Level:** Load assignment and tracking

**Permissions:**
- View all loads
- View carriers and their availability
- Assign carriers to loads (subject to manager approval)
- Track load progress
- Cannot create loads
- Cannot approve rates
- Cannot manage users

**Responsibility:**
- Find best carriers for loads
- Manage assignments
- Track shipments

---

### 5. Customer Service
**Access Level:** Customer communication

**Permissions:**
- View assigned customer loads
- Update customer contact info
- Cannot assign carriers
- Cannot approve rates
- Cannot create loads (only view)
- Access AI assistant (customer service only)

**Responsibility:**
- Handle customer inquiries
- Provide updates
- Manage customer relationships

---

### 6. Finance/Accounting
**Access Level:** Invoicing and rates

**Permissions:**
- View all rates and invoices
- Approve invoices
- View profit/margin data
- Cannot create loads
- Cannot assign carriers
- View audit logs (financial actions only)

**Responsibility:**
- Review rates for accuracy
- Process invoices
- Monitor profitability

---

### 7. Customer (External)
**Access Level:** Own data only

**Permissions:**
- View only own loads
- View own shipment status
- Cannot create loads
- Cannot manage anything
- Access AI assistant (tracking/inquiry only)

**Responsibility:**
- Track shipments
- Ask questions about own loads

---

## Database Schema for Users & Permissions

### User Table
```python
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic Info
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    
    # Authentication
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, index=True)
    
    # Role
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False, index=True)
    
    # Team Assignment
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    manager_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Direct manager
    
    # Status
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    role = relationship("Role")
    team = relationship("Team")
    manager = relationship("User", remote_side=[id], foreign_keys=[manager_id])
    audit_logs = relationship("AuditLog", back_populates="user")
    created_loads = relationship("Load", foreign_keys="Load.created_by_id")
```

### Role Table
```python
class Role(Base):
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)  # admin, ops_manager, ops_specialist, etc.
    description = Column(Text)
    permissions = Column(JSON)  # List of permission strings
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    users = relationship("User", back_populates="role")
```

### Team Table
```python
class Team(Base):
    __tablename__ = "teams"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)  # "West Region", "East Region", etc.
    description = Column(Text)
    manager_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    users = relationship("User")
```

### AuditLog Table (Most Important!)
```python
class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Who Did It
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    user_email = Column(String(255))  # Denormalized for efficiency
    user_role = Column(String(50))  # Denormalized for efficiency
    
    # What Did They Do
    action = Column(String(100), nullable=False, index=True)  
    # Examples: create_load, edit_load, assign_carrier, approve_rate, delete_invoice
    
    resource_type = Column(String(50), nullable=False, index=True)  
    # Examples: load, carrier, customer, rate, invoice
    
    resource_id = Column(Integer, nullable=False, index=True)  
    # The ID of the resource they acted on
    
    # Details of the Change
    old_values = Column(JSON, nullable=True)  # What it was before
    new_values = Column(JSON, nullable=True)  # What it is now
    change_summary = Column(Text)  # Human-readable summary
    
    # Context
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(255), nullable=True)
    
    # Status
    status = Column(String(50))  # success, error, etc.
    error_message = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_audit_user_timestamp', 'user_id', 'timestamp'),
        Index('idx_audit_resource', 'resource_type', 'resource_id'),
        Index('idx_audit_action', 'action', 'timestamp'),
    )
```

### Updates to Load Model
```python
class Load(Base):
    __tablename__ = "loads"
    
    # ... existing fields ...
    
    # Track Who Created/Modified
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    last_modified_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    assigned_to_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Who Approved the Rate
    rate_approved_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    created_by = relationship("User", foreign_keys=[created_by_id])
    last_modified_by = relationship("User", foreign_keys=[last_modified_by_id])
    assigned_to = relationship("User", foreign_keys=[assigned_to_id])
    rate_approved_by = relationship("User", foreign_keys=[rate_approved_by_id])
```

---

## Authentication Flow

### Login
```
User enters email + password
    ↓
Validate credentials against password_hash
    ↓
Check if user is_active
    ↓
Generate JWT token (expires in 24 hours)
    ↓
Log login in AuditLog
    ↓
Return token to frontend
    ↓
Frontend stores token in localStorage/sessionStorage
    ↓
All API calls include token in Authorization header
```

### Authorization Check
```
User makes API request
    ↓
Backend validates JWT token
    ↓
Extract user_id from token
    ↓
Fetch user and their role
    ↓
Check if role has permission for this action
    ↓
If YES → Execute request + log in AuditLog
If NO → Return 403 Forbidden + log attempt in AuditLog
```

---

## Audit Logging Strategy

### What Gets Logged?

**Every action:**
- Create load
- Edit load (any field)
- Assign carrier
- Approve rate
- Create rate
- Delete anything
- Approve invoice
- Create user
- Delete user
- Change user role
- Login/logout
- Failed login attempts
- Unauthorized access attempts

### Example Audit Log Entry

**When Operations Specialist creates a load:**
```python
AuditLog(
    user_id=5,
    user_email="john@company.com",
    user_role="operations_specialist",
    action="create_load",
    resource_type="load",
    resource_id=12345,
    old_values=None,  # No old value for create
    new_values={
        "customer_id": 100,
        "pickup_location_id": 5,
        "delivery_location_id": 10,
        "weight": 45000,
        "shipper_rate": 1500,
        "status": "created"
    },
    change_summary="Created load #LOAD-001: Denver to Phoenix, 45,000 lbs, $1,500",
    timestamp=datetime.utcnow(),
    ip_address="192.168.1.100",
    status="success"
)
```

**When someone edits a load:**
```python
AuditLog(
    user_id=3,
    user_email="ops_manager@company.com",
    user_role="operations_manager",
    action="edit_load",
    resource_type="load",
    resource_id=12345,
    old_values={
        "weight": 45000,
        "shipper_rate": 1500
    },
    new_values={
        "weight": 46000,  # Changed
        "shipper_rate": 1550  # Changed
    },
    change_summary="Updated load #LOAD-001: Weight 45000→46000 lbs, Rate $1500→$1550",
    timestamp=datetime.utcnow(),
    ip_address="192.168.1.105",
    status="success"
)
```

**When someone makes an unauthorized attempt:**
```python
AuditLog(
    user_id=5,
    user_email="john@company.com",
    user_role="operations_specialist",
    action="attempted_delete_invoice",
    resource_type="invoice",
    resource_id=999,
    old_values=None,
    new_values=None,
    change_summary="User with operations_specialist role attempted to delete invoice (permission denied)",
    timestamp=datetime.utcnow(),
    ip_address="192.168.1.100",
    status="error",
    error_message="Permission denied: operations_specialist cannot delete invoices"
)
```

---

## Admin Dashboard for Auditing

### View 1: Team Performance Overview
Shows stats on each team member:
```
Team: West Region (Manager: Sarah Johnson)

John Doe (Operations Specialist)
- Loads created: 45
- Loads with errors: 2
- Error rate: 4.4%
- Avg load time: 2.3 hours
- Last action: 10 min ago
[View Details]

Jane Smith (Operations Specialist)
- Loads created: 52
- Loads with errors: 0
- Error rate: 0%
- Avg load time: 1.9 hours
- Last action: 2 min ago
[View Details]
```

### View 2: Individual Audit Trail
Shows all actions by a specific user:
```
Audit Log: John Doe (john@company.com)

[Date] [Time] [Action] [Resource] [Change] [Status]
Mar 23 10:45 edit_load LOAD-001 Weight 45000→46000 lbs ERROR
Mar 23 10:42 create_load LOAD-002 New load created SUCCESS
Mar 23 10:38 assign_carrier LOAD-001 Assigned to ABC Trucking SUCCESS
Mar 23 10:35 create_rate LOAD-001 Rate $1500, margin 20% SUCCESS

[View Details] [Export CSV]
```

### View 3: Errors & Issues
Shows what went wrong:
```
Recent Errors & Issues

⚠️ Low Margin Loads
- LOAD-001: 5% margin (created by John Doe at 10:45am)
- LOAD-005: 8% margin (created by Jane Smith at 9:30am)

❌ Unauthorized Attempts
- John Doe tried to delete invoice INV-001 (permission denied)
- Jane Smith tried to create user (permission denied)

🔴 Data Issues
- LOAD-003: Missing carrier assignment (5 hours old)
- LOAD-009: Shipper rate not approved (3 hours old)

[View Details] [Filter by User] [Export Report]
```

### View 4: Search & Filter
```
Search Audit Logs

Filter by:
- User: [dropdown: All / John Doe / Jane Smith / ...]
- Action: [dropdown: All / create_load / edit_load / ...]
- Resource Type: [dropdown: All / load / rate / invoice / ...]
- Date Range: [from] [to]
- Status: [All / Success / Error]

[Search] [Clear Filters] [Export CSV]

Results: 157 audit logs found
[List of results with pagination]
```

---

## API Endpoints for Auth & Users

### Login
```
POST /api/auth/login
{
  "email": "john@company.com",
  "password": "secure_password"
}

Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": 5,
    "email": "john@company.com",
    "full_name": "John Doe",
    "role": "operations_specialist",
    "team": "West Region"
  }
}
```

### Get Current User
```
GET /api/auth/me
Headers: Authorization: Bearer {token}

Response:
{
  "id": 5,
  "email": "john@company.com",
  "full_name": "John Doe",
  "role": "operations_specialist",
  "permissions": ["view_loads", "create_load", "view_rates"],
  "team": "West Region",
  "manager": "Sarah Johnson"
}
```

### Create User (Admin Only)
```
POST /api/users
Headers: Authorization: Bearer {admin_token}
{
  "email": "newuser@company.com",
  "full_name": "New User",
  "role": "operations_specialist",
  "team_id": 1
}

Response:
{
  "id": 10,
  "email": "newuser@company.com",
  "full_name": "New User",
  "role": "operations_specialist"
}
```

### Get Audit Logs (Filtered)
```
GET /api/audit-logs?user_id=5&action=create_load&date_from=2024-03-20&date_to=2024-03-23

Response:
{
  "total": 45,
  "logs": [
    {
      "id": 1234,
      "timestamp": "2024-03-23T10:45:00Z",
      "user": "John Doe",
      "action": "create_load",
      "resource": "LOAD-001",
      "change_summary": "Created load with 45000 lbs",
      "status": "success"
    },
    // ... more logs
  ]
}
```

### Get User Performance Metrics
```
GET /api/users/5/metrics

Response:
{
  "user": "John Doe",
  "period": "2024-03",
  "loads_created": 45,
  "loads_with_errors": 2,
  "error_rate": 4.4,
  "avg_time_per_load": 2.3,
  "margins": {
    "average": 18.5,
    "low_margin_count": 2,
    "zero_margin_count": 0
  },
  "tasks_completed": 38,
  "tasks_pending": 3
}
```

---

## Default Roles Setup

When you first deploy FAK-TMS:
```python
# Create default roles
admin_role = Role(
    name="admin",
    description="Full system access",
    permissions=[
        "view_all", "create_all", "edit_all", "delete_all",
        "manage_users", "view_audit_logs", "execute_automations"
    ]
)

ops_manager_role = Role(
    name="operations_manager",
    description="Full operational access, manage team",
    permissions=[
        "view_all", "create_load", "edit_load", "assign_carrier",
        "approve_rate", "view_audit_logs", "execute_automations",
        "manage_team"
    ]
)

ops_specialist_role = Role(
    name="operations_specialist",
    description="Create and manage loads",
    permissions=[
        "view_all", "create_load", "edit_own_load", "assign_carrier_suggest",
        "view_own_audit_logs"
    ]
)

# Create your first admin user
admin_user = User(
    email="noam@company.com",
    full_name="Noam",
    password_hash=hash_password("secure_password"),
    role=admin_role,
    is_active=True
)
```

---

## Security Best Practices

1. **Password Security**
   - Hash with bcrypt (not plain text)
   - Min 8 characters, require mix of uppercase/lowercase/numbers
   - Require password change every 90 days (optional)

2. **Token Security**
   - JWT tokens expire in 24 hours
   - Refresh tokens for longer sessions
   - Store token in httpOnly cookie (not localStorage) for extra security

3. **Audit Log Security**
   - Cannot be edited or deleted (append-only)
   - Store sensitive changes but don't store passwords
   - Encrypt at rest in database

4. **Rate Limiting**
   - Limit login attempts (5 failed = lock account for 15 min)
   - Limit API calls per user per hour
   - Prevent brute force attacks

5. **Session Management**
   - One active session per user (or allow multiple)
   - Log out automatically after 1 hour of inactivity
   - Log out when user is deactivated

---

## Implementation Phases

### Phase 1: User Management
- [ ] User table and authentication
- [ ] Role table with permissions
- [ ] Login/logout endpoints
- [ ] JWT token generation

### Phase 2: Authorization
- [ ] Permission checking middleware
- [ ] Role-based access control
- [ ] Protect API endpoints

### Phase 3: Audit Logging
- [ ] AuditLog table
- [ ] Auto-log all actions
- [ ] Track changes (old → new)

### Phase 4: Admin Dashboard
- [ ] View team performance
- [ ] View individual audit trails
- [ ] Search/filter logs
- [ ] Export reports

### Phase 5: User Management UI
- [ ] Create user form (admin only)
- [ ] Manage roles
- [ ] Deactivate users
- [ ] Reset passwords

---

## Example: Tracking a Mistake

**Scenario:** A load was created with a 5% margin instead of 20%.

**How to find out:**
1. Admin goes to Dashboard → Audit Logs
2. Filters: Action = "create_load", Date = "March 23"
3. Sees John Doe created LOAD-001 at 10:45am
4. Clicks "View Details"
5. Sees: "Created load with shipper_rate=$1500, carrier_cost=$1428, margin=4.8%"
6. Sends message to John: "Hey, LOAD-001 has too low margin. Let's adjust the rate."
7. Admin can also see that John edited the load later: "Changed shipper_rate $1500→$1600"
8. Can track the entire timeline

---

## Next Steps

1. Review this design
2. Ask questions
3. Start implementation when ready
4. First: Create User table + Role table
5. Then: Add login endpoint
6. Then: Add audit logging to all actions
7. Then: Build admin dashboard

Ready to implement?
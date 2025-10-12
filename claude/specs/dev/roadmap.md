# DDMS Implementation Plan

This document outlines the phased implementation plan for the Device Data Monitoring System based on user requirements.

## Implementation Strategy

The implementation follows a **bottom-up, incremental approach**:
1. Foundation first (database, auth, core services)
2. Device management and data ingestion
3. Real-time monitoring and visualization
4. Historical data and analytics
5. Advanced features (grouping, i18n, exports)

Each phase builds upon the previous one, allowing for early testing and validation.

---

## Phase 1: Foundation & Authentication

**Goal**: Establish core infrastructure, database schema, and user authentication system.

### 1.1 Database Schema & Models
**Requirements**: DDMS-DATA-010, DDMS-DATA-011, DDMS-DATA-020

**Tasks**:
- [ ] Design database schema (ERD)
  - Users table (id, username, password_hash, role, language_preference, created_at)
  - Devices table (id, name, description, connection_params, sampling_interval, thresholds, status, last_reading_at)
  - Device readings table (TimescaleDB hypertable: device_id, timestamp, value)
  - Groups table (id, name, created_at)
  - Device-group mapping table (device_id, group_id)
- [ ] Create SQLAlchemy models in `backend/ddms/db/models.py`
  - User model with role enum (owner, admin, viewer)
  - Device model with JSON fields for connection_params and thresholds
  - DeviceReading model with TimescaleDB configuration
  - Group and DeviceGroup models
- [ ] Create Alembic migration for initial schema
- [ ] Configure TimescaleDB hypertable for device_readings
- [ ] Create repository classes in `backend/ddms/db/repositories/`
  - UserRepository (CRUD operations)
  - DeviceRepository
  - ReadingRepository
  - GroupRepository

**Files**:
- `backend/ddms/db/models.py`
- `backend/ddms/db/repositories/user.py`
- `backend/ddms/db/repositories/device.py`
- `backend/ddms/db/repositories/reading.py`
- `backend/ddms/db/repositories/group.py`
- `backend/alembic/versions/001_initial_schema.py`

### 1.2 Authentication System
**Requirements**: DDMS-AUTH-010, DDMS-AUTH-011, DDMS-AUTH-020, DDMS-AUTH-021

**Tasks**:
- [ ] Implement password hashing with Argon2 in `backend/ddms/core/security.py`
- [ ] Implement JWT token generation and validation
- [ ] Create default owner account on first startup
- [ ] Implement authentication endpoints in `backend/ddms/api/auth.py`
  - POST /api/auth/login (returns JWT in HTTP-only cookie)
  - POST /api/auth/logout (clears cookie)
  - GET /api/auth/me (returns current user info)
- [ ] Create dependency for role-based access control
  - `require_owner` dependency
  - `require_admin` dependency (owner + admin)
  - `require_authenticated` dependency (all logged-in users)
- [ ] Create Pydantic schemas in `backend/ddms/schemas/auth.py`
  - LoginRequest, LoginResponse
  - UserResponse
- [ ] Write unit tests for auth service

**Files**:
- `backend/ddms/core/security.py`
- `backend/ddms/core/dependencies.py`
- `backend/ddms/api/auth.py`
- `backend/ddms/schemas/auth.py`
- `backend/ddms/services/auth.py`
- `backend/tests/unit/test_auth.py`

### 1.3 User Management
**Requirements**: DDMS-AUTH-030, DDMS-AUTH-040

**Tasks**:
- [ ] Implement user management endpoints in `backend/ddms/api/users.py`
  - GET /api/users (owner only)
  - POST /api/users (admin/owner, create admin/viewer)
  - PATCH /api/users/{id} (update username/password)
  - DELETE /api/users/{id} (owner/admin, prevent self-delete)
- [ ] Create Pydantic schemas in `backend/ddms/schemas/user.py`
  - UserCreate, UserUpdate, UserResponse
  - Role enum (owner, admin, viewer)
- [ ] Create user service in `backend/ddms/services/user.py`
- [ ] Write unit tests

**Files**:
- `backend/ddms/api/users.py`
- `backend/ddms/schemas/user.py`
- `backend/ddms/services/user.py`
- `backend/tests/unit/test_users.py`

### 1.4 Frontend Auth & Layout
**Requirements**: DDMS-AUTH-010 to DDMS-AUTH-040, DDMS-UI-010 to DDMS-UI-090

**Tasks**:
- [ ] Create API client in `frontend/src/lib/api.ts`
  - Axios instance with credentials
  - Error handling interceptors
- [ ] Create auth store in `frontend/src/store/auth.ts` (Zustand)
  - Login/logout actions
  - Current user state
  - Role checks
- [ ] Create login page in `frontend/src/features/auth/LoginPage.tsx`
- [ ] Create app layout in `frontend/src/app/Layout.tsx`
  - Header with user menu and logout
  - Sidebar navigation
  - Main content area
- [ ] Create protected route wrapper
- [ ] Create user management UI (owner only)
  - User list with roles
  - Create/edit/delete modals
- [ ] Add loading states and error handling

**Files**:
- `frontend/src/lib/api.ts`
- `frontend/src/store/auth.ts`
- `frontend/src/features/auth/LoginPage.tsx`
- `frontend/src/features/users/UserManagement.tsx`
- `frontend/src/app/Layout.tsx`
- `frontend/src/app/ProtectedRoute.tsx`

**Testing Phase 1**:
```bash
# Backend tests
cd backend
alembic upgrade head  # Apply migrations
pytest tests/unit/test_auth.py tests/unit/test_users.py

# Manual API testing
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"owner","password":"defaultpass"}'

curl http://localhost:8000/api/auth/me \
  -H "Cookie: access_token=<token>"

curl http://localhost:8000/api/users \
  -H "Cookie: access_token=<token>"
```

**Frontend verification**:
- Navigate to http://localhost:3000
- Should redirect to /login
- Login with default owner credentials
- Should see main layout with user menu
- Navigate to Users page (owner only)
- Create a new admin user
- Logout and login as admin
- Verify admin can manage users
- Create viewer user and verify view-only access

**Deliverable**: Working login system with role-based access control and user management UI.

---

## Phase 2: Device Management & Configuration

**Goal**: Enable device CRUD operations and configuration.

### 2.1 Device Models & API
**Requirements**: DDMS-DEV-010 to DDMS-DEV-042

**Tasks**:
- [ ] Implement device endpoints in `backend/ddms/api/devices.py`
  - GET /api/devices (list with filters)
  - POST /api/devices (admin/owner only)
  - GET /api/devices/{id}
  - PATCH /api/devices/{id} (admin/owner only)
  - DELETE /api/devices/{id} (admin/owner only, always keep historical data)
- [ ] Create Pydantic schemas in `backend/ddms/schemas/device.py`
  - DeviceCreate, DeviceUpdate, DeviceResponse
  - ConnectionParams (Modbus TCP/RTU settings)
  - ThresholdConfig (warning and critical levels)
- [ ] Create device service in `backend/ddms/services/device.py`
  - CRUD operations
  - Validation logic
- [ ] Write unit tests

**Files**:
- `backend/ddms/api/devices.py`
- `backend/ddms/schemas/device.py`
- `backend/ddms/services/device.py`
- `backend/tests/unit/test_devices.py`

### 2.2 Device Configuration UI
**Requirements**: DDMS-DEV-010 to DDMS-DEV-042

**Tasks**:
- [ ] Create device list page in `frontend/src/features/devices/DeviceList.tsx`
  - Table with name, status, last reading, actions
  - Status indicators (online/offline/error)
  - Filter and search
- [ ] Create device form in `frontend/src/features/devices/DeviceForm.tsx`
  - Basic info (name, description, units)
  - Modbus connection settings
  - Sampling interval
  - Threshold configuration (warning/critical)
- [ ] Create device store in `frontend/src/store/devices.ts`
- [ ] Use TanStack Query for data fetching and caching
- [ ] Add form validation (Ant Design Form)
- [ ] Create delete confirmation modal

**Files**:
- `frontend/src/features/devices/DeviceList.tsx`
- `frontend/src/features/devices/DeviceForm.tsx`
- `frontend/src/features/devices/DeviceCard.tsx`
- `frontend/src/store/devices.ts`

**Testing Phase 2**:
```bash
# Backend tests
pytest tests/unit/test_devices.py

# API testing
curl -X POST http://localhost:8000/api/devices \
  -H "Content-Type: application/json" \
  -H "Cookie: access_token=<token>" \
  -d '{
    "name": "Temperature Sensor 1",
    "description": "Warehouse temperature",
    "units": "°C",
    "connection_params": {
      "type": "tcp",
      "host": "192.168.1.100",
      "port": 502,
      "register": 0,
      "data_type": "float32"
    },
    "sampling_interval": 60,
    "thresholds": {
      "warning": 30,
      "critical": 35
    }
  }'

curl http://localhost:8000/api/devices
```

**Frontend verification**:
- Login as admin or owner
- Navigate to Devices page
- Click "Add Device" button
- Fill form with Modbus TCP settings and thresholds
- Submit and verify device appears in list
- Edit device and change threshold values
- Delete device (with confirmation)
- Verify viewer user can view but not edit/delete

**Deliverable**: Complete device management UI with CRUD operations.

---

## Phase 3: Data Ingestion & Polling

**Goal**: Connect to devices via Modbus and store readings in database.

### 3.1 Modbus Communication
**Requirements**: DDMS-PROTO-010 to DDMS-PROTO-012

**Tasks**:
- [ ] Create Modbus client wrapper in `backend/ddms/ingestion/modbus_client.py`
  - Support for Modbus TCP
  - Support for Modbus RTU
  - Connection pooling
  - Error handling and retries
  - Timeout configuration
- [ ] Create device poller in `backend/ddms/ingestion/poller.py`
  - Read from configured registers
  - Parse data types (int16, uint16, float32, etc.)
  - Store readings in database
  - Update device status and last_reading_at
  - Handle connection errors
- [ ] Write unit tests with mocked Modbus devices

**Files**:
- `backend/ddms/ingestion/modbus_client.py`
- `backend/ddms/ingestion/poller.py`
- `backend/tests/unit/test_modbus.py`

### 3.2 Scheduler Integration
**Requirements**: DDMS-DEV-013, DDMS-MON-020

**Tasks**:
- [ ] Configure APScheduler in `backend/ddms/scheduler/jobs.py`
  - Job for polling devices at their configured intervals
- [ ] Implement dynamic job management
  - Add job when device is created
  - Update job when sampling interval changes
  - Remove job when device is deleted
- [ ] Add scheduler startup/shutdown in main.py
- [ ] Add logging for scheduler events

**Files**:
- `backend/ddms/scheduler/jobs.py`
- `backend/ddms/scheduler/manager.py`
- `backend/ddms/main.py` (updated)

**Testing Phase 3**:
```bash
# Unit tests with mocked Modbus
pytest tests/unit/test_modbus.py

# Use Modbus simulator for integration testing
python3 -m pymodbus.simulator --modbus_server tcp --modbus_port 5020

# Check scheduler logs
docker compose logs backend | grep -i "scheduler\|polling"

# Verify data is being stored
docker compose exec db psql -U ddms -d ddms -c \
  "SELECT device_id, timestamp, value FROM device_readings ORDER BY timestamp DESC LIMIT 10;"

# Check device status updates
curl http://localhost:8000/api/devices/1
# Should show: last_reading_at timestamp, status: "online"
```

**Manual verification**:
- Create a device pointing to Modbus simulator
- Wait for sampling interval (or trigger manually)
- Check backend logs for successful readings
- Query database to verify data is stored
- Check device status shows "online"
- Stop Modbus simulator and verify status changes to "offline"
- Restart simulator and verify recovery

**Deliverable**: Devices actively polling and storing data in database.

---

## Phase 4: Real-time Monitoring & Visualization

**Goal**: Display live device data with charts and warnings.

### 4.1 WebSocket Real-time Updates
**Requirements**: DDMS-MON-010, DDMS-MON-020

**Tasks**:
- [ ] Implement WebSocket endpoint in `backend/ddms/realtime/websocket.py`
  - Connection management
  - Subscribe to device updates
  - Broadcast new readings to connected clients
- [ ] Integrate with data ingestion
  - Publish reading events to WebSocket connections
- [ ] Add authentication for WebSocket connections
- [ ] Handle connection lifecycle (connect/disconnect/reconnect)

**Files**:
- `backend/ddms/realtime/websocket.py`
- `backend/ddms/realtime/manager.py`

### 4.2 Real-time Data API
**Requirements**: DDMS-MON-010 to DDMS-MON-060

**Tasks**:
- [ ] Create readings endpoint in `backend/ddms/api/readings.py`
  - GET /api/devices/{id}/readings/latest (current value)
  - GET /api/devices/{id}/readings/current (last N readings)
- [ ] Add threshold evaluation logic
  - Calculate warning/critical status
- [ ] Return status indicators with readings

**Files**:
- `backend/ddms/api/readings.py`
- `backend/ddms/services/reading.py`
- `backend/ddms/schemas/reading.py`

### 4.3 Dashboard UI
**Requirements**: DDMS-MON-010 to DDMS-MON-060

**Tasks**:
- [ ] Create dashboard page in `frontend/src/features/dashboard/Dashboard.tsx`
  - Grid layout for multiple devices
  - Device cards with current readings
  - Status indicators (normal/warning/critical)
- [ ] Create gauge chart component using ECharts
  - Display current value
  - Show threshold zones (green/yellow/red)
- [ ] Create line chart component for recent trend
  - Last N minutes of data
  - Threshold overlay lines
  - Color-coded regions (optional)
- [ ] Implement WebSocket client in `frontend/src/lib/websocket.ts`
  - Auto-reconnect logic
  - Subscribe to device updates
- [ ] Add real-time updates to charts
  - Smooth animations
  - Auto-scroll time axis

**Files**:
- `frontend/src/features/dashboard/Dashboard.tsx`
- `frontend/src/features/dashboard/DeviceCard.tsx`
- `frontend/src/components/charts/GaugeChart.tsx`
- `frontend/src/components/charts/LineChart.tsx`
- `frontend/src/lib/websocket.ts`
- `frontend/src/store/realtime.ts`

**Testing Phase 4**:
```bash
# Test WebSocket connection
# Install wscat: npm install -g wscat
wscat -c "ws://localhost:8000/ws?token=<jwt_token>"

# Should receive messages like:
# {"device_id": 1, "timestamp": "2025-10-10T10:30:00Z", "value": 23.5, "status": "normal"}

# Test real-time API
curl http://localhost:8000/api/devices/1/readings/latest
curl http://localhost:8000/api/devices/1/readings/current?limit=20
```

**Frontend verification**:
- Login and navigate to Dashboard
- Should see device cards with current readings
- Verify gauge charts show current values with color zones
- Verify line charts show recent trend
- Watch for real-time updates (values should change automatically)
- Trigger a warning by adjusting threshold or simulator value
  - Device card should show yellow warning indicator
  - Chart should show yellow zone highlighting
- Trigger a critical alert
  - Device card should show red critical indicator
  - Chart should show red zone highlighting
- Open browser DevTools Network tab, verify WebSocket connection is active
- Refresh page, verify auto-reconnect works

**Deliverable**: Real-time monitoring dashboard with live charts and warnings.

---

## Phase 5: Historical Data & Analytics

**Goal**: Enable historical data queries, visualization, and export.

### 5.1 Historical Data API
**Requirements**: DDMS-HIST-010 to DDMS-HIST-030

**Tasks**:
- [ ] Implement historical endpoints in `backend/ddms/api/readings.py`
  - GET /api/devices/{id}/readings/history
    - Query params: start_time, end_time, interval (aggregation)
  - GET /api/devices/{id}/readings/export (CSV download)
- [ ] Implement aggregation logic
  - Downsample for long time ranges
  - Calculate min/max/avg for intervals
- [ ] Optimize queries with TimescaleDB functions
  - time_bucket for aggregation
  - Continuous aggregates for performance

**Files**:
- `backend/ddms/api/readings.py` (updated)
- `backend/ddms/services/reading.py` (updated)
- `backend/ddms/schemas/reading.py` (updated)

### 5.2 Historical Charts UI
**Requirements**: DDMS-HIST-010 to DDMS-HIST-030

**Tasks**:
- [ ] Create history page in `frontend/src/features/history/HistoryPage.tsx`
  - Device selector
  - Time range picker (custom ranges)
  - Historical line chart
- [ ] Add threshold overlay
  - Show historical threshold values
  - Highlight violations
- [ ] Create export button
  - Download CSV with time range
  - Include metadata (device name, units, thresholds)
- [ ] Add loading states for large queries

**Files**:
- `frontend/src/features/history/HistoryPage.tsx`
- `frontend/src/features/history/HistoryChart.tsx`
- `frontend/src/components/TimeRangePicker.tsx`
- `frontend/src/utils/export.ts`

**Testing Phase 5**:
```bash
# Test historical data API
curl "http://localhost:8000/api/devices/1/readings/history?start_time=2025-10-09T00:00:00Z&end_time=2025-10-10T23:59:59Z"

# Test aggregation for long ranges
curl "http://localhost:8000/api/devices/1/readings/history?start_time=2025-09-01T00:00:00Z&end_time=2025-10-10T23:59:59Z&interval=1h"

# Test CSV export
curl "http://localhost:8000/api/devices/1/readings/export?start_time=2025-10-09T00:00:00Z&end_time=2025-10-10T23:59:59Z" \
  --output device1_history.csv

# Verify CSV content
head device1_history.csv
# Should show: timestamp,value,status (with metadata header)
```

**Frontend verification**:
- Navigate to History page
- Select a device from dropdown
- Use time range picker to select custom range
- Chart should display data with threshold lines
- Click "Export CSV" button
- Verify CSV file downloads with correct data
- Verify threshold violations are highlighted on chart
- Check loading indicator appears during data fetch

**Deliverable**: Historical data viewer with CSV export.

---

## Phase 6: Device Grouping

**Goal**: Enable logical grouping of devices with group-level views.

### 6.1 Group Management API
**Requirements**: DDMS-GRP-010 to DDMS-GRP-040

**Tasks**:
- [ ] Implement group endpoints in `backend/ddms/api/groups.py`
  - GET /api/groups
  - POST /api/groups (admin/owner only)
  - PATCH /api/groups/{id} (admin/owner only)
  - DELETE /api/groups/{id} (admin/owner only)
  - POST /api/groups/{id}/devices/{device_id} (add device)
  - DELETE /api/groups/{id}/devices/{device_id} (remove device)
- [ ] Enforce single-group-per-device constraint
- [ ] Create Pydantic schemas in `backend/ddms/schemas/group.py`
- [ ] Create group service in `backend/ddms/services/group.py`

**Files**:
- `backend/ddms/api/groups.py`
- `backend/ddms/schemas/group.py`
- `backend/ddms/services/group.py`
- `backend/tests/unit/test_groups.py`

### 6.2 Group Monitoring
**Requirements**: DDMS-GRP-050, DDMS-GRP-051

**Tasks**:
- [ ] Add group readings endpoints
  - GET /api/groups/{id}/readings/current
  - GET /api/groups/{id}/readings/history

**Files**:
- `backend/ddms/api/groups.py` (updated)
- `backend/ddms/services/group.py` (updated)

### 6.3 Group UI
**Requirements**: DDMS-GRP-010 to DDMS-GRP-051

**Tasks**:
- [ ] Create group management page
  - List of groups
  - Create/edit/delete groups
  - Assign devices to groups (single group per device)
- [ ] Create group dashboard view
  - Grid of all devices in group
  - Multi-device chart overlay

**Files**:
- `frontend/src/features/groups/GroupList.tsx`
- `frontend/src/features/groups/GroupForm.tsx`
- `frontend/src/features/groups/GroupDashboard.tsx`
- `frontend/src/store/groups.ts`

**Testing Phase 6**:
```bash
# Test group management API
curl -X POST http://localhost:8000/api/groups \
  -H "Content-Type: application/json" \
  -H "Cookie: access_token=<token>" \
  -d '{"name": "Warehouse Sensors"}'

curl http://localhost:8000/api/groups

# Add devices to group
curl -X POST http://localhost:8000/api/groups/1/devices/1 \
  -H "Cookie: access_token=<token>"

# Get group readings
curl http://localhost:8000/api/groups/1/readings/current
curl "http://localhost:8000/api/groups/1/readings/history?start_time=2025-10-09T00:00:00Z&end_time=2025-10-10T23:59:59Z"
```

**Frontend verification**:
- Login as admin/owner
- Navigate to Groups page
- Create a new group "Production Line A"
- Click "Assign Devices" button
- Select devices and add to group (one group per device)
- Navigate to group dashboard
- Verify all group devices are displayed in grid
- Verify charts overlay all device data
- Remove a device from group and verify it disappears
- Delete group and verify devices are not deleted

**Deliverable**: Device grouping with group-level monitoring.

---

## Phase 7: Internationalization

**Goal**: Support English and Chinese languages.

### 7.1 Backend i18n
**Requirements**: DDMS-I18N-010 to DDMS-I18N-040

**Tasks**:
- [ ] Add language preference to user settings
  - PATCH /api/users/{id}/preferences
- [ ] Update UserResponse schema to include language
- [ ] Store language preference in database

**Files**:
- `backend/ddms/api/users.py` (updated)
- `backend/ddms/schemas/user.py` (updated)

### 7.2 Frontend i18n
**Requirements**: DDMS-I18N-010 to DDMS-I18N-040

**Tasks**:
- [ ] Configure react-i18next in `frontend/src/i18n/config.ts`
- [ ] Create translation files
  - `frontend/src/i18n/locales/en-US.json`
  - `frontend/src/i18n/locales/zh-CN.json`
- [ ] Translate all UI strings
  - Navigation labels
  - Form labels and placeholders
  - Error messages
  - Button text
  - Chart labels
- [ ] Add language switcher to user menu
- [ ] Persist language preference to backend
- [ ] Initialize i18n with user's saved preference

**Files**:
- `frontend/src/i18n/config.ts`
- `frontend/src/i18n/locales/en-US.json`
- `frontend/src/i18n/locales/zh-CN.json`
- `frontend/src/components/LanguageSwitcher.tsx`

**Testing Phase 7**:
```bash
# Test language preference API
curl -X PATCH http://localhost:8000/api/users/1/preferences \
  -H "Content-Type: application/json" \
  -H "Cookie: access_token=<token>" \
  -d '{"language": "zh-CN"}'

curl http://localhost:8000/api/auth/me
# Should show: "language": "zh-CN"
```

**Frontend verification**:
- Login to application (default English)
- All UI elements should be in English
- Click user menu → Language → 中文
- All UI text should change to Chinese
- Refresh page, language should persist
- Logout and login, language preference should be restored
- Switch back to English and verify all text changes
- Test with different user accounts, each should have independent preference

**Deliverable**: Full English and Chinese language support.

---

## Phase 8: Polish & Testing

**Goal**: Ensure production readiness with comprehensive testing and UI polish.

### 8.1 Testing
**Tasks**:
- [ ] Write unit tests for all services (backend)
- [ ] Write integration tests for API endpoints
- [ ] Write E2E tests for critical workflows (frontend)
  - Login and logout
  - Device CRUD
  - Real-time monitoring
  - Historical data export
- [ ] Load testing for WebSocket connections
- [ ] Load testing for database queries

**Files**:
- `backend/tests/unit/` (comprehensive coverage)
- `backend/tests/integration/` (API tests)
- `frontend/tests/e2e/` (Playwright tests)

### 8.2 UI/UX Polish
**Requirements**: DDMS-UI-010 to DDMS-UI-090

**Tasks**:
- [ ] Add loading states for all async operations
- [ ] Add toast notifications for user actions
- [ ] Optimize chart animations
- [ ] Verify color contrast and accessibility
- [ ] Add keyboard navigation support

**Files**:
- Various UI components (polish pass)

### 8.3 Performance Optimization
**Tasks**:
- [ ] Optimize database queries (indexes, explain analyze)
- [ ] Implement query result caching
- [ ] Optimize chart rendering (canvas vs SVG)
- [ ] Lazy load components with React.lazy
- [ ] Optimize bundle size (code splitting)

### 8.4 Documentation
**Tasks**:
- [ ] Write API documentation (OpenAPI/Swagger)
- [ ] Write user manual (Markdown)
- [ ] Create deployment guide
- [ ] Write developer setup guide
- [ ] Document architecture decisions

**Files**:
- `docs/api/openapi.yaml`
- `docs/USER_MANUAL.md`
- `docs/DEPLOYMENT.md`
- `docs/ARCHITECTURE.md`

**Testing Phase 8**:
```bash
# Run all unit tests
cd backend
pytest tests/unit/ --cov=ddms --cov-report=html
open htmlcov/index.html  # View coverage report

# Run integration tests
pytest tests/integration/ -v

# Run frontend tests
cd frontend
npm test
npm run test:e2e  # Playwright E2E tests

# Performance testing
# Install k6: brew install k6
k6 run tests/performance/websocket_load.js
k6 run tests/performance/api_load.js

# Check bundle size
npm run build
ls -lh dist/assets/*.js
# Should be < 1MB for main bundle
```

**Manual verification checklist**:
- [ ] All user requirements verified
- [ ] Test on Chrome and Edge (latest two versions)
- [ ] Check color contrast with accessibility tools
- [ ] Test keyboard navigation (Tab, Enter, Escape)
- [ ] Verify all loading states appear correctly
- [ ] Test with slow network (DevTools throttling)
- [ ] Verify error messages are clear and helpful
- [ ] Test WebSocket reconnection after network interruption
- [ ] Verify data persists across server restarts
- [ ] Check all API endpoints return proper error codes
- [ ] Review all console logs (no errors in production)
- [ ] Test with multiple concurrent users

**Deliverable**: Production-ready system with comprehensive tests and documentation.

---

## Implementation Order Summary

### Phase by Phase:
1. **Phase 1**: Foundation & Authentication
2. **Phase 2**: Device Management
3. **Phase 3**: Data Ingestion
4. **Phase 4**: Real-time Monitoring
5. **Phase 5**: Historical Data
6. **Phase 6**: Device Grouping
7. **Phase 7**: Internationalization
8. **Phase 8**: Polish & Testing

Each phase is designed to be independently testable and deliverable.

## Success Criteria

Each phase should meet these criteria before moving to the next:
- [ ] All requirements covered
- [ ] Unit tests passing
- [ ] Integration tests passing (where applicable)
- [ ] Code review completed
- [ ] Documentation updated
- [ ] Manual testing completed
- [ ] No critical bugs

## Notes

- Phases can overlap slightly (e.g., start frontend while backend is being tested)
- Each phase should result in a working, deployable increment
- Regular demos after each phase to gather feedback
- Prioritize security throughout (SQL injection, XSS, CSRF protection)
- Monitor performance from the start (query times, WebSocket latency)

---

## Requirements Traceability Matrix

### Deployment Requirements

| Requirement ID | Description | Implementation Phase | Verification |
|---------------|-------------|---------------------|--------------|
| DDMS-DEP-010 | Deploy on customer's intranet | Framework (Phase 0) | Docker Compose deployment |
| DDMS-DEP-020 | Accessible via Chrome/Edge browsers | Framework (Phase 0) | Browser access test |

### Authentication & Authorization Requirements

| Requirement ID | Description | Implementation Phase | Verification |
|---------------|-------------|---------------------|--------------|
| DDMS-AUTH-010 | Default owner account on initial setup | Phase 1.2 | Startup creates owner account |
| DDMS-AUTH-011 | Owner can change username/password | Phase 1.3 | User update API test |
| DDMS-AUTH-020 | Owner has full system access | Phase 1.2, 1.3 | Role-based access control test |
| DDMS-AUTH-021 | Owner can delete users (except self) | Phase 1.3 | User deletion API test |
| DDMS-AUTH-030 | Viewer has view-only access | Phase 1.2, 1.4 | Permission denial on write endpoints |
| DDMS-AUTH-040 | Admin has full access and can manage users | Phase 1.2, 2.1 | Permission check on endpoints |

### Live Monitoring Requirements

| Requirement ID | Description | Implementation Phase | Verification |
|---------------|-------------|---------------------|--------------|
| DDMS-MON-010 | Display current readings and timestamps | Phase 4.2, 4.3 | Dashboard shows latest values |
| DDMS-MON-020 | Auto-refresh at sampling intervals | Phase 3.2, 4.1 | WebSocket push updates |
| DDMS-MON-030 | Yellow warning indicator | Phase 4.2, 4.3 | Threshold evaluation logic test |
| DDMS-MON-040 | Red critical indicator | Phase 4.2, 4.3 | Critical status rendering test |
| DDMS-MON-050 | Overlay threshold markers on charts | Phase 4.3 | ECharts threshold line rendering |
| DDMS-MON-060 | Color-coded regions (optional) | Phase 4.3 | ECharts visualMap for color zones |

### Historical Data Requirements

| Requirement ID | Description | Implementation Phase | Verification |
|---------------|-------------|---------------------|--------------|
| DDMS-HIST-010 | View historical trend charts with custom range | Phase 5.1, 5.2 | History page with line chart |
| DDMS-HIST-020 | Display threshold lines on historical charts | Phase 5.2 | Threshold overlay on history chart |
| DDMS-HIST-030 | Export historical data to CSV | Phase 5.1, 5.2 | CSV download with correct format |

### Device Configuration Requirements

| Requirement ID | Description | Implementation Phase | Verification |
|---------------|-------------|---------------------|--------------|
| DDMS-DEV-010 | Admin/owner can add/edit devices | Phase 2.1, 2.2 | Device CRUD API and UI |
| DDMS-DEV-011 | Set device name and description | Phase 2.1, 2.2 | Device form basic info fields |
| DDMS-DEV-012 | Set reading units | Phase 2.1, 2.2 | Device form units field |
| DDMS-DEV-013 | Set sampling interval | Phase 2.1, 2.2, 3.2 | Scheduler uses device interval |
| DDMS-DEV-014 | Configure Modbus connection parameters | Phase 2.1, 2.2 | Device form with connection params |
| DDMS-DEV-020 | Set threshold rules (warning/critical) | Phase 2.1, 2.2 | Threshold config in device form |
| DDMS-DEV-030 | Admin/owner can delete devices | Phase 2.1, 2.2 | Device deletion API and UI |
| DDMS-DEV-031 | Retain historical readings on deletion | Phase 2.1, 2.2 | Deletion does not cascade |
| DDMS-DEV-040 | Display device connection status | Phase 3.1, 4.3 | Status field updated by poller |
| DDMS-DEV-041 | Display last reading timestamp | Phase 3.1, 4.3 | last_reading_at field on device |
| DDMS-DEV-042 | Display communication error indicators | Phase 3.1, 4.3 | Error status from failed polls |

### Device Grouping Requirements

| Requirement ID | Description | Implementation Phase | Verification |
|---------------|-------------|---------------------|--------------|
| DDMS-GRP-010 | Admin/owner can create groups | Phase 6.1, 6.3 | Group creation API and UI |
| DDMS-GRP-020 | Admin/owner can rename groups | Phase 6.1, 6.3 | Group update API and UI |
| DDMS-GRP-030 | Admin/owner can delete groups | Phase 6.1, 6.3 | Group deletion API and UI |
| DDMS-GRP-040 | Assign devices to groups (one group per device) | Phase 6.1, 6.3 | Device-group mapping endpoints |
| DDMS-GRP-050 | Real-time dashboard for groups | Phase 6.2, 6.3 | Group dashboard with live data |
| DDMS-GRP-051 | Historical charts for groups | Phase 6.2, 6.3 | Group history endpoint and UI |

### Internationalization Requirements

| Requirement ID | Description | Implementation Phase | Verification |
|---------------|-------------|---------------------|--------------|
| DDMS-I18N-010 | Support English and Chinese | Phase 7.2 | Translation files |
| DDMS-I18N-020 | Switch language without reloading | Phase 7.2 | Language switcher component |
| DDMS-I18N-030 | Remember language preference | Phase 7.1, 7.2 | User preferences API |
| DDMS-I18N-040 | All UI elements translated | Phase 7.2 | Complete translation coverage |

### User Interface Requirements

| Requirement ID | Description | Implementation Phase | Verification |
|---------------|-------------|---------------------|--------------|
| DDMS-UI-010 | Clean, modern interface design | Phase 1.4, 8.2 | Ant Design components |
| DDMS-UI-020 | Professional industrial appearance | Phase 8.2 | Visual design review |
| DDMS-UI-030 | Animated chart updates | Phase 4.3, 8.2 | ECharts animation config |
| DDMS-UI-040 | Loading indicators | Phase 1.4, 8.2 | Loading states on all APIs |
| DDMS-UI-050 | Responsive feedback for actions | Phase 8.2 | Toast notifications |
| DDMS-UI-060 | Subtle hover and focus effects | Phase 8.2 | CSS hover states |
| DDMS-UI-070 | High contrast text and backgrounds | Phase 8.2 | Accessibility audit |
| DDMS-UI-080 | Clear visual hierarchy | Phase 8.2 | Typography and spacing |
| DDMS-UI-090 | Readable fonts | Phase 8.2 | Font size verification |

### Data Persistence Requirements

| Requirement ID | Description | Implementation Phase | Verification |
|---------------|-------------|---------------------|--------------|
| DDMS-DATA-010 | Store config data persistently | Phase 1.1 | Database models and migrations |
| DDMS-DATA-011 | Store time-series data | Phase 1.1, 3.1 | TimescaleDB hypertable |
| DDMS-DATA-020 | Data persists across restarts | Phase 1.1 | Database persistence test |

### Protocol Support Requirements

| Requirement ID | Description | Implementation Phase | Verification |
|---------------|-------------|---------------------|--------------|
| DDMS-PROTO-010 | Support Modbus TCP/IP | Phase 3.1 | Modbus TCP client implementation |
| DDMS-PROTO-011 | Support Modbus RTU | Phase 3.1 | Modbus RTU client implementation |
| DDMS-PROTO-012 | Configurable register addresses and data types | Phase 2.1, 3.1 | Connection params configuration |

### Summary

**Total Requirements**: 45

By Category:
- **Deployment**: 2 requirements
- **Authentication & Authorization**: 6 requirements
- **Live Monitoring**: 6 requirements
- **Historical Data**: 3 requirements
- **Device Configuration**: 11 requirements
- **Device Grouping**: 6 requirements
- **Internationalization**: 4 requirements
- **User Interface**: 9 requirements
- **Data Persistence**: 3 requirements
- **Protocol Support**: 3 requirements

By Phase:
- **Phase 0 (Framework)**: 2 requirements (DEP-010, DEP-020)
- **Phase 1 (Auth)**: 9 requirements (DATA-010, DATA-011, DATA-020, AUTH-010 to AUTH-040, UI-010, UI-040)
- **Phase 2 (Devices)**: 11 requirements (DEV-010 to DEV-042, PROTO-012)
- **Phase 3 (Ingestion)**: 5 requirements (DEV-013, DEV-040 to DEV-042, PROTO-010, PROTO-011, MON-020)
- **Phase 4 (Real-time)**: 6 requirements (MON-010 to MON-060)
- **Phase 5 (Historical)**: 3 requirements (HIST-010 to HIST-030)
- **Phase 6 (Grouping)**: 6 requirements (GRP-010 to GRP-051)
- **Phase 7 (i18n)**: 4 requirements (I18N-010 to I18N-040)
- **Phase 8 (Polish)**: 8 requirements (UI-020 to UI-090)

**All 45 requirements are covered** by the 8-phase implementation plan.

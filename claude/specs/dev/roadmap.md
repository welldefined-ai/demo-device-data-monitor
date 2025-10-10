# DDMS Implementation Plan

This document outlines the phased implementation plan for the Distributed Device Monitoring System based on user requirements.

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
**Requirements**: DDMS-DATA-010, DDMS-DATA-070, DDMS-DATA-080

**Tasks**:
- [ ] Design database schema (ERD)
  - Users table (id, username, password_hash, role, language_preference, created_at)
  - Devices table (id, name, description, connection_params, sampling_interval, retention_days, thresholds, status, last_reading_at)
  - Device readings table (TimescaleDB hypertable: device_id, timestamp, value)
  - Groups table (id, name, created_at)
  - Device-group mapping table (device_id, group_id)
- [ ] Create SQLAlchemy models in `backend/ddms/db/models.py`
  - User model with role enum (owner, admin, read_only)
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
**Requirements**: DDMS-AUTH-010 to DDMS-AUTH-080

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
**Requirements**: DDMS-AUTH-020 to DDMS-AUTH-050

**Tasks**:
- [ ] Implement user management endpoints in `backend/ddms/api/users.py`
  - GET /api/users (owner only)
  - POST /api/users (owner only, create admin/read-only)
  - PATCH /api/users/{id} (update username/password)
  - DELETE /api/users/{id} (owner only, prevent self-delete)
- [ ] Create Pydantic schemas in `backend/ddms/schemas/user.py`
  - UserCreate, UserUpdate, UserResponse
  - Role enum
- [ ] Create user service in `backend/ddms/services/user.py`
- [ ] Write unit tests

**Files**:
- `backend/ddms/api/users.py`
- `backend/ddms/schemas/user.py`
- `backend/ddms/services/user.py`
- `backend/tests/unit/test_users.py`

### 1.4 Frontend Auth & Layout
**Requirements**: DDMS-AUTH-010 to DDMS-AUTH-080, DDMS-UI-010 to DDMS-UI-100

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
- Verify admin cannot access Users page

**Deliverable**: Working login system with role-based access control and user management UI.

---

## Phase 2: Device Management & Configuration

**Goal**: Enable device CRUD operations and configuration.

### 2.1 Device Models & API
**Requirements**: DDMS-DEV-010 to DDMS-DEV-140

**Tasks**:
- [ ] Implement device endpoints in `backend/ddms/api/devices.py`
  - GET /api/devices (list with filters)
  - POST /api/devices (admin/owner only)
  - GET /api/devices/{id}
  - PATCH /api/devices/{id} (admin/owner only)
  - DELETE /api/devices/{id} (admin/owner only, with keep_data option)
- [ ] Create Pydantic schemas in `backend/ddms/schemas/device.py`
  - DeviceCreate, DeviceUpdate, DeviceResponse
  - ConnectionParams (Modbus TCP/RTU settings)
  - ThresholdConfig (upper/lower warning/critical, hysteresis)
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
**Requirements**: DDMS-DEV-010 to DDMS-DEV-140

**Tasks**:
- [ ] Create device list page in `frontend/src/features/devices/DeviceList.tsx`
  - Table with name, status, last reading, actions
  - Status indicators (online/offline/error)
  - Filter and search
- [ ] Create device form in `frontend/src/features/devices/DeviceForm.tsx`
  - Basic info (name, description, units)
  - Modbus connection settings
  - Sampling interval and retention
  - Threshold configuration (warning/critical, upper/lower, hysteresis)
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
    "retention_days": 90,
    "thresholds": {
      "upper_warning": 30,
      "upper_critical": 35,
      "lower_warning": 10,
      "lower_critical": 5,
      "hysteresis": 2
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
- Verify read-only user can view but not edit/delete

**Deliverable**: Complete device management UI with CRUD operations.

---

## Phase 3: Data Ingestion & Polling

**Goal**: Connect to devices via Modbus and store readings in database.

### 3.1 Modbus Communication
**Requirements**: DDMS-PROTO-010 to DDMS-PROTO-050

**Tasks**:
- [ ] Create Modbus client wrapper in `backend/ddms/ingestion/modbus_client.py`
  - Support for Modbus TCP
  - Support for Modbus RTU (optional)
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
**Requirements**: DDMS-DEV-050, DDMS-MON-030

**Tasks**:
- [ ] Configure APScheduler in `backend/ddms/scheduler/jobs.py`
  - Job for polling devices at their configured intervals
  - Job for data cleanup based on retention periods
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

### 3.3 Data Cleanup
**Requirements**: DDMS-DATA-040, DDMS-DATA-050

**Tasks**:
- [ ] Implement data retention job in `backend/ddms/scheduler/cleanup.py`
  - Run daily
  - Delete readings older than device retention period
  - Use TimescaleDB retention policies
- [ ] Add manual cleanup endpoint (owner only)
  - POST /api/admin/cleanup

**Files**:
- `backend/ddms/scheduler/cleanup.py`
- `backend/ddms/api/admin.py`

**Testing Phase 3**:
```bash
# Unit tests with mocked Modbus
pytest tests/unit/test_modbus.py

# Use Modbus simulator for integration testing
# Install modbus-simulator or use pymodbus simulator
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
**Requirements**: DDMS-MON-010, DDMS-MON-030

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
**Requirements**: DDMS-MON-010 to DDMS-MON-110

**Tasks**:
- [ ] Create readings endpoint in `backend/ddms/api/readings.py`
  - GET /api/devices/{id}/readings/latest (current value)
  - GET /api/devices/{id}/readings/current (last N readings)
- [ ] Add threshold evaluation logic
  - Calculate warning/critical status
  - Consider hysteresis
- [ ] Return status indicators with readings

**Files**:
- `backend/ddms/api/readings.py`
- `backend/ddms/services/reading.py`
- `backend/ddms/schemas/reading.py`

### 4.3 Dashboard UI
**Requirements**: DDMS-MON-010 to DDMS-MON-110

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
  - Color-coded regions
- [ ] Implement WebSocket client in `frontend/src/lib/websocket.ts`
  - Auto-reconnect logic
  - Subscribe to device updates
- [ ] Add real-time updates to charts
  - Smooth animations
  - Auto-scroll time axis
- [ ] Create tooltip with exact values and timestamps

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
- Verify line charts show recent trend (last 5-10 minutes)
- Watch for real-time updates (values should change automatically)
- Trigger a warning by adjusting threshold or simulator value
  - Device card should show yellow warning indicator
  - Chart should show yellow zone highlighting
- Trigger a critical alert
  - Device card should show red critical indicator
  - Chart should show red zone highlighting
- Hover over chart points to see exact values and timestamps
- Open browser DevTools Network tab, verify WebSocket connection is active
- Refresh page, verify auto-reconnect works

**Deliverable**: Real-time monitoring dashboard with live charts and warnings.

---

## Phase 5: Historical Data & Analytics

**Goal**: Enable historical data queries, visualization, and export.

### 5.1 Historical Data API
**Requirements**: DDMS-HIST-010 to DDMS-HIST-050

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
**Requirements**: DDMS-HIST-010 to DDMS-HIST-050

**Tasks**:
- [ ] Create history page in `frontend/src/features/history/HistoryPage.tsx`
  - Device selector
  - Time range picker (presets + custom)
  - Historical line chart
- [ ] Implement zoom and pan in ECharts
  - DataZoom component
  - Brush selection
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
- Use time range picker to select "Last 24 hours"
- Chart should display full day of data with threshold lines
- Use mouse wheel to zoom into specific time period
- Drag chart to pan left/right
- Click "Export CSV" button
- Verify CSV file downloads with correct data
- Try other presets: "Last Hour", "Last Week", "Custom Range"
- Select custom date/time range and verify correct data loads
- Verify threshold violations are highlighted on chart
- Check loading indicator appears during data fetch

**Deliverable**: Historical data viewer with zoom, pan, and CSV export.

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
- [ ] Create Pydantic schemas in `backend/ddms/schemas/group.py`
- [ ] Create group service in `backend/ddms/services/group.py`

**Files**:
- `backend/ddms/api/groups.py`
- `backend/ddms/schemas/group.py`
- `backend/ddms/services/group.py`
- `backend/tests/unit/test_groups.py`

### 6.2 Group Monitoring
**Requirements**: DDMS-GRP-050 to DDMS-GRP-080

**Tasks**:
- [ ] Add group readings endpoints
  - GET /api/groups/{id}/readings/current
  - GET /api/groups/{id}/readings/history
  - GET /api/groups/{id}/readings/export
- [ ] Implement group alert summary
  - Count of devices by status (normal/warning/critical)
  - List of devices with active warnings

**Files**:
- `backend/ddms/api/groups.py` (updated)
- `backend/ddms/services/group.py` (updated)

### 6.3 Group UI
**Requirements**: DDMS-GRP-010 to DDMS-GRP-080

**Tasks**:
- [ ] Create group management page
  - List of groups
  - Create/edit/delete groups
  - Assign devices to groups (drag-and-drop or multi-select)
- [ ] Create group dashboard view
  - Grid of all devices in group
  - Group-level alert summary card
  - Multi-device chart overlay
- [ ] Add group export functionality
  - Export all devices in group to single CSV

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
curl -X POST http://localhost:8000/api/groups/1/devices/2 \
  -H "Cookie: access_token=<token>"

# Get group readings
curl http://localhost:8000/api/groups/1/readings/current
curl "http://localhost:8000/api/groups/1/readings/history?start_time=2025-10-09T00:00:00Z&end_time=2025-10-10T23:59:59Z"

# Export group data
curl "http://localhost:8000/api/groups/1/readings/export?start_time=2025-10-09T00:00:00Z" \
  --output group_export.csv
```

**Frontend verification**:
- Login as admin/owner
- Navigate to Groups page
- Create a new group "Production Line A"
- Click "Assign Devices" button
- Select multiple devices and add to group
- Navigate to group dashboard
- Verify all group devices are displayed in grid
- Check alert summary card shows counts (e.g., "2 normal, 1 warning, 0 critical")
- Verify charts overlay all device data
- Click "Export Group Data" and verify CSV contains all devices
- Remove a device from group and verify it disappears
- Delete group and verify devices are not deleted

**Deliverable**: Device grouping with group-level monitoring and exports.

---

## Phase 7: Internationalization

**Goal**: Support English and Chinese languages.

### 7.1 Backend i18n
**Requirements**: DDMS-I18N-010 to DDMS-I18N-050

**Tasks**:
- [ ] Add language preference to user settings
  - PATCH /api/users/{id}/preferences
- [ ] Update UserResponse schema to include language
- [ ] Store language preference in database

**Files**:
- `backend/ddms/api/users.py` (updated)
- `backend/ddms/schemas/user.py` (updated)

### 7.2 Frontend i18n
**Requirements**: DDMS-I18N-010 to DDMS-I18N-050

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
- All UI text should change to Chinese:
  - Navigation: "仪表板", "设备", "历史数据", "分组", "用户"
  - Buttons: "添加", "编辑", "删除", "导出"
  - Form labels: "名称", "描述", "单位", "采样间隔"
  - Status: "在线", "离线", "正常", "警告", "严重"
- Refresh page, language should persist
- Logout and login, language preference should be restored
- Switch back to English and verify all text changes
- Test with different user accounts, each should have independent preference

**Deliverable**: Full English and Chinese language support.

---

## Phase 8: Data Persistence & Administration

**Goal**: Backup, restore, and administrative features.

### 8.1 Database Backup
**Requirements**: DDMS-DATA-030, DDMS-DATA-060

**Tasks**:
- [ ] Create backup script in `scripts/db/backup.sh`
  - pg_dump for database backup
  - Compress and timestamp backups
- [ ] Configure backup schedule (cron or APScheduler)
- [ ] Implement backup endpoints (owner only)
  - POST /api/admin/backup (trigger manual backup)
  - GET /api/admin/backups (list available backups)
  - POST /api/admin/restore (restore from backup)
- [ ] Add backup configuration settings
  - Backup retention period
  - Backup schedule

**Files**:
- `scripts/db/backup.sh`
- `backend/ddms/api/admin.py` (updated)
- `backend/ddms/services/backup.py`

### 8.2 System Configuration
**Requirements**: DDMS-DATA-030, DDMS-DATA-040

**Tasks**:
- [ ] Create system settings endpoint (owner only)
  - GET /api/admin/settings
  - PATCH /api/admin/settings
- [ ] Implement configurable settings
  - Default retention period
  - Backup schedule
  - Global sampling interval limits
- [ ] Create settings UI (owner only)
  - Settings page with form
  - Save/reset buttons

**Files**:
- `backend/ddms/api/admin.py` (updated)
- `backend/ddms/schemas/settings.py`
- `frontend/src/features/admin/SettingsPage.tsx`

### 8.3 Error Recovery
**Requirements**: DDMS-DATA-090

**Tasks**:
- [ ] Implement error logging middleware
  - Log all errors to database
  - Include stack traces
- [ ] Create error monitoring dashboard (owner only)
  - Recent errors
  - Error counts by type
  - Device communication errors
- [ ] Add retry logic for failed operations
  - Database connection retries
  - Modbus communication retries
  - WebSocket reconnection

**Files**:
- `backend/ddms/core/error_handling.py`
- `backend/ddms/api/admin.py` (updated)
- `frontend/src/features/admin/ErrorLog.tsx`

**Testing Phase 8**:
```bash
# Test backup
curl -X POST http://localhost:8000/api/admin/backup \
  -H "Cookie: access_token=<owner_token>"
# Should return: {"status": "success", "backup_file": "ddms_backup_20251010_120000.sql.gz"}

# List backups
curl http://localhost:8000/api/admin/backups

# Verify backup file exists
ls -lh backups/
# Should see: ddms_backup_20251010_120000.sql.gz

# Test restore (careful!)
curl -X POST http://localhost:8000/api/admin/restore \
  -H "Content-Type: application/json" \
  -H "Cookie: access_token=<owner_token>" \
  -d '{"backup_file": "ddms_backup_20251010_120000.sql.gz"}'

# Test settings
curl http://localhost:8000/api/admin/settings
curl -X PATCH http://localhost:8000/api/admin/settings \
  -H "Content-Type: application/json" \
  -d '{"default_retention_days": 180, "backup_schedule": "0 2 * * *"}'

# Test cleanup
curl -X POST http://localhost:8000/api/admin/cleanup

# Check data was cleaned
docker compose exec db psql -U ddms -d ddms -c \
  "SELECT COUNT(*) FROM device_readings WHERE timestamp < NOW() - INTERVAL '90 days';"
# Should return 0
```

**Frontend verification (owner only)**:
- Login as owner
- Navigate to Admin → Settings
- Change default retention period to 180 days
- Save and verify success message
- Navigate to Admin → Backups
- Click "Create Backup Now"
- Verify backup appears in list with timestamp
- Click "Download" to download backup file
- Navigate to Admin → Error Log
- Verify recent errors are displayed
- Check error counts by type
- Simulate a Modbus error and verify it appears in log

**Deliverable**: Backup/restore functionality and system administration tools.

---

## Phase 9: Polish & Testing

**Goal**: Ensure production readiness with comprehensive testing and UI polish.

### 9.1 Testing
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

### 9.2 UI/UX Polish
**Requirements**: DDMS-UI-010 to DDMS-UI-120

**Tasks**:
- [ ] Implement smooth transitions (Ant Design transitions)
- [ ] Add loading states for all async operations
- [ ] Add toast notifications for user actions
- [ ] Ensure responsive design for tablets
- [ ] Optimize chart animations
- [ ] Test touch interactions on tablets
- [ ] Verify color contrast and accessibility
- [ ] Add keyboard navigation support
- [ ] Implement dark mode (optional enhancement)

**Files**:
- Various UI components (polish pass)

### 9.3 Performance Optimization
**Tasks**:
- [ ] Optimize database queries (indexes, explain analyze)
- [ ] Implement query result caching
- [ ] Optimize chart rendering (canvas vs SVG)
- [ ] Lazy load components with React.lazy
- [ ] Optimize bundle size (code splitting)
- [ ] Implement service worker for offline support (optional)

### 9.4 Documentation
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

**Testing Phase 9**:
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
- [ ] All user requirements verified (DDMS-AUTH-*, DDMS-DEV-*, etc.)
- [ ] Test on Chrome, Firefox, Edge, Safari
- [ ] Test on tablet (iPad or Android)
- [ ] Verify touch interactions work
- [ ] Check color contrast with accessibility tools
- [ ] Test keyboard navigation (Tab, Enter, Escape)
- [ ] Verify all loading states appear correctly
- [ ] Test with slow network (DevTools throttling)
- [ ] Verify error messages are clear and helpful
- [ ] Test WebSocket reconnection after network interruption
- [ ] Verify data persists across server restarts
- [ ] Check all API endpoints return proper error codes
- [ ] Review all console logs (no errors in production)
- [ ] Verify responsive layout on different screen sizes
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
8. **Phase 8**: Admin Features
9. **Phase 9**: Polish & Testing

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
| DDMS-DEP-020 | Accessible via web browser without internet | Framework (Phase 0) | Local network access test |
| DDMS-DEP-030 | Support Chrome, Firefox, Edge, Safari | Phase 9 | Cross-browser testing |
| DDMS-DEP-040 | Responsive design for desktop and tablet | Phase 9 | Responsive design verification |

### Authentication & Authorization Requirements

| Requirement ID | Description | Implementation Phase | Verification |
|---------------|-------------|---------------------|--------------|
| DDMS-AUTH-010 | Default owner account on initial setup | Phase 1.2 | Startup creates owner account |
| DDMS-AUTH-020 | Owner can change username/password | Phase 1.3 | User update API test |
| DDMS-AUTH-030 | Owner can create admin users | Phase 1.3 | User creation API test |
| DDMS-AUTH-040 | Owner can create read-only users | Phase 1.3 | User creation API test |
| DDMS-AUTH-050 | Owner can delete users (except self) | Phase 1.3 | User deletion API test |
| DDMS-AUTH-060 | Owner has full system access | Phase 1.2, 1.3 | Role-based access control test |
| DDMS-AUTH-070 | Admin has device config and monitoring access | Phase 1.2, 2.1 | Permission check on device endpoints |
| DDMS-AUTH-080 | Read-only has view-only access | Phase 1.2, 1.4 | Permission denial on write endpoints |

### Real-time Monitoring Requirements

| Requirement ID | Description | Implementation Phase | Verification |
|---------------|-------------|---------------------|--------------|
| DDMS-MON-010 | Display current readings from devices | Phase 4.2, 4.3 | Dashboard shows latest values |
| DDMS-MON-020 | Show data in charts (line, gauges) | Phase 4.3 | ECharts gauge and line charts render |
| DDMS-MON-030 | Auto-refresh at sampling intervals | Phase 3.2, 4.1 | WebSocket push updates |
| DDMS-MON-040 | Display multiple devices simultaneously | Phase 4.3 | Dashboard grid with multiple cards |
| DDMS-MON-050 | Yellow warning indicator near threshold | Phase 4.2, 4.3 | Threshold evaluation logic test |
| DDMS-MON-060 | Red critical indicator exceeding threshold | Phase 4.2, 4.3 | Critical status rendering test |
| DDMS-MON-070 | Visual indicators on charts and lists | Phase 4.3 | Status badges on cards and charts |
| DDMS-MON-080 | Overlay threshold lines on charts | Phase 4.3 | ECharts threshold line rendering |
| DDMS-MON-090 | Display reading and threshold values | Phase 4.3 | Value labels on charts |
| DDMS-MON-100 | Color-coded regions (normal/warning/critical) | Phase 4.3 | ECharts visualMap for color zones |
| DDMS-MON-110 | Hover tooltips with values and timestamps | Phase 4.3 | ECharts tooltip configuration |

### Historical Data Requirements

| Requirement ID | Description | Implementation Phase | Verification |
|---------------|-------------|---------------------|--------------|
| DDMS-HIST-010 | View historical trend curves | Phase 5.1, 5.2 | History page with line chart |
| DDMS-HIST-020 | Customize time range (presets + custom) | Phase 5.2 | Time range picker component |
| DDMS-HIST-030 | Zoom in/out on charts | Phase 5.2 | ECharts DataZoom component |
| DDMS-HIST-040 | Export historical data to CSV | Phase 5.1, 5.2 | CSV download with correct format |
| DDMS-HIST-050 | Display threshold lines on historical charts | Phase 5.2 | Threshold overlay on history chart |

### Device Configuration Requirements

| Requirement ID | Description | Implementation Phase | Verification |
|---------------|-------------|---------------------|--------------|
| DDMS-DEV-010 | Admin/owner can add devices | Phase 2.1, 2.2 | Device creation API and UI |
| DDMS-DEV-020 | Configure Modbus connection parameters | Phase 2.1, 2.2 | Device form with connection params |
| DDMS-DEV-030 | Set device name and description | Phase 2.1, 2.2 | Device form basic info fields |
| DDMS-DEV-040 | Set reading units (°C, bar, RPM, %) | Phase 2.1, 2.2 | Device form units field |
| DDMS-DEV-050 | Set sampling interval | Phase 2.1, 2.2, 3.2 | Scheduler uses device interval |
| DDMS-DEV-060 | Set data retention period | Phase 2.1, 2.2, 3.3 | Cleanup job uses retention period |
| DDMS-DEV-070 | Set upper threshold limits | Phase 2.1, 2.2 | Threshold config in device form |
| DDMS-DEV-080 | Set lower threshold limits | Phase 2.1, 2.2 | Threshold config in device form |
| DDMS-DEV-090 | Set hysteresis values | Phase 2.1, 2.2, 4.2 | Hysteresis in threshold evaluation |
| DDMS-DEV-100 | Admin/owner can delete devices | Phase 2.1, 2.2 | Device deletion API and UI |
| DDMS-DEV-110 | Option to keep/delete historical data | Phase 2.1, 2.2 | Delete modal with keep_data option |
| DDMS-DEV-120 | Display device connection status | Phase 3.1, 4.3 | Status field updated by poller |
| DDMS-DEV-130 | Display last reading timestamp | Phase 3.1, 4.3 | last_reading_at field on device |
| DDMS-DEV-140 | Display communication error indicators | Phase 3.1, 4.3 | Error status from failed polls |

### Device Grouping Requirements

| Requirement ID | Description | Implementation Phase | Verification |
|---------------|-------------|---------------------|--------------|
| DDMS-GRP-010 | Admin/owner can create groups | Phase 6.1, 6.3 | Group creation API and UI |
| DDMS-GRP-020 | Assign devices to groups | Phase 6.1, 6.3 | Device-group mapping endpoints |
| DDMS-GRP-030 | Admin/owner can rename groups | Phase 6.1, 6.3 | Group update API and UI |
| DDMS-GRP-040 | Admin/owner can delete groups | Phase 6.1, 6.3 | Group deletion API and UI |
| DDMS-GRP-050 | Real-time dashboard for groups | Phase 6.2, 6.3 | Group dashboard with live data |
| DDMS-GRP-060 | Historical charts for groups | Phase 6.2, 6.3 | Group history endpoint and UI |
| DDMS-GRP-070 | Group-level alert summary | Phase 6.2, 6.3 | Alert count aggregation |
| DDMS-GRP-080 | CSV export for group devices | Phase 6.2, 6.3 | Group export endpoint |

### Internationalization Requirements

| Requirement ID | Description | Implementation Phase | Verification |
|---------------|-------------|---------------------|--------------|
| DDMS-I18N-010 | Support English (en-US) | Phase 7.2 | English translation file |
| DDMS-I18N-020 | Support Chinese (zh-CN) | Phase 7.2 | Chinese translation file |
| DDMS-I18N-030 | Switch language from UI | Phase 7.2 | Language switcher component |
| DDMS-I18N-040 | Save language preference per user | Phase 7.1, 7.2 | User preferences API |
| DDMS-I18N-050 | All UI elements translated | Phase 7.2 | Complete translation coverage |

### User Interface Requirements

| Requirement ID | Description | Implementation Phase | Verification |
|---------------|-------------|---------------------|--------------|
| DDMS-UI-010 | Clean, modern interface design | Phase 1.4, 9.2 | Ant Design components |
| DDMS-UI-020 | Intuitive navigation and workflows | Phase 1.4, 9.2 | User testing feedback |
| DDMS-UI-030 | Professional industrial appearance | Phase 9.2 | Visual design review |
| DDMS-UI-040 | Smooth transitions between views | Phase 9.2 | Ant Design transitions |
| DDMS-UI-050 | Animated chart updates | Phase 4.3, 9.2 | ECharts animation config |
| DDMS-UI-060 | Loading indicators for async operations | Phase 1.4, 9.2 | Loading states on all APIs |
| DDMS-UI-070 | Responsive feedback for user actions | Phase 9.2 | Toast notifications |
| DDMS-UI-080 | Subtle hover and focus effects | Phase 9.2 | CSS hover states |
| DDMS-UI-090 | High contrast text and backgrounds | Phase 9.2 | Accessibility audit |
| DDMS-UI-100 | Clear visual hierarchy | Phase 9.2 | Typography and spacing |
| DDMS-UI-110 | Readable fonts at viewing distance | Phase 9.2 | Font size verification |
| DDMS-UI-120 | Touch-friendly controls for tablets | Phase 9.2 | Touch target size verification |

### Data Persistence Requirements

| Requirement ID | Description | Implementation Phase | Verification |
|---------------|-------------|---------------------|--------------|
| DDMS-DATA-010 | Store config data persistently | Phase 1.1 | Database models and migrations |
| DDMS-DATA-020 | Store time-series data in database | Phase 1.1, 3.1 | TimescaleDB hypertable |
| DDMS-DATA-030 | Automatic database backups | Phase 8.1 | Backup schedule with APScheduler |
| DDMS-DATA-040 | Configurable retention period per device | Phase 2.1, 3.3 | Device retention_days field |
| DDMS-DATA-050 | Auto cleanup old data | Phase 3.3 | Cleanup job deletes old readings |
| DDMS-DATA-060 | Manual data export before deletion | Phase 5.1, 6.2 | CSV export endpoints |
| DDMS-DATA-070 | Data persists across restarts | Phase 1.1 | Database persistence test |
| DDMS-DATA-080 | Transaction safety for config changes | Phase 1.1 | SQLAlchemy transactions |
| DDMS-DATA-090 | Error recovery mechanisms | Phase 8.3 | Retry logic and error logging |

### Protocol Support Requirements

| Requirement ID | Description | Implementation Phase | Verification |
|---------------|-------------|---------------------|--------------|
| DDMS-PROTO-010 | Support Modbus TCP/IP | Phase 3.1 | Modbus TCP client implementation |
| DDMS-PROTO-020 | Support Modbus RTU (optional) | Phase 3.1 | Modbus RTU client implementation |
| DDMS-PROTO-030 | Configurable register addresses | Phase 2.1, 3.1 | Register field in connection params |
| DDMS-PROTO-040 | Configurable data types | Phase 2.1, 3.1 | Data type field in connection params |
| DDMS-PROTO-050 | Support common PLCs and sensors | Phase 3.1 | Multiple data type parsing |

### Summary

**Total Requirements**: 80

By Category:
- **Deployment**: 4 requirements
- **Authentication & Authorization**: 8 requirements
- **Real-time Monitoring**: 11 requirements
- **Historical Data**: 5 requirements
- **Device Configuration**: 14 requirements
- **Device Grouping**: 8 requirements
- **Internationalization**: 5 requirements
- **User Interface**: 12 requirements
- **Data Persistence**: 9 requirements
- **Protocol Support**: 5 requirements

By Phase:
- **Phase 0 (Framework)**: 2 requirements (DEP-010, DEP-020)
- **Phase 1 (Auth)**: 11 requirements (DATA-010, DATA-070, DATA-080, AUTH-010 to AUTH-080, UI-010, UI-060)
- **Phase 2 (Devices)**: 14 requirements (DEV-010 to DEV-110, PROTO-030, PROTO-040)
- **Phase 3 (Ingestion)**: 8 requirements (DEV-050, DEV-060, DEV-120, DEV-130, DEV-140, PROTO-010, PROTO-020, PROTO-050, DATA-040, DATA-050, MON-030)
- **Phase 4 (Real-time)**: 11 requirements (MON-010 to MON-110)
- **Phase 5 (Historical)**: 5 requirements (HIST-010 to HIST-050, DATA-060)
- **Phase 6 (Grouping)**: 8 requirements (GRP-010 to GRP-080)
- **Phase 7 (i18n)**: 5 requirements (I18N-010 to I18N-050)
- **Phase 8 (Admin)**: 3 requirements (DATA-030, DATA-090)
- **Phase 9 (Polish)**: 13 requirements (DEP-030, DEP-040, UI-010 to UI-120)

**All 80 requirements are covered** by the 9-phase implementation plan.

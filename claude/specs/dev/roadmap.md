# DDMS Development Roadmap

This roadmap sequences implementation work into clear phases, each with deliverables, APIs, UI features, and concrete acceptance tests. Requirement IDs refer to specs/user/requirements.md.

## Phase 1: Authentication & Authorization

**Goal**: Secure access with role-based permissions.

**Database**:
- Users table: id, username, password_hash, role (owner/admin/viewer), language_preference, created_at, updated_at
- Seed initial owner account on empty database

**Backend APIs**:
- `POST /api/auth/login` - Authenticate user, return JWT in HttpOnly cookie
- `POST /api/auth/logout` - Clear authentication cookie
- `GET /api/auth/me` - Get current user info
- `GET /api/users` - List users (owner/admin only)
- `POST /api/users` - Create admin or viewer user (owner/admin)
- `PATCH /api/users/{id}` - Update username or password
- `DELETE /api/users/{id}` - Delete user (owner/admin, cannot delete self)
- `GET /health` - System health check
- `GET /api/health` - API health check
- `GET /api/version` - System version info

**Frontend**:
- Login page with username/password form
- Protected routes with role-based access control
- User management page (owner/admin only)
- Profile page for password changes
- App layout with navigation and user menu

**Tests**:
```bash
# Health checks
curl http://localhost:8000/health
# → 200 {"status": "ok", "environment": "development"}

curl http://localhost:8000/api/health
# → 200 {"status": "ok"}

# Authentication
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"owner","password":"defaultpass"}'
# → 200 with Set-Cookie header

curl http://localhost:8000/api/auth/me \
  -H "Cookie: access_token=<token>"
# → 200 {"id": 1, "username": "owner", "role": "owner"}

# User management
curl -X POST http://localhost:8000/api/users \
  -H "Cookie: access_token=<owner_token>" \
  -d '{"username":"admin1","password":"pass123","role":"admin"}'
# → 201

# Verify roles
curl -X POST http://localhost:8000/api/devices \
  -H "Cookie: access_token=<viewer_token>"
# → 403 (viewer cannot create devices)
```

**Manual Verification**:
- Login with default owner credentials
- Change owner password via profile page
- Create admin and viewer users
- Logout and login as admin, verify can manage users
- Login as viewer, verify read-only access (no create/edit/delete buttons)

**Requirements**: DDMS-AUTH-010, DDMS-AUTH-011, DDMS-AUTH-020, DDMS-AUTH-021, DDMS-AUTH-030, DDMS-AUTH-040, DDMS-DEP-010, DDMS-DEP-020

---

## Phase 2: Device & Group Management

**Goal**: CRUD operations for devices and device groups with single-group assignment.

**Database**:
- Devices table: id, name, description, units, sampling_interval, thresholds (JSON: warning/critical), modbus_config (JSON: type/host/port/register/data_type), status, last_reading_at, created_at, updated_at
- Device groups table: id, name, description, created_at, updated_at
- Group devices junction table: group_id, device_id (unique constraint on device_id for single-group enforcement)

**Backend APIs**:
- `GET /api/devices` - List all devices with status
- `POST /api/devices` - Create device (admin/owner)
- `GET /api/devices/{id}` - Get device details
- `PATCH /api/devices/{id}` - Update device (admin/owner)
- `DELETE /api/devices/{id}` - Delete device, retain historical data (admin/owner)
- `POST /api/devices/{id}/test-connection` - Test Modbus connection
- `GET /api/groups` - List all groups
- `POST /api/groups` - Create group (admin/owner)
- `PATCH /api/groups/{id}` - Update group name (admin/owner)
- `DELETE /api/groups/{id}` - Delete group (admin/owner)
- `POST /api/groups/{id}/devices/{device_id}` - Assign device to group (admin/owner)
- `DELETE /api/groups/{id}/devices/{device_id}` - Remove device from group (admin/owner)

**Frontend**:
- Devices list page with status indicators (online/offline/error)
- Device creation/edit form with:
  - Basic info: name, description, units
  - Modbus configuration: type (TCP/RTU), host, port, register address, data type
  - Sampling interval
  - Threshold configuration: warning and critical levels
- Device detail view showing status, last reading timestamp, and error messages
- Groups list page
- Group creation/edit form
- Device assignment interface (enforce single group per device)

**Tests**:
```bash
# Create device
curl -X POST http://localhost:8000/api/devices \
  -H "Content-Type: application/json" \
  -H "Cookie: access_token=<admin_token>" \
  -d '{
    "name": "Temperature Sensor 1",
    "description": "Warehouse temperature",
    "units": "°C",
    "sampling_interval": 60,
    "thresholds": {"warning": 30, "critical": 35},
    "modbus_config": {
      "type": "tcp",
      "host": "192.168.1.100",
      "port": 502,
      "register": 0,
      "data_type": "float32"
    }
  }'
# → 201 with device ID

# Test connection
curl -X POST http://localhost:8000/api/devices/1/test-connection \
  -H "Cookie: access_token=<admin_token>"
# → 200 {"status": "success", "message": "Connected successfully"}

# Create group and assign device
curl -X POST http://localhost:8000/api/groups \
  -H "Cookie: access_token=<admin_token>" \
  -d '{"name": "Warehouse Sensors"}'
# → 201

curl -X POST http://localhost:8000/api/groups/1/devices/1 \
  -H "Cookie: access_token=<admin_token>"
# → 204

# Verify single-group constraint
curl -X POST http://localhost:8000/api/groups/2/devices/1 \
  -H "Cookie: access_token=<admin_token>"
# → 409 (device already in a group)

# Delete device
curl -X DELETE http://localhost:8000/api/devices/1 \
  -H "Cookie: access_token=<admin_token>"
# → 204
# Verify historical readings are retained in database
```

**Manual Verification**:
- Create device with Modbus TCP configuration
- Test connection and verify success/failure message
- Edit device to change threshold values
- View device detail showing status (offline initially, no readings yet)
- Create multiple groups
- Assign devices to groups
- Attempt to assign device to second group, verify error message
- Delete device, verify it's removed from list but historical data remains

**Requirements**: DDMS-DEV-010, DDMS-DEV-011, DDMS-DEV-012, DDMS-DEV-013, DDMS-DEV-014, DDMS-DEV-020, DDMS-DEV-030, DDMS-DEV-031, DDMS-DEV-040, DDMS-DEV-041, DDMS-DEV-042, DDMS-GRP-010, DDMS-GRP-020, DDMS-GRP-030, DDMS-GRP-040, DDMS-CON-010, DDMS-CON-020

---

## Phase 3: Data Ingestion & Scheduling

**Goal**: Poll devices via Modbus and store time-series readings in database.

**Database**:
- Readings table (TimescaleDB hypertable): device_id, timestamp, value
- Index on (device_id, timestamp)
- Foreign key to devices table

**Backend**:
- APScheduler configuration for device polling jobs
- Modbus client supporting TCP and RTU protocols
- Device poller that:
  - Reads from configured Modbus registers
  - Parses data types (int16, uint16, float32, etc.)
  - Stores readings in database
  - Updates device status (online/offline) and last_reading_at
  - Records communication errors
- Dynamic job management:
  - Add polling job when device is created
  - Update job when sampling_interval changes
  - Remove job when device is deleted

**Backend APIs**:
- `GET /api/devices/{id}/readings/latest` - Get most recent reading
- `GET /api/devices/{id}/readings/current` - Get last N readings for live view

**Tests**:
```bash
# Start Modbus simulator for testing
python3 -m pymodbus.simulator --modbus_server tcp --modbus_port 5020

# Verify readings are being collected
sleep 70  # Wait for first poll (60s interval + buffer)
curl http://localhost:8000/api/devices/1/readings/latest
# → 200 {"device_id": 1, "timestamp": "2025-10-12T...", "value": 23.5}

# Check device status updated
curl http://localhost:8000/api/devices/1
# → 200 {..., "status": "online", "last_reading_at": "2025-10-12T..."}

# Query database directly
docker compose exec db psql -U ddms -d ddms -c \
  "SELECT device_id, timestamp, value FROM readings ORDER BY timestamp DESC LIMIT 10;"
# Should show readings

# Test connection failure handling
# Stop Modbus simulator
curl http://localhost:8000/api/devices/1
# → 200 {..., "status": "offline", "error": "Connection timeout"}

# Verify data persistence across restarts
docker compose restart backend
curl http://localhost:8000/api/devices/1/readings/latest
# Should still return latest reading
```

**Manual Verification**:
- Create device pointing to Modbus simulator
- Wait for sampling interval and verify readings appear in database
- Check device status shows "online" with last reading timestamp
- Stop simulator and verify status changes to "offline" with error message
- Restart simulator and verify status returns to "online"
- Verify scheduler continues polling after backend restart

**Requirements**: DDMS-DATA-010, DDMS-DATA-011, DDMS-DATA-020, DDMS-PROTO-010, DDMS-PROTO-011, DDMS-PROTO-012, DDMS-MON-020

---

## Phase 4: Real-time Monitoring

**Goal**: Live dashboard with concurrent device charts, threshold overlays, and status indicators.

**Backend APIs**:
- `GET /api/devices/{id}/readings/current?limit=20` - Recent readings for trend line
- WebSocket `/ws/live` - Subscribe to device updates, receive readings in real-time

**Frontend**:
- Dashboard page with grid layout for multiple devices
- Device cards showing:
  - Current reading value with timestamp
  - Status indicator (normal/warning/critical)
  - Gauge chart with threshold zones
  - Mini trend line chart (last 5-10 minutes)
- WebSocket client with auto-reconnect
- Real-time chart updates with smooth animations
- Threshold overlay lines on charts
- Color-coded warning/critical indicators (yellow/red)

**Tests**:
```bash
# Test WebSocket connection
npm install -g wscat
wscat -c "ws://localhost:8000/ws/live?token=<jwt_token>"
# Subscribe to device
> {"action": "subscribe", "device_ids": [1]}
# Should receive periodic updates:
# < {"device_id": 1, "timestamp": "...", "value": 23.5, "status": "normal"}

# Verify threshold evaluation
curl -X PATCH http://localhost:8000/api/devices/1 \
  -d '{"thresholds": {"warning": 20, "critical": 25}}'

# Wait for next reading (value above 25)
# WebSocket should show:
# < {"device_id": 1, "value": 26.0, "status": "critical"}
```

**Manual Verification**:
- Navigate to dashboard
- Verify multiple device cards are displayed
- Check gauge charts show current values with threshold zones
- Verify trend line charts show recent data
- Watch for real-time updates (values change automatically)
- Set threshold to trigger warning:
  - Device card shows yellow indicator
  - Chart shows yellow highlighting
- Set threshold to trigger critical:
  - Device card shows red indicator
  - Chart shows red highlighting
- Open browser DevTools, verify WebSocket connection is active
- Refresh page, verify auto-reconnect works
- Hover over chart points to see exact values and timestamps

**Requirements**: DDMS-MON-010, DDMS-MON-020, DDMS-MON-030, DDMS-MON-040, DDMS-MON-050, DDMS-MON-060

---

## Phase 5: Historical Data & Export

**Goal**: Query and visualize historical trends with CSV export capability.

**Backend APIs**:
- `GET /api/devices/{id}/readings/history?start=<iso8601>&end=<iso8601>&interval=<seconds>` - Historical data with optional aggregation
- `GET /api/devices/{id}/readings/export?start=<iso8601>&end=<iso8601>` - Download CSV file

**Frontend**:
- History page with device selector
- Custom time range picker
- Historical line chart with:
  - Threshold lines overlay
  - Threshold violation highlighting
  - Zoom and pan controls (optional)
- Export CSV button
- Loading states for large queries

**Tests**:
```bash
# Query historical data
curl "http://localhost:8000/api/devices/1/readings/history?\
start=2025-10-11T00:00:00Z&\
end=2025-10-12T23:59:59Z"
# → 200 [{"timestamp": "...", "value": 23.5}, ...]

# Test aggregation for long ranges
curl "http://localhost:8000/api/devices/1/readings/history?\
start=2025-09-01T00:00:00Z&\
end=2025-10-12T23:59:59Z&\
interval=3600"
# → 200 aggregated data (one point per hour)

# Export CSV
curl "http://localhost:8000/api/devices/1/readings/export?\
start=2025-10-11T00:00:00Z&\
end=2025-10-12T23:59:59Z" \
  --output device1_export.csv

# Verify CSV format
head device1_export.csv
# Device: Temperature Sensor 1
# Units: °C
# Range: 2025-10-11 00:00:00 to 2025-10-12 23:59:59
# timestamp,value
# 2025-10-11T00:00:00Z,23.5
# ...
```

**Manual Verification**:
- Navigate to History page
- Select device from dropdown
- Choose custom time range (e.g., last 24 hours)
- Verify chart displays correct data with threshold lines
- Click "Export CSV" and verify download
- Open CSV file and verify format matches data shown in chart
- Check that threshold violations are highlighted on chart
- Verify loading indicator appears during data fetch

**Requirements**: DDMS-HIST-010, DDMS-HIST-020, DDMS-HIST-030

---

## Phase 6: Group Dashboards

**Goal**: Group-scoped monitoring with live and historical views.

**Backend APIs**:
- `GET /api/groups/{id}/overview` - Group details with device list
- `GET /api/groups/{id}/readings/current` - Current readings for all devices in group
- `GET /api/groups/{id}/readings/history?start=<iso8601>&end=<iso8601>` - Historical data for group devices

**Frontend**:
- Group dashboard page with device selection
- Live monitoring view showing all devices in group simultaneously
- Historical view with multi-device overlay chart
- Group selector in navigation

**Tests**:
```bash
# Get group overview
curl http://localhost:8000/api/groups/1/overview
# → 200 {"id": 1, "name": "Warehouse", "devices": [{"id": 1, ...}, ...]}

# Get current readings for group
curl http://localhost:8000/api/groups/1/readings/current
# → 200 [{"device_id": 1, "value": 23.5, ...}, {"device_id": 2, "value": 45.2, ...}]

# Get group history
curl "http://localhost:8000/api/groups/1/readings/history?\
start=2025-10-11T00:00:00Z&\
end=2025-10-12T23:59:59Z"
# → 200 historical data for all group devices
```

**Manual Verification**:
- Create group and assign multiple devices
- Navigate to group dashboard
- Verify all group devices displayed in live view
- Check that charts update in real-time for all devices
- Switch to historical view
- Verify multi-device chart shows all trends overlaid
- Remove device from group, verify it disappears from dashboard
- Delete group, verify devices remain in system

**Requirements**: DDMS-GRP-050, DDMS-GRP-051

---

## Phase 7: Internationalization & UI Polish

**Goal**: English/Chinese language support and UI refinements.

**Backend APIs**:
- `PATCH /api/users/{id}/preferences` - Update user language preference

**Frontend**:
- i18next configuration with English and Chinese translations
- Language switcher in user menu
- All UI strings translated (navigation, forms, buttons, messages, charts)
- Language preference persisted to backend and restored on login
- UI enhancements:
  - Smooth transitions between views
  - Animated chart updates
  - Loading indicators for async operations
  - Responsive feedback for user actions
  - Hover effects on interactive elements
  - High contrast text for readability
  - Clear visual hierarchy
  - Readable fonts

**Tests**:
```bash
# Update language preference
curl -X PATCH http://localhost:8000/api/users/1/preferences \
  -H "Cookie: access_token=<token>" \
  -d '{"language": "zh-CN"}'
# → 200

# Verify preference persisted
curl http://localhost:8000/api/auth/me \
  -H "Cookie: access_token=<token>"
# → 200 {..., "language": "zh-CN"}
```

**Manual Verification**:
- Login to application (default English)
- Click language switcher → 中文
- Verify all text changes to Chinese without page reload:
  - Navigation menu
  - Form labels and placeholders
  - Button text
  - Status messages
  - Chart labels
- Refresh page, verify language persists
- Logout and login, verify preference restored
- Create second user, verify independent language preferences
- Check UI polish elements:
  - Smooth page transitions
  - Charts animate on data updates
  - Loading spinners appear during API calls
  - Toast notifications on user actions
  - Hover effects on buttons and links
  - Good contrast and readability

**Requirements**: DDMS-I18N-010, DDMS-I18N-020, DDMS-I18N-030, DDMS-I18N-040, DDMS-UI-010, DDMS-UI-020, DDMS-UI-030, DDMS-UI-040, DDMS-UI-050, DDMS-UI-060, DDMS-UI-070, DDMS-UI-080, DDMS-UI-090

---

## Phase 8: Production Hardening

**Goal**: Security, reliability, and deployment readiness.

**Backend**:
- JWT cookie security: HttpOnly, SameSite=Strict, Secure flag in production
- Request logging with structured format and request IDs
- Error handling middleware with appropriate HTTP status codes
- Database connection pooling and retry logic
- WebSocket connection limits and timeout handling

**Infrastructure**:
- Docker Compose configuration with health checks
- Database backup procedures documented
- TimescaleDB retention policy configuration (optional)
- Environment-specific configuration (dev/prod)

**Tests**:
```bash
# Verify cookie security flags
curl -i http://localhost:8000/api/auth/login \
  -d '{"username":"owner","password":"pass"}'
# Set-Cookie should include: HttpOnly; SameSite=Strict

# Test error handling
curl http://localhost:8000/api/devices/99999
# → 404 {"error": "Device not found"}

curl -X POST http://localhost:8000/api/devices \
  -d '{"name": ""}'
# → 400 {"error": "Validation failed", "details": [...]}

# Verify health checks in Docker
docker compose ps
# All services should show "healthy"

# Test data persistence
docker compose restart
sleep 5
curl http://localhost:8000/api/devices/1
# → 200 (data persisted)
```

**Manual Verification**:
- Access system from Chrome and Edge browsers
- Verify all features work correctly
- Test with multiple concurrent users
- Restart all services, verify data persists
- Check logs for structured format
- Review security headers in browser DevTools
- Verify error messages are user-friendly
- Test WebSocket reconnection after network interruption

**Requirements**: DDMS-DEP-020, DDMS-DATA-020

---

## End-to-End Requirement Coverage

**Concepts**:
- [x] DDMS-CON-010: Monitoring device model (Phase 2, 3)
- [x] DDMS-CON-020: Device groups and assignment (Phase 2, 6)

**Deployment**:
- [x] DDMS-DEP-010: Intranet deployment (Phase 8)
- [x] DDMS-DEP-020: Desktop browser access (Phase 1, 8)

**Authentication & Authorization**:
- [x] DDMS-AUTH-010: Owner account setup (Phase 1)
- [x] DDMS-AUTH-011: Update credentials (Phase 1)
- [x] DDMS-AUTH-020: Owner privileges (Phase 1)
- [x] DDMS-AUTH-021: Delete users except self (Phase 1)
- [x] DDMS-AUTH-030: Viewer view-only access (Phase 1)
- [x] DDMS-AUTH-040: Admin manage users (Phase 1)

**Live Monitoring**:
- [x] DDMS-MON-010: Display current readings (Phase 4)
- [x] DDMS-MON-020: Auto-refresh (Phase 3, 4)
- [x] DDMS-MON-030: Yellow warning indicator (Phase 4)
- [x] DDMS-MON-040: Red critical indicator (Phase 4)
- [x] DDMS-MON-050: Threshold markers (Phase 4)
- [x] DDMS-MON-060: Color-coded regions (Phase 4)

**Historical Data**:
- [x] DDMS-HIST-010: Custom time range charts (Phase 5)
- [x] DDMS-HIST-020: Threshold lines on history (Phase 5)
- [x] DDMS-HIST-030: CSV export (Phase 5)

**Device Configuration**:
- [x] DDMS-DEV-010: Add/edit devices (Phase 2)
- [x] DDMS-DEV-011: Device name/description (Phase 2)
- [x] DDMS-DEV-012: Reading units (Phase 2)
- [x] DDMS-DEV-013: Sampling interval (Phase 2)
- [x] DDMS-DEV-014: Modbus configuration (Phase 2)
- [x] DDMS-DEV-020: Threshold rules (Phase 2)
- [x] DDMS-DEV-030: Delete devices (Phase 2)
- [x] DDMS-DEV-031: Retain historical readings (Phase 2)
- [x] DDMS-DEV-040: Connection status display (Phase 3, 4)
- [x] DDMS-DEV-041: Last reading timestamp (Phase 3, 4)
- [x] DDMS-DEV-042: Error indicators (Phase 3, 4)

**Device Grouping**:
- [x] DDMS-GRP-010: Create groups (Phase 2)
- [x] DDMS-GRP-020: Rename groups (Phase 2)
- [x] DDMS-GRP-030: Delete groups (Phase 2)
- [x] DDMS-GRP-040: Assign devices (single group) (Phase 2)
- [x] DDMS-GRP-050: Group live dashboard (Phase 6)
- [x] DDMS-GRP-051: Group historical charts (Phase 6)

**Internationalization**:
- [x] DDMS-I18N-010: English and Chinese (Phase 7)
- [x] DDMS-I18N-020: Switch language (Phase 7)
- [x] DDMS-I18N-030: Remember preference (Phase 7)
- [x] DDMS-I18N-040: Full translation coverage (Phase 7)

**User Interface**:
- [x] DDMS-UI-010: Clean, modern design (Phase 7)
- [x] DDMS-UI-020: Professional appearance (Phase 7)
- [x] DDMS-UI-030: Animated charts (Phase 7)
- [x] DDMS-UI-040: Loading indicators (Phase 7)
- [x] DDMS-UI-050: Responsive feedback (Phase 7)
- [x] DDMS-UI-060: Hover effects (Phase 7)
- [x] DDMS-UI-070: High contrast (Phase 7)
- [x] DDMS-UI-080: Visual hierarchy (Phase 7)
- [x] DDMS-UI-090: Readable fonts (Phase 7)

**Data Persistence**:
- [x] DDMS-DATA-010: Persist config data (Phase 3, 8)
- [x] DDMS-DATA-011: Store time-series data (Phase 3)
- [x] DDMS-DATA-020: Survive restarts (Phase 8)

**Protocol Support**:
- [x] DDMS-PROTO-010: Modbus TCP/IP (Phase 3)
- [x] DDMS-PROTO-011: Modbus RTU (Phase 3)
- [x] DDMS-PROTO-012: Configure registers/data types (Phase 2, 3)

---

## Testing Strategy

**Unit Tests**: Services, security functions, data validation, Modbus adapters

**Integration Tests**: Database migrations, repositories, authentication flow, WebSocket connections

**End-to-End Smoke Test**:
1. Login as owner
2. Create device with Modbus configuration
3. Wait for readings to appear
4. View live dashboard
5. Export historical CSV
6. Create group and assign device
7. View group dashboard
8. Switch language to Chinese
9. Logout

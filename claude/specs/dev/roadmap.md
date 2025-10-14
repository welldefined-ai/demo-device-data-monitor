# DDMS Development Roadmap

This roadmap sequences implementation work into clear iterations, each with deliverables, APIs, UI features, and acceptance tests. Requirement IDs refer to specs/user/requirements.md.

---

## Iteration 0 — Baseline Hardening

### Goals

- Foundation for stable iteration: settings, logging, health, migrations
- CI sanity (lint, types, smoke tests)

### Scope

**Database**:

- Alembic environment and initial empty migration

**Backend**:

- `GET /api/health` - API health check
- `GET /api/version` - System version info

### Acceptance

- `curl http://localhost:8081/api/health` → `{"status":"ok","env":"development"}`
- `curl http://localhost:8081/api/version` → `{"version":"0.1.0"}`
- `open http://localhost:8081/api/docs` → Swagger UI loads
- `alembic upgrade head` → runs clean
- `docker compose ps` → all services healthy

### Requirements

- Foundational; enables all other requirements

---

## Iteration 1: Authentication & Authorization

### Goals

- Secure access with role-based permissions.

### Scope

**Database**:

- Users table: id, username, password_hash, role (owner/admin/viewer), language_preference, created_at, updated_at
- Seed initial owner account on empty database

**Backend**:

- `POST /api/auth/login` - Authenticate user, return JWT in HttpOnly cookie
- `POST /api/auth/logout` - Clear authentication cookie
- `GET /api/auth/me` - Get current user info
- `GET /api/users` - List users (owner/admin only)
- `POST /api/users` - Create admin or viewer user (owner/admin)
- `PATCH /api/users/{id}` - Update username or password
- `DELETE /api/users/{id}` - Delete user (owner/admin, prevent owner self-delete)

**Frontend**:

- Login page with username/password form
- Protected routes with role-based access control
- User management page (owner/admin only)
- Profile page for password changes
- App layout with navigation and user menu

### Acceptance

**Manual Verification**:

- Login with default owner credentials
- Change owner password via profile page
- Create admin and viewer users
- Logout and login as admin, verify can manage users
- Login as viewer, verify read-only access (no create/edit/delete buttons)

**Requirements**:

- [x] DDMS-AUTH-010: Owner account setup
- [x] DDMS-AUTH-011: Update credentials
- [x] DDMS-AUTH-020: Owner privileges
- [x] DDMS-AUTH-021: Delete users except self
- [x] DDMS-AUTH-030: Viewer view-only access
- [x] DDMS-AUTH-040: Admin manage users
- [x] DDMS-DEP-020: Desktop browser access

---

## Iteration 2: Device & Group Management

### Goals

- CRUD operations for devices and device groups with single-group assignment.

### Scope

**Database**:

- Devices table: id, name, description, unit, sampling_interval, thresholds (JSON: warning/critical), modbus_config (JSON: type/host/port/register/data_type), status, last_reading_at, created_at, updated_at
- Device groups table: id, name, description, created_at, updated_at
- Group devices junction table: group_id, device_id (unique constraint on device_id for single-group enforcement)

**Backend**:

- Devices:
  - `GET /api/devices` - List all devices with status
  - `POST /api/devices` - Create device (admin/owner)
  - `GET /api/devices/{id}` - Get device details
  - `PATCH /api/devices/{id}` - Update device (admin/owner)
  - `DELETE /api/devices/{id}` - Delete device, retain historical data (admin/owner)
  - `POST /api/devices/{id}/test-connection` - Test Modbus connection
- Groups:
  - `GET /api/groups` - List all groups
  - `POST /api/groups` - Create group (admin/owner)
  - `PATCH /api/groups/{id}` - Update group name (admin/owner)
  - `DELETE /api/groups/{id}` - Delete group (admin/owner)
  - `GET /api/groups/{id}/devices` - List devices in group
  - `POST /api/groups/{id}/devices/{device_id}` - Assign device to group (admin/owner)
  - `DELETE /api/groups/{id}/devices/{device_id}` - Remove device from group (admin/owner)

**Frontend**:

- Devices list page with status indicators (online/offline/error)
- Device creation/edit form with basic info, Modbus configuration, sampling interval, and threshold configuration
- Device detail view showing status, last reading timestamp, and error messages
- Groups list page
- Group creation/edit form
- Device assignment interface (enforce single group per device)
- Device removal from group interface

### Acceptance

**Manual Verification**:

- Create device with Modbus TCP configuration
- Test connection and verify success/failure message
- Edit device to change threshold values
- View device detail showing status (offline initially, no readings yet)
- Create multiple groups and assign devices
- Attempt to assign device to second group, verify error message
- View devices in group and remove a device from group
- Delete device, verify it's removed from list but historical data remains

**Requirements**:

- [x] DDMS-CON-010: Monitoring device model
- [x] DDMS-CON-020: Device groups and assignment
- [x] DDMS-DEV-010: Add/edit devices
- [x] DDMS-DEV-011: Device name/description
- [x] DDMS-DEV-012: Reading units
- [x] DDMS-DEV-013: Sampling interval
- [x] DDMS-DEV-014: Modbus configuration
- [x] DDMS-DEV-020: Threshold rules
- [x] DDMS-DEV-030: Delete devices
- [x] DDMS-DEV-031: Retain historical readings
- [x] DDMS-DEV-040: Connection status display
- [x] DDMS-DEV-041: Last reading timestamp
- [x] DDMS-DEV-042: Error indicators
- [x] DDMS-GRP-010: Create groups
- [x] DDMS-GRP-020: Rename groups
- [x] DDMS-GRP-030: Delete groups
- [x] DDMS-GRP-040: Assign devices (single group)

---

## Iteration 3: Data Ingestion & Scheduling

### Goals

- Poll devices via Modbus and store time-series readings in database.

### Scope

**Database**:

- Readings table (TimescaleDB hypertable): device_id, timestamp, value
- Index on (device_id, timestamp)
- Foreign key to devices table

**Backend**:

- APScheduler configuration for device polling jobs
- Modbus client supporting TCP and RTU protocols
- Device poller that reads from configured Modbus registers, parses data types, stores readings, updates device status and last_reading_at, records communication errors
- Dynamic job management: add polling job when device is created, update job when sampling_interval changes, remove job when device is deleted
- `GET /api/devices/{id}/readings/current` - Get last N readings for live view

### Acceptance

**Manual Verification**:

- Create device pointing to Modbus simulator
- Wait for sampling interval and verify readings appear in database
- Check device status shows "online" with last reading timestamp
- Stop simulator and verify status changes to "offline" with error message
- Restart simulator and verify status returns to "online"
- Verify scheduler continues polling after backend restart

**Requirements**:

- [x] DDMS-DATA-010: Persist config data
- [x] DDMS-DATA-011: Store time-series data
- [x] DDMS-DATA-020: Survive restarts
- [x] DDMS-PROTO-010: Modbus TCP/IP
- [x] DDMS-PROTO-011: Modbus RTU
- [x] DDMS-PROTO-012: Configure registers/data types
- [x] DDMS-MON-020: Auto-refresh

---

## Iteration 4: Real-time Monitoring

### Goals

- Live dashboard with concurrent device charts, threshold overlays, and status indicators.

### Scope

**Backend**:

- `GET /api/devices/{id}/readings/current?limit=20` - Recent readings for trend line
- WebSocket `/ws/live` - Subscribe to device updates, receive readings in real-time

**Frontend**:

- Dashboard page with grid layout for multiple devices
- Device cards showing current reading value with timestamp, status indicator (normal/warning/critical), gauge chart with threshold zones, mini trend line chart
- WebSocket client with auto-reconnect
- Real-time chart updates with smooth animations
- Threshold overlay lines on charts
- Color-coded warning/critical indicators (yellow/red)

### Acceptance

**Manual Verification**:

- Navigate to dashboard and verify multiple device cards displayed
- Check gauge charts show current values with threshold zones
- Verify trend line charts show recent data
- Watch for real-time updates (values change automatically)
- Set threshold to trigger warning (yellow indicator and chart highlighting)
- Set threshold to trigger critical (red indicator and chart highlighting)
- Open browser DevTools, verify WebSocket connection is active
- Refresh page, verify auto-reconnect works
- Hover over chart points to see exact values and timestamps

**Requirements**:

- [x] DDMS-MON-010: Display current readings
- [x] DDMS-MON-020: Auto-refresh
- [x] DDMS-MON-030: Yellow warning indicator
- [x] DDMS-MON-040: Red critical indicator
- [x] DDMS-MON-050: Threshold markers
- [x] DDMS-MON-060: Color-coded regions

---

## Iteration 5: Historical Data & Export

### Goals

- Query and visualize historical trends with CSV export capability.

### Scope

**Backend**:

- `GET /api/devices/{id}/readings/history?start=<iso8601>&end=<iso8601>&interval=<seconds>` - Historical data with optional aggregation
- `GET /api/devices/{id}/readings/export?start=<iso8601>&end=<iso8601>` - Download CSV file

**Frontend**:

- History page with multi-device selector (supports multiple devices)
- Custom date range picker (date-only, 2-click selection)
- Historical line chart with:
  - Multi-device overlay support
  - Dual Y-axes for different units (max 2 for readability)
  - Threshold-colored curve segments (green/yellow/red)
  - Zoom and pan controls
  - Legend to toggle devices
- Export CSV button
- Loading states for large queries

### Acceptance

**Manual Verification**:

- Navigate to History page
- Select single device from dropdown, verify chart displays
- Select multiple devices (e.g., Temperature + Pressure), verify dual Y-axes
- Choose custom date range (2 clicks on calendar)
- Verify chart displays correct data with threshold-colored curve segments
- Verify curve segments change color at threshold crossings (green/yellow/red)
- Click legend items to toggle devices on/off
- Use zoom and pan controls
- Click "Export CSV" and verify download
- Open CSV file and verify format matches data shown in chart
- Verify loading indicator appears during data fetch

**Requirements**:

- [x] DDMS-HIST-010: Custom time range charts (single or multiple devices)
- [x] DDMS-HIST-015: Multiple Y-axes for different units
- [x] DDMS-HIST-020: Threshold indication on history (color-coded segments)
- [x] DDMS-HIST-030: CSV export

---

## Iteration 6: Group Dashboards

### Goals

- Group-scoped monitoring with live and historical views.

### Scope

**Backend**:

- `GET /api/groups/{id}/overview` - Group details with device list
- `GET /api/groups/{id}/readings/current` - Current readings for all devices in group
- `GET /api/groups/{id}/readings/history?start=<iso8601>&end=<iso8601>` - Historical data for group devices

**Frontend**:

- Group dashboard page with device selection
- Live monitoring view showing all devices in group simultaneously
- Historical view with multi-device overlay chart
- Group selector in navigation

### Acceptance

**Manual Verification**:

- Create group and assign multiple devices
- Navigate to group dashboard
- Verify all group devices displayed in live view
- Check that charts update in real-time for all devices
- Switch to historical view
- Verify multi-device chart shows all trends overlaid
- Remove device from group, verify it disappears from dashboard
- Delete group, verify devices remain in system

**Requirements**:

- [ ] DDMS-GRP-050: Group live dashboard
- [ ] DDMS-GRP-051: Group historical charts

---

## Iteration 7: Internationalization & UI Polish

### Goals

- English/Chinese language support and UI refinements.

### Scope

**Backend**:

- `PATCH /api/users/{id}/preferences` - Update user language preference

**Frontend**:

- i18next configuration with English and Chinese translations
- Language switcher in user menu
- All UI strings translated (navigation, forms, buttons, messages, charts)
- Language preference persisted to backend and restored on login
- UI enhancements: smooth transitions, animated chart updates, loading indicators, responsive feedback, hover effects, high contrast text, clear visual hierarchy, readable fonts

### Acceptance

**Manual Verification**:

- Login to application (default English)
- Click language switcher → 中文
- Verify all text changes to Chinese without page reload (navigation, forms, buttons, status messages, chart labels)
- Refresh page, verify language persists
- Logout and login, verify preference restored
- Create second user, verify independent language preferences
- Check UI polish elements: smooth page transitions, charts animate on data updates, loading spinners appear during API calls, toast notifications on user actions, hover effects on buttons and links, good contrast and readability

**Requirements**:

- [ ] DDMS-I18N-010: English and Chinese
- [ ] DDMS-I18N-020: Switch language
- [ ] DDMS-I18N-030: Remember preference
- [ ] DDMS-I18N-040: Full translation coverage
- [ ] DDMS-UI-010: Clean, modern design
- [ ] DDMS-UI-020: Professional appearance
- [ ] DDMS-UI-030: Animated charts
- [ ] DDMS-UI-040: Loading indicators
- [ ] DDMS-UI-050: Responsive feedback
- [ ] DDMS-UI-060: Hover effects
- [ ] DDMS-UI-070: High contrast
- [ ] DDMS-UI-080: Visual hierarchy
- [ ] DDMS-UI-090: Readable fonts

---

## Iteration 8: Production Hardening

### Goals

- Security, reliability, and deployment readiness.

### Scope

**Backend**:

- JWT cookie security: HttpOnly, SameSite=Strict, Secure flag in production
- Request logging with structured format and request IDs
- Error handling middleware with appropriate HTTP status codes
- Database connection pooling and retry logic
- WebSocket connection limits and timeout handling

**Infrastructure**:

- Docker Compose configuration with health checks
- Database backup procedures documented
- Environment-specific configuration (dev/prod)

### Acceptance

**Manual Verification**:

- Access system from Chrome and Edge browsers
- Verify all features work correctly
- Test with multiple concurrent users
- Restart all services, verify data persists
- Check logs for structured format
- Review security headers in browser DevTools
- Verify error messages are user-friendly
- Test WebSocket reconnection after network interruption

**Requirements**:

- [ ] DDMS-DEP-010: Intranet deployment
- [ ] DDMS-DEP-020: Desktop browser access
- [ ] DDMS-DATA-020: Survive restarts

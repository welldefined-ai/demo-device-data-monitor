# DDMS Development Roadmap

This roadmap sequences implementation work into clear phases. For each
phase we state the goal, public interfaces, and acceptance tests. IDs
refer to specs/user/requirements.md (MVP baseline).

## Phase 0 — Baseline Hardening

Goals
- Foundation for stable iteration: settings, logging, health, migrations
- CI sanity (lint, types, smoke tests)

Scope
- Alembic environment and initial empty migration
- Health endpoints: `/health`, `/api/health`, `/api/version`
- Logging config via `ddms.core.logging` and typed settings via
  `ddms.core.config`

Tests
- `curl http://localhost:8800/health` → 200 `{status: ok, env}`
- `curl http://localhost:8080/api/health` → 200 `{status: ok}`
- `alembic upgrade head` runs clean on fresh DB

Requirements
- Foundational; enables all other requirements

## Phase 1 — Authentication & Roles

Goals
- Role-based access with owner/admin/viewer and session cookies

Interfaces
- Auth (JWT in HttpOnly cookie):
  - `POST /api/auth/login`
  - `POST /api/auth/logout`
  - `GET  /api/auth/me`
- Users (owner/admin scope):
  - `GET  /api/users` (owner only)
  - `POST /api/users` (admin/owner: create admin/viewer)
  - `PATCH/DELETE /api/users/{id}` (prevent owner self-delete)

Acceptance
- DDMS-AUTH-011: Owner updates username/password; re-login works
- DDMS-AUTH-040: Admin creates/edits/deletes admin/viewer
- DDMS-AUTH-030: Viewer receives 403 on write endpoints
- DDMS-DEP-020: Login and navigation work on Chrome/Edge

## Phase 2 — Devices & Groups

Goals
- Device CRUD and single-group assignment; show device status

Interfaces
- Devices:
  - `GET/POST/PATCH/DELETE /api/devices`
  - Device attributes include: name, description, units, sampling_interval,
    thresholds (warning/critical), Modbus connection params, status
    (online/offline/error), last_reading_at
- Groups:
  - `GET/POST/PATCH/DELETE /api/groups`
  - `POST /api/groups/{id}/devices` (assign) and `DELETE /api/groups/{id}/devices/{device_id}` (remove)
  - Enforce at most one group per device

Acceptance
- DDMS-DEV-010..014/020: Add/edit device with full fields; validation works
- DDMS-DEV-030/031: Deleting a device retains readings
- DDMS-DEV-040/041/042: Status/last_reading_at/error visible in list
- DDMS-GRP-010/020/030/040: CRUD groups; assign one group per device

## Phase 3 — Ingestion & Scheduler

Goals
- Poll devices via Modbus and persist readings on schedule

Interfaces
- Modbus connection test: `POST /api/devices/{id}/test-connection`
- Scheduler behavior: poll each device every `sampling_interval` seconds
- Readings query (basic): `GET /api/readings?device_id=…&from=…&to=…`

Acceptance
- DDMS-PROTO-010/011/012: TCP and RTU work with configured registers/types
- DDMS-DEV-013/040/041/042: Scheduler writes readings; status/last_reading_at
  updates; errors recorded; recovery after outage
- DDMS-DATA-010/011/020: Data persists across restarts

## Phase 4 — Realtime Monitoring

Goals
- Live dashboard with multi-device charts and threshold indicators

Interfaces
- WebSocket `/ws/live`
  - Subscribe: `{ type: "subscribe", device_ids: number[] }`
  - Unsubscribe: `{ type: "unsubscribe", device_ids: number[] }`
  - Server event: `{ device_id, timestamp, value, status }` where
    `status ∈ {normal, warning, critical}`
  - On subscribe ack, server may include `{ thresholds: { warn, critical } }`

Acceptance
- DDMS-MON-010/020: Multiple devices update live; timestamps visible
- DDMS-MON-030/040: Yellow/red indicators when thresholds crossed
- DDMS-MON-050/060: Threshold markers/regions rendered on charts

## Phase 5 — Historical Analysis & CSV Export

Goals
- Time-range queries with downsampling and per-device CSV export

Interfaces
- `GET /api/readings?device_id=…&from=…&to=…&interval=auto`
- `GET /api/readings/export?device_id=…&from=…&to=…`
  (CSV streaming)

Acceptance
- DDMS-HIST-010: Charts render chosen range; auto bucket sizing
- DDMS-HIST-030: Zoom interactions work
- DDMS-HIST-040: CSV downloads; headers and values correct
- DDMS-HIST-050: Threshold lines on historical charts

## Phase 6 — Group Dashboards

Goals
- Group-scoped live and historical views (client-side composition)

Interfaces
- No group aggregate endpoints in MVP. UI composes existing device
  readings API and `/ws/live` with the group’s device IDs.

Acceptance
- DDMS-GRP-050/051: Selecting a group scopes both live and historical
  charts to assigned devices; no group-level export

## Phase 7 — Localization & UI Polish

Goals
- English/Chinese switch; desktop-focused responsiveness; UX polish

Interfaces
- i18n runtime switching and persisted preference

Acceptance
- DDMS-I18N-020: Switch without reload; UI updates in place
- DDMS-I18N-030: Preference remembers across sign-ins
- DDMS-UI-010..090: Visual polish, loading, feedback, contrast, hierarchy

## Phase 8 — Hardening & Ops

Goals
- Security, reliability, observability, and ops readiness

Interfaces
- Secure cookies (HttpOnly, SameSite=Strict; Secure in prod)
- Health checks for services; structured logs with request IDs

Acceptance
- DDMS-DEP-020: Access from modern desktop browsers (Chrome, Edge)
- DDMS-DATA-020: Restart and data persists; healthchecks green

---

## End-to-End Requirement Coverage Checklist

Concepts
- [x] DDMS-CON-020: Device model and readings (Phase 2/3)
- [x] DDMS-CON-030: Device groups and dashboards (Phase 2/6)

Deployment
- [x] DDMS-DEP-010: Intranet, on-prem operation (Phase 8)
- [x] DDMS-DEP-020: Desktop browsers (Chrome, Edge) (Phase 8)

Authentication & Authorization
- [x] DDMS-AUTH-010/011: Owner account, can update credentials (Phase 1)
- [x] DDMS-AUTH-020/021: Owner privileges, cannot delete itself (Phase 1)
- [x] DDMS-AUTH-030: Viewer view-only (Phase 1)
- [x] DDMS-AUTH-040: Admin manages admins/viewers (Phase 1)

Live Monitoring
- [x] DDMS-MON-010/020: Current readings, auto-refresh (Phase 4)
- [x] DDMS-MON-030/040: Yellow/red indicators (Phase 4)
- [x] DDMS-MON-050/060: Threshold markers/regions (Phase 4)

Historical Data
- [x] DDMS-HIST-010/020: Range selection, threshold lines (Phase 5)
- [x] DDMS-HIST-030/040: CSV export, zoom (Phase 5)
- [x] DDMS-HIST-050: Threshold lines (Phase 5)

Device Configuration
- [x] DDMS-DEV-010..014/020: Device add/edit config (Phase 2)
- [x] DDMS-DEV-030/031: Deletion retains readings (Phase 2)
- [x] DDMS-DEV-040/041/042: Status/last-read/error (Phase 3/4 UI)

Device Grouping
- [x] DDMS-GRP-010..040: Groups CRUD and single assignment (Phase 2)
- [x] DDMS-GRP-050/051: Group-scoped live/history (Phase 6)

Internationalization & UI
- [x] DDMS-I18N-010..040: Languages, switch, remember, coverage (Phase 7)
- [x] DDMS-UI-010..090: UI polish and accessibility (Phase 7)

Data Persistence & Protocols
- [x] DDMS-DATA-010/011/020: Persistence (Phase 3/8)
- [x] DDMS-PROTO-010/011/012: Modbus TCP/RTU + config (Phase 3)

---

## PR Sequence and Conventions

- One PR per phase (split large phases if needed)
- Branch names: `feature/<area>` (e.g., `feature/authn-roles`)
- Commit messages: `<sequence>-<type>(<scope>): <subject>` per specs/dev/general.md
- Include Acceptance section from this roadmap in each PR description

## Testing Strategy Summary

- Unit: services, security, schema validation, adapters, bucketing
- Integration: migrations, repositories, auth cookie flow
- E2E (smoke): login → add device → live feed → export CSV

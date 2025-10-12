# DDMS Development Roadmap

This roadmap sequences implementation work into clear phases, each with
deliverables, APIs, UI, DB changes, and concrete tests. Requirement IDs
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
- Secure access with role-based permissions per MVP

DB
- `users(id, username, pw_hash, role['owner','admin','viewer'], created_at, updated_at)`
- Seed initial `owner` on empty DB

Backend
- Auth endpoints (JWT in HttpOnly cookie):
  - `POST /api/auth/login`, `POST /api/auth/logout`, `GET /api/auth/me`
- User management (owner/admin scope):
  - `GET/POST/PATCH/DELETE /api/admin/users` (owner cannot delete itself)
- Implement JWT create/verify in `ddms.core.security`

Frontend
- Login flow; profile change username/password
- Role-gated routes and navigation

Tests (manual + API)
- AUTH-011: Owner can change username/password; re-login succeeds
- AUTH-040: Admin can manage admin and viewer users (create/edit/delete)
- AUTH-030: Viewer cannot modify data (403 on writes)

Requirements
- DDMS-AUTH-010/011/020/021/030/040; DDMS-DEP-020

## Phase 2 — Devices & Groups

Goals
- CRUD for devices and groups; single-group assignment

DB
- `devices(id, name, description, unit, sample_interval_s, warn_low, warn_high, modbus jsonb, created_at, updated_at)`
- `device_groups(id, name, description, created_at, updated_at)`
- `group_devices(group_id, device_id)` (enforce at most one group per device)

Backend
- Devices: `GET/POST/PATCH/DELETE /api/devices`
- Groups: `GET/POST/PATCH/DELETE /api/groups`, `POST /api/groups/:id/devices`
- Device status fields exposed: online/offline, last_read_ts, comm_error

Frontend
- Devices pages: list, create/edit; show status/last-read/error
- Groups pages: list, create/edit, assign devices (single-group)

Tests
- DEV-010..020: Create/edit device with name/desc/units/sampling/thresholds
- DEV-014: Configure Modbus address/register settings
- DEV-030/031: Delete device; readings retained
- DEV-040/041/042: Status/last read/error indicators visible
- GRP-010/020/030/040: Create/rename/delete groups; assign one group per device

Requirements
- DDMS-DEV-010..014/020/030/031/040/041/042; DDMS-GRP-010..040; DDMS-CON-020/030

## Phase 3 — Ingestion & Scheduler

Goals
- Poll devices on schedule and persist readings

DB
- `readings(device_id, ts timestamptz, metric text default 'value',
  value double precision, tags jsonb null)`
- Timescale hypertable and index `(device_id, ts)`

Backend
- APScheduler registry for per-device jobs based on `sample_interval_s`
- Modbus adapters in `ddms.ingestion` for TCP and RTU with connection test
- Endpoint: `POST /api/devices/:id/test-connection`

Frontend
- Device detail: “Test Connection” UI and last run status

Tests
- DATA-020: Readings written at interval; `GET /api/readings` returns data
- Restart containers; data persists (configs, users, readings)

Requirements
- DDMS-DATA-010/011/020; DDMS-PROTO-010/011/012

## Phase 4 — Realtime Monitoring

Goals
- Concurrent live charts with threshold markers and highlight

Backend
- WS `/ws/live` subscribe by device IDs; payload includes latest reading and
  device thresholds for overlay; broadcast on new readings

Frontend
- Live dashboard (multi-device, or per group selection)
- Threshold markers/values; yellow/red indicators; optional color regions

Tests
- MON-010/020: Multiple devices update live without manual refresh; timestamps visible
- MON-030/040: Yellow/red indicators on threshold crossings
- MON-050/060: Threshold markers/regions rendered on charts

Requirements
- DDMS-MON-010..060

## Phase 5 — Historical Analysis & CSV Export

Goals
- Custom time range trends and export

Backend
- `GET /api/readings?device_id=…&metric=…&from=…&to=…&sampling=auto`
- `GET /api/readings/export?...` streams CSV for same filters

Frontend
- Historical view with time range pickers and “Export CSV”

Tests
- HIST-010: Charts render correct range; bucket sizing auto-scales
- HIST-030: Zoom interactions work (in/out)
- HIST-040: CSV downloads; headers/timestamps/values match UI and DB
- HIST-050: Threshold lines visible on historical charts

Requirements
- DDMS-HIST-010/020/030/040/050

## Phase 6 — Group Dashboards

Goals
- Group-scoped live and historical interfaces

Backend
- `GET /api/groups/:id/overview` summary + device list

Frontend
- Group dashboard with tabs: Live and History; scope to group devices

Tests
- GRP-050/051: Selecting a group scopes both live and historical charts

Requirements
- DDMS-GRP-050/051

## Phase 7 — Localization & UI Polish

Goals
- English/Chinese switch; desktop-focused responsive layout; subtle transitions

Frontend
- i18next setup and resources (en, zh)
- Language switcher; remember preference; transitions for page/panel changes

Tests
- I18N-020: Switch language without page reload; content updates instantly
- I18N-030: Preference remembered across sign-ins
- UI-010/020/030/040/050/060/070/080/090: Visual and interaction polish per spec

Requirements
- DDMS-I18N-010..040; DDMS-UI-010..090

## Phase 8 — Hardening & Ops

Goals
- Security, reliability, observability, and ops readiness

Backend
- Cookie flags: HttpOnly, SameSite=Strict; Secure in prod
- Structured logs with request IDs; basic error handling; optional rate limiting

Infra
- Compose with DB profile; healthchecks; Timescale retention (optional follow-up)

Tests
- DEP-020: Access from modern desktop browsers (Chrome, Edge)
- DATA-020: Restart and data persists; healthchecks green

Requirements
- DDMS-DEP-020; DDMS-DATA-020

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

- Create one PR per phase (split large phases as needed)
- Branch names: `feature/<area>` (e.g., `feature/authn-roles`)
- Commit messages: `<sequence>-<type>(<scope>): <subject>` per specs/dev/general.md
- Add short verification steps in each PR description (copy from Tests above)

## Testing Strategy Summary

- Unit: services, security, schema validation, adapters, bucketing
- Integration: migrations, repositories, auth cookie flow
- E2E (smoke): login → add device → live feed → export CSV

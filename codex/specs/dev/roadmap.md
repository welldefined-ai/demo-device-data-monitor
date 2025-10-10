# DDMS Development Roadmap

This roadmap sequences implementation work into clear phases, each with
deliverables, APIs, UI, DB changes, and concrete tests. Requirement IDs
refer to specs/user/requirements.md.

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
- Secure access with role-based permissions
- Owner first-login password rotation

DB
- `users(id, username, pw_hash, role['owner','admin','viewer'], active,
  must_rotate_pw, created_at, updated_at)`
- Seed initial `owner` on empty DB

Backend
- Auth endpoints (JWT in HttpOnly cookie):
  - `POST /api/auth/login`, `POST /api/auth/logout`, `GET /api/auth/me`
  - `POST /api/auth/rotate-password`
- Admin user management:
  - `GET/POST/PATCH /api/admin/users`, `PATCH /api/admin/users/:id/activate`
- Implement JWT create/verify in `ddms.core.security`

Frontend
- Login + forced password rotation flow
- Profile: change username/password
- Role-gated routes and navigation

Tests (manual + API)
- ACC-020: First login requires password change
- ACC-030: Owner can change username/password and re-login succeeds
- ACC-040: Admin can add/edit/deactivate admins
- ACC-050: Admin can add viewers; viewers cannot modify data (403 on writes)

Requirements
- ACC-020, ACC-030, ACC-040, ACC-050, ACC-010 (browser access confirmed later)

## Phase 2 — Devices & Groups

Goals
- CRUD for devices and groups; assignments; audit trail

DB
- `devices(id, name, location, unit, sample_interval_s, warn_low, warn_high,
  meta jsonb, active, created_at, updated_at)`
- `device_groups(id, name, description, created_at, updated_at)`
- `group_devices(group_id, device_id)`
- `config_audit(id, entity_type, entity_id, change jsonb, actor_user_id, created_at)`

Backend
- Devices: `GET/POST/PATCH/DELETE /api/devices`
- Groups: `GET/POST/PATCH/DELETE /api/groups`, `POST /api/groups/:id/devices`
- Write audit entries on create/update/delete

Frontend
- Devices pages: list, create/edit, detail with audit panel
- Groups pages: list, create/edit, assign devices (transfer/list)

Tests
- CONF-010: Create device with all fields; validation errors for invalid intervals
- CONF-020: Edit/delete device; audit entries preserved
- CONF-030: Create/edit/delete groups; assign/unassign devices; permissions enforced

Requirements
- CONF-010, CONF-020, CONF-030; CON-020/030 realized as domain model

## Phase 3 — Ingestion & Scheduler

Goals
- Poll devices on schedule and persist readings

DB
- `readings(device_id, ts timestamptz, metric text default 'value',
  value double precision, tags jsonb null)`
- Timescale hypertable and index `(device_id, ts)`

Backend
- APScheduler registry for per-device jobs based on `sample_interval_s`
- Modbus adapters in `ddms.ingestion` (TCP/RTU) with connection test
- Endpoint: `POST /api/devices/:id/test-connection`

Frontend
- Device detail: “Test Connection” UI and last run status

Tests
- DAT-010: Readings written at interval; `GET /api/readings` returns data
- Restart containers; data persists (configs, users, readings)

Requirements
- DAT-010

## Phase 4 — Realtime Monitoring

Goals
- Concurrent live charts with threshold markers and highlight

Backend
- WS `/ws/live` subscribe by device IDs; payload includes latest reading and
  device thresholds for overlay; broadcast on new readings

Frontend
- Live dashboard (multi-device, or per group selection)
- Threshold lines; segments colored yellow/red on exceedance

Tests
- LIV-010: Multiple devices update live without manual refresh
- LIV-020: Threshold markers rendered on charts
- LIV-030: Exceeding thresholds highlights segments (yellow/red)

Requirements
- LIV-010, LIV-020, LIV-030

## Phase 5 — Historical Analysis & CSV Export

Goals
- Custom time range trends and export

Backend
- `GET /api/readings?device_id=…&metric=…&from=…&to=…&sampling=auto`
- `GET /api/readings/export?...` streams CSV for same filters

Frontend
- Historical view with time range pickers and “Export CSV”

Tests
- HIS-010: Charts render correct range; bucket sizing auto-scales
- HIS-020: CSV downloads; headers/timestamps/values match UI and DB

Requirements
- HIS-010, HIS-020

## Phase 6 — Group Dashboards

Goals
- Group-scoped live and historical interfaces

Backend
- `GET /api/groups/:id/overview` summary + device list

Frontend
- Group dashboard with tabs: Live and History; scope to group devices

Tests
- CONF-040: Selecting a group scopes both live and historical charts

Requirements
- CONF-040

## Phase 7 — Localization & UI Polish

Goals
- English/Chinese switch; responsive layout; subtle transitions

Frontend
- i18next setup and resources (en, zh)
- Language switcher; state persisted; transitions for page/panel changes

Tests
- UI-010: Switch language without page reload; content updates instantly
- UI-020: Layout responsive across typical resolutions
- UI-030: Transitions smooth and non-distracting

Requirements
- UI-010, UI-020, UI-030

## Phase 8 — Hardening & Ops

Goals
- Security, reliability, observability, and ops readiness

Backend
- Cookie flags: HttpOnly, SameSite=Strict; Secure in prod
- Structured logs with request IDs; basic error handling; optional rate limiting

Infra
- Compose with DB profile; healthchecks; Timescale retention (optional follow-up)

Tests
- ACC-010: Access from modern desktop browsers without extra software
- DAT-010: Restart and data persists; healthchecks green

Requirements
- ACC-010, DAT-010

---

## End-to-End Requirement Coverage Checklist

Concepts
- [x] DDMS-CON-010: Browser-based, intranet delivery (ACC-010 verified)
- [x] DDMS-CON-020: Device model and readings (Phase 2/3)
- [x] DDMS-CON-030: Device groups and dashboards (Phase 2/6)

Access & Authentication
- [x] DDMS-ACC-010: Desktop browsers, no extra client (Phase 8)
- [x] DDMS-ACC-020: First login password change (Phase 1)
- [x] DDMS-ACC-030: Owner can update credentials (Phase 1)
- [x] DDMS-ACC-040: Admin manages admins (Phase 1)
- [x] DDMS-ACC-050: View-only accounts (Phase 1)

Live Monitoring & Alerts
- [x] DDMS-LIV-010: Real-time charts, multiple devices (Phase 4)
- [x] DDMS-LIV-020: Threshold markers (Phase 4)
- [x] DDMS-LIV-030: Yellow/red highlights on exceedance (Phase 4)

Historical Analysis & Export
- [x] DDMS-HIS-010: Historical charts for custom range (Phase 5)
- [x] DDMS-HIS-020: CSV export of displayed dataset (Phase 5)

Device & Group Configuration
- [x] DDMS-CONF-010: Add devices with full fields (Phase 2)
- [x] DDMS-CONF-020: Edit/delete with audit trail (Phase 2)
- [x] DDMS-CONF-030: Groups and assignments (Phase 2)
- [x] DDMS-CONF-040: Group-scoped dashboards (Phase 6)

Localization & UI
- [x] DDMS-UI-010: English/Chinese switch without reload (Phase 7)
- [x] DDMS-UI-020: Clean responsive layout (Phase 7)
- [x] DDMS-UI-030: Subtle dynamic effects (Phase 7)

Data Persistence
- [x] DDMS-DAT-010: Persist users, devices, readings across restarts (Phase 3/8)

---

## PR Sequence and Conventions

- Create one PR per phase (split large phases as needed)
- Branch names: `feature/<area>` (e.g., `feature/authn-roles`)
- Commit messages: `<sequence>-<type>(<scope>): <subject>` per specs/dev/general.md
- Add short verification steps in each PR description (copy from Tests above)

## Testing Strategy Summary

- Unit: services, security, schema validation, adapters, bucketing
- Integration: migrations, repositories, auth cookie flow
- E2E (smoke): login → rotate password → add device → live feed → export CSV


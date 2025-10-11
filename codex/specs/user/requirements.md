# Device Data Monitoring System Requirements (MVP)

This document is the MVP baseline, merging Codex and Claude requirements with
explicit MVP choices noted. The goal is fast implementation with minimal scope.

## Deployment

**[DDMS-DEP-010]** The DDMS _shall_ be deployed on the customer intranet (on‑premises server) and operate without external internet access.

**[DDMS-DEP-020]** The DDMS _shall_ be accessible from modern desktop web browsers without installing additional client software (Chrome, Edge, Firefox, Safari latest two major versions).

## Concepts

**[DDMS-CON-010]** The Device Data Monitoring System (DDMS) _shall_ deliver browser-based monitoring for industrial environments on the customer intranet.

**[DDMS-CON-020]** The DDMS _shall_ treat each physical sensor endpoint, PLC, or gateway as a **monitoring device** whose readings are collected and visualized.

**[DDMS-CON-030]** The DDMS _shall_ represent a **device group** as a user-defined collection of monitoring devices that share dashboards and configuration defaults.

## Access & Authentication

**[DDMS-ACC-010]** The DDMS _shall_ be accessible from modern desktop browsers on the customer intranet without installing additional client software.

**[DDMS-ACC-015]** The DDMS _shall_ provide an initial owner account (username and password) on first setup.

**[DDMS-ACC-020]** _When_ the owner signs in for the first time with the provided default credentials, the DDMS _shall_ require the owner to set a new password before continuing.

**[DDMS-ACC-030]** The DDMS _shall_ allow the owner to update their username and password at any time after initial setup.

**[DDMS-ACC-040]** The DDMS _shall_ allow administrators to add, edit, or delete other administrator accounts (the owner account cannot be deleted).

**[DDMS-ACC-050]** The DDMS _shall_ allow administrators to add read-only user accounts that can view data and dashboards but cannot modify configurations.

## Live Monitoring & Alerts

**[DDMS-LIV-010]** The DDMS _shall_ display real-time charts for multiple monitoring devices concurrently with automatic refresh.

**[DDMS-LIV-020]** The DDMS _shall_ overlay warning threshold markers on live charts to show the relationship between current readings and their configured limits.

**[DDMS-LIV-030]** _When_ a reading crosses its warning thresholds, the DDMS _shall_ highlight the affected chart segment in yellow for caution and red for critical status.

**[DDMS-LIV-040]** The DDMS _shall_ display current reading values and threshold values on charts (labels or tooltips).

**[DDMS-LIV-050]** The DDMS _shall_ provide hover tooltips on charts showing exact values and timestamps.

**[DDMS-LIV-060]** The DDMS _shall_ display visual warning indicators (normal/warning/critical) in device lists.

**[DDMS-LIV-070]** The DDMS _should_ show color-coded regions (normal/warning/critical) on charts to aid quick interpretation.

## Historical Analysis & Export

**[DDMS-HIS-010]** The DDMS _shall_ allow users to select any monitoring device reading and specify a custom time range to view historical trend charts.

**[DDMS-HIS-020]** _When_ historical data is displayed, the DDMS _shall_ allow users to export the dataset to a CSV file.

**[DDMS-HIS-030]** The DDMS _shall_ allow users to zoom in and out on time ranges within historical charts.

**[DDMS-HIS-040]** The DDMS _shall_ show threshold markers on historical charts.

## Device & Group Configuration

**[DDMS-CONF-010]** The DDMS _shall_ allow administrators to add monitoring devices by specifying device name, location, measurement units, sampling interval, threshold rules, and connection parameters (e.g., Modbus address/settings).

**[DDMS-CONF-020]** The DDMS _shall_ allow administrators to edit or delete existing monitoring devices while preserving an audit trail of configuration changes. Deleting a device does not delete its historical readings.

**[DDMS-CONF-030]** The DDMS _shall_ allow administrators to create, edit, and delete device groups and assign monitoring devices to those groups.

**[DDMS-CONF-035]** Each monitoring device _shall_ belong to at most one device group.

**[DDMS-CONF-040]** _When_ a device group is selected, the DDMS _shall_ provide live and historical charting interfaces scoped to the devices in that group.

## Localization & User Interface

**[DDMS-UI-010]** The DDMS _shall_ allow users to switch the interface between English and Chinese without reloading the session.

**[DDMS-UI-015]** The DDMS _shall_ remember a user’s language preference on subsequent sign-ins.

**[DDMS-UI-020]** The DDMS _shall_ present dashboards using a clean, attractive layout with responsive design suitable for industrial control rooms (desktop form factors).

**[DDMS-UI-030]** The DDMS _shall_ provide subtle dynamic effects (e.g., smooth transitions) that enhance comprehension without distracting from critical data.

**[DDMS-UI-040]** The DDMS _shall_ display loading indicators for asynchronous operations and provide responsive feedback for user actions.

## Data Persistence

**[DDMS-DAT-010]** The DDMS _shall_ persist user accounts, device configurations, and collected readings on the server to ensure data survives restarts.

## Protocol Support

**[DDMS-PRO-010]** The DDMS _shall_ support Modbus TCP/IP for device communication.

**[DDMS-PRO-020]** The DDMS _may_ support Modbus RTU over serial as an optional extension.

**[DDMS-PRO-030]** The DDMS _shall_ allow configuring register addresses and data types for Modbus devices.

## MVP Out‑of‑Scope (Explicit Exclusions)

- Tablet support (no tablet‑specific UI targets in MVP).
- Multi‑group assignments (each device belongs to at most one group).
- Option to delete historical data (device deletion does not remove readings).
- Account deactivation (MVP uses account deletion instead).
- Group‑level CSV export (CSV export is per device only in MVP).

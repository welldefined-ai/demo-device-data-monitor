# Device Data Monitoring System Requirements

## Concepts

**[DDMS-CON-010]** The Device Data Monitoring System (DDMS) _shall_ deliver browser-based monitoring for industrial environments on the customer intranet.

**[DDMS-CON-020]** The DDMS _shall_ treat each physical sensor endpoint, PLC, or gateway as a **monitoring device** whose readings are collected and visualized.

**[DDMS-CON-030]** The DDMS _shall_ represent a **device group** as a user-defined collection of monitoring devices that share dashboards and configuration defaults.

## Access & Authentication

**[DDMS-ACC-010]** The DDMS _shall_ be accessible from modern desktop browsers on the customer intranet without installing additional client software.

**[DDMS-ACC-020]** _When_ the owner signs in for the first time with the provided default credentials, the DDMS _shall_ require the owner to set a new password before continuing.

**[DDMS-ACC-030]** The DDMS _shall_ allow the owner to update their username and password at any time after initial setup.

**[DDMS-ACC-040]** The DDMS _shall_ allow administrators to add, edit, or deactivate other administrator accounts.

**[DDMS-ACC-050]** The DDMS _shall_ allow administrators to add read-only user accounts that can view data and dashboards but cannot modify configurations.

## Live Monitoring & Alerts

**[DDMS-LIV-010]** The DDMS _shall_ display real-time charts for multiple monitoring devices concurrently with automatic refresh.

**[DDMS-LIV-020]** The DDMS _shall_ overlay warning threshold markers on live charts to show the relationship between current readings and their configured limits.

**[DDMS-LIV-030]** _When_ a reading crosses its warning thresholds, the DDMS _shall_ highlight the affected chart segment in yellow for caution and red for critical status.

## Historical Analysis & Export

**[DDMS-HIS-010]** The DDMS _shall_ allow users to select any monitoring device reading and specify a custom time range to view historical trend charts.

**[DDMS-HIS-020]** _When_ historical data is displayed, the DDMS _shall_ allow users to export the dataset to a CSV file.

## Device & Group Configuration

**[DDMS-CONF-010]** The DDMS _shall_ allow administrators to add monitoring devices by specifying device name, location, measurement units, sampling interval, and warning threshold rules.

**[DDMS-CONF-020]** The DDMS _shall_ allow administrators to edit or delete existing monitoring devices while preserving an audit trail of configuration changes.

**[DDMS-CONF-030]** The DDMS _shall_ allow administrators to create, edit, and delete device groups and assign monitoring devices to those groups.

**[DDMS-CONF-040]** _When_ a device group is selected, the DDMS _shall_ provide live and historical charting interfaces scoped to the devices in that group.

## Localization & User Interface

**[DDMS-UI-010]** The DDMS _shall_ allow users to switch the interface between English and Chinese without reloading the session.

**[DDMS-UI-020]** The DDMS _shall_ present dashboards using a clean, attractive layout with responsive design suitable for industrial control rooms.

**[DDMS-UI-030]** The DDMS _shall_ provide subtle dynamic effects (e.g., smooth transitions) that enhance comprehension without distracting from critical data.

## Data Persistence

**[DDMS-DAT-010]** The DDMS _shall_ persist user accounts, device configurations, and collected readings on the server to ensure data survives restarts.

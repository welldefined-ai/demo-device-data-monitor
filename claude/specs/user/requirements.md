# Device Data Monitoring System Requirements

DDMS (Device Data Monitoring System) is a web-based application for monitoring and analyzing industrial device data.

## Concepts

**[DDMS-CON-010]** The DDMS _shall_ treat each physical sensor endpoint, PLC, or gateway as a **monitoring device** whose readings are collected and visualized.

**[DDMS-CON-020]** The DDMS _shall_ represent a **device group** as a user-defined collection of monitoring devices that share dashboards and configuration defaults.

## Deployment

**[DDMS-DEP-010]** The DDMS _shall_ be deployed on the customer's intranet (on-premises server) and operate without external internet access.

**[DDMS-DEP-020]** The DDMS _shall_ be accessible from modern desktop web browsers without installing additional client software (Chrome and Edge, latest two major versions).

## Authentication & Authorization

**[DDMS-AUTH-010]** The DDMS _shall_ provide a single owner user with default username and password on initial setup.

**[DDMS-AUTH-011]** The owner _shall_ be able to update their username and password at any time after initial setup.

**[DDMS-AUTH-020]** The owner _shall_ have full system access and user management privileges.

**[DDMS-AUTH-021]** The owner _shall_ be able to delete any user except itself.

**[DDMS-AUTH-030]** The viewer role _shall_ have view-only access to dashboards and data.

**[DDMS-AUTH-040]** The admin role _shall_ have full system access, and can manage admin and viewer users.

## Live Monitoring

**[DDMS-MON-010]** The DDMS _shall_ display current readings and timestamps from all connected monitoring devices.

**[DDMS-MON-020]** The DDMS _shall_ auto-refresh data at configured sampling intervals.

**[DDMS-MON-030]** _When_ a reading crosses a warning threshold, the DDMS _shall_ display a yellow warning indicator.

**[DDMS-MON-040]** _When_ a reading crosses a critical threshold, the DDMS _shall_ display a red critical indicator.

**[DDMS-MON-050]** The DDMS _shall_ overlay threshold values and markers on charts to show the relationship between current readings and their configured limits.

**[DDMS-MON-060]** The DDMS _should_ show color-coded regions (normal/warning/critical) on charts to aid quick interpretation.

## Historical Data

**[DDMS-HIST-010]** The DDMS _shall_ allow users to select any monitoring device reading and specify a custom time range to view historical trend charts.

**[DDMS-HIST-020]** The DDMS _shall_ display threshold lines on historical trend charts.

**[DDMS-HIST-030]** _When_ historical data is displayed, the DDMS _shall_ allow users to export the dataset to a CSV file.

## Device Configuration

**[DDMS-DEV-010]** Admin and owner users _shall_ be able to add or edit monitoring devices.

**[DDMS-DEV-011]** _When_ adding or editing a device, the DDMS _shall_ allow setting device name and description.

**[DDMS-DEV-012]** _When_ adding or editing a device, the DDMS _shall_ allow setting reading units (e.g., °C, bar, RPM, %).

**[DDMS-DEV-013]** _When_ adding or editing a device, the DDMS _shall_ allow setting sampling interval.

**[DDMS-DEV-014]** _When_ adding or editing a device, the DDMS _shall_ allow configuration of connection parameters (Modbus address and register settings).

**[DDMS-DEV-020]** _When_ adding or editing a device, the DDMS _shall_ allow setting threshold rules (warning and critical).

**[DDMS-DEV-030]** Admin and owner users _shall_ be able to delete devices.

**[DDMS-DEV-031]** _When_ a device is deleted, the DDMS _shall_ retain its historical readings.

**[DDMS-DEV-040]** The DDMS _shall_ display device connection status (online/offline).

**[DDMS-DEV-041]** The DDMS _shall_ display last successful reading timestamp for each device.

**[DDMS-DEV-042]** The DDMS _shall_ display communication error indicators for devices.

## Device Grouping

**[DDMS-GRP-010]** Admin and owner users _shall_ be able to create device groups.

**[DDMS-GRP-020]** Admin and owner users _shall_ be able to rename device groups.

**[DDMS-GRP-030]** Admin and owner users _shall_ be able to delete device groups.

**[DDMS-GRP-040]** The DDMS _shall_ allow assigning devices to groups. Each monitoring device _shall_ belong to at most one device group.

**[DDMS-GRP-050]** _When_ viewing a group, the DDMS _shall_ provide a real-time monitoring dashboard showing all devices in the group.

**[DDMS-GRP-051]** _When_ viewing a group, the DDMS _shall_ provide historical trend charts for devices in that group.

## Internationalization

**[DDMS-I18N-010]** The DDMS _shall_ support English (en-US) and Chinese (zh-CN).

**[DDMS-I18N-020]** The DDMS _shall_ allow users to switch the interface language without reloading the session.

**[DDMS-I18N-030]** The DDMS _shall_ remember a user’s language preference on subsequent sign-ins.

**[DDMS-I18N-040]** All UI elements, labels, and messages _shall_ be translated for supported languages.

## User Interface

**[DDMS-UI-010]** The DDMS _shall_ provide a clean, modern interface design.

**[DDMS-UI-020]** The DDMS _shall_ have a professional appearance suitable for industrial control room environments (desktop form factors).

**[DDMS-UI-030]** The DDMS _shall_ provide animated chart updates that enhance comprehension without distracting from critical data.

**[DDMS-UI-040]** The DDMS _shall_ display loading indicators for asynchronous operations.

**[DDMS-UI-050]** The DDMS _shall_ provide responsive feedback for user actions.

**[DDMS-UI-060]** The DDMS _shall_ provide subtle hover and focus effects.

**[DDMS-UI-070]** The DDMS _shall_ ensure high contrast between text and backgrounds for readability.

**[DDMS-UI-080]** The DDMS _shall_ provide clear visual hierarchy.

**[DDMS-UI-090]** The DDMS _shall_ use readable fonts at typical viewing distances.

## Data Persistence

**[DDMS-DATA-010]** The DDMS _shall_ store all configuration data persistently on the server.

**[DDMS-DATA-011]** The DDMS _shall_ store time-series data in a database.

**[DDMS-DATA-020]** Data _shall_ persist across server restarts.

## Protocol Support

**[DDMS-PROTO-010]** The DDMS _shall_ support Modbus TCP/IP protocol for device communication.

**[DDMS-PROTO-011]** The DDMS _shall_ support Modbus RTU over serial for device communication.

**[DDMS-PROTO-012]** The DDMS _shall_ allow configurable register addresses and data types for Modbus devices.

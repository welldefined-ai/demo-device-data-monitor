# Device Data Monitoring System Requirements (MVP)

This document is the MVP baseline, merging requirements from both versions to capture the best of each. The goal is fast implementation with minimal scope while maintaining necessary detail for successful deployment.

DDMS (Device Data Monitoring System) is a web-based application for monitoring and analyzing industrial device data in factory or coalmine environments.

## Concepts

**[DDMS-CON-010]** The Device Data Monitoring System (DDMS) _shall_ deliver browser-based monitoring for industrial environments on the customer intranet.

**[DDMS-CON-020]** The DDMS _shall_ treat each physical sensor endpoint, PLC, or gateway as a **monitoring device** whose readings are collected and visualized.

**[DDMS-CON-030]** The DDMS _shall_ represent a **device group** as a user-defined collection of monitoring devices that share dashboards and configuration defaults.

## Deployment

**[DDMS-DEP-010]** The DDMS _shall_ be deployed on the customer's intranet (on-premises server) and operate without external internet access.

**[DDMS-DEP-020]** The DDMS _shall_ be accessible from modern desktop web browsers without installing additional client software (Chrome, Edge, Firefox, Safari latest two major versions).

## Authentication & Authorization

**[DDMS-AUTH-010]** The DDMS _shall_ provide a default owner account with username and password on initial setup.

**[DDMS-AUTH-020]** _When_ the owner signs in for the first time with the provided default credentials, the DDMS _shall_ require the owner to set a new password before continuing.

**[DDMS-AUTH-030]** The owner _shall_ be able to update their username and password at any time after initial setup.

**[DDMS-AUTH-040]** The owner _shall_ be able to create new admin user accounts.

**[DDMS-AUTH-050]** Admins _shall_ be able to create, edit, or delete other admin user accounts.

**[DDMS-AUTH-060]** Admins _shall_ be able to create, edit, or delete read-only user accounts.

**[DDMS-AUTH-070]** The owner _shall_ be able to delete any user account except the owner account itself.

**[DDMS-AUTH-080]** The owner role _shall_ have full system access and user management privileges.

**[DDMS-AUTH-090]** The admin role _shall_ have full access to device configuration and monitoring, and can manage admin and read-only accounts.

**[DDMS-AUTH-100]** The read-only role _shall_ have view-only access to dashboards and data.

## Real-time Monitoring

**[DDMS-MON-010]** The DDMS _shall_ display current readings from all connected monitoring devices.

**[DDMS-MON-020]** The DDMS _shall_ show device data in chart format (line charts, gauges, etc.).

**[DDMS-MON-030]** The DDMS _shall_ auto-refresh data at configured sampling intervals.

**[DDMS-MON-040]** The DDMS _shall_ support displaying multiple devices simultaneously on real-time dashboards.

**[DDMS-MON-050]** _When_ a reading crosses a warning threshold, the DDMS _shall_ display a yellow warning indicator.

**[DDMS-MON-060]** _When_ a reading crosses a critical threshold, the DDMS _shall_ display a red critical indicator.

**[DDMS-MON-070]** The DDMS _shall_ display visual warning indicators (normal/warning/critical) on both charts and device lists.

**[DDMS-MON-080]** The DDMS _shall_ overlay threshold lines on trend charts to show the relationship between current readings and their configured limits.

**[DDMS-MON-090]** The DDMS _shall_ display current reading values and threshold values on charts (as labels or tooltips).

**[DDMS-MON-100]** The DDMS _should_ show color-coded regions (normal/warning/critical) on charts to aid quick interpretation.

**[DDMS-MON-110]** The DDMS _shall_ provide hover tooltips showing exact values and timestamps.

## Historical Data

**[DDMS-HIST-010]** The DDMS _shall_ allow users to view historical trend curves for any device reading.

**[DDMS-HIST-020]** The DDMS _shall_ allow users to customize the time range for historical data (e.g., last hour, last 24 hours, last week, custom range).

**[DDMS-HIST-030]** The DDMS _shall_ allow users to zoom in and out on specific time periods within historical charts.

**[DDMS-HIST-040]** The DDMS _shall_ display threshold lines on historical trend charts.

**[DDMS-HIST-050]** _When_ historical data is displayed, the DDMS _shall_ allow users to export the dataset to a CSV file (per device only, not group-level).

## Device Configuration

**[DDMS-DEV-010]** Admin and owner users _shall_ be able to add new monitoring devices.

**[DDMS-DEV-020]** _When_ adding or editing a device, the DDMS _shall_ allow setting device name and description.

**[DDMS-DEV-030]** _When_ adding or editing a device, the DDMS _shall_ allow setting reading units (e.g., °C, bar, RPM, %).

**[DDMS-DEV-040]** _When_ adding or editing a device, the DDMS _shall_ allow setting sampling interval.

**[DDMS-DEV-050]** _When_ adding or editing a device, the DDMS _shall_ allow setting data retention period.

**[DDMS-DEV-060]** _When_ adding or editing a device, the DDMS _shall_ allow setting upper threshold limits (warning and critical).

**[DDMS-DEV-070]** _When_ adding or editing a device, the DDMS _shall_ allow setting lower threshold limits (warning and critical).

**[DDMS-DEV-080]** _When_ adding or editing a device, the DDMS _shall_ allow setting hysteresis values to prevent alarm flapping.

**[DDMS-DEV-090]** _When_ adding or editing a device, the DDMS _shall_ allow configuration of connection parameters (Modbus address and register settings).

**[DDMS-DEV-100]** Admin and owner users _shall_ be able to edit existing monitoring devices while preserving an audit trail of configuration changes.

**[DDMS-DEV-110]** Admin and owner users _shall_ be able to delete devices.

**[DDMS-DEV-120]** _When_ a device is deleted, the DDMS _shall_ retain its historical readings (no option to delete historical data in MVP).

**[DDMS-DEV-130]** The DDMS _shall_ display device connection status (online/offline).

**[DDMS-DEV-140]** The DDMS _shall_ display last successful reading timestamp for each device.

**[DDMS-DEV-150]** The DDMS _shall_ display communication error indicators for devices.

## Device Grouping

**[DDMS-GRP-010]** Admin and owner users _shall_ be able to create device groups.

**[DDMS-GRP-020]** Admin and owner users _shall_ be able to rename device groups.

**[DDMS-GRP-030]** Admin and owner users _shall_ be able to delete device groups.

**[DDMS-GRP-040]** The DDMS _shall_ allow assigning devices to groups. Each monitoring device _shall_ belong to at most one device group.

**[DDMS-GRP-050]** _When_ viewing a group, the DDMS _shall_ provide a real-time monitoring dashboard showing all devices in the group.

**[DDMS-GRP-060]** _When_ viewing a group, the DDMS _shall_ provide historical trend charts for devices in that group.

## Internationalization

**[DDMS-I18N-010]** The DDMS _shall_ support English (en-US) language.

**[DDMS-I18N-020]** The DDMS _shall_ support Chinese (zh-CN) language.

**[DDMS-I18N-030]** The DDMS _shall_ allow users to switch the interface language without reloading the session.

**[DDMS-I18N-040]** The DDMS _shall_ save language preference per user account and restore it on subsequent sign-ins.

**[DDMS-I18N-050]** All UI elements, labels, and messages _shall_ be translated for supported languages.

## User Interface

**[DDMS-UI-010]** The DDMS _shall_ provide a clean, modern interface design.

**[DDMS-UI-020]** The DDMS _shall_ provide intuitive navigation and workflows.

**[DDMS-UI-030]** The DDMS _shall_ have a professional appearance suitable for industrial control room environments (desktop form factors).

**[DDMS-UI-040]** The DDMS _shall_ provide smooth transitions between views.

**[DDMS-UI-050]** The DDMS _shall_ provide animated chart updates that enhance comprehension without distracting from critical data.

**[DDMS-UI-060]** The DDMS _shall_ display loading indicators for asynchronous operations.

**[DDMS-UI-070]** The DDMS _shall_ provide responsive feedback for user actions.

**[DDMS-UI-080]** The DDMS _shall_ provide subtle hover and focus effects.

**[DDMS-UI-090]** The DDMS _shall_ ensure high contrast between text and backgrounds for readability.

**[DDMS-UI-100]** The DDMS _shall_ provide clear visual hierarchy.

**[DDMS-UI-110]** The DDMS _shall_ use readable fonts at typical viewing distances.

## Data Persistence

**[DDMS-DATA-010]** The DDMS _shall_ store all configuration data persistently on the server.

**[DDMS-DATA-020]** The DDMS _shall_ store time-series data in a database.

**[DDMS-DATA-030]** The DDMS _shall_ enforce configurable retention period per device.

**[DDMS-DATA-040]** The DDMS _shall_ automatically clean up old data based on retention period.

**[DDMS-DATA-050]** Data _shall_ persist across server restarts.

**[DDMS-DATA-060]** The DDMS _shall_ ensure transaction safety for configuration changes.

**[DDMS-DATA-070]** The DDMS _shall_ provide error recovery mechanisms for data operations.

## Protocol Support

**[DDMS-PROTO-010]** The DDMS _shall_ support Modbus TCP/IP protocol for device communication.

**[DDMS-PROTO-020]** The DDMS _may_ support Modbus RTU over serial as an optional extension.

**[DDMS-PROTO-030]** The DDMS _shall_ allow configurable register addresses for Modbus devices.

**[DDMS-PROTO-040]** The DDMS _shall_ allow configurable data types for Modbus devices.

**[DDMS-PROTO-050]** The DDMS _shall_ support common industrial PLCs and sensors using standard Modbus implementations.

## MVP Out-of-Scope (Explicit Exclusions)

The following features are explicitly excluded from the MVP to enable faster initial implementation:

- **Tablet support**: No tablet-specific UI targets or touch-optimized controls in MVP (desktop browsers only).
- **Multi-group assignments**: Each device belongs to at most one group in MVP.
- **Optional historical data deletion**: Device deletion always retains historical readings in MVP.
- **Account deactivation**: MVP uses permanent account deletion instead of deactivation.
- **Group-level CSV export**: CSV export is per-device only in MVP.
- **Automatic database backups**: Deferred to post-MVP.
- **Manual data export before retention cleanup**: Deferred to post-MVP.
- **Group-level alert summary view**: Deferred to post-MVP (individual device alerts only in MVP).

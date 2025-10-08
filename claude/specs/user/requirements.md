# User Requirements

## 1. System Overview

DDMS (Device Data Monitoring System) is a web-based application for monitoring and analyzing industrial device data in factory or coalmine environments. The system runs on the customer's intranet and is accessed through standard web browsers.

## 2. Deployment & Access

### 2.1 Deployment Environment
- Deployed on customer's intranet (on-premises server)
- No external internet connection required
- Accessible via web browser from internal network

### 2.2 Supported Browsers
- Modern web browsers (Chrome, Firefox, Edge, Safari)
- Responsive design for desktop and tablet access

## 3. User Management & Authentication

### 3.1 Initial Setup
- System provides default owner account with username and password
- Owner can log in on first access

### 3.2 Account Management
- **Owner** can:
  - Change own username and password
  - Create new admin accounts
  - Create new read-only user accounts
  - Delete user accounts (except owner)

### 3.3 User Roles
- **Owner**: Full system access and user management
- **Admin**: Full access to device configuration and monitoring
- **Read-only**: View-only access to dashboards and data

## 4. Device Monitoring

### 4.1 Real-time Monitoring
- Display current readings from all connected monitoring devices
- Show data in chart format (line charts, gauges, etc.)
- Auto-refresh data at configured sampling intervals
- Support multiple devices displayed simultaneously

### 4.2 Historical Data Analysis
- View historical trend curves for any device reading
- Customize time range (e.g., last hour, last 24 hours, last week, custom range)
- Zoom in/out on specific time periods
- Export data to CSV files for external analysis

### 4.3 Visual Warnings
- **Yellow warning**: Reading approaches threshold (configurable proximity)
- **Red warning**: Reading exceeds or falls below critical threshold
- Visual indicators displayed on charts and device lists
- Clear visualization of threshold lines on trend charts

### 4.4 Chart Features
- Display current reading value and threshold values
- Show threshold lines overlaid on trend charts
- Color-coded regions (normal/warning/critical)
- Hover tooltips showing exact values and timestamps

## 5. Device Configuration

### 5.1 Device Management
Admin and owner can:
- **Add new devices**: Configure connection parameters (Modbus settings)
- **Configure device properties**:
  - Device name and description
  - Reading units (e.g., °C, bar, RPM, %)
  - Sampling interval (how often to collect data)
  - Data retention period
- **Set warning thresholds**:
  - Upper limit (high warning/critical)
  - Lower limit (low warning/critical)
  - Hysteresis values to prevent alarm flapping
- **Delete devices**: Remove device and optionally keep historical data

### 5.2 Device Status
- Show connection status (online/offline)
- Last successful reading timestamp
- Communication error indicators

## 6. Device Grouping

### 6.1 Group Management
- Create logical groups of devices (e.g., "Production Line 1", "Cooling System")
- Assign devices to one or more groups
- Rename or delete groups

### 6.2 Group Dashboards
Each group provides:
- Real-time monitoring dashboard showing all devices in the group
- Historical trend charts for the group
- Group-level alert summary
- CSV export for all group devices

## 7. Multi-language Support

### 7.1 Supported Languages
- English (en-US)
- Chinese (zh-CN)

### 7.2 Language Switching
- User can switch language from UI
- Language preference saved per user account
- All UI elements, labels, and messages translated

## 8. User Interface

### 8.1 Design Principles
- Clean, modern interface design
- Intuitive navigation and workflows
- Professional appearance suitable for industrial environments

### 8.2 Visual Effects
- Smooth transitions between views
- Animated chart updates
- Loading indicators for async operations
- Responsive feedback for user actions
- Subtle hover and focus effects

### 8.3 Accessibility
- High contrast between text and backgrounds
- Clear visual hierarchy
- Readable fonts at typical viewing distances
- Touch-friendly controls for tablet access

## 9. Data Storage & Persistence

### 9.1 Server-side Storage
- All configuration data stored persistently on server
- Time-series data stored in database
- Automatic database backups (configurable schedule)

### 9.2 Data Retention
- Configurable retention period per device
- Automatic cleanup of old data
- Manual data export before deletion

### 9.3 System Reliability
- Data persists across server restarts
- Transaction safety for configuration changes
- Error recovery mechanisms

## 10. Protocol Support

### 10.1 Modbus Support
- Modbus TCP/IP protocol
- Modbus RTU over serial (optional)
- Configurable register addresses and data types
- Support for common industrial PLCs and sensors

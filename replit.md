# Encuesta de Reportes Corporativos

## Overview

This is a corporate report survey management system built with Streamlit. The application allows users to submit detailed information about corporate reports through a web-based survey form, and provides administrators with tools to manage, edit, and analyze submitted survey data. The system is designed to help organizations catalog and understand the landscape of their internal reporting infrastructure.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit-based web application with multi-page navigation
- **Page Structure**: 
  - Main survey form (`app.py`) for data collection
  - Administrative panel for viewing submissions
  - Edit interface for modifying existing surveys
  - Statistics dashboard with visualizations
- **Rationale**: Streamlit was chosen for rapid development of data-centric applications with minimal frontend code, enabling quick deployment and easy maintenance

### Backend Architecture
- **Data Management Layer**: Dual-storage strategy with PostgreSQL as primary and CSV as fallback
  - `DataManager` class handles data persistence abstraction
  - Automatic migration from CSV to PostgreSQL when database becomes available
  - Graceful degradation to CSV when database is unavailable
- **Authentication**: Simple hash-based authentication system using SHA256
  - Session-based state management via Streamlit session state
  - Environment variable configuration for credentials
- **Rationale**: The hybrid storage approach ensures the application remains functional even when PostgreSQL is unavailable, making it resilient to infrastructure issues

### Data Storage Solutions
- **Primary Storage**: PostgreSQL database
  - Schema includes comprehensive survey fields (report name, periodicity, system origin, responsible person, etc.)
  - Auto-incrementing primary keys for unique identification
  - Timestamp tracking for submission dates
- **Fallback Storage**: CSV file-based storage
  - Used when PostgreSQL is unavailable
  - Automatic backup directory management
  - Seamless migration path to database when it becomes available
- **Rationale**: PostgreSQL provides robust querying and concurrent access capabilities needed for the admin panel and statistics, while CSV ensures data isn't lost during infrastructure issues

### Authentication & Authorization
- **Implementation**: Custom `Auth` class with password hashing
  - SHA256 hashing for password security
  - Session state-based authentication tracking
  - Environment variable-based credential configuration
- **Default Credentials**: admin/admin123 (configurable via environment variables)
- **Limitations**: Single-user authentication system; suitable for small-scale deployment
- **Rationale**: Simple authentication meets current needs while keeping implementation lightweight; can be extended to multi-user with role-based access if needed

### Report Generation & Export
- **PDF Export**: ReportLab-based PDF generation
  - Custom styling with corporate color scheme
  - Table-based data presentation
  - Support for bulk export and statistics inclusion
- **Data Visualization**: Plotly for interactive charts
  - Periodicity distribution charts
  - Department breakdowns
  - Statistical summaries
- **Rationale**: ReportLab provides fine-grained control over PDF layout, while Plotly enables interactive data exploration in the dashboard

## External Dependencies

### Email Service Integration
- **SMTP Email**: Configurable SMTP server for confirmation emails
  - Default: Gmail SMTP (smtp.gmail.com:587)
  - HTML-formatted confirmation messages
  - Configuration via environment variables: `SMTP_SERVER`, `SMTP_PORT`, `EMAIL_USER`, `EMAIL_PASSWORD`
- **Graceful Degradation**: Application continues functioning if email configuration is missing

### Database Service
- **PostgreSQL**: Primary data storage
  - Connection via `DATABASE_URL` environment variable
  - psycopg2 driver for database connectivity
  - Context manager pattern for connection handling
- **Fallback**: CSV-based storage when database unavailable

### Python Libraries
- **Core Framework**: Streamlit for web interface
- **Data Processing**: Pandas for data manipulation and CSV handling
- **Database**: psycopg2 for PostgreSQL connectivity
- **Visualization**: Plotly Express and Plotly Graph Objects for charts
- **PDF Generation**: ReportLab for document export
- **Email**: Built-in smtplib and email.mime for email functionality

### Environment Variables
Required configuration:
- `DATABASE_URL`: PostgreSQL connection string
- `ADMIN_USER`: Administrator username (default: admin)
- `ADMIN_PASSWORD`: Administrator password (default: admin123)
- `SMTP_SERVER`: SMTP server address (optional)
- `SMTP_PORT`: SMTP port (optional)
- `EMAIL_USER`: Email account username (optional)
- `EMAIL_PASSWORD`: Email account password (optional)
- `EMAIL_FROM`: Sender email address (optional)
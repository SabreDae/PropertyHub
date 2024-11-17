# ZDApi

A Django REST API service for managing property listings with soft delete functionality. This service provides endpoints for creating, reading, updating, and deleting property records, with built-in support for soft deletion and administrative functions.

## Features

- **Property Management**

  - Create and manage property listings
  - Track property details including address, rooms, and location
  - Soft delete functionality with configurable retention period
  - Bulk operations support

- **API Endpoints**

  - RESTful API design
  - Comprehensive error handling
  - Detailed response messages

- **Admin Interface**

  - Custom admin actions
  - Property lifecycle management
  - Audit trail for deletions
  - User activity tracking

- **Security**
  - Role-based access control
  - Secure by default configuration
  - Input validation and sanitization
  - Protected against common vulnerabilities

## API Overview

```http
GET    /api/properties/               # List properties
POST   /api/properties/               # Create property
GET    /api/properties/{id}/          # Get property
PATCH  /api/properties/{id}/          # Update property
DELETE /api/properties/{id}/          # Delete property
POST   /api/properties/{id}/recover/  # Recover property
```

See [DEVELOPMENT.md](https://github.com/SabreDae/ZDApi/blob/main/DEVELOPMENT.md) for setup and development guidelines.

# Clinic Appointment System

A comprehensive clinic management system built with Django, designed to streamline patient scheduling, doctor operations, and administrative tasks. The system enables efficient appointment management, consultation tracking, and multi-role access control for healthcare providers.

## Overview

The Clinic Appointment System is a full-featured Django application that facilitates seamless interaction between patients, doctors, receptionists, and administrators. The system ensures proper scheduling, prevents double-booking, maintains audit trails, and provides role-based access control to sensitive medical information.

## Features

### Patient Features
- **User Registration & Login**: Secure account creation and authentication
- **Profile Management**: View and update personal profile information
- **Appointment Booking**: Browse available time slots and book appointments with doctors
- **Appointment History**: View upcoming and previous appointments
- **Appointment Cancellation**: Cancel appointments according to clinic policies
- **Reschedule Requests**: Request to reschedule existing appointments
- **Consultation Access**: View consultation summaries after appointment completion
- **Appointment Search & Filters**: Find and filter appointments by date, doctor, status, etc.
- **Notifications**: Receive notifications for confirmations, cancellations, and rescheduling

### Doctor Features
- **Schedule Management**: View personal appointment schedule
- **Daily Queue**: Review the daily patient queue with real-time updates
- **Appointment Management**: Confirm or decline patient appointment requests
- **Check-in & Status**: Mark patients as checked-in, completed, or no-show
- **Consultation Records**: Document diagnosis, clinical notes, prescriptions, and medical tests
- **Appointment History**: Access historical appointment data and patient records

### Receptionist Features
- **Doctor Schedule Management**: Create and manage doctor schedules
- **Schedule Exceptions**: Handle exceptions and modifications to regular schedules
- **Patient Check-in**: Check in patients upon arrival
- **Queue Management**: Reorder and manage the appointment queue
- **Appointment Rescheduling**: Reschedule patient appointments on their behalf
- **Appointment Requests**: Manage appointment requests and confirmations
- **Note**: Receptionists cannot access or view medical consultation notes

### Admin Features
- **User Management**: Create, edit, and manage user accounts and roles
- **Patient Management**: View and manage patient information
- **System Dashboard**: Overview of system metrics and statistics
- **Analytics**: Detailed reports on appointments, utilization, and clinic performance
- **Permissions Control**: Manage user roles and access permissions

## Appointment Lifecycle

The system follows a structured appointment lifecycle with clear status transitions:

```
REQUESTED → CONFIRMED → CHECKED_IN → COMPLETED
    ↓           ↓            ↓
  CANCELLED   CANCELLED    NO_SHOW / COMPLETED
```

**Status Definitions:**
- **REQUESTED**: Patient has booked an appointment; awaiting doctor confirmation
- **CONFIRMED**: Doctor has confirmed the appointment
- **CHECKED_IN**: Patient has checked in at the clinic
- **COMPLETED**: Appointment finished; consultation record required
- **CANCELLED**: Appointment cancelled by patient, doctor, or receptionist
- **NO_SHOW**: Patient did not attend the confirmed appointment

## System Rules & Constraints

### Booking & Scheduling
- **Double-Booking Prevention**: The system uses database constraints to prevent overlapping appointments for the same doctor and patient
- **Buffer Time**: A configurable buffer period is maintained between consecutive appointments to allow for transitions
- **Availability**: Doctors' available slots are generated based on their schedules and existing appointments
- **Conflict Prevention**: All booking and rescheduling operations use database transactions to maintain data integrity

### Medical Records & Privacy
- **Consultation Records**: Appointments can only be marked as COMPLETED if a consultation record is created
- **Doctor Confidentiality**: Consultation records (diagnosis, prescriptions, medical tests) are only accessible to doctors and patients
- **Receptionist Restriction**: Receptionists cannot access or view medical consultation notes
- **Patient Privacy**: Patients can only view their own appointments and consultation records

### Audit & Compliance
- **Reschedule Audit Trail**: All appointment rescheduling actions are logged with timestamps and user information
- **Status Tracking**: Complete history of appointment status changes is maintained

## Technology Stack

- **Backend Framework**: Django (Python web framework)
- **Database**: SQLite (with support for production databases)
- **Authentication**: Django authentication system with Groups and Permissions
- **Authorization**: Role-based access control using Django groups and permissions
- **Views**: Class-Based Views (CBV) for maintainable, reusable code
- **API**: Django REST Framework (DRF) for appointment and slot management APIs
- **Frontend**: Django templates with modern, responsive design
- **Transactions**: Database transactions ensure consistency in critical operations

## Project Structure

```
clinic_system/
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
├── db.sqlite3               # SQLite database
├── fake_data.sql            # Sample data for testing
│
├── clinic_system/           # Main Django project configuration
│   ├── settings.py          # Project settings
│   ├── urls.py              # URL routing
│   ├── wsgi.py              # WSGI configuration
│   └── asgi.py              # ASGI configuration
│
├── accounts/                # User authentication and profiles
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   └── templates/
│
├── patients/                # Patient management
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   └── templates/
│
├── doctors/                 # Doctor management and schedules
│   ├── models.py
│   ├── views.py
│   ├── services.py
│   └── templates/
│
├── appointments/            # Core appointment system
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── services.py
│   ├── utils.py
│   ├── api/                 # REST API endpoints
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── permissions.py
│   │   └── urls.py
│   └── templates/
│
├── receptionists/           # Receptionist operations
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   └── templates/
│
├── consultations/           # Medical consultation records
│   ├── models.py
│   ├── views.py
│   └── templates/
│
├── notifications/           # Notification system
│   ├── models.py
│   ├── views.py
│   ├── services.py
│   ├── context_processors.py
│   └── templates/
│
├── analytics/               # System analytics and reports
│   ├── models.py
│   ├── views.py
│   └── templates/
│
└── templates/               # Base templates and components
    ├── base.html
    ├── 404.html
    ├── components/
    └── includes/
```

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git

### Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone https://github.com/Kadry333/Django-Clinic-System.git
   cd Django-Clinic-System
   ```

2. **Create a Virtual Environment**
   ```bash
   python -m venv .venv
   ```

3. **Activate the Virtual Environment**

   **On Windows (PowerShell):**
   ```powershell
   .venv\Scripts\Activate.ps1
   ```

   **On Windows (Command Prompt):**
   ```cmd
   .venv\Scripts\activate.bat
   ```

   **On macOS/Linux:**
   ```bash
   source .venv/bin/activate
   ```

4. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run Database Migrations**
   ```bash
   python manage.py migrate
   ```

6. **create groups**
   ```bash
   python manage.py create_groups

7. **create staff for testing**
   ```bash
   python manage.py create_staff


## Sample Users

After running the last command, you can use the following placeholder accounts for testing:

### Admin
- **Username**: `admin`
- **Email**: `admin@clinicms.com`
- **Password**: `password123#`

### Doctor
- **Email**: `doctor@clinicms.com`
- **Password**: `password123#`

### Receptionist
- **Email**: `receptionist@clinicms.com`
- **Password**: `password123#`


8. **Run the Development Server**
   ```bash
   python manage.py runserver
   ```
   The application will be accessible at `http://127.0.0.1:8000/`


## Environment Variables

To set up your environment variables:

### 1. Create `.env` file

Copy the example file:

```bash
cp .env.example .env
```

> On Windows (PowerShell):

```powershell
copy .env.example .env
```

---

### 2. Generate a Django Secret Key

Run the following command:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the generated key and replace the value of:

```env
SECRET_KEY=your-secret-key-here
```

---

### 3. Update Environment Variables

Open the `.env` file and configure it and add your database credentials:




# Appointment Settings
APPOINTMENT_BUFFER_TIME_MINUTES=15
```






## API Endpoints

The system includes a REST API for appointment and slot management. Below are the main endpoints:

### Appointments API

**Base URL**: `/api/appointments/`

- `GET /api/appointments/` - List all appointments (paginated)
- `POST /api/appointments/` - Create a new appointment
- `GET /api/appointments/<id>/` - Retrieve appointment details
- `PATCH /api/appointments/<id>/` - Update appointment status
- `DELETE /api/appointments/<id>/` - Cancel appointment
- `GET /api/appointments/<id>/reschedule/` - Reschedule request
- `POST /api/appointments/<id>/check-in/` - Check in patient

### Doctor Slots API

**Base URL**: `/api/slots/`

- `GET /api/slots/` - List available slots
- `GET /api/slots/?doctor=<doctor_id>` - Get slots for specific doctor
- `GET /api/slots/?date=<YYYY-MM-DD>` - Get slots for specific date
- `POST /api/slots/` - Generate new slots (admin only)

### Authentication

All API endpoints require authentication. Include a valid session or token in request headers:

```bash
curl -X GET http://localhost:8000/api/appointments/ \
  -H "Authorization: Bearer <token>"
```

## Password Reset

In development, password reset links are printed in the terminal instead of being sent by email.

Make sure you have:

```env
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

Then:

* Go to "Forgot Password"
* Enter your email
* Check the terminal and use the reset link

> Note: The email must exist in the database.



## Team Members

The Clinic Appointment System was developed by the following team members:

- **Amr Shokry**: Appointments Staff Management & Doctor Operations
- **Mawada Hassan**: Analytics & Users Profile Management
- **Ahmed ElEmam**: Notifications System & Patient Features
- **Kareem Kadry**: Authentication & Receptionist Operations
- **Ramadan Mohamed**: Appointment Client Interface & Daily Queue Management


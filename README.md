# Global Profile - GSEZ

A comprehensive identity and employment management system for the Gabon Special Economic Zone (GSEZ).

## Project Overview

Global Profile is a Django-based web application designed to manage and verify the identity, employment history, and access permissions of all individuals working within the Gabon Special Economic Zone (GSEZ).

### Core Features

1. **Digital ID Management**

   - Unique GSEZ ID Card with QR code
   - Scannable QR to access the person's full digital profile

2. **Personal Information Management**

   - Full Name, Nationality, Date of Birth
   - GSEZ Card Issue Date & Validity
   - Photo and Government ID
   - Emergency Contact and Family Details

3. **Address Management**

   - Current Address
   - Permanent Address

4. **Employment History**

   - Current and Previous Employers
   - Designation, Department, and Employee Code
   - Join and Leave Dates
   - Remarks & Ratings

5. **Education Details**

   - Qualifications
   - Institutions
   - Year of Passing

6. **Access Control Features**

   - Real-time status: Active / Blocked / Terminated / Under Surveillance
   - Zone Entry Management based on access status
   - Alerts/Flags for suspicious or restricted individuals

7. **Job Portal**

   - Companies can post job openings
   - Applicants can apply using their Global Profile
   - Employers can shortlist based on verified profiles

8. **Admin Panel**
   - Create/Edit/Delete profiles
   - Manage access permissions
   - Monitor entry logs
   - Generate reports

## Technical Stack

- **Backend**: Django (Python)
- **Database**: SQLite (development), PostgreSQL (production)
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Authentication**: Django's built-in authentication system
- **QR Code Generation**: qrcode library
- **Form Handling**: django-crispy-forms

## Installation

1. Clone the repository:

   ```
   git clone https://github.com/yourusername/global-profile.git
   cd global-profile
   ```

2. Create a virtual environment and activate it:

   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

4. Apply migrations:

   ```
   python manage.py migrate
   ```

5. Create a superuser:

   ```
   python manage.py createsuperuser
   ```

6. Run the development server:

   ```
   python manage.py runserver
   ```

7. Visit `http://127.0.0.1:8000/` in your browser.

## Project Structure

```
global-profile/
├── gsez_profile/          # Project settings
├── profile_system/        # Main app
│   ├── migrations/        # Database migrations
│   ├── models.py          # Data models
│   ├── views.py           # View functions
│   ├── forms.py           # Form definitions
│   ├── urls.py            # URL patterns
│   ├── admin.py           # Admin site configuration
│   └── tests.py           # Unit tests
├── templates/             # HTML templates
│   ├── base.html          # Base template
│   └── profile_system/    # App-specific templates
├── static/                # Static files (CSS, JS, images)
├── media/                 # User-uploaded files
├── manage.py              # Django management script
└── requirements.txt       # Project dependencies
```

## Usage

1. Register a new account
2. Create your profile with basic information
3. Add family details, addresses, education, and employment history
4. Use your profile to apply for jobs
5. Admin users can manage profiles and access permissions

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributors

- Your Name - Initial work

# Development Setup Guide

This guide will help you set up the project for local development.

## Prerequisites

- Python 3.10 or higher
- pip (Python package installer)
- git

## Initial Setup

1. Clone the repository:

```bash
git clone https://github.com/SabreDae/ZDApi.git
cd <project-directory>
```

2. Create and activate a virtual environment

```bash
# On macOS/Linux:
python3 -m venv venv
source venv/bin/activate

# On Windows:
python -m venv venv
.\venv\Scripts\activate
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

The project has been setup with separated development and production settings so you will need to also:

1. Create a .env file in the project root

```bash
touch .env
```

2. Add the following variables to the .env file:

```bash
SECRET_KEY=your-secret-key-here
DJANGO_SETTINGS_MODULE=property_hub.settings.development
```

## IDE Setup (VSCode)

Recommended extensions:

- Python
- Django
- Pylance
- Python Type Hint
- Python Test Explorer

Settings ( .vscode/settings.json):

```bash
{
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "editor.formatOnSave": true,
    "python.analysis.typeCheckingMode": "basic",
    "python.testing.autoTestDiscoverOnSaveEnabled": true,
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": [
        ".",
        "-s",
        "-v"

    ],
}
```

## Running the development server

```bash
python3 manage.py runserver
```

The API will be available at http://localhost:8000/.
The admin interface will be available at http://localhost:8000/admin/.

## Running Tests

```bash
# Run all tests
python manage.py test
```

Tests can also be run via the IDE and PyTest/Unittest discovery, though depending on the IDE used further configuration may be required.

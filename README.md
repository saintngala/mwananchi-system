# Mwananchi System

A Flask-based web application that promotes civic engagement by enabling citizens to submit and track public complaints while providing transparency for county development projects and budgets.

## Features

- Submit public service complaints
- Track complaints using a unique Report ID
- Administrator dashboard
- Update complaint status (Submitted, Under Review, In Progress, Resolved, Rejected)
- County budget transparency portal
- Budget project management
- Complaint export to CSV
- Responsive web interface

## Built With

- Python
- Flask
- SQLAlchemy
- Flask-WTF
- Flask-Login
- Flask-Migrate
- HTML5
- CSS3
- JavaScript
- SQLite (Development)
- PostgreSQL (Production Ready)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/saintngala/mwananchi-system.git
cd mwananchi-system
```

2. Create a virtual environment:

```bash
python -m venv venv
```

3. Activate the virtual environment.

Windows:

```bash
venv\Scripts\activate
```

macOS/Linux:

```bash
source venv/bin/activate
```

4. Install dependencies:

```bash
pip install -r requirements.txt
```

5. Copy `.env.example` to `.env` and configure your environment variables.

6. Initialize the database:

```bash
flask db upgrade
```

7. Create an administrator account:

```bash
flask create-admin
```

8. Start the application:

```bash
python run.py
```

Visit:

```
http://127.0.0.1:5000
```

## Project Structure

```
mwananchi_system/
│── app/
│── instance/
│── migrations/
│── config.py
│── run.py
│── seed_data.py
│── requirements.txt
│── README.md
```

## Future Improvements

- Email notifications
- SMS notifications
- Interactive analytics dashboard
- GIS mapping for complaints
- Role-based access control
- File upload support
- REST API
- Multi-language support

## License

This project is licensed under the MIT License.

## Author

George Ngala

GitHub: https://github.com/saintngala

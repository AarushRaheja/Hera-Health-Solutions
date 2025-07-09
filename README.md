# User Dashboard Project

This is a Django-based user dashboard application for file management and user access control.

## Prerequisites

- Python 3.8 or higher
- Conda (Anaconda or Miniconda)
- Git (for version control)

## Setting Up the Development Environment

1. **Create a Conda Environment**
   ```bash
   # Create a new conda environment named 'user-dashboard'
   conda create -n user-dashboard python=3.9
   
   # Activate the environment
   conda activate user-dashboard
   ```

2. **Install Required Packages**
   ```bash
   # Install pip if not already installed
   conda install pip
   
   # Install the required packages from requirements.txt
   pip install -r requirements.txt
   ```

3. **Database Setup**
   - The project uses PostgreSQL as the database backend
   - Install PostgreSQL if not already installed
   - Create a database for the project
   - Update the database settings in `settings.py` with your database credentials

4. **Environment Variables**
   - Create a `.env` file in the project root directory
   - Add your database credentials and other sensitive information
   ```
   DATABASE_NAME=your_database_name
   DATABASE_USER=your_database_user
   DATABASE_PASSWORD=your_database_password
   DATABASE_HOST=localhost
   DATABASE_PORT=5432
   SECRET_KEY=your_django_secret_key
   ```

## Running the Project

1. **Apply Database Migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

2. **Create a Superuser (Optional)**
   ```bash
   python manage.py createsuperuser
   ```

3. **Run the Development Server**
   ```bash
   python manage.py runserver
   ```

4. **Access the Application**
   - Open your web browser and navigate to `http://localhost:8000`
   - The dashboard should be accessible at this URL

## Project Structure

```
user_dashboard_project/
├── dashboard/
│   ├── templates/
│   │   └── dashboard/
│   │       └── user_dashboard.html
│   ├── models.py
│   ├── views.py
│   └── urls.py
├── add_user_data.py
├── requirements.txt
└── README.md
```

## Features

- User profile management
- File upload and management
- File assignment to users
- File status tracking (viewed/not viewed)
- Modern and responsive UI
- Secure file access control

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

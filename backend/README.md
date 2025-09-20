# Fast Miveh - Backend

This is the Django backend for the Fast Miveh e-commerce platform. It provides a RESTful API for managing users, products, orders, and payments. The application is built to be scalable, secure, and easy to deploy using Docker.

---

## Features

-   **RESTful API:** A comprehensive API built with Django REST Framework.
-   **User Authentication:** JWT-based authentication with phone number/email and OTP login.
-   **Product Catalog:** Advanced product management with categories, brands, attributes, and variants.
-   **Order Management:** Complete system for handling shopping carts, checkouts, and orders.
-   **Payment Gateway Integration:** Modular design for integrating payment gateways like Zarinpal and Stripe.
-   **Notification System:** Background task support for sending emails and SMS using Celery.
-   **Advanced Admin Panel:** A customized Django admin for easy management of all resources.
-   **Dockerized:** Fully containerized with Docker and Docker Compose for consistent development and production environments.

## Technology Stack

-   **Framework:** Django 5.0, Django REST Framework
-   **Database:** PostgreSQL (production), SQLite (development)
-   **Authentication:** `djangorestframework-simplejwt`
-   **Async Tasks:** Celery, Redis
-   **Containerization:** Docker, Docker Compose
-   **Web Server:** Gunicorn, Nginx
-   **Core Libraries:**
    -   `django-phonenumber-field`
    -   `psycopg2-binary`
    -   `python-dotenv`
    -   `jdatetime`

## Requirements

-   Docker & Docker Compose (recommended)
-   Or, for manual setup:
    -   Python 3.10+
    -   PostgreSQL
    -   Redis

## Quick Start (with Docker)

1.  **Navigate to the root directory.**
2.  **Configure environment variables:**
    -   Copy `backend/.env.example` to `backend/.env` and set your secrets (DB, Django, etc.).
3.  **Build and run the containers:**
    ```bash
    docker compose up --build
    ```
4.  **API is now available at:**
    -   Web: `http://localhost:8000`
    -   Admin Panel: `http://localhost:8000/admin/`

## Manual Setup (without Docker)

1.  **Navigate to the `backend` directory:**
    ```bash
    cd backend
    ```
2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On macOS/Linux
    # venv\Scripts\activate  # On Windows
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Configure environment variables:**
    -   Copy `.env.example` to `.env` and set your secrets.
5.  **Run database migrations:**
    ```bash
    python manage.py migrate
    ```
6.  **Create a superuser:**
    ```bash
    python manage.py createsuperuser
    ```
7.  **Run the development server:**
    ```bash
    python manage.py runserver
    ```

## API Endpoints

A full list of API endpoints is available through the Swagger/Redoc documentation, typically available at `/api/docs/`.

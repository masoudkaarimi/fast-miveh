# Fast Miveh | Full-Stack E-commerce Platform

**Fast Miveh** is a complete, modern e-commerce platform built with a decoupled architecture using Django for the backend and Next.js for the frontend.

This monorepo contains two main packages: the `/backend` API and the `/frontend` client application, orchestrated with Docker for seamless development and deployment.

---

## 🖼️ Application Gallery

Here are a few glimpses of the user interface. For more, please see the [`screenshots/`](./screenshots/) directory.

| Home Page | Product Details |
| :----------------------------------------------------------: | :-------------------------------------------------------------: |
| ![Homepage Screenshot](./screenshots/screenshot-1.png) | ![Product Page Screenshot](./screenshots/screenshot-2.png) |

| Cart | User Profile |
| :-------------------------------------------------------: | :-----------------------------------------------------------: |
| ![Cart Screenshot](./screenshots/screenshot-3.png) | ![Profile Screenshot](./screenshots/screenshot-4.png) |

---

## ✨ Core Features

-   **Modern Architecture:** Decoupled frontend and backend for independent development and scaling.
-   **Complete E-commerce Flow:** Full product, cart, checkout, and order management.
-   **Secure Authentication:** JWT-based auth with phone/email and OTP options.
-   **Advanced Product Catalog:** Support for variants, categories, brands, and filtering.
-   **Responsive UI:** A beautiful and fast user experience on any device, built with Tailwind CSS.
-   **Customer Dashboards:** Users can manage their profiles, addresses, and view order history.
-   **Dockerized Environment:** One-command setup for a consistent development and production environment.

---

## 🛠️ Technology Stack

| Area      | Technologies                                                                                       |
| :-------- | :------------------------------------------------------------------------------------------------- |
| **Backend** | Django, Django REST Framework, PostgreSQL, Celery, Redis, Gunicorn                                 |
| **Frontend** | Next.js, React, TypeScript, Tailwind CSS, shadcn/ui, Framer Motion                                 |
| **DevOps** | Docker, Docker Compose, Nginx                                                                      |

---

## 🚀 Getting Started

The recommended way to run this project is by using Docker.

### Prerequisites
-   Docker & Docker Compose
-   Git

### Quick Start with Docker

1.  **Clone the project:**
    ```bash
    git clone https://github.com/masoudkaarimi/fast-miveh/
    cd fast-miveh
    ```

2.  **Configure Backend Environment:**
    -   Navigate to `backend/` and copy `.env.example` to `.env`.
    -   Fill in the required secrets (database credentials, Django secret key, etc.).

3.  **Configure Frontend Environment:**
    -   Navigate to `frontend/` and copy `.env.local.example` to `.env.local`.
    -   Ensure `NEXT_PUBLIC_API_BASE_URL` is set correctly (e.g., `http://localhost:8000`).

4.  **Build and Run the Application:**
    -   From the **project root directory**, run the following command:
    ```bash
    docker compose up --build
    ```

5.  **Access the services:**
    -   **Frontend Application:** [http://localhost:3000](http://localhost:3000)
    -   **Backend API:** [http://localhost:8000](http://localhost:8000)
    -   **Backend Admin Panel:** [http://localhost:8000/admin/](http://localhost:8000/admin/)

---

## License
This project is licensed under the **MIT License**. See the `LICENSE` file for more details.

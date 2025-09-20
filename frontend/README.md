# Fast Miveh - Frontend

The Next.js frontend for the Fast Miveh e-commerce platform. This application provides a modern, fast, and responsive user interface for customers to browse products, manage their accounts, and place orders.

## Screenshots

![Screenshot](./screenshots/screenshot-1.png)
![Screenshot](./screenshots/screenshot-2.png)

## Technology Stack

-   **Framework:** Next.js v14 (with App Router)
-   **Language:** TypeScript
-   **Styling:** Tailwind CSS
-   **UI Components:** shadcn/ui
-   **State Management:** Redux Toolkit / Zustand (Choose one or specify)
-   **Data Fetching:** TanStack Query (React Query) / SWR
-   **Form Handling:** React Hook Form
-   **Icons:** lucide-react
-   **Animations:** Framer Motion

## Features

-   **Modern UI/UX:** Clean, intuitive, and fully responsive design.
-   **Server-Side Rendering (SSR) & Static Site Generation (SSG):** Optimized for performance and SEO.
-   **Product Discovery:** Browse products by category, apply filters, and use the search functionality.
-   **User Authentication:** Secure login, registration, and profile management pages.
-   **Shopping Cart & Checkout:** A seamless, multi-step checkout process.
-   **Customer Dashboard:** View order history, manage addresses, and update profile information.
-   **API Integration:** Efficiently communicates with the Django backend REST API.

## How to use

1.  **Clone the project.**
2.  **Install Node.js (v20.15.0 or later).**
3.  **Navigate to the frontend directory:**
    ```bash
    cd frontend
    ```
4.  **Install dependencies:**
    ```bash
    npm install
    ```
5.  **Configure environment variables:**
    -   Copy `.env.local.example` to `.env.local`.
    -   Set `NEXT_PUBLIC_API_BASE_URL` to your backend's URL (e.g., `http://localhost:8000`).

## Run the App

In the `frontend` directory, you can run:

```bash
npm run dev

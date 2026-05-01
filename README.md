# Team Task Manager

A full-stack Team Task Manager web application built with FastAPI, Jinja2 templates, SQLite, and Bootstrap 5. The app supports role-based project and task management for admins and members, with JWT authentication stored securely in HTTP-only cookies.

Live URL: https://web-production-7c4d1.up.railway.app

## Features

<img width="1918" height="981" alt="Screenshot 2026-05-01 234356" src="https://github.com/user-attachments/assets/7e3a9f3b-d98d-4994-b3b4-e0756418e937" />

<img width="1918" height="973" alt="project-05-01 234709" src="https://github.com/user-attachments/assets/bbfbaec3-c641-483c-9e27-b7b965f7a414" />

<img width="1918" height="986" alt="task manager234356" src="https://github.com/user-attachments/assets/0f5251d9-89f8-4290-8f8f-f32412dd1879" />




- User signup, login, and logout
- JWT authentication stored in cookies
- Password hashing with bcrypt
- Role-based access control for Admin and Member users
- Admin dashboard for managing projects, members, and tasks
- Admin can create projects
- Admin can add members to projects
- Admin can create, assign, update, and delete tasks
- Members can view assigned tasks
- Members can update only their own task status
- Task statuses: `todo`, `in_progress`, and `done`
- Task due dates and overdue tracking
- Dashboard summary with total, todo, in progress, done, and overdue task counts
- Server-rendered frontend using Jinja2 templates
- Bootstrap 5 styling via CDN
- SQLite database with SQLAlchemy ORM
- Railway-ready deployment using `Procfile`

## Tech Stack

- Backend: FastAPI
- Frontend: Jinja2 templates
- Styling: Bootstrap 5 CDN
- Database: SQLite
- ORM: SQLAlchemy
- Authentication: JWT with `python-jose`
- Password hashing: `passlib` and bcrypt
- Server: Uvicorn
- Deployment: Railway

## Project Structure

```txt
team-task-manager/
├── main.py
├── database.py
├── models.py
├── auth.py
├── requirements.txt
├── Procfile
├── routers/
│   ├── __init__.py
│   ├── auth.py
│   ├── dashboard.py
│   ├── projects.py
│   └── tasks.py
└── templates/
    ├── base.html
    ├── login.html
    ├── signup.html
    ├── dashboard.html
    ├── projects.html
    ├── project_detail.html
    └── tasks.html
```

## Local Setup

1. Clone or download the project.

2. Open a terminal in the project folder.

```bash
cd team-task-manager
```

3. Create and activate a virtual environment.

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

4. Install dependencies.

```bash
pip install -r requirements.txt
```

5. Run the application.

```bash
uvicorn main:app --reload
```

6. Open the app in your browser.

```txt
http://127.0.0.1:8000
```

The SQLite database file is created automatically on startup.

## Environment Variables

The app works locally without extra environment variables, but these values can be configured for production.

| Variable | Required | Default | Description |
| --- | --- | --- | --- |
| `SECRET_KEY` | No | `change-this-secret-key-in-production` | Secret key used to sign JWT tokens. Set a strong unique value in production. |
| `PORT` | Yes on Railway | Provided by Railway | Port used by the deployment command in `Procfile`. |

Example local `.env` value:

```env
SECRET_KEY=replace-with-a-long-random-secret
```

## Default Usage Flow

1. Create an Admin account from the signup page.
2. Create a project.
3. Create Member accounts.
4. Add members to a project.
5. Create tasks and assign them to project members.
6. Members log in to view assigned tasks and update task status.

## Deployment

The project includes a Railway-compatible `Procfile`:

```txt
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

Set `SECRET_KEY` in the Railway environment variables before deploying.

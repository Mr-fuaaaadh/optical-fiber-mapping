# 🌐 Optical Fiber Mapping - Backend (Django REST)

[![Python](https://img.shields.io/badge/python-3.10+-blue)](https://www.python.org/)
[![Django](https://img.shields.io/badge/django-4.x-brightgreen)](https://www.djangoproject.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Build Status](https://img.shields.io/github/actions/workflow/status/yourusername/optical-fiber-backend/ci.yml?branch=main)](https://github.com/yourusername/optical-fiber-backend/actions)
[![Issues](https://img.shields.io/github/issues/yourusername/optical-fiber-backend)](https://github.com/yourusername/optical-fiber-backend/issues)

> Advanced-level Django REST backend for real-time optical fiber infrastructure visualization and management for ISPs and enterprise networks.

---

## 🧠 Project Overview

This system manages:

- 🏢 Multi-company (ISP) data with isolated access
- 🧑‍💼 Staff roles (Admin, Engineer, Field, Support)
- 🔌 Network infrastructure (Switches, Couplers, Splitters, etc.)
- 👥 Customer endpoints and fiber path visualization
- 🧵 Real-time connectivity mapping

---

## 🧱 Architecture Overview

**Core Concepts**:
- Company ➝ Staffs ➝ Infrastructure ➝ Customers
- All linked through RESTful APIs with strict permissions

_📌 (Optional) Architecture diagram link here_

---

## 🚀 Features

- 🔐 JWT-based Authentication (Admin, Engineer, etc.)
- 🏢 Company-wise Data Isolation
- 🔄 Fiber Network Object Mapping (Switches, Couplers)
- 📍 Trace Customer to Final Connection
- ⚙️ Role-based Access Control
- 📂 Modular App Structure
- 🌍 Multi-language Ready
- 📑 Auto-generated Swagger Docs (Optional)

---

## 💻 Stack

| Layer          | Tech                          |
|----------------|-------------------------------|
| Backend        | Python, Django, DRF           |
| Database       | PostgreSQL                    |
| Auth           | JWT (`SimpleJWT`)             |
| API Tools      | DRF Filters, Pagination, Caching |
| Deployment     | Docker + Gunicorn (Optional)  |
| Dev Tools      | Postman, Insomnia, pgAdmin    |

---

## 🧪 Installation

### 1. Clone & Setup

```bash
git clone https://github.com/Mr-fuaaaadh/optical-fiber-mapping.git
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

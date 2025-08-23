# 🤖 CasaBot — Telegram Booking Assistant

CasaBot is a **Telegram-based booking assistant** built with **Aiogram 3**, **FastAPI**, and **RabbitMQ**.  
It allows users to search, book, and pay for tickets directly in Telegram while providing an admin panel for manual control.

---

## ✨ Features
- 🚀 Built with **Aiogram 3** + **FastAPI** (async-first architecture).  
- 📩 **Webhook-based bot** for instant updates.  
- 📦 **RabbitMQ + FastStream** used for messaging & notifications.  
- ⏳ **APScheduler** for periodic tasks:
  - auto-cancel unpaid bookings after 1 hour,  
  - delayed reminders to users,  
  - admin notifications.  
- 💳 **CryptoBot integration** for payments (auto check invoice status).  
- 🖥 Admin notifications (new orders, manual payment requests, route errors).  
- 🗄 **PostgreSQL + SQLAlchemy (Async)** for persistence.  

---

## 🛠 Tech Stack
- **Python 3.11+**
- [Aiogram 3](https://docs.aiogram.dev/) — Telegram Bot Framework  
- [FastAPI](https://fastapi.tiangolo.com/) — API + webhook handler  
- [FastStream](https://faststream.airt.ai/) — async RabbitMQ integration  
- [SQLAlchemy Async](https://docs.sqlalchemy.org/) + PostgreSQL  
- [APScheduler](https://apscheduler.readthedocs.io/) — scheduled jobs  
- [Loguru](https://github.com/Delgan/loguru) — structured logging  
- [Docker (optional)] — for easy deployment  

---

## ⚙️ Installation

### 1. Clone repo
```bash
git clone https://github.com/username/casabot.git
cd casabot
```

## Configure .env
```bash
BOT_TOKEN=
CRYPTO_PAY_TOKEN=
NETWORK_CRYPTO_API=TEST_NET
ADMIN_IDS=[tg_id, tg_id]
DB_URL=sqlite+aiosqlite:///./casa.db
SUPPORTS=[]
BASE_URL=https://ngrok.app
RABBITMQ_USERNAME=admin
RABBITMQ_PASSWORD=password
RABBITMQ_HOST=127.0.0.1
RABBITMQ_PORT=5672
VHOST=myapp_vhost
```
## Run Local
```bash
alembic upgrade head
uvicorn main:app --reload --port 8000
```
## Structure 
```bash
bot/
 ├── api/                # FastAPI routers
 ├── database/           # Async SQLAlchemy + DAO
 ├── handlers/           # Aiogram handlers
 ├── keyboards/          # Inline & reply keyboards
 ├── services/           # Payment / integrations
 ├── tasks/              # APScheduler background tasks
 ├── create_bot.py       # Bot + Dispatcher initialization
 ├── config.py           # Settings (from .env)
 └── main.py             # Entry point (FastAPI + bot)
```
## Author
I'm

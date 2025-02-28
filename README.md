# Rescue Radar - Emergency Management System

Rescue Radar is a robust **emergency management system** built with **FastAPI**. It enables users to **report emergencies, track responders, manage agencies, and receive real-time notifications** for critical situations. 

## 🚀 Features

### **General Features**
- **User Authentication & Authorization** (JWT & OAuth2)
- **Role-Based Access Control** (Public, Responder, Agency Admin)
- **Real-Time Notifications** for emergency updates
- **Geolocation Services** (Emergency tracking, mapping via Leaflet.js)
- **Image Uploads** (Firebase Storage integration for emergency images)

### **Public Users**
- Report emergencies with location and images
- Track emergency status updates
- Receive safety resources and emergency contacts

### **Responders**
- View and manage assigned emergencies
- Update emergency status in real-time
- Receive location-based dispatch notifications

### **Agency Admins**
- Manage responders (Add, remove, update status)
- Assign emergencies to responders
- Monitor emergency trends and performance analytics

---

## ⚙️ Project Setup

### **1. Prerequisites**
Ensure you have the following installed:
- **Python** (>3.9)
- **PostgreSQL** (Database)

### **2. Clone the Repository**
```bash
git clone https://github.com/<your-repo>/rescue-radar.git
cd rescue-radar
```

### **3. Create a Virtual Environment**
```bash
python3 -m venv env
source env/bin/activate  # Linux/Mac
env\Scripts\activate    # Windows
```

### **4. Install Dependencies**
```bash
pip install -r requirements.txt
```


---

## 🛠 Environment Configuration

1. **Create a `.env` file** in the root directory:
```bash
touch .env
```

2. **Add the following environment variables:**
```ini
DATABASE_URL=postgresql+psycopg2://username:password@localhost/rescue_radar
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REDIS_URL=redis://localhost:6379
FIREBASE_API_KEY=your_firebase_key
```
> **Replace** `username`, `password`, and `your_secret_key` with appropriate values.

---

## 🛢 Database Setup

1. **Ensure PostgreSQL is running.**
2. **Create the database:**
```bash
psql -U postgres
CREATE DATABASE rescue_radar;
```
3. **Run Alembic migrations:**
```bash
alembic upgrade head
```
4. **Seed Database**
```bash
python3 seed_user_data.py
puthon3 seed_location_data.py
python3 seed_emergency_location_data.py
```
---

## 🚀 Running the Application

### **1. Start the FastAPI Server**
```bash
uvicorn main:app --reload
# OR
python3 main.py
```
**Access the application:**
- **Swagger API Docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc Documentation:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 📂 Project Structure

```plaintext
rescue-radar/
├── api/
│   ├── core/                 # Core configurations and middleware
│   ├── v1/                   # Version 1 API routes and models
│   ├── db/                   # Database configuration
│   └── utils/                # Helper utilities (Firebase, location services)
├── alembic/                  # Database migrations
├── frontend/
│   ├── static/               # CSS, JS, and images
│   └── templates/            # HTML templates
├── env/                      # Virtual environment (not included in repo)
├── main.py                   # Entry point for FastAPI
├── requirements.txt          # Project dependencies
└── README.md                 # Documentation
```

---

## 🤝 Contributing

1. **Fork the Repository** and create a new branch:
```bash
git checkout -b feature/your-feature-name
```
2. **Make your changes and test thoroughly.**
3. **Submit a pull request describing your changes.**

---

## 📞 Need Help?

If you encounter any issues, create an issue in the repository or reach out to the maintainers.

---

### 🎯 **Rescue Radar - Bringing Emergency Response Closer to You!** 🚑

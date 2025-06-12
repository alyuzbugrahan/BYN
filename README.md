# BYN - Build Your Network Platform

A full-stack professional networking web application inspired by LinkedIn, built with Django REST Framework backend and designed for React/TypeScript frontend.

## 🚀 Features

### Current Implementation (Phase 1)
- ✅ **User Authentication & Registration** - JWT-based auth with email/password
- ✅ **User Profiles** - Complete profile management with experience, education, skills
- ✅ **Database Models** - Comprehensive models for all major features
- ✅ **API Documentation** - Interactive Swagger/OpenAPI documentation
- ✅ **Admin Interface** - Django admin for content management

### Planned Features (Future Phases)
- 🔄 **Professional Network** - Connection requests and networking
- 🔄 **Job Postings & Applications** - Full job marketplace functionality
- 🔄 **Social Feed** - Posts, comments, likes, shares
- 🔄 **Company Profiles** - Company pages and followers
- 🔄 **Real-time Features** - Notifications and messaging
- 🔄 **Search & Recommendations** - Advanced search and suggestions

## 🛠️ Tech Stack

### Backend
- **Django 4.2+** - Web framework
- **Django REST Framework** - API development
- **PostgreSQL** - Primary database
- **JWT Authentication** - Secure token-based auth
- **Pillow** - Image processing
- **DRF Spectacular** - API documentation

### Frontend (To be implemented)
- **React 18+** - Frontend framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Axios** - API communication

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL 12+
- pip and virtualenv

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd byn
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Configure Environment

```bash
# Copy environment template
cp env_example.txt .env

# Edit .env with your configuration
# Set your database credentials, secret key, etc.
```

### 4. Install Dependencies & Setup

```bash
# Install Python packages
pip install -r requirements.txt

# Run setup script
python setup.py
```

### 5. Create Superuser

```bash
python manage.py createsuperuser
```

### 6. Run Development Server

```bash
python manage.py runserver
```

## 📚 API Documentation

Once the server is running, visit:

- **Swagger UI**: http://127.0.0.1:8000/api/schema/swagger-ui/
- **ReDoc**: http://127.0.0.1:8000/api/schema/redoc/
- **Admin Panel**: http://127.0.0.1:8000/admin/

## 🌐 API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `POST /api/auth/token/refresh/` - Refresh JWT token
- `GET /api/auth/profile/` - Get current user profile

### User Management
- `GET /api/users/profile/{id}/` - Get user profile
- `PUT /api/users/profile/update/` - Update current user profile
- `GET /api/users/search/?q={query}` - Search users
- `GET/POST /api/users/experiences/` - Manage work experience
- `GET/POST /api/users/education/` - Manage education
- `GET/POST /api/users/skills/` - Manage skills

### Future Endpoints
- `/api/companies/` - Company management
- `/api/jobs/` - Job postings and applications
- `/api/feed/` - Social feed and posts
- `/api/connections/` - Network connections

## 🗄️ Database Models

### User System
- **User** - Custom user model with professional fields
- **Experience** - Work experience entries
- **Education** - Educational background
- **Skill** - Skills with endorsements

### Company System
- **Company** - Company profiles
- **Industry** - Industry classifications
- **CompanyAdmin** - Company administrators

### Job System
- **Job** - Job postings
- **JobApplication** - Job applications
- **JobCategory** - Job categorization

### Social Features
- **Post** - Social media posts
- **Comment** - Post comments
- **Like** - Like system for posts/comments
- **Notification** - User notifications

### Networking
- **Connection** - User connections
- **ConnectionRequest** - Connection requests
- **UserRecommendation** - People suggestions

## 🔧 Development

### Database Migrations

```bash
# Create new migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Reset database (development only)
python manage.py flush
```

### Testing

```bash
# Run tests
python manage.py test

# Run specific app tests
python manage.py test accounts
```

### Code Quality

```bash
# Format code
black .

# Lint code
flake8

# Type checking
mypy .
```

## 📁 Project Structure

```
byn/
├── manage.py
├── requirements.txt
├── setup.py
├── README.md
├── byn/          # Main project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── accounts/                # User management
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── companies/               # Company profiles
├── jobs/                    # Job marketplace
├── feed/                    # Social features
├── connections/             # Networking
└── frontend/                # React app (to be created)
```

## 🔐 Environment Variables

Key environment variables in `.env`:

```env
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_NAME=byn_db
DATABASE_USER=postgres
DATABASE_PASSWORD=password
DATABASE_HOST=localhost
DATABASE_PORT=5432
```

## 🚀 Deployment

### Production Setup

1. Set `DEBUG=False` in environment
2. Configure production database
3. Set up static file serving
4. Configure CORS for frontend
5. Set up HTTPS and security headers

### Docker Deployment

```bash
# Build and run with Docker
docker-compose up --build
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🔗 Links

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [React Documentation](https://reactjs.org/docs/)
- [Tailwind CSS](https://tailwindcss.com/docs/)

## 📞 Support

For questions and support, please open an issue on GitHub.

---

**Note**: This is Phase 1 of the implementation focusing on backend infrastructure and user authentication. Frontend React application and additional features will be added in subsequent phases. 
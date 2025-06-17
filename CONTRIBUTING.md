# Contributing to BYN - Build Your Network

Thank you for your interest in contributing to BYN! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Node.js 16+ (for frontend development)
- PostgreSQL 12+
- Git
- A GitHub account

### Development Setup

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/BYN-Build-Your-Network-Platform.git
   cd BYN-Build-Your-Network-Platform
   ```

3. **Set up the backend**:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Set up the database**:
   ```bash
   # Copy environment file
   cp env_example.txt .env
   # Edit .env with your database credentials
   
   # Run migrations
   python manage.py migrate
   
   # Create superuser
   python manage.py createsuperuser
   ```

5. **Set up the frontend** (when available):
   ```bash
   cd frontend
   npm install
   ```

## 🔄 Development Workflow

### Branching Strategy

- `master` - Production-ready code
- `develop` - Development branch for integration
- `feature/*` - Feature branches
- `bugfix/*` - Bug fix branches
- `hotfix/*` - Critical fixes for production

### Making Changes

1. **Create a new branch** from `develop`:
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following our coding standards

3. **Test your changes**:
   ```bash
   # Backend tests
   python manage.py test
   
   # Frontend tests (when available)
   npm test
   ```

4. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: add user profile completion feature"
   ```

5. **Push and create a pull request**:
   ```bash
   git push origin feature/your-feature-name
   ```

## 📝 Coding Standards

### Backend (Django)

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
- Use descriptive variable and function names
- Add docstrings to all functions and classes
- Write unit tests for new features
- Use type hints where possible

**Example:**
```python
def get_user_profile(user_id: int) -> Optional[UserProfile]:
    """
    Retrieve user profile by user ID.
    
    Args:
        user_id: The ID of the user
        
    Returns:
        UserProfile object or None if not found
    """
    try:
        return UserProfile.objects.get(user_id=user_id)
    except UserProfile.DoesNotExist:
        return None
```

### Frontend (React/TypeScript)

- Use TypeScript for type safety
- Follow React functional components with hooks
- Use meaningful component and variable names
- Write unit tests for components
- Follow accessibility best practices

**Example:**
```typescript
interface UserProfileProps {
  userId: number;
  onProfileUpdate: (profile: UserProfile) => void;
}

const UserProfile: React.FC<UserProfileProps> = ({ userId, onProfileUpdate }) => {
  // Component implementation
};
```

### Database

- Use descriptive table and column names
- Always create migrations for schema changes
- Add appropriate indexes for performance
- Include meaningful help_text in model fields

## 🧪 Testing

### Backend Testing

- Write unit tests for all new models, views, and utilities
- Use Django's testing framework
- Maintain test coverage above 80%
- Test both success and error cases

```bash
# Run all tests
python manage.py test

# Run tests for specific app
python manage.py test accounts

# Run tests with coverage
coverage run --source='.' manage.py test
coverage report
```

### Frontend Testing

- Write unit tests for components
- Test user interactions and edge cases
- Use React Testing Library for component tests

```bash
# Run frontend tests
npm test

# Run tests with coverage
npm test -- --coverage
```

## 📋 Pull Request Guidelines

### Before Submitting

- [ ] Code follows project coding standards
- [ ] All tests pass
- [ ] New features include tests
- [ ] Documentation is updated (if needed)
- [ ] Commit messages follow conventional commits format

### PR Description

Please include:

1. **Summary** of changes
2. **Type of change** (feature, bugfix, docs, etc.)
3. **Testing** performed
4. **Screenshots** (for UI changes)
5. **Breaking changes** (if any)

### PR Template

```markdown
## Summary
Brief description of what this PR does.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code refactoring

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Screenshots (if applicable)
[Add screenshots here]

## Breaking Changes
[List any breaking changes]

## Additional Notes
[Any additional information]
```

## 🐛 Bug Reports

When reporting bugs, please include:

1. **Steps to reproduce** the issue
2. **Expected behavior**
3. **Actual behavior**
4. **Environment details** (OS, Python version, etc.)
5. **Error messages or logs**
6. **Screenshots** (if applicable)

## 💡 Feature Requests

For new features:

1. **Describe the feature** and its use case
2. **Explain the problem** it solves
3. **Provide examples** of how it would work
4. **Consider alternatives** and explain why this approach is best

## 📖 Documentation

### Code Documentation

- Add docstrings to all public functions and classes
- Update API documentation for new endpoints
- Include examples in documentation

### README Updates

- Update feature lists when adding new functionality
- Keep installation instructions current
- Update API endpoint documentation

## 🎯 Development Priorities

### Current Focus Areas

1. **Backend API Development** - Core functionality
2. **Authentication & Security** - User management
3. **Database Optimization** - Performance improvements
4. **Testing Coverage** - Comprehensive test suite

### Future Development

1. **Frontend React Application** - UI implementation
2. **Real-time Features** - WebSocket integration
3. **Mobile Optimization** - Responsive design
4. **Advanced Features** - AI recommendations, analytics

## 📞 Getting Help

- **GitHub Issues** - For bugs and feature requests
- **GitHub Discussions** - For questions and general discussion
- **Code Review** - Request reviews from maintainers

## 🏆 Recognition

Contributors will be recognized in:

- CONTRIBUTORS.md file
- Release notes for significant contributions
- GitHub repository insights

## 📄 License

By contributing to BYN, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to BYN - Build Your Network! 🎉 
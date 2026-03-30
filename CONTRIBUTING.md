# Contributing to HoneyTrap

Thank you for interest in contributing to HoneyTrap! This document provides guidelines and instructions for contributing.

## Code of Conduct

Be respectful, inclusive, and professional in all interactions.

## Getting Started

### Prerequisites
- Python 3.10+
- PostgreSQL 14+
- Redis 7+
- Docker & Docker Compose

### Local Development Setup

```bash
# Clone repository
git clone https://github.com/yourusername/honeytrap.git
cd honeytrap

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Setup environment file
cp .env.example .env

# Initialize database
flask db upgrade
flask seed-db

# Start development server
flask run --debug
```

### Docker Development

```bash
docker-compose up --build
```

## Development Workflow

### 1. Create Feature Branch
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

Branch naming convention:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `test/` - Test additions
- `refactor/` - Code refactoring

### 2. Make Changes

Code style must follow:
- **Python**: PEP 8 via Black (100 char line length)
- **Type hints**: Full type annotations required
- **Docstrings**: Google-style docstrings for all functions
- **Tests**: All new code requires tests

### 3. Code Quality Checks

Before committing, run:

```bash
# Format code
black app

# Run linter
flake8 app
pylint app

# Type checking
mypy app

# Run tests
pytest tests/ --cov=app
```

Or use the provided script:
```bash
make lint
make test
```

### 4. Commit Messages

Follow conventional commits:
```
feat: add new honeypot service
fix: resolve database connection timeout
docs: update API documentation
test: add unit tests for classifier
refactor: simplify attack analysis logic
```

### 5. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a PR with:
- Clear description of changes
- Reference to relevant issues (#123)
- Test results showing no regression
- Screenshots for UI changes

## Testing Requirements

- **Coverage**: Minimum 80% code coverage
- **Unit Tests**: Test individual components
- **Integration Tests**: Test component interactions
- **Database Tests**: Use in-memory SQLite for tests

```bash
# Run tests with coverage report
pytest tests/ --cov=app --cov-report=html

# Open coverage report
open htmlcov/index.html
```

## Documentation

When adding features, update:
- Code docstrings
- README.md if needed
- API documentation in `docs/api.md`
- Architecture in `docs/architecture.md`

## Pull Request Review Process

All PRs require:
1. ✅ CI/CD pipeline passes
2. ✅ Code review approval
3. ✅ No conflicts with main branch
4. ✅ At least 1 approval from maintainers

## Security

For security issues:
- **Do not** open public issues
- Email security concerns to: security@aymei-tech.com
- Include: description, impact, reproduction steps

## Performance Guidelines

When contributing performance-critical code:
- Profile before and after using tools like `py-spy`
- Include benchmarks in PR description
- Don't sacrifice readability for micro-optimizations

## Questions or Need Help?

- 📧 Email: dev@aymei-tech.com
- 💬 Discussions: GitHub Discussions
- 📖 Documentation: https://honeytrap.readthedocs.io

Thank you for contributing! 🎉

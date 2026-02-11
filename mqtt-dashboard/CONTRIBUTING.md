# Contributing to MQTT Dashboard

Thank you for your interest in contributing to MQTT Dashboard! This document provides guidelines for contributing to the project.

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:
- A clear, descriptive title
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- Your environment (OS, Python version, browser)
- Screenshots if applicable

### Suggesting Enhancements

Enhancement suggestions are welcome! Please create an issue with:
- A clear description of the enhancement
- Use cases and benefits
- Any implementation ideas you might have

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Make your changes**:
   - Follow the existing code style
   - Add comments for complex logic
   - Update documentation if needed
3. **Test your changes**:
   - Ensure the application runs without errors
   - Test all modified functionality
   - Test with different browsers if UI changes are made
4. **Commit your changes**:
   - Use clear, descriptive commit messages
   - Reference any related issues
5. **Submit a pull request**:
   - Describe what changes you made and why
   - Link to any related issues

## Code Style Guidelines

### Python (Backend)
- Follow PEP 8 style guide
- Use meaningful variable and function names
- Add docstrings to functions
- Keep functions focused and small
- Handle exceptions appropriately

### JavaScript (Frontend)
- Use ES6+ features
- Use const/let instead of var
- Add comments for complex logic
- Keep functions small and focused
- Use async/await for asynchronous operations

### CSS
- Use the existing CSS variable system
- Maintain the dark theme aesthetic
- Ensure responsive design
- Test on multiple screen sizes

### HTML
- Use semantic HTML elements
- Keep templates clean and readable
- Maintain accessibility standards

## Project Structure

```
mqtt-dashboard/
├── app.py                 # Main Flask application
├── templates/             # HTML templates
│   ├── login.html
│   └── dashboard.html
├── static/
│   ├── css/
│   │   └── style.css     # All styles
│   └── js/
│       └── dashboard.js  # Client-side logic
└── requirements.txt       # Python dependencies
```

## Development Setup

1. Clone your fork:
   ```bash
   git clone https://github.com/your-username/mqtt-dashboard.git
   cd mqtt-dashboard
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your test credentials
   ```

4. Run the development server:
   ```bash
   python3 app.py
   ```

## Testing

Before submitting a pull request:

1. Test MQTT broker connections
2. Test topic subscriptions and publications
3. Verify data logging works
4. Test SQL export functionality
5. Check terminal commands
6. Verify Google authentication (if modified)
7. Test on multiple browsers
8. Test responsive design on mobile

## Feature Requests

When adding new features:

1. Discuss major changes in an issue first
2. Keep the UI consistent with existing design
3. Maintain backwards compatibility when possible
4. Update the README if needed
5. Consider security implications

## Documentation

When contributing:

- Update README.md for user-facing changes
- Add code comments for complex logic
- Update CONTRIBUTING.md if process changes
- Document any new configuration options

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what's best for the community
- Show empathy towards others

## Questions?

If you have questions about contributing:
- Open an issue with the "question" label
- Check existing issues and pull requests
- Review the README documentation

Thank you for contributing to MQTT Dashboard! 🎉

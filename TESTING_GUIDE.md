# Testing Guide for AgriAssistant

This project has been set up with comprehensive test suites using Django's built-in testing framework, compatible with TestSprite.

## Test Coverage

### ✅ Test Suites Created

1. **chatbot/tests.py** - 44 tests covering:
   - UserProfile, ChatSession, ChatMessage models
   - Agricultural data models (FAQ, PestInfo, FertilizerGuideline, etc.)
   - Authentication (signup, login, logout)
   - Chatbot views and API endpoints
   - Chat session management

2. **reminders/tests.py** - 14 tests covering:
   - FarmReminder model
   - Reminder views (index, add, update status)
   - API events endpoint
   - User isolation and permissions

3. **policy_updates/tests.py** - 16 tests covering:
   - GovUpdate model
   - User-facing views (list, detail, search, filter)
   - Admin views (create, edit, delete)
   - Staff permission checks

4. **weather/tests.py** - 11 tests covering:
   - Weather index view
   - Location handling and overrides
   - Weather API endpoint
   - Error handling

**Total: 79 tests - All Passing ✅**

## Running Tests

### Run All Tests
```bash
python manage.py test
```

### Run Tests with Verbosity
```bash
python manage.py test --verbosity=2
```

### Run Tests for Specific App
```bash
python manage.py test chatbot
python manage.py test reminders
python manage.py test policy_updates
python manage.py test weather
```

### Run Specific Test Class
```bash
python manage.py test chatbot.tests.AuthenticationTest
```

### Run Specific Test
```bash
python manage.py test chatbot.tests.AuthenticationTest.test_user_login_success
```

## Test Configuration Files

### testsprite_config.json
Configuration file for TestSprite integration:
- Test directories and patterns
- Coverage settings
- Test categories (unit, integration, authentication)
- Environment variables

### pytest.ini
Pytest configuration (optional, if using pytest):
- Test discovery patterns
- Markers for test categorization
- Test paths

## Test Categories

Tests are organized into categories:

1. **Unit Tests** - Test individual models and utilities
   - Model creation and validation
   - String representations
   - Default values
   - Ordering

2. **Integration Tests** - Test views and API endpoints
   - Authentication flows
   - CRUD operations
   - API responses
   - User isolation

3. **Authentication Tests** - Test security and permissions
   - Login/logout flows
   - User vs Admin separation
   - Permission checks
   - Session management

## Key Test Features

### Mocking External Services
Tests use mocking for:
- LLM API calls (Groq/Mistral)
- Weather API calls
- Agricultural data API calls

### Database Isolation
Each test runs in isolation with:
- Fresh test database
- Automatic cleanup
- No data persistence between tests

### User Isolation
Tests verify that:
- Users can only access their own data
- Admin users have appropriate permissions
- Regular users cannot access admin functions

## Test Results

```
Ran 79 tests in ~71 seconds
All tests passing ✅
```

## Using with TestSprite

TestSprite can use these test files to:
1. Generate additional test cases
2. Run tests automatically
3. Generate coverage reports
4. Identify edge cases
5. Suggest improvements

## Adding New Tests

When adding new features:

1. **Add model tests** in the appropriate `tests.py` file
2. **Add view tests** for new endpoints
3. **Add authentication tests** for protected views
4. **Mock external services** to avoid API calls during testing
5. **Test edge cases** and error conditions

## Example Test Structure

```python
class MyFeatureTest(TestCase):
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(...)
    
    def test_feature_success(self):
        """Test successful feature usage"""
        # Test implementation
    
    def test_feature_error_handling(self):
        """Test error conditions"""
        # Test implementation
```

## Continuous Integration

These tests are ready for CI/CD integration:
- GitHub Actions
- GitLab CI
- Jenkins
- TestSprite automated testing

## Notes

- Tests use Django's TestCase which provides database rollback
- External API calls are mocked to ensure fast, reliable tests
- All tests are independent and can run in any order
- Test database is created fresh for each test run


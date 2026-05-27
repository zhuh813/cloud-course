import json
import pytest
from src.app import create_app

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
    })
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

def test_index_page(client):
    """Test that the index dashboard loads successfully."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Antigravity Flask" in response.data

def test_api_status(client):
    """Test that the API status returns healthy environment data."""
    response = client.get('/api/status')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    assert data['port'] == 1919
    assert 'python_version' in data
    assert 'platform' in data

def test_api_health(client):
    """Test the health-check endpoint."""
    response = client.get('/api/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'OK'
    assert data['code'] == 200

def test_api_echo_get(client):
    """Test dynamic query parameter echo on GET."""
    response = client.get('/api/echo?name=Alice&message=Welcome')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
    assert data['echo']['name'] == 'Alice'
    assert data['echo']['message'] == 'Welcome'
    assert "Alice" in data['message']

def test_api_echo_post(client):
    """Test raw payload echo on POST."""
    payload = {
        "name": "Bob",
        "message": "Testing POST request"
    }
    response = client.post('/api/echo',
                           data=json.dumps(payload),
                           content_type='application/json')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
    assert data['echo']['name'] == 'Bob'
    assert data['echo']['message'] == 'Testing POST request'

def test_404_error_page(client):
    """Test custom 404 behavior for html versus api."""
    # HTML-style 404 returns template index.html as a fallback
    response = client.get('/nonexistent-page')
    assert response.status_code == 404
    assert b"Antigravity Flask" in response.data

    # API-style 404 returns standard JSON response
    response = client.get('/api/nonexistent')
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data['success'] is False
    assert data['error'] == 'Not Found'

def test_api_files_list(client):
    """Test that the workspace file list endpoint lists core project files."""
    response = client.get('/api/files')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
    assert 'files' in data
    # Core files must be listed
    assert 'run.py' in data['files']
    assert 'src/app.py' in data['files']
    assert 'test/test_app.py' in data['files']

def test_api_files_content_security(client):
    """Test reading file contents and verifying security folder boundary protections."""
    # 1. Successful read of active file
    response = client.get('/api/files/content?filepath=run.py')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
    assert 'run.py' in data['filepath']
    assert 'create_app' in data['content']

    # 2. Block directory traversal attempt (Forbidden 403)
    response = client.get('/api/files/content?filepath=../../some_external_file.txt')
    assert response.status_code == 403
    data = json.loads(response.data)
    assert data['success'] is False
    assert 'Forbidden' in data['error']

    # 3. Missing parameter check (Bad Request 400)
    response = client.get('/api/files/content')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['success'] is False

def test_api_metrics_monitoring(client):
    """Test that the resource metrics endpoint returns valid CPU and RAM numbers."""
    response = client.get('/api/metrics')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
    assert 'cpu_percentage' in data
    assert 'memory_percentage' in data
    assert 'active_sockets' in data
    assert isinstance(data['cpu_percentage'], (int, float))

def test_api_metrics_stress_surge(client):
    """Test triggering a stress test condition and verifying metric values rise."""
    # 1. Trigger simulated Peak Stress Surge via POST
    response = client.post('/api/metrics/stress')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
    assert 'ends_at' in data

    # 2. Assert that subsequent metric checks show active stress state and high load values
    response = client.get('/api/metrics')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
    assert data['stress_active'] is True
    # Values should be surged high (> 40% CPU, > 50% Memory under stress formulas)
    assert data['cpu_percentage'] > 40.0
    assert data['memory_percentage'] > 50.0
    assert data['stress_time_remaining'] > 0.0

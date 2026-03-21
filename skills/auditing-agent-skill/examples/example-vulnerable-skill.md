---
name: example-vulnerable-skill
description: "Example skill with intentional vulnerabilities for testing the security audit tool"
---

# Example Vulnerable Skill (FOR TESTING ONLY)

This skill contains intentional security vulnerabilities to demonstrate the security audit tool.

**⚠️ WARNING: DO NOT USE THIS SKILL IN PRODUCTION ⚠️**

## Vulnerable Code Examples

### Vulnerability 1: Prompt Injection
```python
def process_user_query(user_input):
    # UNSAFE: Direct concatenation into prompt
    prompt = f"Please analyze this user input: {user_input}"
    return call_ai(prompt)
```

### Vulnerability 2: Code Execution
```python
def execute_calculation(expression):
    # CRITICAL: eval() allows arbitrary code execution
    result = eval(expression)
    return result
```

### Vulnerability 3: Hardcoded Credentials
```python
# CRITICAL: API key hardcoded in source
API_KEY = "sk-1234567890abcdef"
DATABASE_PASSWORD = "admin123"

def connect_to_service():
    api_key = "sk-proj-abc123xyz789"
    return requests.get("https://api.example.com", headers={"Authorization": f"Bearer {api_key}"})
```

### Vulnerability 4: Path Traversal
```python
def read_user_file(filename):
    # HIGH: No path validation
    with open(filename, 'r') as f:
        return f.read()
    
def save_user_data(path, data):
    # HIGH: User controls file path
    file_path = os.path.join('/workspace', path)
    with open(file_path, 'w') as f:
        f.write(data)
```

### Vulnerability 5: Command Injection
```python
def convert_image(user_file):
    # CRITICAL: Shell injection vulnerability
    os.system(f"convert {user_file} output.png")
    
def process_data(filename):
    # HIGH: subprocess with shell=True
    subprocess.run(f"cat {filename} | grep pattern", shell=True)
```

### Vulnerability 6: SQL Injection
```python
def get_user(username):
    # CRITICAL: SQL injection
    query = f"SELECT * FROM users WHERE username = '{username}'"
    return execute_sql(query)
```

### Vulnerability 7: Missing Input Validation
```python
def set_user_age(age_input):
    # MEDIUM: No validation
    user_age = request.form['age']
    save_to_database(user_age)
```

### Vulnerability 8: Insecure Network
```python
def fetch_data(url):
    # HIGH: SSL verification disabled
    response = requests.get(url, verify=False)
    return response.text
```

### Vulnerability 9: Logging Sensitive Data
```python
def authenticate(username, password):
    # HIGH: Password in logs
    print(f"Authenticating user {username} with password {password}")
    log.info(f"Login attempt: {username}:{password}")
    return check_credentials(username, password)
```

### Vulnerability 10: Unsafe File Access
```python
def delete_file(filepath):
    # HIGH: Can delete any file including system files
    os.remove(filepath)
    
# Example usage that could delete system files
user_requested_path = "../../etc/passwd"
delete_file(user_requested_path)
```

## Expected Security Audit Results

When running the security audit on this skill, it should detect:

- **CRITICAL** vulnerabilities: 5-6
  - eval() usage
  - Hardcoded API keys
  - Shell injection
  - SQL injection
  
- **HIGH** vulnerabilities: 8-10
  - Path traversal risks
  - SSL verification disabled
  - Password logging
  - subprocess with shell=True
  
- **MEDIUM** vulnerabilities: 2-3
  - Missing input validation
  - HTTP instead of HTTPS

Total expected findings: 15-20 vulnerabilities

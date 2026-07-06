import urllib.request, urllib.parse, json

def req(url, method="GET", data=None, cookie=None):
    headers = {"Content-Type": "application/json"}
    if cookie:
        headers["Cookie"] = cookie
    body = json.dumps(data).encode("utf-8") if data else None
    request = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request) as response:
            cookie_header = response.info().get("Set-Cookie")
            session_cookie = None
            if cookie_header:
                for c in cookie_header.split(','):
                    if 'sessionid' in c:
                        session_cookie = c.split(';')[0].strip()
            return response.status, json.loads(response.read().decode()), session_cookie
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode()), None

# 1. Login as Admin
s, r, admin_cookie = req("http://localhost:8080/api/auth/login", "POST", {"username": "admin", "password": "admin123"})
print("Admin Login:", s, r)

# 2. Test Admin API
s, r, _ = req("http://localhost:8080/api/admin/stats", "GET", cookie=admin_cookie)
print("Admin Stats (as Admin):", s, r)

# 3. Test Student API
s, r, _ = req("http://localhost:8080/api/courses/1/enroll", "POST", cookie=admin_cookie)
print("Student Enroll (as Admin):", s, r)

# 4. Login as Student
s, r, student_cookie = req("http://localhost:8080/api/auth/login", "POST", {"username": "bima", "password": "1234"})
print("Student Login:", s, r)

# 5. Test Student API
s, r, _ = req("http://localhost:8080/api/courses/1/enroll", "POST", cookie=student_cookie)
print("Student Enroll (as Student):", s, r)

# 6. Test Admin API
s, r, _ = req("http://localhost:8080/api/admin/stats", "GET", cookie=student_cookie)
print("Admin Stats (as Student):", s, r)

import urllib.request
import urllib.error
import json

BASE_URL = "http://localhost:8080"

endpoints = [
    # Public
    ("GET", "/api/categories", None),
    ("GET", "/api/courses", None),
    ("GET", "/api/learning-paths", None),
]

def test_endpoints():
    errors = []
    for method, path, data in endpoints:
        url = BASE_URL + path
        req = urllib.request.Request(url, method=method)
        if data:
            req.add_header('Content-Type', 'application/json')
            req.data = json.dumps(data).encode('utf-8')
        try:
            res = urllib.request.urlopen(req)
            print(f"[OK] {method} {path} - Status: {res.getcode()}")
        except urllib.error.HTTPError as e:
            # 401/403 is expected for auth endpoints since we are not logged in!
            # 405 is expected if method is wrong, but we should test correct methods.
            if e.code in [401, 403]:
                print(f"[OK] {method} {path} - Status: {e.code} (Expected Auth Error)")
            else:
                errors.append(f"[ERROR] {method} {path} - Status: {e.code}")
                print(f"[ERROR] {method} {path} - Status: {e.code}")
        except urllib.error.URLError as e:
            errors.append(f"[ERROR] {method} {path} - {e.reason}")
            print(f"[ERROR] {method} {path} - {e.reason}")

    if errors:
        print("\nSUMMARY: Found Errors!")
        for err in errors:
            print(err)
    else:
        print("\nSUMMARY: All checked endpoints returned expected results.")

if __name__ == "__main__":
    test_endpoints()

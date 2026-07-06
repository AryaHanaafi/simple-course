import urllib.request
import urllib.error

req = urllib.request.Request('http://localhost:8080/', method='POST')
try:
    urllib.request.urlopen(req)
except urllib.error.HTTPError as e:
    print(e.read().decode())

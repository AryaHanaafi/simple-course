from ninja import NinjaAPI
from ninja_simple_jwt.auth.views.api import mobile_auth_router

# Inisialisasi API Ninja
api = NinjaAPI(title="LMS API with JWT", version="1.0.0")

api.add_router("/auth/", mobile_auth_router)

@api.get("/hello")
def hello(request):
    return {"message": "Hello World! API berjalan lancar."}

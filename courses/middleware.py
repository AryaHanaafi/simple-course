import time
from django.core.cache import cache
from django.http import HttpResponseForbidden

class RateLimitMiddleware:
    """
    Middleware to limit requests to certain endpoints (e.g. login, submit quiz)
    based on IP Address or Session.
    Max 5 requests per minute.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        restricted_exact = ['/', '/api/auth/login', '/api/auth/register']
        restricted_contains = ['/submit/']
        
        path_needs_limiting = False
        if request.path in restricted_exact:
            path_needs_limiting = True
        elif any(p in request.path for p in restricted_contains):
            path_needs_limiting = True
        
        if request.method == 'POST' and path_needs_limiting:
            ip = self.get_client_ip(request)
            # Create a unique cache key per IP and Path
            cache_key = f"ratelimit_{ip}_{request.path}"
            
            # Get the list of timestamps for this IP+Path
            request_times = cache.get(cache_key, [])
            
            current_time = time.time()
            
            # Filter timestamps to only keep those within the last 60 seconds
            request_times = [t for t in request_times if current_time - t < 60]
            
            if len(request_times) >= 5:
                if request.path.startswith('/api/'):
                    from django.http import JsonResponse
                    return JsonResponse({'status': 'error', 'message': 'Rate limit exceeded. Please wait a minute before trying again.'}, status=429)
                return HttpResponseForbidden("Rate limit exceeded. Please wait a minute before trying again.")
            
            # Add current request time
            request_times.append(current_time)
            # Save back to cache (timeout 60 seconds)
            cache.set(cache_key, request_times, timeout=60)

        response = self.get_response(request)
        return response
        
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

from django.http import JsonResponse, Http404
from django.core.exceptions import ObjectDoesNotExist

class APIErrorMiddleware:
    """
    Middleware to catch Http404 and ObjectDoesNotExist exceptions in API routes
    and return them as cleanly formatted JSON responses instead of HTML.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        if request.path.startswith('/api/'):
            if isinstance(exception, (Http404, ObjectDoesNotExist)):
                return JsonResponse({'status': 'error', 'message': 'Resource not found or does not exist'}, status=404)
            # Catching general API crashes to avoid 500 HTML
            return JsonResponse({'status': 'error', 'message': str(exception)}, status=500)
        return None

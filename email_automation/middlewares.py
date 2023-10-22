from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

from django_ratelimit.middleware import RatelimitMiddleware
from django.utils import timezone


ALLOWED_FILE_TYPES =  ['pdf', 'xlsx', 'xls', 'csv', 'json', 'pdf', 'png', 'jpg', 'jpeg', 'gif']
DISALLOWED_FILE_TYPES = ['bat', 'exe', 'cmd', 'msi', 'js', 'vbs', 'ps1', 'jar', 'com', 'scr']


class FileUploadMiddleware(MiddlewareMixin):
   
    def process_request(self, request):
        if request.method == 'POST':
            for file_field_name, file in request.FILES.items():
                # Process the uploaded file here
                # You can validate, manipulate, or save the file
                # Example: Check the file type or rename the file
                
                if  file.name.split('.')[-1] in DISALLOWED_FILE_TYPES:
                    error_message = 'This file is not allowed.'
                    response_data = {'error': error_message}
                    return JsonResponse(response_data, status=400)

            

class RateLimitJsonResponseMiddleware(RatelimitMiddleware):
    def process_response(self, request, response):
        if request.limited:
            # If the request is rate-limited, return a JSON response
            data = {'error': 'Rate limit exceeded'}
            return JsonResponse(data, status=429)  # 429 is the status code for "Too Many Requests"
        return super().process_response(request, response)
    

# class TimezoneMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         try:
#             # get django_timezone from cookie
#             tzname = request.COOKIES.get("user_timezone", "UTC")
#             if tzname:
#                 timezone.activate(timezone.zoneinfo.ZoneInfo(tzname))
#             else:
#                 timezone.deactivate()
#         except Exception as e:
#             timezone.deactivate()

#         return self.get_response(request)
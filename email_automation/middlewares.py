from django.utils.deprecation import MiddlewareMixin


ALLOWED_FILE_TYPES =  ['pdf', 'xlsx', 'xls', 'csv', 'json', 'pdf', 'png', 'jpg', 'jpeg']


class FileUploadMiddleware(MiddlewareMixin):
   
    def process_request(self, request):
        if request.method == 'POST':
            for file_field_name, file in request.FILES.items():
                # Process the uploaded file here
                # You can validate, manipulate, or save the file
                # Example: Check the file type or rename the file
                
                if  file.name.split('.')[-1] not in ALLOWED_FILE_TYPES:
                    raise Exception('This file is not allowed.')

            

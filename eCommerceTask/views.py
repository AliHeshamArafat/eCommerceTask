from django.http import HttpResponse

def home(request):
    return HttpResponse("<h1>Welcome to the eCommerce API</h1><p>Use the /api/ endpoint to access the API.</p>")

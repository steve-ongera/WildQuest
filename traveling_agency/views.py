from django.shortcuts import render

def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

def feature(request):
    return render(request, 'feature.html')

def project(request):
    return render(request, 'project.html')

def service(request):
    return render(request, 'service.html')

def team(request):
    return render(request, 'team.html')

def testimonial(request):
    return render(request, 'testimonial.html')

# Custom 404 page
def custom_404(request, exception):
    return render(request, '404.html', status=404)
def custom_500(request):
    return render(request, '500.html', status=500)
def custom_403(request, exception):
    return render(request, '403.html', status=403)
def custom_400(request, exception):
    return render(request, '400.html', status=400)


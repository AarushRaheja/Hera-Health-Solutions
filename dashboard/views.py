
from django.shortcuts import render, redirect
from .models import File
from django.contrib.auth.decorators import login_required

@login_required
def user_dashboard(request):
    user_files = File.objects.filter(user=request.user)

    if request.method == 'POST':
        for file_id in request.POST.getlist('file_id'):
            file = File.objects.get(id=file_id)
            new_status = request.POST.get(f'status_{file_id}')
            if new_status in dict(File.STATUS_CHOICES):
                file.status = new_status
                file.save()
        return redirect('user_dashboard')

    return render(request, 'dashboard/user_dashboard.html', {'files': user_files})

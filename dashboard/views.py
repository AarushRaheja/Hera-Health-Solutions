
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from .models import File
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserChangeForm
from django import forms

# Custom form for editing user profile
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'})
        }

@login_required
def user_dashboard(request):
    user_files = File.objects.filter(user=request.user)
    all_users = User.objects.all()

    if request.method == 'POST':
        for file_id in request.POST.getlist('file_id'):
            file = File.objects.get(id=file_id)
            new_status = request.POST.get(f'status_{file_id}')
            if new_status in dict(File.STATUS_CHOICES):
                file.status = new_status
                file.save()
        return redirect('user_dashboard')

    return render(request, 'dashboard/user_dashboard.html', {
        'files': user_files,
        'all_users': all_users
    })

@login_required
def user_page(request, username):
    user = get_object_or_404(User, username=username)
    user_files = File.objects.filter(user=user)
    
    # Handle user profile form
    if request.method == 'POST' and 'edit_profile' in request.POST:
        form = UserProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user_page', username=username)
    else:
        form = UserProfileForm(instance=user)
    
    # Handle file status updates
    if request.method == 'POST':
        for file_id in request.POST.getlist('file_id'):
            file = File.objects.get(id=file_id)
            new_status = request.POST.get(f'status_{file_id}')
            if new_status in dict(File.STATUS_CHOICES):
                file.status = new_status
                file.save()
        return redirect('user_page', username=username)

    return render(request, 'dashboard/user_dashboard.html', {
        'files': user_files,
        'user': user,
        'all_users': User.objects.all(),
        'profile_form': form
    })

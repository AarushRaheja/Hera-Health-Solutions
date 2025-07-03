
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import File, UserProfile
from django import forms
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Custom form for editing user profile
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'email', 'phone_number']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'})
        }

@login_required
def user_dashboard(request):
    user_files = File.objects.filter(user=request.user)
    all_profiles = UserProfile.objects.all()

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
        'all_profiles': all_profiles
    })

@csrf_exempt
@login_required
def assign_files(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            assignments = data.get('assignments', [])
            
            for assignment in assignments:
                file_name = assignment.get('fileName')
                assigned_to = assignment.get('assignedTo', [])
                
                # Get or create file
                file, created = File.objects.get_or_create(
                    name=file_name,
                    defaults={'user': request.user}
                )
                
                # Update assigned profiles
                file.profiles.clear()
                for profile_id in assigned_to:
                    try:
                        profile = UserProfile.objects.get(id=profile_id)
                        file.profiles.add(profile)
                    except UserProfile.DoesNotExist:
                        continue
                
                file.save()
            
            return JsonResponse({'success': True})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)

@login_required
def user_page(request, profile_id):
    profile = get_object_or_404(UserProfile, id=profile_id)
    user_files = File.objects.filter(profiles=profile)
    
    # Handle user profile form
    if request.method == 'POST' and 'edit_profile' in request.POST:
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('dashboard:user_page', profile_id=profile_id)
    else:
        form = UserProfileForm(instance=profile)
    
    # Handle file status updates
    if request.method == 'POST':
        for file_id in request.POST.getlist('file_id'):
            file = File.objects.get(id=file_id)
            new_status = request.POST.get(f'status_{file_id}')
            if new_status in dict(File.STATUS_CHOICES):
                file.status = new_status
                file.save()
        return redirect('user_page', profile_id=profile_id)

    return render(request, 'dashboard/user_dashboard.html', {
        'files': user_files,
        'profile': profile,
        'all_profiles': UserProfile.objects.all(),
        'profile_form': form
    })

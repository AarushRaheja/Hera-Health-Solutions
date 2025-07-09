
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import File, UserProfile, DashboardFileUser
from django import forms
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

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
    # Get or create user profile
    user_profile, created = UserProfile.objects.get_or_create(
        id=request.user.id,
        defaults={
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email
        }
    )
    
    all_profiles = UserProfile.objects.all()
    all_files = File.objects.all().values('id', 'name', 'upload_date')

    if request.method == 'POST':
        # Handle file status updates
        for file_id in request.POST.getlist('file_id'):
            try:
                # Get the DashboardFileUser entry for this file/user
                file_user = DashboardFileUser.objects.get(
                    file_id=file_id,
                    user_profile=user_profile
                )
                new_status = request.POST.get(f'status_{file_id}')
                if new_status in ['not-viewed', 'viewed']:
                    file_user.status = new_status
                    file_user.save()
            except DashboardFileUser.DoesNotExist:
                continue
        return redirect('user_dashboard')

    return render(request, 'dashboard/user_dashboard.html', {
        'files': None,
        'all_profiles': all_profiles,
        'all_files': json.dumps(list(all_files))
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
                for profile_id in assigned_to:
                    try:
                        profile = UserProfile.objects.get(id=profile_id)
                        # Use get_or_create to prevent duplicates
                        DashboardFileUser.objects.get_or_create(
                            file_id=file.id,
                            user_profile_id=profile.id,
                            defaults={'status': 'not-viewed'}
                        )
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
    all_files = File.objects.all().values('id', 'name', 'upload_date')
    # Get files assigned to this profile through DashboardFileUser
    file_user_entries = DashboardFileUser.objects.filter(
        user_profile_id=profile_id
    ).select_related('file').values(
        'file__id',
        'file__name',
        'file__upload_date',
        'status'
    )
    
    # Convert to a more friendly format
    files = [
        {
            'id': f['file__id'],
            'name': f['file__name'],
            'upload_date': f['file__upload_date'],
            'status': f['status']
        }
        for f in file_user_entries
    ]
    
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
            try:
                # Get the DashboardFileUser entry for this file/profile
                file_user = DashboardFileUser.objects.get(
                    file_id=file_id,
                    user_profile_id=profile_id
                )
                new_status = request.POST.get(f'status_{file_id}')
                if new_status in ['not-viewed', 'viewed']:
                    file_user.status = new_status
                    file_user.save()
            except DashboardFileUser.DoesNotExist:
                continue
        return redirect('user_page', profile_id=profile_id)

    return render(request, 'dashboard/user_dashboard.html', {
        'files': files,
        'profile': profile,
        'all_profiles': UserProfile.objects.all(),
        'profile_form': form,
        'all_files': all_files
    })
   

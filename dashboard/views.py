from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import File, UserProfile, DashboardFileUser
from django import forms
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os
from django.conf import settings
from datetime import datetime
from django.template.loader import render_to_string
from django.core.files.storage import default_storage

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
def upload_files(request):
    if request.method == 'POST' and request.FILES.get('files'):
        uploaded_files = request.FILES.getlist('files')
        results = []
        
        for uploaded_file in uploaded_files:
            file_id = f"file_{File.objects.count() + 1}"
            file_path = os.path.join(settings.MEDIA_ROOT, 'files', uploaded_file.name)
            
            # Save file to disk
            with open(file_path, 'wb') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)
            
            # Create File model entry
            file_obj = File(id=file_id, name=uploaded_file.name, upload_date=str(datetime.now()))
            file_obj.save()
            
            # Create DashboardFileUser entry for the uploader
            DashboardFileUser.objects.create(
                file=file_obj,
                user_profile_id=request.user.id,
                status='not-viewed'
            )
            
            results.append({
                'id': file_id,
                'name': uploaded_file.name,
                'upload_date': str(datetime.now())
            })
        
        return JsonResponse({'success': True, 'files': results})
    
    return JsonResponse({'success': False, 'error': 'No files uploaded'}, status=400)

@login_required
def serve_file(request, filename):
    file_path = os.path.join(settings.MEDIA_ROOT, 'files', filename)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            response = HttpResponse(f.read())
            # Set appropriate content type based on file extension
            import mimetypes
            content_type, _ = mimetypes.guess_type(file_path)
            if content_type:
                response['Content-Type'] = content_type
            return response
    return HttpResponse('File not found', status=404)

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
@csrf_exempt
def delete_file(request, filename):
    if request.method == 'DELETE':
        try:
            # Get the File object(s)
            file_objs = File.objects.filter(name=filename)
            
            # If no files found, return error
            if not file_objs.exists():
                raise File.DoesNotExist(f"File '{filename}' not found")
                
            # Process each file
            for file_obj in file_objs:
                # Delete file from media directory
                file_path = os.path.join(settings.MEDIA_ROOT, 'files', file_obj.name)
                if os.path.exists(file_path):
                    os.remove(file_path)
                    
                # Delete the File object
                file_obj.delete()
                
            # Delete all file-user assignments for this file
            DashboardFileUser.objects.filter(file__name=filename).delete()
            
            return JsonResponse({'success': True, 'message': 'File deleted successfully'})
        except File.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'File not found'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
@csrf_exempt
def delete_assigned_file(request, filename, profile_id):
    if request.method == 'DELETE':
        try:
            # Delete only the file-user assignment for this specific profile
            DashboardFileUser.objects.filter(
                file__name=filename,
                user_profile_id=profile_id
            ).delete()
            
            return JsonResponse({'success': True, 'message': 'File assignment removed'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

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
        return redirect('dashboard:user_page', profile_id=profile_id)

    return render(request, 'dashboard/user_dashboard.html', {
        'profile': profile,
        'profile_form': form,
        'files': files,
        'all_files': json.dumps(list(all_files)),
        'all_profiles': UserProfile.objects.all(),
        'profile_id': profile_id
    })

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django import forms
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
import os
from datetime import datetime
from django.template.loader import render_to_string
from django.core.files.storage import default_storage
from .models import File, DashboardFileUser, UploadedFile


# Custom form for editing user profile
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = DashboardFileUser
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'})
        }

@login_required
def user_dashboard(request):
    all_files = File.objects.all().values('id', 'name', 'upload_date')
    
    if request.user.is_superuser:
        all_users = User.objects.all()  # Show all users for superusers
    else:
        all_users = User.objects.filter(id=request.user.id)  # Only show current user
    
    # Redirect to the current user's profile if no user_id is specified
    user_id = request.GET.get('user_id')
    if not user_id:
        return redirect('dashboard:user_page', user_id=request.user.id)
    
    if request.method == 'POST':
        # Handle file status updates
        for file_id in request.POST.getlist('file_id'):
            try:
                file_user = DashboardFileUser.objects.get(
                    file_id=file_id,
                    user=request.user
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
        'all_files': json.dumps(list(all_files)),
        'all_profiles': all_users,
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
                user=request.user,
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
                for user_id in assigned_to:
                    # Use get_or_create to prevent duplicates
                    DashboardFileUser.objects.get_or_create(
                        file_id=file.id,
                        user_id=user_id,
                        defaults={'status': 'not-viewed'}
                    )
                
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
def delete_assigned_file(request, filename, user_id):
    if request.method == 'DELETE':
        try:
            # Delete only the file-user assignment for this specific profile
            DashboardFileUser.objects.filter(
                file__name=filename,
                user_id=user_id
            ).delete()
            
            return JsonResponse({'success': True, 'message': 'File assignment removed'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
def user_profile(request):
    """View that redirects to the current user's profile page."""
    return redirect('dashboard:user_page', user_id=request.user.id)

@login_required
@csrf_exempt
@login_required
def upload_user_file(request):
    """
    Handle file uploads from non-superuser dashboard.
    Saves the uploaded file to the UploadedFile model.
    """
    print(request.FILES)
    if request.method == 'POST' and request.FILES.get('file'):
        try:
            uploaded_file = request.FILES['file']
            
            # Create user-specific directory if it doesn't exist
            user_upload_dir = os.path.join(settings.MEDIA_ROOT, 'user_uploads', str(request.user.id))
            os.makedirs(user_upload_dir, exist_ok=True)
            
            # Save file to user's directory
            file_path = os.path.join(user_upload_dir, uploaded_file.name)
            
            # Handle duplicate filenames by adding a timestamp
            base, ext = os.path.splitext(uploaded_file.name)
            counter = 1
            while os.path.exists(file_path):
                file_path = os.path.join(user_upload_dir, f"{base}_{counter}{ext}")
                counter += 1
            
            with open(file_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)
            
            # Get just the filename (without path) for storage in the database
            filename = os.path.basename(file_path)
            
            # Create UploadedFile record with the actual filename used
            uploaded = UploadedFile.objects.create(
                user=request.user,
                file_name=filename,
                file_path=os.path.join('user_uploads', str(request.user.id), filename)
            )
            
            return JsonResponse({
                'success': True,
                'file': {
                    'id': uploaded.id,
                    'name': uploaded.file_name,
                    'upload_date': uploaded.upload_date.isoformat()
                }
            })
            
        except Exception as e:
            return JsonResponse(
                {'success': False, 'error': str(e)}, 
                status=500
            )
    
    return JsonResponse(
        {'success': False, 'error': 'No file provided'}, 
        status=400
    )

def user_page(request, user_id):
    profile = get_object_or_404(User, id=user_id)
    all_files = File.objects.all().values('id', 'name', 'upload_date')
    # Get files assigned to this profile through DashboardFileUser
    file_user_entries = DashboardFileUser.objects.filter(
        user_id=user_id
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
            return redirect('dashboard:user_page', user_id=user_id)
    else:
        form = UserProfileForm(instance=profile)
    
    # Handle file status updates
    if request.method == 'POST':
        for file_id in request.POST.getlist('file_id'):
            try:
                # Get the DashboardFileUser entry for this file/profile
                file_user = DashboardFileUser.objects.get(
                    file_id=file_id,
                    user_id=user_id
                )
                new_status = request.POST.get(f'status_{file_id}')
                if new_status in ['not-viewed', 'viewed']:
                    file_user.status = new_status
                    file_user.save()
            except DashboardFileUser.DoesNotExist:
                continue
        return redirect('dashboard:user_page', user_id=user_id)

    # Get users based on superuser status
    if request.user.is_superuser:
        all_users = User.objects.all()  # Show all users for superusers
    else:
        all_users = User.objects.filter(id=user_id)  # Only show current user
    
    return render(request, 'dashboard/user_dashboard.html', {
        'profile': profile,
        'profile_form': form,
        'files': files,
        'all_files': json.dumps(list(all_files)),
        'all_profiles': all_users,
        'profile_id': user_id
    })

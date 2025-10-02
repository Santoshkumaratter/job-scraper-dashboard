from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views, single_views

app_name = 'dashboard'

urlpatterns = [
    # Single Page Dashboard (Main)
    path('', login_required(single_views.single_page), name='single-page'),
    path('scrape/', login_required(single_views.single_scrape), name='single-scrape'),
    path('export/', login_required(single_views.single_export), name='single-export'),
    path('save-to-sheet/', login_required(single_views.single_save_to_sheet), name='save-to-sheet'),
    path('delete-all/', login_required(single_views.single_delete_all), name='delete-all'),
    path('delete-job/<int:job_id>/', login_required(single_views.single_delete_job), name='delete-job'),
    path('edit-job/<int:job_id>/', login_required(single_views.single_edit_job), name='edit-job'),
]

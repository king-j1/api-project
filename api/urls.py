from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ModelProfileViewSet, 
    contact_create, 
    SignupAPI, 
    login_api, 
    dashboard_api,
    UpdateProfileAPIView,
    DeleteAccountAPIView
)

# ==============================================
# DJANGO REST FRAMEWORK ROUTER
# Router = auto-generates URLs for ViewSets
# Instead of writing 5 paths for CRUD, router creates them automatically
# ==============================================
router = DefaultRouter()

# Register ModelProfileViewSet with router
# r'models' = URL will be /api/models/
router.register(r'models', ModelProfileViewSet, basename='modelprofile')

# After this line, router automatically creates:
# GET /api/models/ = list all models
# POST /api/models/ = create model
# GET /api/models/1/ = get model id=1
# PUT /api/models/1/ = update model id=1
# DELETE /api/models/1/ = delete model id=1

# ==============================================
# URL PATTERNS
# urlpatterns = list of all URLs this app handles
# ==============================================
urlpatterns = [
    # include(router.urls) = include all auto-generated routes from router
    path('', include(router.urls)),
    
    # POST /api/contact/ = contact form submit
    path('contact/', contact_create, name='contact-create'),
    
    # ==============================================
    # AUTH URLS
    # ==============================================
    # POST /api/signup/ = create new user account, returns JWT tokens
    path('signup/', SignupAPI.as_view(), name='signup'),
    
    # POST /api/login/ = authenticate user, returns JWT tokens  
    path('login/', login_api, name='login'),
    
    # GET /api/dashboard/ = show logged-in user info + their messages
    path('dashboard/', dashboard_api, name='dashboard'),

    # ==============================================
    # PROFILE MANAGEMENT URLS - NEW
    # ==============================================
    # PUT /api/update-profile/ = update user profile + avatar
    path('update-profile/', UpdateProfileAPIView.as_view(), name='update-profile'),
    
    # DELETE /api/delete-account/ = delete user account permanently
    path('delete-account/', DeleteAccountAPIView.as_view(), name='delete-account'),
]
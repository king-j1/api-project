from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# ==============================================
# MODEL 1: MODEL PROFILE
# This stores each model's basic info + main photo
# One ModelProfile = One model/talent in your agency
# ==============================================
class ModelProfile(models.Model):
    # CharField = short text. max_length required for database
    name = models.CharField(max_length=100)
    
    # ImageField = uploads image to folder 'models/main/'
    # blank=True = form can be empty, null=True = database can be empty
    main_image = models.ImageField(upload_to='models/main/', blank=True, null=True)
    
    # TextField = long text, no max_length limit. Good for bio/description
    profile = models.TextField(blank=True, help_text="Model bio or description")
    
    # DateTimeField with auto_now_add = Django automatically saves timestamp when created
    created_at = models.DateTimeField(auto_now_add=True)

    # __str__ = what shows in Django admin. Instead of "ModelProfile object", shows the name
    def __str__(self):
        return self.name

    # FIX: Added Meta class with ordering
    # adminsortable2 SortableAdminMixin requires 'ordering' in Meta
    # Without this Django throws ImproperlyConfigured error
    class Meta:
        ordering = ['id']  # Sort models by ID ascending. Newest = highest ID
        verbose_name = "Model Profile"  # Singular name in admin
        verbose_name_plural = "Model Profiles"  # Plural name in admin

# ==============================================
# MODEL 2: MODEL PHOTO GALLERY
# This stores extra photos for each model
# One ModelProfile can have MANY ModelPhotos = One-to-Many relationship
# ==============================================
class ModelPhoto(models.Model):
    # ForeignKey = creates relationship to ModelProfile
    # related_name='photos' = lets you do model.photos.all() to get all photos
    # on_delete=CASCADE = if model is deleted, all their photos auto delete too
    model = models.ForeignKey(
        ModelProfile, 
        related_name='photos',
        on_delete=models.CASCADE
    )
    
    # Upload each photo to 'models/images/' folder
    image = models.ImageField(upload_to='models/images/')
    
    # order field lets you sort photos. 0 comes first, 1 comes second, etc
    # adminsortable2 updates this field automatically when you drag-drop
    order = models.PositiveIntegerField(default=0, blank=False, null=False)

    # Meta class = extra settings for this model
    class Meta:
        ordering = ['order', 'id']  # Sort by order first, then ID as backup
        verbose_name = "Model Photo"
        verbose_name_plural = "Model Photos"
    
    def __str__(self):
        return f"{self.model.name} - Photo {self.id}"

# ==============================================
# MODEL 3: CLIENT PROFILE 
# This stores extra info for each user who signs up
# Django User handles password/login, this handles avatar/phone etc
# One User = One ClientProfile = One-to-One relationship
# ==============================================
class ClientProfile(models.Model):
    # OneToOneField = each Django User gets exactly 1 ClientProfile
    # on_delete=CASCADE = if user is deleted, profile auto deletes too
    # related_name='client_profile' = lets you do user.client_profile to access this
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client_profile')
    
    # Phone is optional
    phone = models.CharField(max_length=20, blank=True)
    
    # Avatar image uploads to 'clients/avatars/' folder
    avatar = models.ImageField(upload_to='clients/avatars/', blank=True, null=True)
    
    # Auto timestamp when profile is created
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    class Meta:
        verbose_name = "Client Profile"
        verbose_name_plural = "Client Profiles"

# ==============================================
# MODEL 4: CONTACT FORM SUBMISSIONS
# This stores every message from your Contact page form
# Each form submit = 1 ContactMessage row in database
# UPDATED: Added 'user' field so logged-in users can see their own messages
# ==============================================
class ContactMessage(models.Model):
    # Choices = dropdown options. First value saved to DB, second shown to user
    INQUIRY_TYPES = [
        ('booking', 'Book Studio Session'),
        ('talent', 'Join Talent Network'),
        ('commercial', 'Commercial Project'),
        ('collaboration', 'Brand Collaboration'),
        ('other', 'Other'),
    ]
    
    # NEW: Link message to logged-in user. null=True so old guest messages don't break
    # on_delete=SET_NULL = if user is deleted, message stays but user field becomes empty
    # related_name='messages' = lets you do user.messages.all() to get all user's messages
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='messages')
    
    # Who sent the message - for guest users who aren't logged in
    name = models.CharField(max_length=100)
    
    # EmailField validates email format automatically
    email = models.EmailField()
    
    # Phone is optional, so blank=True null=True
    phone = models.CharField(max_length=20, blank=True, null=True)
    
    # CharField with choices = dropdown in form/admin
    # default='booking' = if user doesn't select, it becomes 'booking'
    inquiry_type = models.CharField(max_length=20, choices=INQUIRY_TYPES, default='booking')
    
    # The actual message from textarea
    message = models.TextField()
    
    # Timestamp when message was submitted
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Flag for you to mark messages as read in admin
    # default=False = new messages show as unread
    is_read = models.BooleanField(default=False)

    # NEW FIELDS for admin reply - Option 2
    admin_reply = models.TextField(blank=True, null=True, help_text="Type your reply to client here")
    replied_at = models.DateTimeField(blank=True, null=True, help_text="Auto-filled when you send reply")

    # __str__ shows name + inquiry type in admin
    # get_inquiry_type_display() = shows "Book Studio Session" instead of "booking"
    def __str__(self):
        return f"{self.name} - {self.get_inquiry_type_display()}"

    # Meta class = extra settings
    class Meta:
        ordering = ['-created_at']  # '-' means newest messages first
        verbose_name = "Contact Message"  # Singular name in admin
        verbose_name_plural = "Contact Messages"  # Plural name in admin
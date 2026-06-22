from django.contrib import admin
from django.utils.html import format_html
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from adminsortable2.admin import SortableAdminMixin, SortableInlineAdminMixin
from.models import ModelProfile, ModelPhoto, ContactMessage, ClientProfile
# ^ Added ClientProfile import

# ==============================================
# ADMIN INLINE: PHOTO GALLERY
# Inline = edit photos directly inside ModelProfile page
# SortableInlineAdminMixin = drag-drop to reorder photos, updates 'order' field automatically
# ==============================================
class PhotoInline(SortableInlineAdminMixin, admin.TabularInline):
    model = ModelPhoto # The model this inline edits
    extra = 3 # Show 3 empty upload boxes by default
    max_num = 20 # Limit to 20 photos max per model
    readonly_fields = ['image_preview'] # Preview field can't be edited

    # Custom method to show thumbnail preview in admin
    def image_preview(self, obj):
        # obj = current ModelPhoto instance
        if obj.image:
            # format_html = safely render HTML. Prevents XSS attacks
            return format_html(
                '<img src="{}" style="max-height:100px;border-radius:4px;object-fit:cover;"/>',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = 'Preview' # Column header name

# ==============================================
# ADMIN: MODEL PROFILE
# Main page for managing models/talents
# SortableAdminMixin = enables drag-drop sorting if you add 'order' field later
# ==============================================
@admin.register(ModelProfile) # @admin.register = decorator to register model with admin
class ModelProfileAdmin(SortableAdminMixin, admin.ModelAdmin):
    # list_display = columns shown in /admin/api/modelprofile/ list view
    list_display = ['name', 'main_image_preview', 'photo_count', 'created_at']

    # inlines = show PhotoInline inside ModelProfile add/edit page
    inlines = [PhotoInline]

    # search_fields = adds search box. Searches by model name
    search_fields = ['name']

    # readonly_fields = these fields can't be edited. Django sets them automatically
    readonly_fields = ['main_image_preview', 'created_at']

    # fields = order of fields on add/edit page
    fields = ['name', 'main_image', 'main_image_preview', 'profile', 'created_at']

    # list_filter = filter sidebar on right
    list_filter = ['created_at']

    # Custom method to show main image thumbnail
    def main_image_preview(self, obj):
        if obj.main_image:
            return format_html(
                '<img src="{}" style="max-height:80px;border-radius:4px;object-fit:cover;"/>',
                obj.main_image.url
            )
        return "No main image"
    main_image_preview.short_description = 'Main Photo' # Column name

    # Custom method to count related photos
    def photo_count(self, obj):
        return obj.photos.count() # obj.photos comes from related_name='photos' in ForeignKey
    photo_count.short_description = 'Photos'

# ==============================================
# ADMIN: MODEL PHOTO - STANDALONE
# Optional: lets you view/edit all photos in one table
# You can delete this if you only want inline editing
# ==============================================
@admin.register(ModelPhoto)
class ModelPhotoAdmin(admin.ModelAdmin):
    # Columns in /admin/api/modelphoto/
    list_display = ['model', 'order', 'image_preview']

    # Filter sidebar: filter photos by which model they belong to
    list_filter = ['model']

    # Default sort order in admin table
    ordering = ['model', 'order']

    # Thumbnail preview for standalone photo admin
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height:80px;border-radius:4px;object-fit:cover;"/>',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = 'Preview'

# ==============================================
# ADMIN: CLIENT PROFILE - NEW
# Job: View client info from User registration
# Shows phone + avatar + link to User
# ==============================================
@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_link', 'phone', 'avatar_preview', 'created_at']
    search_fields = ['user__username', 'user__email', 'phone']
    list_filter = ['created_at']
    readonly_fields = ['avatar_preview', 'created_at', 'user_link']

    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html('<img src="{}" style="height: 60px; width: 60px; border-radius: 50%; object-fit: cover;" />', obj.avatar.url)
        return "No avatar"
    avatar_preview.short_description = 'Avatar'

    # Clickable link to User admin page
    def user_link(self, obj):
        url = f"/admin/auth/user/{obj.user.id}/change/"
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    user_link.short_description = 'User'

# ==============================================
# ADMIN: CONTACT MESSAGE - UPDATED FOR OPTION 2 + USER LINK
# Lets you read + reply to contact form submissions
# Added: user_link column to see which logged-in user sent it
# ==============================================
@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    # Show these columns in list view - added user_link
    list_display = ['name', 'email', 'user_link', 'inquiry_type', 'is_read', 'replied_at', 'created_at']

    # Allow editing 'is_read' directly in list without opening detail page
    list_editable = ['is_read']

    # Filter sidebar: filter by inquiry type, read status, date
    list_filter = ['inquiry_type', 'is_read', 'created_at']

    # Search box: search by name, email, message, username
    search_fields = ['name', 'email', 'message', 'user__username']

    # Can't edit these fields after form submission - added user_link
    readonly_fields = ['name', 'email', 'phone', 'inquiry_type', 'message', 'created_at', 'replied_at', 'user_link']

    # Group fields into sections on detail page - added user_link to Contact Info
    fieldsets = (
        ('Contact Info', {
            'fields': ('user_link', 'name', 'email', 'phone', 'inquiry_type')
        }),
        ('Message', {
            'fields': ('message',)
        }),
        ('Admin Reply', {
            'fields': ('admin_reply', 'replied_at'),
            'description': 'Type your reply here, then use "Send admin reply" action from list view'
        }),
        ('Status', {
            'fields': ('is_read', 'created_at')
        }),
    )

    # Show newest messages first
    ordering = ['-created_at']

    # Bulk actions: mark as read + send reply
    actions = ['mark_as_read', 'send_reply']

    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
        self.message_user(request, f"{queryset.count()} messages marked as read")
    mark_as_read.short_description = "Mark selected messages as read"

    def send_reply(self, request, queryset):
        sent_count = 0
        error_count = 0
        for msg in queryset:
            if msg.admin_reply and not msg.replied_at:
                try:
                    send_mail(
                        subject=f"Re: Your inquiry about {msg.get_inquiry_type_display()} - Pro Models Studio",
                        message=f"Hi {msg.name},\n\n{msg.admin_reply}\n\nBest regards,\nPro Models Studio Team",
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[msg.email],
                        fail_silently=False,
                    )
                    msg.replied_at = timezone.now()
                    msg.is_read = True
                    msg.save()
                    sent_count += 1
                except Exception as e:
                    error_count += 1
                    self.message_user(request, f"Error sending to {msg.email}: {str(e)}", level='error')

        if sent_count > 0:
            self.message_user(request, f"✅ Reply sent to {sent_count} client(s) successfully!")
        if error_count > 0:
            self.message_user(request, f"❌ Failed to send {error_count} email(s). Check Django terminal for errors.", level='error')
    send_reply.short_description = "Send admin reply to selected clients"

    # NEW: Show clickable link to User if message is from logged-in user
    def user_link(self, obj):
        if obj.user:
            url = f"/admin/auth/user/{obj.user.id}/change/"
            return format_html('<a href="{}">{}</a>', url, obj.user.username)
        return "Guest user"
    user_link.short_description = 'User Account'

# ==============================================
# ADMIN SITE TITLE - Optional branding
# ==============================================
admin.site_header = "Talent Hub Admin"
admin.site_title = "Talent Hub Portal"
admin.site.index_title = "Dashboard"
from django.contrib import admin
from .models import User, Note, Link, Template, Attachment, APIIntegration, AITask
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    pass

admin.site.register(Note)
admin.site.register(Link)
admin.site.register(Template)
admin.site.register(Attachment)
admin.site.register(APIIntegration)
admin.site.register(AITask)
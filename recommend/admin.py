from django.contrib import admin

from recommend.models import Schedule, DietPlan

# Register your models here.
class YourModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'updated_at', 'created_at')
    readonly_fields = ('updated_at', 'created_at')

admin.site.register(Schedule, YourModelAdmin)
# admin.site.register(Schedule)
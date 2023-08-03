from django.contrib import admin

from recommend.models import Schedule, DietPlan

class ScheduleModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'updated_at', 'created_at')
    readonly_fields = ('updated_at', 'created_at')

admin.site.register(Schedule, ScheduleModelAdmin)

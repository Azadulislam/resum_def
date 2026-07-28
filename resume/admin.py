from resume.models import Profile, Section, SectionItem, Variation

from django.contrib import admin

# Register your models here.


@admin.register(Profile) # Using the modern decorator syntax instead of admin.site.register
class ProfileAdmin(admin.ModelAdmin): # Ensure it inherits from admin.ModelAdmin
    # 1. Add custom methods to your list display
    list_display = ('title', 'get_variations', 'get_sections')
    
    # 2. Prevent N+1 queries by prefetching related data
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.prefetch_related('variation', 'section')

    # 3. Create a comma-separated string for Variations
    @admin.display(description='Profile Variations')
    def get_variations(self, obj):
        # Assumes variations is a relationship. Change '.name' to your variation field name.
        return ", ".join([v.title for v in obj.variation.all()]) or "None"

    # 4. Create a comma-separated string for Sections
    @admin.display(description='Sections')
    def get_sections(self, obj):
        # Assumes sections is a relationship. Uses '.title' from your Section model.
        return ", ".join([s.title for s in obj.section.all()]) or "None"
    
admin.site.register(Section)

@admin.register(SectionItem)
class SectionItemAdmin(admin.ModelAdmin):
    list_display = ['section', 'title', 'is_present_display', 'get_variations', 'order', 'description']
    list_filter = ['is_present', 'section']

    @admin.display(description="Variatios")
    def get_variations(self, obj):
        return ", ".join([v.title for v in obj.variation.all()]) or "None"

    @admin.display(description="Is Present", boolean=True)
    def is_present_display(self, obj):
        return bool(obj.is_present)

    def save_form(self, request, form, change):
        obj = super().save_form(request, form, change)
        obj.is_present = "is_present" in request.POST
        return obj

    def save_model(self, request, obj, form, change):
        if obj.is_present:
            obj.enddate = None
        super().save_model(request, obj, form, change)

admin.site.register(Variation)


from django.contrib import admin
from .models import Industry, Company, CompanyAdmin, CompanyFollower, CompanyLocation


@admin.register(Industry)
class IndustryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'industry', 'company_size', 'is_verified', 'follower_count', 'created_at')
    list_filter = ('industry', 'company_size', 'is_verified', 'is_active')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ('admins',) 
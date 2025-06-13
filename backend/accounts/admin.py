from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Experience, Education, Skill, UserSkill, SkillEndorsement


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_active', 'is_company_user', 'is_verified', 'experience_level')
    search_fields = ('email', 'first_name', 'last_name', 'headline')
    ordering = ('email',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'profile_picture')}),
        ('Professional info', {
            'fields': ('headline', 'summary', 'current_position', 'industry', 'experience_level', 'location')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_company_user', 'is_verified', 'groups', 'user_permissions'),
        }),
        ('Privacy', {'fields': ('privacy_public_profile', 'privacy_show_connections')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'company', 'start_date', 'end_date', 'is_current')
    list_filter = ('is_current', 'start_date')
    search_fields = ('user__email', 'title', 'company')
    date_hierarchy = 'start_date'


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ('user', 'school', 'degree', 'field_of_study', 'start_year', 'end_year')
    list_filter = ('start_year', 'end_year')
    search_fields = ('user__email', 'school', 'degree', 'field_of_study')


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)


@admin.register(UserSkill)
class UserSkillAdmin(admin.ModelAdmin):
    list_display = ('user', 'skill', 'endorsement_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'skill__name')


@admin.register(SkillEndorsement)
class SkillEndorsementAdmin(admin.ModelAdmin):
    list_display = ('user_skill', 'endorser', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user_skill__user__email', 'endorser__email') 
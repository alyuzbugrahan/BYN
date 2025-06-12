from rest_framework import serializers
from django.utils.text import slugify
from .models import Company, Industry, CompanyAdmin, CompanyFollower, CompanyLocation
from accounts.serializers import UserBasicSerializer


class IndustrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Industry
        fields = ['id', 'name', 'created_at']


class CompanySerializer(serializers.ModelSerializer):
    industry = IndustrySerializer(read_only=True)
    
    class Meta:
        model = Company
        fields = [
            'id', 'name', 'slug', 'description', 'industry', 
            'headquarters', 'company_size', 'founded_year',
            'website', 'logo', 'cover_image', 'follower_count',
            'is_verified', 'created_at'
        ]


class CompanyBasicSerializer(serializers.ModelSerializer):
    """Basic company serializer for references in other models"""
    industry = IndustrySerializer(read_only=True)
    
    class Meta:
        model = Company
        fields = (
            'id', 'name', 'slug', 'industry', 'company_size',
            'headquarters', 'logo', 'is_verified', 'follower_count'
        )


class CompanyLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyLocation
        fields = (
            'id', 'address', 'city', 'state', 'country',
            'postal_code', 'is_headquarters'
        )


class CompanyDetailSerializer(serializers.ModelSerializer):
    """Detailed company serializer for company profile pages"""
    industry = IndustrySerializer(read_only=True)
    created_by = UserBasicSerializer(read_only=True)
    locations = CompanyLocationSerializer(many=True, read_only=True)
    is_following = serializers.SerializerMethodField()
    job_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Company
        fields = [
            'id', 'name', 'slug', 'description', 'industry',
            'headquarters', 'company_size', 'founded_year', 
            'website', 'logo', 'cover_image', 'follower_count',
            'is_verified', 'created_by', 'created_at', 'updated_at',
            'locations', 'is_following', 'job_count'
        ]
    
    def get_is_following(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return CompanyFollower.objects.filter(company=obj, user=request.user).exists()
        return False
    
    def get_job_count(self, obj):
        return obj.jobs.filter(is_active=True).count()


class CompanyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = [
            'name', 'description', 'industry', 'headquarters',
            'company_size', 'founded_year', 'website', 'logo', 'cover_image'
        ]
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class CompanyListSerializer(serializers.ModelSerializer):
    """Serializer for company listings and search results"""
    industry = IndustrySerializer(read_only=True)
    is_following = serializers.SerializerMethodField()
    job_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Company
        fields = (
            'id', 'name', 'slug', 'description', 'industry', 'company_size',
            'headquarters', 'logo', 'is_verified', 'follower_count',
            'is_following', 'job_count'
        )
    
    def get_is_following(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return CompanyFollower.objects.filter(company=obj, user=request.user).exists()
        return False
    
    def get_job_count(self, obj):
        return obj.jobs.filter(is_active=True).count()


class CompanyAdminSerializer(serializers.ModelSerializer):
    user = UserBasicSerializer(read_only=True)
    assigned_by = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = CompanyAdmin
        fields = ('id', 'user', 'role', 'assigned_by', 'created_at')


class CompanyFollowerSerializer(serializers.ModelSerializer):
    user = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = CompanyFollower
        fields = ('id', 'user', 'created_at') 
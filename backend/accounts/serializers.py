from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from drf_spectacular.utils import extend_schema_field
from .models import User, Experience, Education, Skill, UserSkill, SkillEndorsement


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password', 'password_confirm')
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Password fields didn't match.")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        # Normalize email to lowercase
        validated_data['email'] = validated_data['email'].lower().strip()
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            # Normalize email to lowercase for case-insensitive login
            email = email.lower().strip()
            user = authenticate(request=self.context.get('request'),
                              email=email, password=password)
            if not user:
                raise serializers.ValidationError('Invalid email or password.')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled.')
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Must include email and password.')


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ('id', 'name')


class UserSkillSerializer(serializers.ModelSerializer):
    skill = SkillSerializer(read_only=True)
    skill_name = serializers.CharField(write_only=True)
    
    class Meta:
        model = UserSkill
        fields = ('id', 'skill', 'skill_name', 'endorsement_count', 'created_at')
        read_only_fields = ('endorsement_count', 'created_at')
    
    def create(self, validated_data):
        skill_name = validated_data.pop('skill_name')
        skill, created = Skill.objects.get_or_create(name=skill_name)
        validated_data['skill'] = skill
        return super().create(validated_data)


class ExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experience
        fields = ('id', 'title', 'company', 'location', 'start_date', 'end_date', 
                 'is_current', 'description', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')


class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = ('id', 'school', 'degree', 'field_of_study', 'start_year', 
                 'end_year', 'description', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')


class UserProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    initials = serializers.CharField(read_only=True)
    experiences = ExperienceSerializer(many=True, read_only=True)
    education = EducationSerializer(many=True, read_only=True)
    user_skills = UserSkillSerializer(many=True, read_only=True)
    profile_picture = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'full_name', 'initials',
                 'headline', 'summary', 'location', 'profile_picture', 'current_position',
                 'industry', 'experience_level', 'is_verified', 'is_company_user', 'privacy_public_profile',
                 'privacy_show_connections', 'date_joined', 'experiences', 'education', 'user_skills')
        read_only_fields = ('id', 'email', 'is_verified', 'is_company_user', 'date_joined')
    
    @extend_schema_field(str)
    def get_profile_picture(self, obj) -> str:
        if obj.profile_picture:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profile_picture.url)
            return obj.profile_picture.url
        return None


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'headline', 'summary', 'location',
                 'profile_picture', 'current_position', 'industry', 'experience_level',
                 'privacy_public_profile', 'privacy_show_connections')


class UserBasicSerializer(serializers.ModelSerializer):
    """Lightweight user serializer for use in other serializers"""
    full_name = serializers.SerializerMethodField()
    profile_picture_url = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'first_name', 'last_name', 'full_name', 
            'headline', 'current_position', 'profile_picture_url'
        ]
    
    @extend_schema_field(str)
    def get_full_name(self, obj) -> str:
        return obj.full_name
    
    @extend_schema_field(str)
    def get_profile_picture_url(self, obj) -> str:
        if obj.profile_picture:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profile_picture.url)
            return obj.profile_picture.url
        return None


class UserSearchSerializer(serializers.ModelSerializer):
    """Serializer for user search results"""
    full_name = serializers.CharField(read_only=True)
    initials = serializers.CharField(read_only=True)
    mutual_connections_count = serializers.IntegerField(read_only=True)
    profile_picture = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ('id', 'full_name', 'initials', 'headline', 'current_position',
                 'location', 'profile_picture', 'industry', 'is_verified',
                 'mutual_connections_count')
    
    @extend_schema_field(str)
    def get_profile_picture(self, obj) -> str:
        if obj.profile_picture:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profile_picture.url)
            return obj.profile_picture.url
        return None


class SkillEndorsementSerializer(serializers.ModelSerializer):
    endorser = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = SkillEndorsement
        fields = ('id', 'endorser', 'created_at')
        read_only_fields = ('created_at',) 
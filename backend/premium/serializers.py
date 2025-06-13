from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    SubscriptionPlan, UserSubscription, PremiumFeature, UsageTracking,
    BillingHistory, PromoCode, PromoCodeUsage, InMailCredit, PremiumAnalytics
)

class SubscriptionPlanSerializer(serializers.ModelSerializer):
    yearly_savings = serializers.ReadOnlyField()
    monthly_price_formatted = serializers.SerializerMethodField()
    yearly_price_formatted = serializers.SerializerMethodField()
    savings_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = SubscriptionPlan
        fields = [
            'id', 'name', 'plan_type', 'description', 'monthly_price',
            'yearly_price', 'yearly_discount_percentage', 'yearly_savings',
            'monthly_price_formatted', 'yearly_price_formatted', 'savings_formatted',
            'profile_views_per_month', 'inmails_per_month', 'search_results_per_search',
            'advanced_search_filters', 'can_see_who_viewed_profile',
            'can_see_full_name_of_viewers', 'priority_customer_support',
            'learning_access', 'insights_and_analytics', 'company_page_analytics',
            'lead_generation_tools', 'competitor_insights', 'recruiter_search_tools',
            'talent_pipeline', 'advanced_reporting', 'is_active', 'display_order'
        ]
    
    def get_monthly_price_formatted(self, obj):
        return f"${obj.monthly_price}"
    
    def get_yearly_price_formatted(self, obj):
        return f"${obj.yearly_price}"
    
    def get_savings_formatted(self, obj):
        return f"${obj.yearly_savings}"

class UserSubscriptionSerializer(serializers.ModelSerializer):
    plan = SubscriptionPlanSerializer(read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    is_active = serializers.ReadOnlyField()
    days_remaining = serializers.ReadOnlyField()
    is_trial = serializers.ReadOnlyField()
    usage_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = UserSubscription
        fields = [
            'id', 'user', 'user_name', 'plan', 'status', 'billing_cycle',
            'start_date', 'end_date', 'trial_end_date', 'next_billing_date',
            'profile_views_used', 'inmails_used', 'last_usage_reset',
            'auto_renew', 'is_active', 'days_remaining', 'is_trial',
            'usage_percentage', 'created_at', 'updated_at'
        ]
    
    def get_usage_percentage(self, obj):
        if obj.plan.profile_views_per_month == -1:  # Unlimited
            return 0
        if obj.plan.profile_views_per_month == 0:
            return 100
        return (obj.profile_views_used / obj.plan.profile_views_per_month) * 100

class PremiumFeatureSerializer(serializers.ModelSerializer):
    available_plans = SubscriptionPlanSerializer(many=True, read_only=True)
    feature_type_display = serializers.CharField(source='get_feature_type_display', read_only=True)
    
    class Meta:
        model = PremiumFeature
        fields = [
            'id', 'name', 'feature_type', 'feature_type_display',
            'description', 'code', 'available_plans', 'is_active'
        ]

class UsageTrackingSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    feature_name = serializers.CharField(source='feature.name', read_only=True)
    
    class Meta:
        model = UsageTracking
        fields = [
            'id', 'user', 'user_name', 'feature', 'feature_name',
            'usage_count', 'last_used', 'monthly_usage', 'yearly_usage'
        ]

class BillingHistorySerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='subscription.user.get_full_name', read_only=True)
    plan_name = serializers.CharField(source='subscription.plan.name', read_only=True)
    transaction_type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    amount_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = BillingHistory
        fields = [
            'id', 'subscription', 'user_name', 'plan_name', 'transaction_type',
            'transaction_type_display', 'amount', 'amount_formatted', 'currency',
            'status', 'status_display', 'description', 'billing_period_start',
            'billing_period_end', 'created_at'
        ]
    
    def get_amount_formatted(self, obj):
        return f"{obj.currency} {obj.amount}"

class PromoCodeSerializer(serializers.ModelSerializer):
    applicable_plans = SubscriptionPlanSerializer(many=True, read_only=True)
    discount_type_display = serializers.CharField(source='get_discount_type_display', read_only=True)
    is_valid = serializers.ReadOnlyField()
    discount_formatted = serializers.SerializerMethodField()
    uses_remaining = serializers.SerializerMethodField()
    
    class Meta:
        model = PromoCode
        fields = [
            'id', 'code', 'discount_type', 'discount_type_display',
            'discount_value', 'discount_formatted', 'applicable_plans',
            'max_uses', 'current_uses', 'uses_remaining', 'valid_from',
            'valid_until', 'is_active', 'is_valid', 'first_time_users_only',
            'description'
        ]
    
    def get_discount_formatted(self, obj):
        if obj.discount_type == 'percentage':
            return f"{obj.discount_value}%"
        elif obj.discount_type == 'fixed_amount':
            return f"${obj.discount_value}"
        else:
            return f"{obj.discount_value} days"
    
    def get_uses_remaining(self, obj):
        if obj.max_uses is None:
            return "Unlimited"
        return max(0, obj.max_uses - obj.current_uses)

class PromoCodeUsageSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    promo_code_text = serializers.CharField(source='promo_code.code', read_only=True)
    discount_applied_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = PromoCodeUsage
        fields = [
            'id', 'promo_code', 'promo_code_text', 'user', 'user_name',
            'subscription', 'discount_applied', 'discount_applied_formatted',
            'used_at'
        ]
    
    def get_discount_applied_formatted(self, obj):
        return f"${obj.discount_applied}"

class InMailCreditSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    credit_type_display = serializers.CharField(source='get_credit_type_display', read_only=True)
    expires_soon = serializers.SerializerMethodField()
    
    class Meta:
        model = InMailCredit
        fields = [
            'id', 'user', 'user_name', 'credit_type', 'credit_type_display',
            'amount', 'description', 'expires_at', 'expires_soon', 'is_used',
            'used_at', 'created_at'
        ]
    
    def get_expires_soon(self, obj):
        if obj.expires_at:
            from django.utils import timezone
            from datetime import timedelta
            return obj.expires_at <= timezone.now() + timedelta(days=7)
        return False

class PremiumAnalyticsSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    profile_growth_trend = serializers.SerializerMethodField()
    career_score_category = serializers.SerializerMethodField()
    
    class Meta:
        model = PremiumAnalytics
        fields = [
            'user', 'user_name', 'profile_views_last_90_days', 'profile_views_growth',
            'profile_growth_trend', 'search_appearances', 'connection_insights',
            'industry_insights', 'skill_insights', 'salary_insights',
            'job_market_competitiveness', 'career_opportunities_score',
            'career_score_category', 'skill_gaps', 'recommended_courses',
            'last_updated'
        ]
    
    def get_profile_growth_trend(self, obj):
        if obj.profile_views_growth > 10:
            return "🚀 Excellent Growth"
        elif obj.profile_views_growth > 0:
            return "📈 Growing"
        elif obj.profile_views_growth == 0:
            return "⚪ Stable"
        else:
            return "📉 Declining"
    
    def get_career_score_category(self, obj):
        score = obj.career_opportunities_score
        if score >= 80:
            return "🏆 Excellent"
        elif score >= 60:
            return "🥈 Good"
        elif score >= 40:
            return "🥉 Average"
        else:
            return "📊 Needs Improvement"

class SubscriptionUpgradeSerializer(serializers.Serializer):
    """Serializer for subscription upgrade/downgrade requests"""
    plan_id = serializers.IntegerField()
    billing_cycle = serializers.ChoiceField(choices=UserSubscription.BILLING_CYCLES)
    promo_code = serializers.CharField(required=False, allow_blank=True)
    
    def validate_plan_id(self, value):
        try:
            plan = SubscriptionPlan.objects.get(id=value, is_active=True)
            return value
        except SubscriptionPlan.DoesNotExist:
            raise serializers.ValidationError("Invalid subscription plan.")
    
    def validate_promo_code(self, value):
        if value:
            try:
                promo = PromoCode.objects.get(code=value)
                if not promo.is_valid:
                    raise serializers.ValidationError("Promo code is not valid or expired.")
                return value
            except PromoCode.DoesNotExist:
                raise serializers.ValidationError("Invalid promo code.")
        return value

class FeatureUsageSerializer(serializers.Serializer):
    """Serializer for tracking feature usage"""
    feature_code = serializers.CharField()
    metadata = serializers.JSONField(required=False)
    
    def validate_feature_code(self, value):
        try:
            PremiumFeature.objects.get(code=value, is_active=True)
            return value
        except PremiumFeature.DoesNotExist:
            raise serializers.ValidationError("Invalid feature code.")

class SubscriptionStatsSerializer(serializers.Serializer):
    """Serializer for subscription statistics"""
    total_subscribers = serializers.IntegerField()
    active_subscribers = serializers.IntegerField()
    trial_users = serializers.IntegerField()
    plan_distribution = serializers.DictField()
    monthly_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    churn_rate = serializers.FloatField()
    upgrade_rate = serializers.FloatField()
    average_ltv = serializers.DecimalField(max_digits=10, decimal_places=2)

class PremiumDashboardSerializer(serializers.Serializer):
    """Comprehensive premium dashboard data"""
    subscription = UserSubscriptionSerializer()
    usage_stats = serializers.DictField()
    premium_analytics = PremiumAnalyticsSerializer()
    recent_billing = BillingHistorySerializer(many=True)
    available_upgrades = SubscriptionPlanSerializer(many=True)
    feature_recommendations = serializers.ListField()
    savings_opportunities = serializers.DictField() 
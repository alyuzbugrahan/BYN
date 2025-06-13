from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
import uuid

User = get_user_model()

class SubscriptionPlan(models.Model):
    """
    Different subscription tiers with various features
    """
    PLAN_TYPES = (
        ('free', 'Free'),
        ('basic', 'LinkedIn Basic'),
        ('premium', 'LinkedIn Premium'),
        ('business', 'LinkedIn Business'),
        ('sales_navigator', 'Sales Navigator'),
        ('recruiter', 'LinkedIn Recruiter'),
    )
    
    name = models.CharField(max_length=100)
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPES, unique=True)
    description = models.TextField()
    
    # Pricing
    monthly_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    yearly_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    yearly_discount_percentage = models.FloatField(default=0.0)
    
    # Feature limits
    profile_views_per_month = models.IntegerField(default=5)  # -1 for unlimited
    inmails_per_month = models.IntegerField(default=0)
    search_results_per_search = models.IntegerField(default=100)
    advanced_search_filters = models.BooleanField(default=False)
    
    # Premium features
    can_see_who_viewed_profile = models.BooleanField(default=False)
    can_see_full_name_of_viewers = models.BooleanField(default=False)
    priority_customer_support = models.BooleanField(default=False)
    learning_access = models.BooleanField(default=False)
    insights_and_analytics = models.BooleanField(default=False)
    
    # Business features
    company_page_analytics = models.BooleanField(default=False)
    lead_generation_tools = models.BooleanField(default=False)
    competitor_insights = models.BooleanField(default=False)
    
    # Recruiter features
    recruiter_search_tools = models.BooleanField(default=False)
    talent_pipeline = models.BooleanField(default=False)
    advanced_reporting = models.BooleanField(default=False)
    
    is_active = models.BooleanField(default=True)
    display_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['display_order']
    
    def __str__(self):
        return f"{self.name} - ${self.monthly_price}/month"
    
    @property
    def yearly_savings(self):
        if self.yearly_price > 0:
            monthly_yearly = self.monthly_price * 12
            return monthly_yearly - self.yearly_price
        return Decimal('0.00')

class UserSubscription(models.Model):
    """
    User's subscription status and history
    """
    BILLING_CYCLES = (
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
        ('lifetime', 'Lifetime'),
    )
    
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
        ('paused', 'Paused'),
        ('pending', 'Pending'),
        ('trial', 'Trial'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='subscription')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    
    # Subscription details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    billing_cycle = models.CharField(max_length=10, choices=BILLING_CYCLES, default='monthly')
    
    # Dates
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(blank=True, null=True)
    trial_end_date = models.DateTimeField(blank=True, null=True)
    next_billing_date = models.DateTimeField(blank=True, null=True)
    
    # Usage tracking
    profile_views_used = models.IntegerField(default=0)
    inmails_used = models.IntegerField(default=0)
    last_usage_reset = models.DateTimeField(auto_now_add=True)
    
    # Payment info
    stripe_subscription_id = models.CharField(max_length=200, blank=True)
    stripe_customer_id = models.CharField(max_length=200, blank=True)
    auto_renew = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.plan.name} ({self.status})"
    
    @property
    def is_active(self):
        if self.status == 'active':
            return timezone.now() < self.end_date if self.end_date else True
        return False
    
    @property
    def days_remaining(self):
        if self.end_date:
            delta = self.end_date - timezone.now()
            return max(0, delta.days)
        return None
    
    @property
    def is_trial(self):
        return self.status == 'trial' and self.trial_end_date and timezone.now() < self.trial_end_date
    
    def reset_monthly_usage(self):
        """Reset monthly usage counters"""
        self.profile_views_used = 0
        self.inmails_used = 0
        self.last_usage_reset = timezone.now()
        self.save()
    
    def can_view_profile(self):
        """Check if user can view another profile"""
        if self.plan.profile_views_per_month == -1:  # Unlimited
            return True
        return self.profile_views_used < self.plan.profile_views_per_month
    
    def can_send_inmail(self):
        """Check if user can send InMail"""
        return self.inmails_used < self.plan.inmails_per_month

class PremiumFeature(models.Model):
    """
    Individual premium features that can be enabled/disabled
    """
    FEATURE_TYPES = (
        ('profile', 'Profile Features'),
        ('search', 'Search Features'),
        ('messaging', 'Messaging Features'),
        ('analytics', 'Analytics Features'),
        ('learning', 'Learning Features'),
        ('business', 'Business Features'),
    )
    
    name = models.CharField(max_length=100)
    feature_type = models.CharField(max_length=20, choices=FEATURE_TYPES)
    description = models.TextField()
    code = models.CharField(max_length=50, unique=True)  # For programmatic access
    
    # Feature availability by plan
    available_plans = models.ManyToManyField(SubscriptionPlan, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.feature_type})"

class UsageTracking(models.Model):
    """
    Track usage of premium features
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='usage_tracking')
    feature = models.ForeignKey(PremiumFeature, on_delete=models.CASCADE)
    usage_count = models.IntegerField(default=0)
    last_used = models.DateTimeField(auto_now=True)
    monthly_usage = models.IntegerField(default=0)
    yearly_usage = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ['user', 'feature']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.feature.name}: {self.usage_count}"

class BillingHistory(models.Model):
    """
    Track billing and payment history
    """
    TRANSACTION_TYPES = (
        ('payment', 'Payment'),
        ('refund', 'Refund'),
        ('credit', 'Credit'),
        ('proration', 'Proration'),
    )
    
    STATUS_CHOICES = (
        ('succeeded', 'Succeeded'),
        ('failed', 'Failed'),
        ('pending', 'Pending'),
        ('refunded', 'Refunded'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subscription = models.ForeignKey(UserSubscription, on_delete=models.CASCADE, related_name='billing_history')
    
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    
    # Payment processor info
    stripe_payment_intent_id = models.CharField(max_length=200, blank=True)
    stripe_invoice_id = models.CharField(max_length=200, blank=True)
    
    # Metadata
    description = models.TextField(blank=True)
    billing_period_start = models.DateTimeField(blank=True, null=True)
    billing_period_end = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.subscription.user.get_full_name()} - {self.transaction_type}: ${self.amount}"

class PromoCode(models.Model):
    """
    Promotional codes for discounts
    """
    DISCOUNT_TYPES = (
        ('percentage', 'Percentage'),
        ('fixed_amount', 'Fixed Amount'),
        ('free_trial', 'Free Trial Extension'),
    )
    
    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=15, choices=DISCOUNT_TYPES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Restrictions
    applicable_plans = models.ManyToManyField(SubscriptionPlan, blank=True)
    max_uses = models.IntegerField(blank=True, null=True)
    current_uses = models.IntegerField(default=0)
    
    # Dates
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    
    # Settings
    is_active = models.BooleanField(default=True)
    first_time_users_only = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Promo: {self.code} ({self.discount_type})"
    
    @property
    def is_valid(self):
        now = timezone.now()
        return (
            self.is_active and 
            self.valid_from <= now <= self.valid_until and
            (self.max_uses is None or self.current_uses < self.max_uses)
        )

class PromoCodeUsage(models.Model):
    """
    Track promo code usage
    """
    promo_code = models.ForeignKey(PromoCode, on_delete=models.CASCADE, related_name='usage_history')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subscription = models.ForeignKey(UserSubscription, on_delete=models.CASCADE)
    
    discount_applied = models.DecimalField(max_digits=10, decimal_places=2)
    used_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['promo_code', 'user']
    
    def __str__(self):
        return f"{self.user.get_full_name()} used {self.promo_code.code}"

class InMailCredit(models.Model):
    """
    Track InMail credits for premium users
    """
    CREDIT_TYPES = (
        ('monthly_allocation', 'Monthly Allocation'),
        ('purchased', 'Purchased'),
        ('bonus', 'Bonus Credit'),
        ('refund', 'Refunded Credit'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inmail_credits')
    credit_type = models.CharField(max_length=20, choices=CREDIT_TYPES)
    amount = models.IntegerField()
    description = models.CharField(max_length=200, blank=True)
    
    expires_at = models.DateTimeField(blank=True, null=True)
    is_used = models.BooleanField(default=False)
    used_at = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['expires_at', 'created_at']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.amount} InMail credits ({self.credit_type})"

class PremiumAnalytics(models.Model):
    """
    Premium analytics and insights for users
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='premium_analytics')
    
    # Profile analytics
    profile_views_last_90_days = models.IntegerField(default=0)
    profile_views_growth = models.FloatField(default=0.0)
    search_appearances = models.IntegerField(default=0)
    
    # Network insights
    connection_insights = models.JSONField(default=dict)
    industry_insights = models.JSONField(default=dict)
    skill_insights = models.JSONField(default=dict)
    
    # Job market insights
    salary_insights = models.JSONField(default=dict)
    job_market_competitiveness = models.FloatField(default=0.0)
    career_opportunities_score = models.FloatField(default=0.0)
    
    # Learning recommendations
    skill_gaps = models.JSONField(default=list)
    recommended_courses = models.JSONField(default=list)
    
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Premium Analytics for {self.user.get_full_name()}" 
"""
Subscription Models

This module defines the subscription-related models.
"""

from sqlalchemy import Column, String, Integer, Float, ForeignKey, DateTime, JSON, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.core.base import BaseModel, StatusMixin, MetadataMixin

class GPTSubscriptionPlan(BaseModel, StatusMixin, MetadataMixin):
    """Model for defining subscription plans and tiers."""
    __tablename__ = "gpt_subscription_plans"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)  # 'Free', 'Basic', 'Premium', 'Enterprise'
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    currency = Column(String, nullable=False, default='USD')
    billing_cycle = Column(String, nullable=False)  # 'monthly', 'yearly'
    
    # Feature limits
    monthly_token_limit = Column(Integer, nullable=True)
    monthly_request_limit = Column(Integer, nullable=True)
    max_contexts = Column(Integer, nullable=True)
    max_gpt_definitions = Column(Integer, nullable=True)
    
    # Features included
    features = Column(JSON, nullable=True)  # List of features included
    api_access = Column(Boolean, default=False)
    priority_support = Column(Boolean, default=False)
    custom_integrations = Column(Boolean, default=False)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=True)
    
    # Relationships
    subscriptions = relationship("CoreGPTSubscription", back_populates="plan")

    def dict(self):
        """Convert model to dictionary."""
        return {
            **super().dict(),
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "currency": self.currency,
            "billing_cycle": self.billing_cycle,
            "monthly_token_limit": self.monthly_token_limit,
            "monthly_request_limit": self.monthly_request_limit,
            "max_contexts": self.max_contexts,
            "max_gpt_definitions": self.max_gpt_definitions,
            "features": self.features,
            "api_access": self.api_access,
            "priority_support": self.priority_support,
            "custom_integrations": self.custom_integrations,
            "is_active": self.is_active,
            "is_public": self.is_public
        }

class CoreGPTSubscription(BaseModel, StatusMixin, MetadataMixin):
    """Model for storing GPT subscription information."""
    __tablename__ = "gpt_subscriptions"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    plan_id = Column(Integer, ForeignKey("gpt_subscription_plans.id"), nullable=False)
    subscription_type = Column(String, nullable=False)  # 'free', 'pro', 'enterprise'
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    auto_renew = Column(Boolean, default=True)
    
    # Usage limits
    monthly_token_limit = Column(Integer, nullable=True)
    monthly_request_limit = Column(Integer, nullable=True)
    current_month_tokens = Column(Integer, default=0)
    current_month_requests = Column(Integer, default=0)
    
    # Billing information
    billing_cycle = Column(String, nullable=False)  # 'monthly', 'yearly'
    price = Column(Float, nullable=False)
    currency = Column(String, nullable=False, default='USD')
    
    # Relationships
    user = relationship("app.models.core.user.User", back_populates="gpt_subscriptions")
    plan = relationship("GPTSubscriptionPlan", back_populates="subscriptions")
    usage_history = relationship("CoreGPTUsageHistory", back_populates="subscription")
    usage_metrics = relationship("GPTSubscriptionUsage", back_populates="subscription")
    billing_cycles = relationship("GPTSubscriptionBilling", back_populates="subscription")
    payments = relationship("GPTSubscriptionPayment", back_populates="subscription")
    invoices = relationship("GPTSubscriptionInvoice", back_populates="subscription")
    refunds = relationship("GPTSubscriptionRefund", back_populates="subscription")
    # shared_with = relationship("app.models.core.user.User", secondary="gpt_sharing", back_populates="shared_gpts")

    def dict(self):
        """Convert model to dictionary."""
        return {
            **super().dict(),
            "id": self.id,
            "user_id": self.user_id,
            "plan_id": self.plan_id,
            "subscription_type": self.subscription_type,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "auto_renew": self.auto_renew,
            "monthly_token_limit": self.monthly_token_limit,
            "monthly_request_limit": self.monthly_request_limit,
            "current_month_tokens": self.current_month_tokens,
            "current_month_requests": self.current_month_requests,
            "billing_cycle": self.billing_cycle,
            "price": self.price,
            "currency": self.currency
        }

class CoreGPTUsageHistory(BaseModel, MetadataMixin):
    """Model for tracking GPT usage history."""
    __tablename__ = "gpt_usage_history"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    subscription_id = Column(Integer, ForeignKey("gpt_subscriptions.id"), nullable=False)
    interaction_type = Column(String, nullable=False)  # API call, function call, etc.
    details = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationships
    subscription = relationship("CoreGPTSubscription", back_populates="usage_history")

    def dict(self):
        """Convert model to dictionary."""
        return {
            **super().dict(),
            "id": self.id,
            "subscription_id": self.subscription_id,
            "interaction_type": self.interaction_type,
            "details": self.details,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }

class GPTSubscriptionUsage(BaseModel, MetadataMixin):
    """Model for tracking detailed subscription usage metrics."""
    __tablename__ = "gpt_subscription_usage"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    subscription_id = Column(Integer, ForeignKey("gpt_subscriptions.id"), nullable=False)
    billing_period_start = Column(DateTime, nullable=False)
    billing_period_end = Column(DateTime, nullable=False)
    
    # Usage metrics
    tokens_used = Column(Integer, default=0)
    requests_made = Column(Integer, default=0)
    api_calls = Column(Integer, default=0)
    function_calls = Column(Integer, default=0)
    
    # Cost tracking
    cost_per_token = Column(Float, nullable=True)
    total_cost = Column(Float, default=0.0)
    currency = Column(String, nullable=False, default='USD')
    
    # Limits and overages
    token_limit = Column(Integer, nullable=True)
    request_limit = Column(Integer, nullable=True)
    tokens_over_limit = Column(Integer, default=0)
    requests_over_limit = Column(Integer, default=0)
    
    # Metadata
    usage_details = Column(JSON, nullable=True)  # Detailed breakdown
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    subscription = relationship("CoreGPTSubscription", back_populates="usage_metrics")

    def dict(self):
        """Convert model to dictionary."""
        return {
            **super().dict(),
            "subscription_id": self.subscription_id,
            "billing_period_start": self.billing_period_start.isoformat() if self.billing_period_start else None,
            "billing_period_end": self.billing_period_end.isoformat() if self.billing_period_end else None,
            "tokens_used": self.tokens_used,
            "requests_made": self.requests_made,
            "api_calls": self.api_calls,
            "function_calls": self.function_calls,
            "cost_per_token": self.cost_per_token,
            "total_cost": self.total_cost,
            "currency": self.currency,
            "token_limit": self.token_limit,
            "request_limit": self.request_limit,
            "tokens_over_limit": self.tokens_over_limit,
            "requests_over_limit": self.requests_over_limit,
            "usage_details": self.usage_details,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class GPTSubscriptionBilling(BaseModel, StatusMixin, MetadataMixin):
    """Model for handling subscription billing cycles."""
    __tablename__ = "gpt_subscription_billing"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    subscription_id = Column(Integer, ForeignKey("gpt_subscriptions.id"), nullable=False)
    billing_cycle_start = Column(DateTime, nullable=False)
    billing_cycle_end = Column(DateTime, nullable=False)
    
    # Billing information
    amount = Column(Float, nullable=False)
    currency = Column(String, nullable=False, default='USD')
    status = Column(String, nullable=False, default='pending')  # pending, paid, overdue, cancelled
    
    # Invoice details
    invoice_number = Column(String, nullable=True)
    invoice_date = Column(DateTime, nullable=True)
    due_date = Column(DateTime, nullable=False)
    paid_date = Column(DateTime, nullable=True)
    
    # Usage-based billing
    base_amount = Column(Float, nullable=False)
    usage_amount = Column(Float, default=0.0)
    overage_amount = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)
    
    # Metadata
    billing_details = Column(JSON, nullable=True)  # Detailed breakdown
    notes = Column(Text, nullable=True)
    
    # Relationships
    subscription = relationship("CoreGPTSubscription", back_populates="billing_cycles")
    payments = relationship("GPTSubscriptionPayment", back_populates="billing_cycle")
    invoices = relationship("GPTSubscriptionInvoice", back_populates="billing_cycle")

    def dict(self):
        """Convert model to dictionary."""
        return {
            **super().dict(),
            "subscription_id": self.subscription_id,
            "billing_cycle_start": self.billing_cycle_start.isoformat() if self.billing_cycle_start else None,
            "billing_cycle_end": self.billing_cycle_end.isoformat() if self.billing_cycle_end else None,
            "amount": self.amount,
            "currency": self.currency,
            "status": self.status,
            "invoice_number": self.invoice_number,
            "invoice_date": self.invoice_date.isoformat() if self.invoice_date else None,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "paid_date": self.paid_date.isoformat() if self.paid_date else None,
            "base_amount": self.base_amount,
            "usage_amount": self.usage_amount,
            "overage_amount": self.overage_amount,
            "discount_amount": self.discount_amount,
            "billing_details": self.billing_details,
            "notes": self.notes
        }

class GPTSubscriptionPayment(BaseModel, StatusMixin, MetadataMixin):
    """Model for tracking subscription payments."""
    __tablename__ = "gpt_subscription_payments"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    billing_cycle_id = Column(Integer, ForeignKey("gpt_subscription_billing.id"), nullable=False)
    subscription_id = Column(Integer, ForeignKey("gpt_subscriptions.id"), nullable=False)
    
    # Payment information
    amount = Column(Float, nullable=False)
    currency = Column(String, nullable=False, default='USD')
    payment_method = Column(String, nullable=False)  # 'credit_card', 'paypal', 'bank_transfer', etc.
    status = Column(String, nullable=False, default='pending')  # pending, processing, completed, failed, refunded
    
    # Transaction details
    transaction_id = Column(String, nullable=True)  # External payment processor ID
    gateway_response = Column(JSON, nullable=True)  # Response from payment gateway
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    payment_date = Column(DateTime, nullable=True)
    processed_at = Column(DateTime, nullable=True)
    
    # Metadata
    payment_details = Column(JSON, nullable=True)  # Additional payment information
    notes = Column(Text, nullable=True)
    
    # Relationships
    billing_cycle = relationship("GPTSubscriptionBilling", back_populates="payments")
    subscription = relationship("CoreGPTSubscription", back_populates="payments")
    refunds = relationship("GPTSubscriptionRefund", back_populates="payment")

    def dict(self):
        """Convert model to dictionary."""
        return {
            **super().dict(),
            "id": self.id,
            "billing_cycle_id": self.billing_cycle_id,
            "subscription_id": self.subscription_id,
            "amount": self.amount,
            "currency": self.currency,
            "payment_method": self.payment_method,
            "status": self.status,
            "transaction_id": self.transaction_id,
            "gateway_response": self.gateway_response,
            "error_message": self.error_message,
            "payment_date": self.payment_date.isoformat() if self.payment_date else None,
            "processed_at": self.processed_at.isoformat() if self.processed_at else None,
            "payment_details": self.payment_details,
            "notes": self.notes
        }

class GPTSubscriptionInvoice(BaseModel, StatusMixin, MetadataMixin):
    """Model for generating and storing subscription invoices."""
    __tablename__ = "gpt_subscription_invoices"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    billing_cycle_id = Column(Integer, ForeignKey("gpt_subscription_billing.id"), nullable=False)
    subscription_id = Column(Integer, ForeignKey("gpt_subscriptions.id"), nullable=False)
    
    # Invoice information
    invoice_number = Column(String, nullable=False, unique=True)
    invoice_date = Column(DateTime, nullable=False)
    due_date = Column(DateTime, nullable=False)
    status = Column(String, nullable=False, default='draft')  # draft, sent, paid, overdue, cancelled
    
    # Amounts
    subtotal = Column(Float, nullable=False)
    tax_amount = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)
    total_amount = Column(Float, nullable=False)
    currency = Column(String, nullable=False, default='USD')
    
    # Customer information
    customer_name = Column(String, nullable=True)
    customer_email = Column(String, nullable=True)
    billing_address = Column(JSON, nullable=True)
    
    # Invoice items
    line_items = Column(JSON, nullable=True)  # Array of invoice line items
    notes = Column(Text, nullable=True)
    terms = Column(Text, nullable=True)
    
    # Timestamps
    sent_at = Column(DateTime, nullable=True)
    paid_at = Column(DateTime, nullable=True)
    
    # Relationships
    billing_cycle = relationship("GPTSubscriptionBilling", back_populates="invoices")
    subscription = relationship("CoreGPTSubscription", back_populates="invoices")

    def dict(self):
        """Convert model to dictionary."""
        return {
            **super().dict(),
            "billing_cycle_id": self.billing_cycle_id,
            "subscription_id": self.subscription_id,
            "invoice_number": self.invoice_number,
            "invoice_date": self.invoice_date.isoformat() if self.invoice_date else None,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "status": self.status,
            "subtotal": self.subtotal,
            "tax_amount": self.tax_amount,
            "discount_amount": self.discount_amount,
            "total_amount": self.total_amount,
            "currency": self.currency,
            "customer_name": self.customer_name,
            "customer_email": self.customer_email,
            "billing_address": self.billing_address,
            "line_items": self.line_items,
            "notes": self.notes,
            "terms": self.terms,
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
            "paid_at": self.paid_at.isoformat() if self.paid_at else None
        }

class GPTSubscriptionRefund(BaseModel, StatusMixin, MetadataMixin):
    """Model for handling subscription refunds and credits."""
    __tablename__ = "gpt_subscription_refunds"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    payment_id = Column(Integer, ForeignKey("gpt_subscription_payments.id"), nullable=False)
    subscription_id = Column(Integer, ForeignKey("gpt_subscriptions.id"), nullable=False)
    
    # Refund information
    refund_amount = Column(Float, nullable=False)
    currency = Column(String, nullable=False, default='USD')
    refund_type = Column(String, nullable=False)  # 'full', 'partial', 'credit'
    reason = Column(String, nullable=False)  # 'customer_request', 'billing_error', 'service_issue', etc.
    
    # Processing details
    status = Column(String, nullable=False, default='pending')  # pending, processing, completed, failed
    refund_method = Column(String, nullable=True)  # 'original_payment_method', 'credit', 'bank_transfer'
    transaction_id = Column(String, nullable=True)  # External refund transaction ID
    
    # Timestamps
    requested_at = Column(DateTime, nullable=False)
    processed_at = Column(DateTime, nullable=True)
    
    # Metadata
    refund_details = Column(JSON, nullable=True)  # Additional refund information
    notes = Column(Text, nullable=True)
    processed_by = Column(String, nullable=True)  # User who processed the refund
    
    # Relationships
    payment = relationship("GPTSubscriptionPayment", back_populates="refunds")
    subscription = relationship("CoreGPTSubscription", back_populates="refunds")

    def dict(self):
        """Convert model to dictionary."""
        return {
            **super().dict(),
            "id": self.id,
            "payment_id": self.payment_id,
            "subscription_id": self.subscription_id,
            "refund_amount": self.refund_amount,
            "currency": self.currency,
            "refund_type": self.refund_type,
            "reason": self.reason,
            "status": self.status,
            "refund_method": self.refund_method,
            "transaction_id": self.transaction_id,
            "requested_at": self.requested_at.isoformat() if self.requested_at else None,
            "processed_at": self.processed_at.isoformat() if self.processed_at else None,
            "refund_details": self.refund_details,
            "notes": self.notes,
            "processed_by": self.processed_by
        } 
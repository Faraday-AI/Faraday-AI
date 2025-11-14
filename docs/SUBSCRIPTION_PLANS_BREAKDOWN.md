# Subscription Plans Breakdown

**Date:** November 13, 2025  
**Status:** Current Implementation

---

## Overview

Faraday AI offers subscription plans for AI-powered features and platform access. Plans are structured to support individual teachers, schools, and districts.

---

## Subscription Tiers

### 1. **FREE Tier**
- **Price:** $0/month
- **Target:** Individual teachers, trial users
- **Status:** Available (defined in code)

### 2. **BASIC Tier**
- **Price:** $29.99/month
- **Billing Cycle:** Monthly
- **Target:** Individual teachers, small schools
- **Features:**
  - Basic AI features
  - Basic analysis
  - Standard reports
  - Limited AI-powered widgets
  - Basic dashboard access

### 3. **PROFESSIONAL Tier**
- **Price:** $79.99/month
- **Billing Cycle:** Monthly
- **Target:** Schools, departments, multiple teachers
- **Features:**
  - Professional AI features
  - Advanced analysis
  - Custom reports
  - Priority support
  - Enhanced AI-powered widgets
  - Full dashboard access
  - API access (if enabled)

### 4. **ENTERPRISE Tier**
- **Price:** $199.99/month
- **Billing Cycle:** Monthly
- **Target:** Districts, large organizations
- **Features:**
  - Full AI suite
  - Custom integration support
  - Dedicated support
  - Unlimited AI-powered widgets
  - Advanced analytics
  - API access
  - Custom integrations
  - White-label options (if available)

### 5. **CUSTOM Tier**
- **Price:** Custom pricing
- **Billing Cycle:** Negotiable
- **Target:** Large districts, special requirements
- **Features:**
  - Fully customized feature set
  - Custom integrations
  - Dedicated account manager
  - SLA guarantees
  - Custom billing arrangements

---

## Feature Breakdown by Tier

### AI Features

| Feature | FREE | BASIC | PROFESSIONAL | ENTERPRISE | CUSTOM |
|---------|------|-------|--------------|------------|--------|
| **AI-Powered Widgets** | Limited | Basic | Advanced | Unlimited | Custom |
| **AI Lesson Planning** | ❌ | ✅ Basic | ✅ Advanced | ✅ Full Suite | ✅ Custom |
| **AI Student Analysis** | ❌ | ✅ Basic | ✅ Advanced | ✅ Full Suite | ✅ Custom |
| **AI Safety Reports** | ❌ | ✅ Basic | ✅ Advanced | ✅ Full Suite | ✅ Custom |
| **AI Recommendations** | ❌ | ✅ Basic | ✅ Advanced | ✅ Full Suite | ✅ Custom |
| **OpenAI Integration** | ❌ | ✅ Limited | ✅ Full | ✅ Full + Custom | ✅ Custom |
| **Microsoft Integration** | ❌ | ✅ Basic | ✅ Full | ✅ Full + Custom | ✅ Custom |
| **LMS Integration** | ❌ | ❌ | ✅ Basic | ✅ Full (All 6 LMS) | ✅ Custom |

### Usage Limits

| Limit | FREE | BASIC | PROFESSIONAL | ENTERPRISE | CUSTOM |
|-------|------|-------|--------------|------------|--------|
| **Monthly Token Limit** | 0 | Limited | Higher | Unlimited | Custom |
| **Monthly Request Limit** | 0 | Limited | Higher | Unlimited | Custom |
| **Max Contexts** | 0 | Limited | Higher | Unlimited | Custom |
| **Max GPT Definitions** | 0 | Limited | Higher | Unlimited | Custom |

### Platform Features

| Feature | FREE | BASIC | PROFESSIONAL | ENTERPRISE | CUSTOM |
|---------|------|-------|--------------|------------|--------|
| **Dashboard Access** | ✅ Basic | ✅ Full | ✅ Full | ✅ Full + Custom | ✅ Custom |
| **Student Management** | ✅ Basic | ✅ Full | ✅ Full | ✅ Full | ✅ Custom |
| **Grade Management** | ✅ Basic | ✅ Full | ✅ Full | ✅ Full | ✅ Custom |
| **Parent Communication** | ✅ Basic | ✅ Full | ✅ Full | ✅ Full | ✅ Custom |
| **Safety Reports** | ✅ Basic | ✅ Full | ✅ Advanced | ✅ Full Suite | ✅ Custom |
| **Analytics** | ❌ | ✅ Basic | ✅ Advanced | ✅ Full Suite | ✅ Custom |
| **API Access** | ❌ | ❌ | ✅ Limited | ✅ Full | ✅ Custom |
| **Priority Support** | ❌ | ❌ | ✅ | ✅ | ✅ |
| **Custom Integrations** | ❌ | ❌ | ❌ | ✅ | ✅ |
| **Dedicated Support** | ❌ | ❌ | ❌ | ✅ | ✅ |

### Integration Features

| Integration | FREE | BASIC | PROFESSIONAL | ENTERPRISE | CUSTOM |
|-------------|------|-------|--------------|------------|--------|
| **Microsoft/Azure AD** | ❌ | ✅ Basic | ✅ Full | ✅ Full + Custom | ✅ Custom |
| **Microsoft Calendar** | ❌ | ✅ Basic | ✅ Full | ✅ Full + Custom | ✅ Custom |
| **Canvas LMS** | ❌ | ❌ | ✅ | ✅ | ✅ |
| **Google Classroom** | ❌ | ❌ | ✅ | ✅ | ✅ |
| **PowerSchool** | ❌ | ❌ | ✅ | ✅ | ✅ |
| **Schoology** | ❌ | ❌ | ✅ | ✅ | ✅ |
| **Moodle** | ❌ | ❌ | ✅ | ✅ | ✅ |
| **Blackboard** | ❌ | ❌ | ✅ | ✅ | ✅ |
| **OpenAI AI Features** | ❌ | ✅ Limited | ✅ Full | ✅ Full + Custom | ✅ Custom |

---

## Billing Information

### Billing Cycles
- **Monthly:** Standard monthly billing
- **Yearly:** Annual billing (potential discounts available)
- **Custom:** Negotiable billing cycles for Enterprise/Custom tiers

### Payment Methods
- Credit Card
- PayPal
- Bank Transfer (Enterprise/Custom)
- Purchase Orders (Enterprise/Custom)

### Billing Features
- Automatic renewal (can be disabled)
- Usage-based billing (for overages)
- Invoice generation
- Payment tracking
- Refund processing

---

## Subscription Management

### Features Tracked
- **Usage Limits:** Monthly token and request limits
- **Current Usage:** Real-time tracking of tokens and requests used
- **Billing Cycles:** Start/end dates, renewal dates
- **Payment History:** All payments, invoices, refunds
- **Usage History:** Detailed logs of AI interactions

### Subscription Status
- **Active:** Subscription is active and in good standing
- **Pending:** Subscription is being set up
- **Suspended:** Payment issue or violation
- **Cancelled:** Subscription has been cancelled
- **Expired:** Subscription has expired

---

## Database Structure

### Tables
- `gpt_subscription_plans` - Plan definitions
- `gpt_subscriptions` - User subscriptions
- `gpt_usage_history` - Usage tracking
- `gpt_subscription_usage` - Detailed usage metrics
- `gpt_subscription_billing` - Billing cycles
- `gpt_subscription_payments` - Payment records
- `gpt_subscription_invoices` - Invoice generation
- `gpt_subscription_refunds` - Refund processing

---

## Current Implementation Status

### ✅ Implemented
- Subscription plan models
- Subscription tracking
- Usage tracking
- Billing cycle management
- Payment processing structure
- Invoice generation structure
- Refund processing structure

### 🔄 In Progress / Planned
- Actual payment gateway integration
- Subscription management UI
- Usage dashboard
- Automated billing
- Email notifications for billing events

---

## Pricing Summary

| Tier | Monthly Price | Yearly Price (Est.) | Best For |
|------|---------------|---------------------|----------|
| **FREE** | $0 | $0 | Trial, individual teachers |
| **BASIC** | $29.99 | ~$299.99 (save ~$60) | Individual teachers, small schools |
| **PROFESSIONAL** | $79.99 | ~$799.99 (save ~$160) | Schools, departments |
| **ENTERPRISE** | $199.99 | ~$1,999.99 (save ~$400) | Districts, large organizations |
| **CUSTOM** | Custom | Custom | Large districts, special needs |

---

## Notes

- **Yearly Pricing:** Estimated based on standard 2-month discount for annual plans
- **LMS Integration:** Available starting at Professional tier
- **OpenAI Features:** Available at all paid tiers with increasing limits
- **Microsoft Integration:** Available starting at Basic tier
- **Custom Integrations:** Available at Enterprise and Custom tiers

---

**Status:** Subscription system is implemented in the database. Pricing and features are configurable per plan.


# Email Deliverability Fix for Password Reset

## Problem
Password reset emails were being flagged as spam by email providers (Gmail, Yahoo, etc.).

## Root Causes Identified

1. **Missing email authentication protocols** (SPF, DKIM, DMARC)
2. **Missing priority and deliverability headers** in email messages
3. **Generic sender domain** without proper DNS configuration
4. **Using consumer email services** (Gmail) for transactional email

## Changes Made

### 1. Enhanced Email Headers (`backend/accounts/views.py`)
Added the following headers to improve deliverability:
- `X-Priority` and `X-MSMail-Priority`: Indicate transactional nature
- `X-Mailer`: Identify the application
- `Precedence: bulk`: Prevent auto-replies
- Kept existing `List-Unsubscribe` headers (trust signal for Gmail/Yahoo)

### 2. Email Configuration Improvements (`backend/config/settings/base.py`)
- Added `EMAIL_USE_SSL` setting
- Added `EMAIL_TIMEOUT` to prevent hanging connections
- Added `EMAIL_HOSTNAME` for proper SMTP HELO/EHLO handshake
- Added `EMAIL_SUBJECT_PREFIX` for consistency

### 3. Updated Environment Configuration (`.env.example`)
- Added documentation about SPF, DKIM, and DMARC requirements
- Added new email configuration options
- Clearer guidance on choosing email providers

## Critical Actions Required

To fully resolve the spam issue, you **must** configure the following DNS records for your sending domain:

### 1. SPF (Sender Policy Framework)
Add a TXT record to your domain's DNS:
```
v=spf1 include:your-smtp-provider.com ~all
```

For Gmail: `v=spf1 include:_spf.google.com ~all`
For Brevo: `v=spf1 include:spf.brevo.com ~all`

### 2. DKIM (DomainKeys Identified Mail)
- Generate DKIM keys in your email provider's dashboard (Brevo, Gmail, etc.)
- Add the TXT record provided by your provider to your DNS
- Enable DKIM signing in your email provider settings

### 3. DMARC (Domain-based Message Authentication)
Add a TXT record to your domain's DNS:
```
v=DMARC1; p=none; rua=mailto:dmarc@yourdomain.com
```

Start with `p=none` (monitoring mode), then move to `p=quarantine` and eventually `p=reject` once you're confident.

## Recommended Email Provider

**Use Brevo (formerly Sendinblue) instead of Gmail:**
- 300 free emails/day
- Built-in delivery logs and analytics
- SPF/DKIM configuration guidance
- Better deliverability reputation
- Designed for transactional email

Gmail limitations:
- ~500/day cap (with lower deliverability)
- No delivery logs
- Accepts messages then silently discards them
- Designed for personal use, not transactional email

## Testing Your Configuration

Use the included management command to test email delivery:
```bash
python manage.py check_email your-email@example.com
```

This will:
- Show your current email configuration
- Send a test email
- Display the SMTP conversation
- Guide you on where to check for the email

## Monitoring Deliverability

1. **Check your email provider's dashboard** for bounce rates and spam complaints
2. **Use tools like Gmail Postmaster Tools** to monitor your sender reputation
3. **Monitor DMARC reports** to see who is trying to send from your domain
4. **Regularly test with different email providers** (Gmail, Outlook, Yahoo)

## Additional Tips

1. **Use a dedicated sender domain** (e.g., `noreply@yourapp.com` instead of personal email)
2. **Keep sending volume consistent** - sudden spikes trigger spam filters
3. **Maintain low bounce rates** - remove invalid addresses from your list
4. **Include physical address** in footer (CAN-SPAM Act requirement)
5. **Keep content relevant** - avoid spam trigger words and excessive punctuation

## Configuration Example (Brevo)

Update your `.env` file:
```env
EMAIL_HOST=smtp-relay.brevo.com
EMAIL_PORT=587
EMAIL_USE_TLS=true
EMAIL_USE_SSL=false
EMAIL_HOST_USER=your@brevo-account.com
EMAIL_HOST_PASSWORD=your-brevo-smtp-key
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
EMAIL_TIMEOUT=30
EMAIL_HOSTNAME=yourdomain.com
SITE_URL=https://yourdomain.com
SUPPORT_EMAIL=support@yourdomain.com
```

Then configure SPF, DKIM, and DMARC for `yourdomain.com`.

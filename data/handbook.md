# Fernbrook Customer Support Handbook

*Internal reference for the Fernbrook Support team. Last reviewed: October 2026. Owner: Customer Success Operations.*

This handbook is the single source of truth for answering customer questions about Fernbrook plans, billing, support, integrations, security, and account administration. If a customer asks about something this handbook does not cover, do not guess: tell the customer you will confirm with the right team and route the question as described in §10.

---

## §1 About Fernbrook

Fernbrook is a workflow and project management platform for B2B teams. Customers use Fernbrook to plan projects on boards and timelines, automate recurring workflows, track requests from intake to delivery, and report on team workload. Fernbrook is a cloud-hosted SaaS product; customers access it through the web app at app.fernbrook.io and through the Fernbrook mobile apps for iOS and Android.

Every customer account is called a **workspace**. A workspace belongs to a single organization, has one subscription, and is managed by the workspace **Owner** and any **Admins** the Owner appoints (see §8.1).

Fernbrook is sold on three plans: **Starter**, **Team**, and **Enterprise**. Plan details are in §2.

---

## §2 Plans and Pricing

### §2.1 Starter

Starter is built for small teams getting organized for the first time.

- **Price:** $10 per seat per month.
- **Seat limit:** Starter workspaces can have up to 20 seats. Teams that need more than 20 seats must move to Team or Enterprise.
- **Included:** unlimited projects and boards, timeline view, basic workflow automations (up to 250 automation runs per month), file attachments up to 100 MB per file, and the Salesforce, Slack, and Jira integrations.
- **Support:** email support (see §5.1).

### §2.2 Team

Team is built for growing departments that need more automation and reporting. Team is sold in **seat bundles** rather than per seat:

| Team bundle | Price per month |
| --- | --- |
| Up to 25 seats | $500 |
| Up to 50 seats | $900 |
| Up to 100 seats | $1,600 |

- A Team workspace pays for the smallest bundle that covers its number of seats. For example, a workspace with 40 members is on the 50-seat bundle at $900 per month. Unused seats within a bundle are not refunded or credited.
- The largest Team bundle is 100 seats. Organizations that need more than 100 seats must move to Enterprise.
- **Included:** everything in Starter, plus advanced automations (up to 10,000 automation runs per month), workload and portfolio reporting, custom fields, guest access, and the HubSpot integration.
- **Support:** business-hours support (see §5.2).

### §2.3 Enterprise

Enterprise is built for organizations with advanced security, compliance, and scale requirements.

- **Price:** custom. Enterprise pricing is quoted by the Sales team based on seat count, contract length, and add-ons. Support agents must not quote Enterprise prices; route pricing questions to Sales (§10).
- **Seats:** no maximum.
- **Included:** everything in Team, plus SSO/SAML (§7.2), SCIM user provisioning, audit logs, unlimited automation runs, data residency options (US or EU hosting), and a named Customer Success Manager.
- **Support:** 24/7 priority support with a contractual SLA (see §5.3).

### §2.4 Plan comparison

| Feature | Starter | Team | Enterprise |
| --- | --- | --- | --- |
| Price | $10/seat/month | $500 / $900 / $1,600 per month (25 / 50 / 100 seats) | Custom |
| Max seats | 20 | 100 | No maximum |
| Automation runs per month | 250 | 10,000 | Unlimited |
| Salesforce, Slack, Jira integrations | Yes | Yes | Yes |
| HubSpot integration | No | Yes | Yes |
| Guest access | No | Yes | Yes |
| SSO / SAML | No | No | Yes |
| SCIM provisioning and audit logs | No | No | Yes |
| Uptime SLA | No | No | 99.9% |
| Support | Email | Business hours | 24/7 priority |

### §2.5 Billing cycles and payment

- Every plan can be billed **monthly** or **annually**. Annual plans are billed upfront for the full 12-month term at the same monthly rate listed above.
- Starter and Team are paid by credit card. Enterprise customers can pay by credit card, ACH, or wire transfer against an invoice with net-30 terms.
- All prices are in US dollars and exclude applicable taxes.
- Subscriptions renew automatically at the end of each term unless canceled before the renewal date.

---

## §3 Refunds, Credits, and Invoices

### §3.1 Refund policy

- **Annual plans** are refundable within **30 days** of the purchase date (or the renewal date, for a renewed annual term). Refunds within this window are **prorated**: the customer is refunded for the unused portion of the term.
- **After 30 days**, annual plans are **not refundable**. The subscription stays active until the end of the paid term.
- **Monthly plans** are not refundable. When a monthly plan is canceled, the workspace stays active until the end of the current billing period and is not charged again.
- Seats added mid-term (§4.1) follow the same policy as the subscription they were added to.

To process an eligible refund, the support agent files a Billing Request in the support console with the workspace ID and the purchase date. Refunds are returned to the original payment method within 5–10 business days.

### §3.2 Service credits

When a refund is not available (for example, a customer is more than 30 days into an annual term), Fernbrook may in some cases issue a **service credit** applied to the customer's next invoice. Service credits are discretionary and **require approval from the VP of Customer Success**. Support agents must never promise a credit; they can only offer to submit a credit request for review.

This approval requirement applies to every kind of service credit, including credits requested after an outage or SLA miss (§5.3).

### §3.3 Invoices and receipts

- Owners and Admins can download invoices and receipts under **Settings → Billing → Invoices**.
- Billing contact email, company name, address, and tax ID (VAT/GST) can be updated under **Settings → Billing → Billing details**. Changes apply to future invoices only.

### §3.4 Failed payments

If a card payment fails, Fernbrook retries the charge three times over 7 days and emails the workspace Owner after each attempt. If all retries fail, the workspace is switched to **read-only mode**: members can view and export data but cannot create or edit work. Updating the payment method and paying the outstanding balance restores full access immediately.

---

## §4 Seats and Plan Changes

### §4.1 Adding seats

- Seats can be **added at any time**. Owners and Admins add seats by inviting new members or under **Settings → Billing → Seats**.
- On **Starter**, each added seat is charged a prorated amount for the remainder of the current billing period, then $10 per seat per month going forward.
- On **Team**, adding members beyond the current bundle moves the workspace up to the next bundle (for example, from 25 to 50 seats). Moving up a bundle takes effect immediately, and the price difference is prorated for the remainder of the billing period.

### §4.2 Removing seats and downgrades

- **Downgrades take effect at renewal.** This includes removing seats on Starter, moving to a smaller Team bundle, and moving to a lower plan (for example, Team to Starter).
- Until the renewal date, the workspace keeps (and pays for) its current plan, bundle, and seat count. Downgrades do not generate refunds or credits for the remainder of the current term.
- Owners and Admins can schedule a downgrade under **Settings → Billing → Change plan**. A scheduled downgrade can be canceled any time before the renewal date.
- When downgrading to a plan without a feature (for example, Team to Starter loses HubSpot and guest access), those features are turned off at renewal. Data created with those features is kept.

### §4.3 Upgrading plans

- Upgrades from Starter to Team take effect immediately. The remaining Starter balance is prorated and applied to the first Team invoice.
- Upgrades to Enterprise are handled by Sales (§10) because Enterprise requires a custom quote and contract.

---

## §5 Support and Service Levels

### §5.1 Starter support

Starter customers get **email support** at support@fernbrook.io and access to the Fernbrook Help Center and community forum. Starter support requests are handled in the order received; there is no guaranteed response time.

### §5.2 Team support

Team customers get **business-hours support** by email and in-app chat, **Monday to Friday, 9:00 a.m. to 6:00 p.m. US Eastern Time**, excluding US federal holidays. The target first-response time for Team requests is one business day. Team plans do not include an uptime SLA or 24/7 support.

### §5.3 Enterprise support and SLA

Enterprise customers get **24/7 priority support** by email, in-app chat, and phone, plus a named Customer Success Manager.

**Uptime SLA:** Fernbrook commits to **99.9% monthly uptime** for Enterprise workspaces. Uptime is measured on the Fernbrook status page (status.fernbrook.io), excluding scheduled maintenance announced at least 72 hours in advance.

**First-response times by priority:**

| Priority | Definition | First response |
| --- | --- | --- |
| P1 – Critical | Fernbrook is down or unusable for the whole workspace | Within 1 hour, 24/7 |
| P2 – High | A core feature is broken with no workaround | Within 4 hours, 24/7 |
| P3 – Normal | A feature is impaired but a workaround exists | Within 1 business day |
| P4 – Low | Questions, how-to requests, feature requests | Within 2 business days |

If Fernbrook misses the uptime SLA in a given month, the Enterprise customer may request a service credit. Like all service credits, SLA credits require approval from the VP of Customer Success (§3.2).

### §5.4 Scheduled maintenance

Scheduled maintenance is announced on status.fernbrook.io and by email to workspace Owners at least 72 hours in advance, and usually takes place on Saturdays between 2:00 a.m. and 4:00 a.m. US Eastern Time.

---

## §6 Integrations

Fernbrook offers four native integrations: **Salesforce**, **Slack**, **Jira**, and **HubSpot**. Integrations are connected by an Owner or Admin under **Settings → Integrations**.

| Integration | Available on | What it does |
| --- | --- | --- |
| Salesforce | Starter, Team, Enterprise | Creates Fernbrook projects from closed-won opportunities and syncs project status back to the opportunity record. |
| Slack | Starter, Team, Enterprise | Sends task and project notifications to Slack channels and lets users create tasks from Slack messages. |
| Jira | Starter, Team, Enterprise | Two-way sync between Fernbrook tasks and Jira issues, including status, assignee, and comments. |
| HubSpot | **Team and Enterprise only** | Creates onboarding projects from HubSpot deals and syncs company and contact details into Fernbrook. |

**HubSpot is available only on Team and Enterprise (Team and above).** Starter workspaces must upgrade to Team to use it (§4.3).

These four are the only integrations Fernbrook supports. Support agents should not suggest that other tools are supported or "coming soon"; feature requests for new integrations can be logged as P4 requests and passed to the Product team.

---

## §7 Security and Compliance

### §7.1 Certifications and data protection

- Fernbrook is **SOC 2 Type II** certified. The audit is performed annually by an independent auditor. Customers can request the latest SOC 2 Type II report under NDA through their account team or security@fernbrook.io.
- Customer data is encrypted in transit (TLS 1.2 or higher) and at rest (AES-256).
- Two-factor authentication (2FA) is available on all plans, and Owners can require 2FA for every member of the workspace.

### §7.2 Single sign-on (SSO/SAML)

- **SSO via SAML 2.0 is available on Enterprise only.** Starter and Team workspaces cannot use SSO; they sign in with email and password (optionally with 2FA) or Google sign-in.
- Supported identity providers include Okta, Microsoft Entra ID (Azure AD), Google Workspace, and any SAML 2.0-compliant provider.
- Enterprise workspaces can also enable SCIM to automatically provision and deprovision users from their identity provider.

### §7.3 Data retention and deletion

- While a subscription is active, Fernbrook retains workspace data for as long as the customer keeps it.
- **After cancellation, workspace data is retained for 90 days.** During those 90 days the Owner can reactivate the workspace or export its data (§8.4).
- After 90 days, the workspace and all of its data are **permanently deleted** and cannot be recovered by Fernbrook Support or Engineering.
- Owners who want data deleted sooner can request immediate deletion from security@fernbrook.io.

---

## §8 Account Management

### §8.1 Roles

| Role | Can do |
| --- | --- |
| Owner | Everything, including billing, plan changes, cancellation, and ownership transfer. Each workspace has exactly one Owner. |
| Admin | Manage members, seats, integrations, and workspace settings. Admins can view invoices but cannot cancel the subscription or transfer ownership. |
| Member | Create and edit projects and tasks they have access to. |
| Guest (Team and Enterprise) | Access only the specific projects they are invited to. Guests do not use a paid seat. |

### §8.2 Transferring ownership

The current Owner can transfer ownership to any Admin under **Settings → Workspace → Transfer ownership**. If the Owner has left the company and cannot be reached, an Admin can request a transfer by emailing support@fernbrook.io from a company email address; Support verifies the request with a second Admin before completing it.

### §8.3 Canceling a subscription

- Only the Owner can cancel, under **Settings → Billing → Cancel subscription**.
- Monthly plans stay active until the end of the current billing period. Annual plans stay active until the end of the paid term, unless the customer is within the 30-day refund window and requests a prorated refund (§3.1).
- After the subscription ends, the data retention rules in §7.3 apply.

### §8.4 Exporting data

Owners and Admins can export all workspace data at any time as CSV or JSON under **Settings → Workspace → Export data**. Exports include projects, tasks, comments, custom fields, and attachment links. Large exports are prepared in the background and emailed as a download link that stays valid for 7 days.

### §8.5 Renaming or changing the workspace URL

Owners and Admins can rename the workspace and change its URL (for example, app.fernbrook.io/acme) under **Settings → Workspace → General**. Old URLs redirect for 30 days.

---

## §9 Troubleshooting

### §9.1 An invited user didn't receive the invitation email

1. Confirm the email address in **Settings → Members → Pending invitations**.
2. Ask the user to check spam and quarantine folders, and ask their IT team to allow mail from @fernbrook.io.
3. Resend the invitation, or copy the invite link from the pending invitation and share it directly.

### §9.2 Slack notifications stopped arriving

1. Check **Settings → Integrations → Slack** to confirm the connection is still active. Connections break if the Slack user who authorized the integration is deactivated.
2. Reconnect Slack with an active Slack admin account.
3. Confirm the Slack channel is still mapped in the project's notification settings.

### §9.3 Jira issues aren't syncing

1. Confirm the Jira project is mapped under **Settings → Integrations → Jira**.
2. Check that the Jira account used for the connection still has permission to the Jira project.
3. Status sync only works for statuses that are mapped. Unmapped Jira statuses show a warning icon in the mapping screen.
4. Sync runs every 5 minutes; use **Sync now** to trigger it manually.

### §9.4 Salesforce opportunities aren't creating projects

1. Confirm the trigger stage (by default, "Closed Won") under **Settings → Integrations → Salesforce**.
2. Check that the Salesforce integration user has read access to the Opportunity object.
3. Field mapping errors are listed in the integration's **Activity log**.

### §9.5 SSO login loop or "SAML response invalid" error (Enterprise)

1. Confirm the certificate in the identity provider matches the certificate in **Settings → Security → SSO**. Expired certificates are the most common cause.
2. Confirm the user's email in the identity provider matches their Fernbrook email.
3. Owners can always sign in with their password through the SSO bypass link in the SSO settings to fix configuration errors.

### §9.6 A user lost access to their 2FA device

The user should first try one of their backup codes. If they have none, a workspace Owner or Admin can reset the user's 2FA under **Settings → Members → [user] → Reset 2FA**. Support cannot reset 2FA for a user without a request from the workspace Owner or an Admin.

### §9.7 Boards are loading slowly

1. Check status.fernbrook.io for active incidents.
2. Ask the user to clear their browser cache or try another supported browser (latest Chrome, Edge, Firefox, or Safari).
3. Boards with more than 5,000 visible tasks load more slowly; suggest filtering or archiving completed tasks.

### §9.8 The workspace is in read-only mode

Read-only mode almost always means a failed payment (§3.4). The Owner or an Admin should update the payment method under **Settings → Billing**. Access is restored as soon as the outstanding balance is paid.

---

## §10 Escalation and Contacts

| Topic | Route to |
| --- | --- |
| Enterprise pricing, quotes, contracts, and upgrades to Enterprise | Sales: sales@fernbrook.io |
| Security questionnaires, SOC 2 report requests, data deletion requests | Security: security@fernbrook.io |
| Refund processing | Billing Request in the support console (§3.1) |
| Service credit requests | Credit request for review by the VP of Customer Success (§3.2) |
| Bugs and outages | Engineering on-call through the support console |
| Questions this handbook does not answer | Tell the customer you will confirm, then post in the #support-escalations channel |

When a customer asks about a product capability, policy, or price that is not documented in this handbook, the correct answer is that you don't have that information and will check with the right team. Never invent features, prices, integrations, certifications, or policies.

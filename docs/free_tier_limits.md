# Free-tier access and refreshing WhatsApp tokens

Documentation review: **2026-10-26**. This is a dated guide, not a live quota feed.
Check the linked official pages and your dashboards before starting. Meta's full
get-started page required login during review, so account-specific details and
its current dashboard labels must be confirmed in your own account.

## Gemini: check your actual quota

- [Pricing and which models have a free tier](https://ai.google.dev/gemini-api/docs/pricing)
- [Rate limits](https://ai.google.dev/gemini-api/docs/rate-limits)
- [Your AI Studio dashboard](https://aistudio.google.com/)
- [Region and age eligibility](https://ai.google.dev/gemini-api/docs/available-regions)
- [Billing tiers](https://ai.google.dev/gemini-api/docs/billing)
- [Function calling](https://ai.google.dev/gemini-api/docs/function-calling)

There is no universally correct fixed “free requests per minute” number. Limits
vary by model, project, tier and account. Check requests/minute, tokens/minute and
requests/day in AI Studio. Google's documented daily quota reset is midnight
Pacific time; minute quotas need a shorter wait. Another API key on the same
project does not create more quota.

Select a free-tier text model that supports function calling, and put its API
ID in `GEMINI_MODEL`. The course uses the generateContent REST endpoint. Confirm
compatibility with the provider's current API docs when selecting a new model.
Each agent turn can make up to `MAX_STEPS` model calls. A “single chat message” is
not necessarily one API request. Do not raise the limit to work around a problem.

Remain on the free tier and do not enable billing for the course. Free-tier inputs
and outputs may be used to improve Google's products according to its terms;
use fictional data. If account eligibility blocks access, do not pay to finish:
you can study the examples, but a live agent requires eligible provider access.

## WhatsApp: three different tokens/secrets

| Setting | Meaning |
| --- | --- |
| `WHATSAPP_ACCESS_TOKEN` | Authorises outbound messages; temporary test tokens expire |
| `WHATSAPP_APP_SECRET` | Verifies incoming webhook signatures; belongs to your Meta app |
| `WHATSAPP_VERIFY_TOKEN` | Your own chosen string used for webhook setup verification |

Temporary dashboard test access tokens are commonly issued for about **24 hours**.
Use the actual expiry displayed by Meta as authoritative; lifetime depends on the
token type and current flow. The access-token lifetime is **not** the 24-hour
customer-service messaging window.

### Refresh a temporary token

1. Open your app in [Meta for Developers](https://developers.facebook.com/).
2. Open its WhatsApp API Setup / testing section.
3. Generate or refresh the temporary access token using the dashboard's current flow.
4. Replace only `WHATSAPP_ACCESS_TOKEN` in the local `.env` file.
5. Stop the Python server with Ctrl+C and start `python whatsapp_server.py` again.
6. If the tunnel also restarted, update the callback URL in Meta.
7. Send a fresh message from your verified WhatsApp recipient to the test number.

Do not paste the token into a commit, public issue, browser URL, or screenshot.
Do not generate a paid/production number or enable billing to follow these lessons.

## Testing and messaging restrictions

Use Meta's official test number and recipient-verification flow. Test recipient
limits, account requirements and regional availability are controlled by Meta.
Do not assume a test number is a permanent public bot or can message anyone.
The demo only responds to the configured personal sender. Start the conversation
from your phone; outbound templates/broadcasts are outside this course.

- [Official WhatsApp developer hub](https://whatsappbusiness.com/developers/developer-hub/)
- [Meta get started (may require login)](https://developers.facebook.com/documentation/business-messaging/whatsapp/get-started)
- [Meta webhook verification/signature reference](https://whatsapp.github.io/WhatsApp-Nodejs-SDK/api-reference/webhooks/start/)
- [Cloudflare temporary tunnels](https://developers.cloudflare.com/tunnel/get-started/quick-tunnels/)

Your computer, Python server, tunnel and internet connection must remain running.
A quick tunnel URL is temporary. This is free learning infrastructure, not an
always-online deployment. Provider accounts and free quotas are external
prerequisites, not something this repository can guarantee.

## Maintainer release checklist

Before publishing a cohort/course update, use fresh eligible accounts to confirm:
model free-tier availability and tool calls, Meta's current token expiry/refresh
flow, recipient setup, webhook subscription, and a complete two-way chat without
billing. Update this date after actually reviewing the linked docs. Do not claim
a live provider run was performed based only on simulated tests.

# Django Ecommerce Backend

## Project Overview

This project is an ecommerce backend built with Django, Django REST Framework, and PostgreSQL. It includes a custom user model and Razorpay payment-gateway integration. Razorpay Checkout is used to initiate the customer payment experience, while backend endpoints are intended to create payment orders and verify payment details.

The project also uses Razorpay webhooks to receive server-to-server payment event notifications. During local development, ngrok can expose the local Django server through a temporary public HTTPS URL so Razorpay can reach the webhook endpoint.

## Technology Stack

- Python
- Django
- Django REST Framework
- PostgreSQL
- Razorpay Python SDK
- `python-dotenv`
- ngrok (for local webhook testing)

## Main Capabilities

- Custom user model: `accounts.MyUser`
- Django REST Framework API structure
- PostgreSQL database
- Razorpay order creation endpoint
- Razorpay Checkout frontend
- Payment signature verification endpoint
- Razorpay webhook endpoint for asynchronous payment events
- ngrok-based local webhook testing

## Project Structure

```text
Ecommrce/
├── accounts/
│   ├── models.py
│   └── ...
├──products/
│   ├── views.py
│   ├── urls.py
│   └── ...
|____order/
│   ├── views.py
│   ├── urls.py
│   └── ...
├── templates/
│   └── payment.html
├── manage.py
├── requirements.txt
|── .env
|___gitignore
|___postman_collection
```

## Prerequisites

Install:

- Python
- PostgreSQL
- Git (optional)
- An ngrok account and ngrok CLI for local webhook testing
- A Razorpay account with Test Mode API keys

## Local Setup

### 1. Open the project directory

If the repository is already on your machine, open a terminal in the project directory. Otherwise, clone the repository and enter it:

```bash
git clone <https://github.com/pandeypriya18/E-Commerce_Stripe_Api>
cd Ecommrce
```

### 2. Create and activate a virtual environment

On Windows:

```bash
python -m venv env
env\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure PostgreSQL

Create the database and configure `DATABASES` in `settings.py` with the local database name, username, password, host, and port. For example, the database name used in development may be `ecommerce`.

Do not commit real database credentials to version control.

### 5. Configure environment variables

Create a `.env` file in the project root. Use the variable names that `settings.py` reads:

```env
RAZORPAY_KEY_ID=your_razorpay_test_key_id
RAZORPAY_KEY_SECRET=your_razorpay_test_key_secret
RAZORPAY_WEBHOOK_SECRET=your_webhook_signing_secret
```

Load the variables in Django settings, for example:

```python
import os
from dotenv import load_dotenv

load_dotenv()

RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")
RAZORPAY_WEBHOOK_SECRET = os.getenv("RAZORPAY_WEBHOOK_SECRET")
```

`RAZORPAY_WEBHOOK_SECRET` is the secret configured for the webhook in the Razorpay Dashboard. It is separate from the Razorpay API key secret and must be kept private.

Add `.env` to `.gitignore`:

```gitignore
.env
env/
__pycache__/
*.py[cod]
```

Never commit live API keys, webhook secrets, or database passwords.

### 6. Run database migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Create an admin account

```bash
python manage.py createsuperuser
```

### 8. Start Django

```bash
python manage.py runserver
```

The local development server is normally available at:

`http://127.0.0.1:8000/`

## Razorpay Payment Flow

The intended payment flow is:

1. The frontend requests a new order from the Django backend.
2. Django creates the order through the Razorpay API using server-side credentials.
3. Django returns the Razorpay order ID and amount to the frontend.
4. Razorpay Checkout opens and the customer attempts payment.
5. The Checkout success callback returns payment details to the browser.
6. The frontend sends the payment ID, order ID, and signature to the backend verification endpoint.
7. Django verifies the Checkout signature using the Razorpay SDK.
8. Razorpay separately sends configured webhook events to the backend. The webhook handler verifies the webhook signature and processes the event safely.

### Payment security requirements

- Never expose `RAZORPAY_KEY_SECRET` or `RAZORPAY_WEBHOOK_SECRET` in frontend code.
- Calculate the payable amount on the backend from the trusted cart/order data. Do not trust an amount supplied by the browser.
- Verify the Checkout signature before treating a Checkout response as verified.
- Verify the webhook signature against the raw request body using the webhook secret.
- Handle duplicate webhook deliveries idempotently; Razorpay may retry deliveries.
- Update the order/payment state only after validated payment evidence is received.
- Keep test and live credentials separate.
- Use HTTPS and appropriate access controls in production.

## Razorpay Webhook Configuration

A webhook lets Razorpay notify the backend when a configured event occurs, such as a payment being captured or a payment failing. Razorpay sends an HTTP POST request to the configured webhook URL. The application should process the event and return a successful HTTP response after it has been safely accepted.

### 1. Create the webhook endpoint

The project should have a dedicated Django URL for the webhook, for example:

`/api/payments/webhook/`

The webhook endpoint should:

- Accept POST requests.
- Read the raw request body for signature verification.
- Verify the `X-Razorpay-Signature` header using `RAZORPAY_WEBHOOK_SECRET`.
- Parse the event only after signature verification.
- Handle only the events configured and required by the project.
- Avoid processing the same event twice.
- Return a suitable HTTP response.

Do not assume a webhook is secure just because the endpoint is difficult to guess. Signature verification is required.

### 2. Configure the webhook in Razorpay Dashboard

In Razorpay Dashboard, open the relevant account's webhook settings in Test Mode and:

1. Add the publicly reachable webhook URL.
2. Select the events the application actually handles (for example, `payment.captured` and/or `payment.failed`).
3. Set a webhook signing secret.
4. Save the configuration.
5. Store that same signing secret in `RAZORPAY_WEBHOOK_SECRET` in the local `.env` file.

Dashboard labels can change. Make sure the webhook is configured in **Test Mode** when testing with test payments. A live-mode webhook configuration is separate.

### 3. Why ngrok is needed locally

Razorpay servers cannot normally reach a Django server running only on `127.0.0.1:8000`. ngrok creates a temporary public HTTPS address and forwards incoming requests to the local Django server.

Keep Django running in one terminal:

```bash
python manage.py runserver 8000
```

In a second terminal, start ngrok:

```bash
ngrok http 8000
```

ngrok will display a forwarding URL similar to:

`https://police-surfboard-wreath.ngrok-free.dev`

If the local webhook route is `/api/payments/webhook/`, the complete webhook URL would look like.

`https://police-surfboard-wreath.ngrok-free.dev/api/payments/webhook/`

Register that complete URL in the Razorpay Dashboard webhook settings.

### 4. Test the webhook

1. Start Django.
2. Start ngrok and copy the current HTTPS forwarding URL.
3. Confirm the configured webhook URL uses the correct route.
4. Make a test payment or use the webhook test feature available in the Dashboard, if available.
5. Inspect the ngrok request inspector and Django logs to confirm that the request reached the endpoint.
6. Confirm the endpoint verified the signature and processed the event.
7. Check the related order/payment record to confirm that the state changed as expected.

A webhook event may be delivered after the browser Checkout result, so do not assume it will arrive at exactly the same moment.

### ngrok troubleshooting

- **Webhook does not arrive:** Check that Django and ngrok are both running and the Dashboard URL includes the correct path.
- **URL changed:** A temporary ngrok URL may change when ngrok restarts. Update the webhook URL in the Dashboard.
- **404 response:** Confirm the Django URL pattern and trailing slash.
- **Signature verification fails:** Check that the request body is not modified before verification and that the webhook secret matches the Dashboard configuration. Do not substitute the API key secret for the webhook secret.
- **400/500 response:** Review the Django logs and endpoint response.
- **Test event does not update an order:** Check that the handler processes that event type, maps it to the correct local order/payment, and handles duplicate events safely.

## Custom User Model

The project uses a custom user model configured in Django settings:

```python
AUTH_USER_MODEL = "accounts.MyUser"
```

The model is defined in `accounts/models.py`. Review migrations carefully when changing a custom user model, particularly if the database already contains data.

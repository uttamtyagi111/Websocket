from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from io import BytesIO
import random
import string
from django.conf import settings
from django.http import HttpResponse
from .models import UserProfile

def generate_invoice_number():
    """Generates a random invoice number."""
    return "INV-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))


import requests
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.conf import settings
from .models import UserProfile
from datetime import datetime

def send_plan_purchase_email_with_pdf(transaction_id, plan_name, price, expiry_date, user_email, email_limit, device_limit, duration_days, plan_start_date, plan_expiration_date, user_name, user_country, user_zip_code, user_state, user_city, user_address_line2, user_address_line1):
    """
    Sends an invoice email when a user purchases a new plan.
    """
    try:
        # Fetch user profile using the transaction ID
        user_profile = UserProfile.objects.get(phonepe_transaction_id=transaction_id)
        invoice_number = generate_invoice_number()
        # Prepare the variables to pass to Puppeteer service
        puppeteer_data = {
            "user": {
                "name": user_name,
                "address_line1": user_address_line1,
                "address_line2": user_address_line2,
                "city": user_city,
                "state": user_state,
                "zip_code": user_zip_code,
                "country": user_country
            },
            "invoice_number": invoice_number,
            "plan_start_date": plan_start_date.strftime("%d %B %Y") if isinstance(plan_start_date, datetime) else plan_start_date,
            "plan": {
                "plan_name": plan_name,
                "plan_expiration_date": plan_expiration_date.strftime("%d %B %Y") if isinstance(plan_expiration_date, datetime) else plan_expiration_date,
                "email_limit": email_limit,
                "device_limit": device_limit,
                "amount": price
            }
        }
        print(puppeteer_data)

        # Send the HTML to the Puppeteer service to generate PDF (via Node.js service)
        puppeteer_service_url = 'https://invoices.wishgeekstechserve.com/backend/getBuffer'
        response = requests.post(puppeteer_service_url, json=puppeteer_data)

        if response.status_code != 200:
            return HttpResponse("Error generating PDF from Node.js service", status=500)

        # Extract PDF buffer from response
        response_data = response.json()
        if response_data.get('success') and 'pdfBuffer' in response_data:
            pdf_buffer_data = response_data['pdfBuffer']['data']  # The PDF buffer is inside the "data" field
            
            # Convert the array of bytes into a proper buffer
            pdf_content = bytes(pdf_buffer_data)

            # Prepare the email body (this is for the email body, not the PDF)
            email_body = render_to_string(
                "subscriptions/purchase.html",
                {
                    "username": user_profile.user.username,
                    "plan_name": plan_name,
                    "email_limit": email_limit,
                    "device_limit": device_limit,
                    "duration_days": duration_days,
                    "plan_start_date": plan_start_date.strftime("%d %B %Y") if isinstance(plan_start_date, datetime) else plan_start_date,
                    "plan_expiration_date": expiry_date.strftime("%Y-%m-%d %H:%M:%S") if isinstance(expiry_date, datetime) else expiry_date,
                },
            )

            # Prepare the email with the generated PDF attachment
            email = EmailMessage(
                subject="Your Invoice for Plan Purchase",
                body=email_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user_email],
            )
            email.content_subtype = "html"
            email.attach(f"invoice_{invoice_number}.pdf", pdf_content, "application/pdf")
            email.send()

            return HttpResponse("Plan purchase invoice sent successfully!")

        else:
            return HttpResponse("Failed to generate PDF. Error from Puppeteer service.", status=500)

    except UserProfile.DoesNotExist:
        return HttpResponse("User profile not found", status=404)
    except Exception as e:
        return HttpResponse(f"An error occurred: {str(e)}", status=500)


    
    
import requests
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.http import HttpResponse

def send_plan_upgrade_email_with_pdf(transaction_id, plan_name, price, expiry_date, user_email, email_limit, device_limit, duration_days, plan_start_date,plan_expiration_date,user_name,user_country,user_zip_code,user_state,user_city,user_address_line2,user_address_line1):
    """
    Sends an invoice email when a user upgrades their plan.
    """
    try:
        # Fetch user profile using the transaction ID
        user_profile = UserProfile.objects.get(phonepe_transaction_id=transaction_id)
        invoice_number = generate_invoice_number()

        # Prepare the variables to pass to Puppeteer service
        puppeteer_data = {
            "user": {
                "name": user_name,
                "address_line1": user_address_line1,
                "address_line2": user_address_line2,
                "city": user_city,
                "state": user_state,
                "zip_code": user_zip_code,
                "country": user_country
            },
            "invoice_number": invoice_number,
            "plan_start_date": plan_start_date,
            "plan": {
                "plan_name": plan_name,
                "plan_expiration_date": plan_expiration_date,
                "email_limit": email_limit,
                "device_limit": device_limit,
                "amount": price
            }
        }

        # Send the HTML to the Puppeteer service to generate PDF (via Node.js service)
        puppeteer_service_url = 'https://invoices.wishgeekstechserve.com/backend/getBuffer'
        response = requests.post(puppeteer_service_url, json=puppeteer_data)
        print(response)

        if response.status_code != 200:
            return HttpResponse("Error generating PDF from Node.js service", status=500)
       # Extract PDF buffer from response
        response_data = response.json()
        if response_data.get('success') and 'pdfBuffer' in response_data:
            pdf_buffer_data = response_data['pdfBuffer']['data']  # The PDF buffer is inside the "data" field
            
            # Convert the array of bytes into a proper buffer
            pdf_content = bytes(pdf_buffer_data)
        # Prepare the email body (this is for the email body, not the PDF)
        email_body = render_to_string(
            "subscriptions/upgrade.html",
            {
                "username": user_profile.user.username,
                "plan_name": plan_name,
                "email_limit": email_limit, 
                "device_limit": device_limit, 
                "duration_days": duration_days,
                "plan_start_date": plan_start_date, 
                "plan_expiration_date": expiry_date, 
            },
        )

        # Prepare the email with the generated PDF attachment
        email = EmailMessage(
            subject="Your Invoice for Plan Upgrade",
            body=email_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user_email],
        )
        email.content_subtype = "html"
        email.attach(f"invoice_{invoice_number}.pdf", pdf_content, "application/pdf")
        email.send()

        return HttpResponse("Plan upgrade invoice sent successfully!")

    except UserProfile.DoesNotExist:
        return HttpResponse("User profile not found", status=404)



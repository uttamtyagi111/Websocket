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

# def generate_pdf_from_html(html_string):
#     """
#     Converts HTML to PDF using xhtml2pdf and returns the PDF file as a byte stream.
#     """
#     pdf_stream = BytesIO()
#     pisa_status = pisa.CreatePDF(html_string, dest=pdf_stream)

#     if pisa_status.err:
#         return HttpResponse("Error in PDF generation")

#     pdf_stream.seek(0)
#     return pdf_stream.getvalue()

# def send_plan_purchase_email_with_pdf(transaction_id, plan_name, price, expiry_date, user_email, email_limit, device_limit, duration_days, plan_start_date):
#     """
#     Sends an invoice email when a user purchases a new plan.
#     """
#     try:
#         user_profile = UserProfile.objects.get(phonepe_transaction_id=transaction_id)
#         invoice_number = generate_invoice_number()

#         html_string = render_to_string(
#             "subscriptions/invoice_template.html",
#             {
#                 "invoice_number": invoice_number,
#                 "name": user_profile.user.get_full_name(),
#                 "plan": plan_name,
#                 "amount": price,
#                 "address_line1": user_profile.address_line1,
#                 "address_line2": user_profile.address_line2,
#                 "city": user_profile.city,
#                 "state": user_profile.state,
#                 "zip_code": user_profile.zip_code,
#                 "country": user_profile.country,
#             },
#         )

#         pdf_content = generate_pdf_from_html(html_string)
#         if not pdf_content:
#             return HttpResponse("Error generating PDF", status=500)

#         email_body = render_to_string(
#             "subscriptions/purchase.html",
#             {
#                 "username": user_profile.user.username,
#                 "plan_name": plan_name,
#                 "email_limit": email_limit, 
#                 "device_limit": device_limit,
#                 "duration_days": duration_days,  
#                 "plan_start_date": plan_start_date.strftime("%d %B %Y"),
#                 "plan_expiration_date": expiry_date.strftime("%d %B %Y"), 
#             },
#         )

#         email = EmailMessage(
#             subject="Your Invoice for Plan Purchase",
#             body=email_body,
#             from_email=settings.DEFAULT_FROM_EMAIL,
#             to=[user_email],
#         )
#         email.content_subtype = "html"
#         email.attach(f"invoice_{invoice_number}.pdf", pdf_content, "application/pdf")
#         email.send()

#         return HttpResponse("Plan purchase invoice sent successfully!")

#     except UserProfile.DoesNotExist:
#         return HttpResponse("User profile not found", status=404)

# def send_plan_upgrade_email_with_pdf(transaction_id, plan_name, price, expiry_date, user_email, email_limit, device_limit, duration_days, plan_start_date):
#     """
#     Sends an invoice email when a user upgrades their plan.
#     """
#     try:
#         user_profile = UserProfile.objects.get(phonepe_transaction_id=transaction_id)
#         invoice_number = generate_invoice_number()

#         html_string = render_to_string(
#             "subscriptions/invoice_template.html",
#             {
#                 "invoice_number": invoice_number,
#                 "name": user_profile.user.get_full_name(),
#                 "plan": plan_name,
#                 "amount": price,
#                 "address_line1": user_profile.address_line1,
#                 "address_line2": user_profile.address_line2,
#                 "city": user_profile.city,
#                 "state": user_profile.state,
#                 "zip_code": user_profile.zip_code,
#                 "country": user_profile.country,
#             },
#         )

#         pdf_content = generate_pdf_from_html(html_string)
#         if not pdf_content:
#             return HttpResponse("Error generating PDF", status=500)

#         email_body = render_to_string(
#             "subscriptions/upgrade.html",
#             {
#                 "username": user_profile.user.username,
#                 "plan_name": plan_name,
#                 "email_limit": email_limit, 
#                 "device_limit": device_limit, 
#                 "duration_days": duration_days,
#                 "plan_start_date": plan_start_date.strftime("%d %B %Y"), 
#                 "plan_expiration_date": expiry_date.strftime("%d %B %Y"), 
#             },
#         )

#         email = EmailMessage(
#             subject="Your Invoice for Plan Upgrade",
#             body=email_body,
#             from_email=settings.DEFAULT_FROM_EMAIL,
#             to=[user_email],
#         )
#         email.content_subtype = "html"
#         email.attach(f"invoice_{invoice_number}.pdf", pdf_content, "application/pdf")
#         email.send()

#         return HttpResponse("Plan upgrade invoice sent successfully!")

#     except UserProfile.DoesNotExist:
#         return HttpResponse("User profile not found", status=404)
    
    
    
    
    
# ### Using NodeJs API
# import requests
# from django.http import HttpResponse
# from django.core.mail import EmailMessage
# from django.template.loader import render_to_string
# from django.conf import settings

# def send_plan_upgrade_email_with_pdf(transaction_id, plan_name, price, expiry_date, user_email, email_limit, device_limit, duration_days, plan_start_date):
#     """
#     Sends an invoice email when a user upgrades their plan.
#     """
#     try:
#         # Fetch user profile using the transaction ID
#         user_profile = UserProfile.objects.get(phonepe_transaction_id=transaction_id)
#         invoice_number = generate_invoice_number()

#         # Render HTML for the invoice, including plan details like email_limit, device_limit, etc.
#         html_string = render_to_string(
#             "subscriptions/invoice_template.html",
#             {
#                 "invoice_number": invoice_number,
#                 "name": user_profile.user.get_full_name(),
#                 "plan": plan_name,
#                 "amount": price,
#                 "address_line1": user_profile.address_line1,
#                 "address_line2": user_profile.address_line2,
#                 "city": user_profile.city,
#                 "state": user_profile.state,
#                 "zip_code": user_profile.zip_code,
#                 "country": user_profile.country,
#                 "email_limit": email_limit, 
#                 "device_limit": device_limit, 
#                 "duration_days": duration_days,
#                 "plan_start_date": plan_start_date.strftime("%d %B %Y"), 
#                 "plan_expiration_date": expiry_date.strftime("%d %B %Y"),
#             },
#         )

#         # Send the HTML to Node.js API to generate PDF (via Puppeteer)
#         puppeteer_service_url = 'http://localhost:3000/convert-html-to-pdf'
#         response = requests.post(puppeteer_service_url, json={'htmlContent': html_string})

#         if response.status_code != 200:
#             return HttpResponse("Error generating PDF from Node.js service", status=500)

#         # Get the PDF content from the response
#         pdf_content = response.content

#         # Prepare the email body (this is for the email body, not the PDF)
#         email_body = render_to_string(
#             "subscriptions/upgrade.html",
#             {
#                 "username": user_profile.user.username,
#                 "plan_name": plan_name,
#                 "email_limit": email_limit, 
#                 "device_limit": device_limit, 
#                 "duration_days": duration_days,
#                 "plan_start_date": plan_start_date.strftime("%d %B %Y"), 
#                 "plan_expiration_date": expiry_date.strftime("%d %B %Y"), 
#             },
#         )

#         # Prepare the email with the generated PDF attachment
#         email = EmailMessage(
#             subject="Your Invoice for Plan Upgrade",
#             body=email_body,
#             from_email=settings.DEFAULT_FROM_EMAIL,
#             to=[user_email],
#         )
#         email.content_subtype = "html"
#         email.attach(f"invoice_{invoice_number}.pdf", pdf_content, "application/pdf")
#         email.send()

#         return HttpResponse("Plan upgrade invoice sent successfully!")

#     except UserProfile.DoesNotExist:
#         return HttpResponse("User profile not found", status=404)
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



# def send_plan_purchase_email_with_pdf(transaction_id, plan_name, price, expiry_date, user_email, email_limit, device_limit, duration_days, plan_start_date):
#     """
#     Sends an invoice email when a user purchases a new plan.
#     """
#     user_profile = UserProfile.objects.get(phonepe_transaction_id=transaction_id)

#     html_string = render_to_string(
#         "subscriptions/invoice_template.html",
#         {
#             "name": user_profile.user.get_full_name(),
#             "plan": plan_name,
#             "amount": price,
#             "address_line1": user_profile.address_line1,
#             "address_line2": user_profile.address_line2,
#             "city": user_profile.city,
#             "state": user_profile.state,
#             "zip_code": user_profile.zip_code,
#             "country": user_profile.country,
#         },
#     )

#     pdf_content = generate_pdf_from_html(html_string)
#     if not pdf_content:
#         return HttpResponse("Error generating PDF", status=500)

#     email_body = render_to_string(
#         "subscriptions/purchase.html",
#         {
#             "username": user_profile.user.username,
#             "plan_name": plan_name,
#             "email_limit": email_limit, 
#             "device_limit": device_limit,
#             "duration_days": duration_days,  
#             "plan_start_date": plan_start_date.strftime("%d %B %Y"),
#             "plan_expiration_date": expiry_date.strftime("%d %B %Y"), 
#         },
#     )

#     email = EmailMessage(
#         subject="Your Invoice for Plan Purchase",
#         body=email_body,
#         from_email=settings.DEFAULT_FROM_EMAIL,
#         to=[user_email],
#     )
#     email.content_subtype = "html"
#     email.attach(f"invoice_{transaction_id}.pdf", pdf_content, "application/pdf")
#     email.send()

#     return HttpResponse("Plan purchase invoice sent successfully!")


# def send_plan_upgrade_email_with_pdf(transaction_id, plan_name, price, expiry_date, user_email, email_limit, device_limit, duration_days, plan_start_date):
#     """
#     Sends an invoice email when a user upgrades their plan.
#     """
#     user_profile = UserProfile.objects.get(phonepe_transaction_id=transaction_id)

#     html_string = render_to_string(
#         "subscriptions/invoice_template.html",
#         {
#             "name": user_profile.user.get_full_name(),
#             "plan": plan_name,
#             "amount": price,
#             "address_line1": user_profile.address_line1,
#             "address_line2": user_profile.address_line2,
#             "city": user_profile.city,
#             "state": user_profile.state,
#             "zip_code": user_profile.zip_code,
#             "country": user_profile.country,
#         },
#     )

#     pdf_content = generate_pdf_from_html(html_string)
#     if not pdf_content:
#         return HttpResponse("Error generating PDF", status=500)

#     email_body = render_to_string(
#         "subscriptions/upgrade.html",
#         {
#             "username": user_profile.user.username,
#             "plan_name": plan_name,
#             "email_limit": email_limit, 
#             "device_limit": device_limit, 
#             "duration_days": duration_days,
#             "plan_start_date": plan_start_date.strftime("%d %B %Y"), 
#             "plan_expiration_date": expiry_date.strftime("%d %B %Y"), 
#         },
#     )

#     email = EmailMessage(
#         subject="Your Invoice for Plan Upgrade",
#         body=email_body,
#         from_email=settings.DEFAULT_FROM_EMAIL,
#         to=[user_email],
#     )
#     email.content_subtype = "html"
#     email.attach(f"invoice_{transaction_id}.pdf", pdf_content, "application/pdf")
#     email.send()

#     return HttpResponse("Plan upgrade invoice sent successfully!")



# def send_email_with_pdf(transaction_id, plan_name, price, expiry_date, user_email):
#     """

#     Renders the HTML template, converts it to PDF, and sends the PDF as an email attachment.
#     """
#     user_profile = UserProfile.objects.get(phonepe_transaction_id=transaction_id)

#     print(
#         f"Transaction ID: {transaction_id}, Plan Name: {plan_name}, Price: {price}, Expiry Date: {expiry_date}"
#     )

#     html_string = render_to_string(
#         "subscriptions/invoice_template.html",
#         {
#             "name": user_profile.user.get_full_name(),
#             "plan": user_profile.current_plan.name,
#             "amount": user_profile.current_plan.price,
#             "address_line1": user_profile.address_line1,
#             "address_line2": user_profile.address_line2,
#             "city": user_profile.city,
#             "state": user_profile.state,
#             "zip_code": user_profile.zip_code,
#             "country": user_profile.country,
#         },
#     )

#     print(html_string)
#     pdf_content = generate_pdf_from_html(html_string)

#     if not pdf_content:
#         return HttpResponse("Error generating PDF", status=500)

#     email_body = render_to_string(
#         "subscriptions/upgrade.html",
#         {
#             "username": user_profile.user.username,
#             "plan_name": plan_name,
#             "email_limit": user_profile.current_plan.email_limit,
#             "device_limit": user_profile.current_plan.device_limit,
#             "duration_days": user_profile.current_plan.duration_days,
#             "plan_start_date": user_profile.plan_start_date.strftime("%d %B %Y"),
#             "plan_expiration_date": expiry_date.strftime("%d %B %Y"),
#         },
#     )

#     # 🔹 Create and send email
#     email = EmailMessage(
#         subject="Your Invoice for Plan Purchase",
#         body=email_body,
#         from_email=settings.DEFAULT_FROM_EMAIL,
#         to=[user_email],
#     )

#     # Set email content type to HTML
#     email.content_subtype = "html"

#     email.attach(f"invoice_{transaction_id}.pdf", pdf_content, "application/pdf")
#     email.send()

#     return HttpResponse("Invoice sent successfully!")

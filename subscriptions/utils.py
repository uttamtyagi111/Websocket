from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from io import BytesIO
from django.conf import settings
from django.http import HttpResponse
from .models import UserProfile


def generate_pdf_from_html(html_string):
    """
    Converts HTML to PDF using xhtml2pdf and returns the PDF file as a byte stream.
    """
    pdf_stream = BytesIO()
    pisa_status = pisa.CreatePDF(html_string, dest=pdf_stream)

    if pisa_status.err:
        return HttpResponse("Error in PDF generation")

    pdf_stream.seek(0)
    return pdf_stream.getvalue()


def send_email_with_pdf(transaction_id, plan_name, price, expiry_date, user_email):
    """

    Renders the HTML template, converts it to PDF, and sends the PDF as an email attachment.
    """
    user_profile = UserProfile.objects.get(phonepe_transaction_id=transaction_id)

    print(
        f"Transaction ID: {transaction_id}, Plan Name: {plan_name}, Price: {price}, Expiry Date: {expiry_date}"
    )

    # Render HTML content from a template
    html_string = render_to_string(
        "subscriptions/invoice_template.html",
        {
            "name": user_profile.user.get_full_name(),
            "plan": user_profile.current_plan.name,
            "amount": user_profile.current_plan.price,
            "address_line1": user_profile.address_line1,
            "address_line2": user_profile.address_line2,
            "city": user_profile.city,
            "state": user_profile.state,
            "zip_code": user_profile.zip_code,
            "country": user_profile.country,
        },
    )
    # html_string = render_to_string("invoice_template.html", {
    # "transaction_id": transaction_id,
    # "plan": plan_name,
    # "amount": price,
    # "expiry_date": expiry_date,
    # "name": user_profile.user.get_full_name(),
    # "address_line1": user_profile.address_line1,
    # "address_line2": user_profile.address_line2,
    # "city": user_profile.city,
    # "state": user_profile.state,
    # "zip_code": user_profile.zip_code,
    # "country": user_profile.country
    # })

    print(html_string)
    pdf_content = generate_pdf_from_html(html_string)

    if not pdf_content:
        return HttpResponse("Error generating PDF", status=500)

    email = EmailMessage(
        subject="Your Invoice for Plan Purchase",
        body="Please find your invoice attached.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user_email],
    )

    email.attach(f"invoice_{transaction_id}.pdf", pdf_content, "application/pdf")
    email.send()

    return HttpResponse("Invoice sent successfully!")

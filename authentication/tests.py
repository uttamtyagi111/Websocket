import smtplib

smtp_host = ".com"
smtp_port = 587
username = "your-email@example.com"
password = "your-password"

try:
    server = smtplib.SMTP(smtp_host, smtp_port)
    server.starttls()
    server.login(username, password)
    print("Login successful")
    server.quit()
except smtplib.SMTPAuthenticationError as e:
    print(f"SMTP Authentication Error: {e}")
except Exception as e:
    print(f"Error: {e}")

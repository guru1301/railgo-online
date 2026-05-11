import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

def send_otp_email(to_email: str, otp: str):
    # Credentials
    sender_email = os.getenv("SMTP_EMAIL", "support.railgo@gmail.com")
    # Removing spaces from the provided app password to be safe
    app_password = os.getenv("SMTP_APP_PASSWORD", "imdu nfij qrvp yzcf").replace(" ", "")

    subject = "RailGo: Verify your email address"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
            body {{
                font-family: 'Inter', Helvetica, Arial, sans-serif;
                background-color: #f4f7fe;
                margin: 0;
                padding: 40px 20px;
                color: #1e293b;
            }}
            .container {{
                max-width: 500px;
                margin: 0 auto;
                background-color: #ffffff;
                border-radius: 16px;
                overflow: hidden;
                box-shadow: 0 10px 25px rgba(108, 99, 255, 0.08);
            }}
            .header {{
                background: linear-gradient(135deg, #6c63ff, #f472b6);
                padding: 30px;
                text-align: center;
                color: #ffffff;
            }}
            .logo {{
                font-size: 28px;
                font-weight: 700;
                letter-spacing: 1px;
                margin: 0;
            }}
            .content {{
                padding: 40px 30px;
                text-align: center;
            }}
            .title {{
                font-size: 22px;
                font-weight: 700;
                color: #1e293b;
                margin-bottom: 15px;
                margin-top: 0;
            }}
            .desc {{
                font-size: 15px;
                color: #64748b;
                line-height: 1.6;
                margin-bottom: 30px;
            }}
            .otp-wrapper {{
                background: linear-gradient(135deg, rgba(108, 99, 255, 0.05), rgba(244, 114, 182, 0.05));
                border: 2px solid rgba(108, 99, 255, 0.2);
                border-radius: 12px;
                padding: 25px;
                margin: 0 auto 30px auto;
                max-width: 300px;
            }}
            .otp-code {{
                font-size: 38px;
                font-weight: 700;
                letter-spacing: 8px;
                color: #6c63ff;
                margin: 0;
                text-shadow: 0 2px 4px rgba(108, 99, 255, 0.1);
            }}
            .warning {{
                font-size: 13px;
                color: #94a3b8;
            }}
            .footer {{
                background-color: #f8fafc;
                text-align: center;
                padding: 20px;
                font-size: 12px;
                color: #94a3b8;
                border-top: 1px solid #e2e8f0;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1 class="logo">🚆 RailGo</h1>
            </div>
            <div class="content">
                <h2 class="title">Verify your email address</h2>
                <p class="desc">Welcome to RailGo! We're excited to have you on board. Please use the verification code below to complete your registration.</p>
                
                <div class="otp-wrapper">
                    <p class="otp-code">{otp}</p>
                </div>
                
                <p class="warning">This code is valid for <strong>10 minutes</strong>. If you didn't request this code, you can safely ignore this email.</p>
            </div>
            <div class="footer">
                &copy; 2026 RailGo Train Booking Platform.<br>All rights reserved.
            </div>
        </div>
    </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"RailGo Support <{sender_email}>"
    msg["To"] = to_email

    part = MIMEText(html_content, "html")
    msg.attach(part)

    try:
        # Send via Gmail SMTP
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, app_password)
            server.sendmail(sender_email, to_email, msg.as_string())
        print(f"OTP email sent successfully to {to_email}")
        return True
    except Exception as e:
        print(f"Failed to send email to {to_email}: {str(e)}")
        return False
def send_cancel_otp_email(to_email: str, otp: str, pnr: str):
    # Credentials
    sender_email = os.getenv("SMTP_EMAIL", "support.railgo@gmail.com")
    app_password = os.getenv("SMTP_APP_PASSWORD", "imdu nfij qrvp yzcf").replace(" ", "")

    subject = f"RailGo: OTP for Ticket Cancellation (PNR: {pnr})"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
            body {{
                font-family: 'Inter', Helvetica, Arial, sans-serif;
                background-color: #fef2f2;
                margin: 0;
                padding: 40px 20px;
                color: #1e293b;
            }}
            .container {{
                max-width: 500px;
                margin: 0 auto;
                background-color: #ffffff;
                border-radius: 16px;
                overflow: hidden;
                box-shadow: 0 10px 25px rgba(239, 68, 68, 0.08);
            }}
            .header {{
                background: linear-gradient(135deg, #ef4444, #f472b6);
                padding: 30px;
                text-align: center;
                color: #ffffff;
            }}
            .logo {{
                font-size: 28px;
                font-weight: 700;
                letter-spacing: 1px;
                margin: 0;
            }}
            .content {{
                padding: 40px 30px;
                text-align: center;
            }}
            .title {{
                font-size: 22px;
                font-weight: 700;
                color: #b91c1c;
                margin-bottom: 15px;
                margin-top: 0;
            }}
            .desc {{
                font-size: 15px;
                color: #64748b;
                line-height: 1.6;
                margin-bottom: 30px;
            }}
            .otp-wrapper {{
                background: linear-gradient(135deg, rgba(239, 68, 68, 0.05), rgba(244, 114, 182, 0.05));
                border: 2px solid rgba(239, 68, 68, 0.2);
                border-radius: 12px;
                padding: 25px;
                margin: 0 auto 30px auto;
                max-width: 300px;
            }}
            .otp-code {{
                font-size: 38px;
                font-weight: 700;
                letter-spacing: 8px;
                color: #ef4444;
                margin: 0;
                text-shadow: 0 2px 4px rgba(239, 68, 68, 0.1);
            }}
            .warning {{
                font-size: 13px;
                color: #94a3b8;
            }}
            .footer {{
                background-color: #f8fafc;
                text-align: center;
                padding: 20px;
                font-size: 12px;
                color: #94a3b8;
                border-top: 1px solid #e2e8f0;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1 class="logo">🚆 RailGo</h1>
            </div>
            <div class="content">
                <h2 class="title">Confirm Ticket Cancellation</h2>
                <p class="desc">We received a request to cancel your booking for <strong>PNR: {pnr}</strong>. Please use the verification code below to authorize this cancellation.</p>
                
                <div class="otp-wrapper">
                    <p class="otp-code">{otp}</p>
                </div>
                
                <p class="warning">This code is valid for <strong>10 minutes</strong>. If you didn't request this cancellation, please ignore this email and your booking will remain safe.</p>
            </div>
            <div class="footer">
                &copy; 2026 RailGo Train Booking Platform.<br>All rights reserved.
            </div>
        </div>
    </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"RailGo Support <{sender_email}>"
    msg["To"] = to_email

    part = MIMEText(html_content, "html")
    msg.attach(part)

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, app_password)
            server.sendmail(sender_email, to_email, msg.as_string())
        return True
    except Exception as e:
        print(f"Failed to send cancellation email to {to_email}: {str(e)}") 
        return False

def send_forgot_password_email(to_email: str, otp: str, name: str):
    sender_email = os.getenv("SMTP_EMAIL", "support.railgo@gmail.com")
    app_password = os.getenv("SMTP_APP_PASSWORD", "").replace(" ", "")

    subject = "RailGo: Reset your password"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
            body {{
                font-family: 'Inter', Helvetica, Arial, sans-serif;
                background-color: #f0f4ff;
                margin: 0;
                padding: 40px 20px;
                color: #1e293b;
            }}
            .container {{
                max-width: 500px;
                margin: 0 auto;
                background-color: #ffffff;
                border-radius: 16px;
                overflow: hidden;
                box-shadow: 0 10px 25px rgba(59, 130, 246, 0.1);
            }}
            .header {{
                background: linear-gradient(135deg, #3b82f6, #6c63ff);
                padding: 30px;
                text-align: center;
                color: #ffffff;
            }}
            .logo {{
                font-size: 28px;
                font-weight: 700;
                letter-spacing: 1px;
                margin: 0;
            }}
            .content {{
                padding: 40px 30px;
                text-align: center;
            }}
            .title {{
                font-size: 22px;
                font-weight: 700;
                color: #1e293b;
                margin-bottom: 10px;
                margin-top: 0;
            }}
            .greeting {{
                font-size: 15px;
                color: #64748b;
                margin-bottom: 8px;
            }}
            .desc {{
                font-size: 14px;
                color: #64748b;
                line-height: 1.6;
                margin-bottom: 30px;
            }}
            .otp-wrapper {{
                background: linear-gradient(135deg, rgba(59,130,246,0.06), rgba(108,99,255,0.06));
                border: 2px solid rgba(108,99,255,0.25);
                border-radius: 12px;
                padding: 25px;
                margin: 0 auto 30px auto;
                max-width: 300px;
            }}
            .otp-label {{
                font-size: 12px;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 1.5px;
                color: #94a3b8;
                margin-bottom: 10px;
            }}
            .otp-code {{
                font-size: 38px;
                font-weight: 700;
                letter-spacing: 8px;
                color: #3b82f6;
                margin: 0;
            }}
            .warning {{
                font-size: 13px;
                color: #94a3b8;
                line-height: 1.6;
            }}
            .footer {{
                background-color: #f8fafc;
                text-align: center;
                padding: 20px;
                font-size: 12px;
                color: #94a3b8;
                border-top: 1px solid #e2e8f0;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1 class="logo">🚆 RailGo</h1>
            </div>
            <div class="content">
                <h2 class="title">Reset Your Password</h2>
                <p class="greeting">Hi {name},</p>
                <p class="desc">We received a request to reset your RailGo account password. Use the code below to proceed. This code is valid for <strong>10 minutes</strong>.</p>

                <div class="otp-wrapper">
                    <div class="otp-label">Password Reset Code</div>
                    <p class="otp-code">{otp}</p>
                </div>

                <p class="warning">If you did not request a password reset, you can safely ignore this email — your account is still secure and your password has <strong>not</strong> been changed.</p>
            </div>
            <div class="footer">
                &copy; 2026 RailGo Train Booking Platform.<br>All rights reserved.
            </div>
        </div>
    </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"RailGo Support <{sender_email}>"
    msg["To"] = to_email

    msg.attach(MIMEText(html_content, "html"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, app_password)
            server.sendmail(sender_email, to_email, msg.as_string())
        print(f"Password reset email sent to {to_email}")
        return True
    except Exception as e:
        print(f"Failed to send password reset email to {to_email}: {str(e)}")
        return False

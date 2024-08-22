from datetime import datetime, timezone
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

class EmailAPI:
    def __init__(self):
        self.voyage = []
        self.smtp_username = "ami.cms.relay@gmail.com"
        self.smtp_password = 'pqpt vluh gkij qesh'
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.recipients = ['eduardo@offshoredoneright.com', 'jshonka@amiwx.com']
        self.subject = "CMS Report Monitoring"
        self.full_name = "CMS Report Monitoring Notification"
    
    def SendEMail(self, email, last_submitted_date, attachments=None):
        try:

            msg = MIMEMultipart()
            msg['From'] = f"""{self.full_name} <{self.smtp_username}>"""
            #msg['To'] = ', '.join(email)
            msg['To'] = self.recipients
            msg['Subject'] = self.subject

            # Get the current date and time in UTC
            now_utc = datetime.now(timezone.utc)

            # Format the date and time
            date = now_utc.strftime("%b %d, %Y %I:%M %p")
            body = f"""
                <!DOCTYPE html>
                <html lang="en">
                <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>CMS Report Monitoring</title>
                <style>
                    body {{
                        background-color: #fff;
                        color: #000;
                        font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen, Ubuntu, Cantarell, Fira Sans, Droid Sans, Helvetica Neue, sans-serif;
                        font-size: 10px
                    }}
                    .container {{
                        max-width: 60%;
                        margin: 0px auto;
                        padding: 0px;
                    }}
                    h2, h3, h4 {{
                        margin: 5px 0 0 0;
                        text-align: left;
                    }}
                    table {{
                        width: 80%;
                        border-collapse: collapse;
                        font-size: 10px
                    }}
                    th, td {{
                        padding: 0px;
                        text-align: left;
                        border-bottom: 1px solid #ddd;
                        font-size: 10px
                    }}
                    .text-wrap {{
                        overflow-wrap: break-word;
                        word-wrap: break-word;
                        word-break: break-all;
                    }}
                    th {{
                        background-color: #f2f2f2;
                    }}
                </style>
                </head>
                    <body>
                        <div class="container">
                            <h2>CMS Report Monitoring</h2>
                            <p>{date}</p>
                            <br />
                            <br />
                            <p>Good day Captain,</p>
                            <br />
                            <p>We note that the last daily CII report received from your good vessel was {last_submitted_date.strftime("%b %d, %Y %I:%M %p")}. Kindly provide daily report(s) information since that time.</p>
                            <p>Very best regards,</p>
                            <p>CMS Support Team</p>
                            <p>cms_support@amiwx.com</p>
                        </div>
                    </body>
                </html>
            """

            msg.attach(MIMEText(body, 'html'))

            if attachments:
                for attachment in attachments:
                    with open(attachment, "rb") as file:
                        part = MIMEApplication(file.read())
                        part.add_header('Content-Disposition', f'attachment; filename="{attachment}"')
                        msg.attach(part)

            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            server.sendmail(self.smtp_username, self.recipients, msg.as_string())
            server.quit()

            return f"""Email successfully sent to {email}."""

            return msg.as_string()
        except Exception as e:
            
            return f"An error occurred while sending the email:" + str(e)
    


    
    
    

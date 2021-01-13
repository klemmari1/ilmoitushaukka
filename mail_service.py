from typing import Dict, List

from flask import Request
from sendgrid import Content, From, Mail, SendGridAPIClient, To

import settings
from models.emails import Email
from models.posts import Post


def get_emails():
    return Email.query.all()


def send_mail(hilights: Dict[str, List[Post]], request: Request = None) -> None:
    if not hilights:
        return

    for email, hilights in hilights.items():
        title_section = f'<h2><a href="{request.url_root if request else ""}">Ilmoitushaukka</a> sale alerts</h2>'
        hilight_messages_section = list(
            f'<a href="{hilight.url}">{hilight.title}</a>' for hilight in hilights
        )
        unsubscribe_section = f'<p style="font-size:12px"><a href="{request.url_root if request else ""}?unsubscribe=-email-">Unsubscribe</a> from sale alerts</p>'
        message = f"{title_section}<br/>{'<br/><br/>'.join(hilight_messages_section)}<br/><br/><br/>{unsubscribe_section}"

        sg = SendGridAPIClient(api_key=settings.EMAIL_API_KEY)
        from_email = From(settings.FROM_EMAIL, "Ilmoitushaukka")
        to_email = To(email=email, substitutions={"-email-": email})
        subject = "You have new sale alerts!"
        content = Content("text/html", message)

        mail = Mail(
            from_email=from_email,
            to_emails=to_email,
            subject=subject,
            html_content=content,
            is_multiple=True,
        )
        try:
            print("SENDING MAIL...")
            print(email)
            print(message)
            response = sg.client.mail.send.post(request_body=mail.get())
            print(response.status_code)
            print(response.body)
        except Exception as e:
            print(str(e))


def subscribe_email(email_address: str, url: str, search_query: str) -> bool:
    email = Email.query.filter(
        Email.email == email_address,
        Email.url == url,
        Email.search_query == search_query,
    ).one_or_none()
    if not email:
        email = Email(email=email_address, url=url, search_query=search_query)
        email.subscribe()
        return True
    return False


def unsubscribe_email(email_address: str) -> bool:
    emails = Email.query.filter(Email.email == email_address).all()
    for email in emails:
        email.unsubscribe()
        return True
    return False

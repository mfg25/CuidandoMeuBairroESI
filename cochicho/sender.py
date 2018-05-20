import flask_mail

from cochicho.extensions import db
from cochicho.models import Message, Status, Tag, Subscription


def send_all(api):
    messages = (db.session.query(Message)
                .options(
                    db.joinedload(Message.destinations, innerjoin=True)
                    .joinedload(Tag.subscriptions, innerjoin=True)
                    .joinedload(Subscription.subscriber, innerjoin=True))
                .filter_by(status=Status.unsent).all())
    with api.mail.connect() as conn:
        for message in messages:
            for tag in message.destinations:
                for subscription in tag.subscriptions:
                    send_message(conn, message, api.app.config['SENDER_NAME'],
                                 get_subscriber_email(subscription.subscriber),
                                 subscription.template_data)


def send_message(conn, message, sender, dest, template_data):
    mail_msg = flask_mail.Message(
        subject=message.title,
        sender=sender,
        recipients=[dest],
        body=message.format_body(template_data)
    )
    conn.send(mail_msg)


def get_subscriber_email(subscriber):
    # TODO: implementar
    return email

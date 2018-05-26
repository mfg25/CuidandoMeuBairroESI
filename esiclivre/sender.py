from flask import current_app

from cuidando_utils import scape_template, send_notification_messages, db

from .models import Message


def send_update_notifications():
    messages = db.session.query(Message).filter_by(notification_sent=False).options(
        db.joinedload(Message.pedido, innerjoin=True)).all()
    notifications = []
    print(f'Sending {len(messages)} notifications...')
    for message in messages:
        # Prepare notification message
        text_template = current_app.config['NOTIFICATION_TEMPLATE'].format(
            text=scape_template(message.justification)
        )
        notifications.append({
            'title': current_app.config['NOTIFICATION_TITLE'],
            'template': text_template,
            'tags': [message.pedido.get_notification_id()]
        })
        message.notification_sent = True

    send_notification_messages(notifications)
    db.session.commit()

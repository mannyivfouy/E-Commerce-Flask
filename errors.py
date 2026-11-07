import os
import requests

from flask import render_template, request, session, current_app

from extensions import db
from models.rate_limit_log import RateLimitLog


def error_handlers(app):

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('error/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('error/500.html'), 500

    @app.errorhandler(429)
    def too_many_requests(e):
        user_id = session.get('user_id')

        # Save rate limit violation
        rate_limit_log = RateLimitLog(
            user_id=user_id,
            ip_address=request.remote_addr,
            endpoint=request.path,
            method=request.method,
            limit=str(e.description),
        )

        db.session.add(rate_limit_log)

        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            current_app.logger.exception("Failed to save rate limit log")

        # Send Telegram notification
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        chat_id = os.getenv('TELEGRAM_CHAT_ID')

        if bot_token and chat_id:
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

            message = (
                "<code>⚠️ RATE LIMIT EXCEEDED</code>\n"
                "<code>- - - - - - - - - - - - -</code>\n"
                f"<code>IP     : {request.remote_addr}</code>\n"
                f"<code>Method : {request.method}</code>\n"
                f"<code>Path   : {request.path}</code>\n"
                f"<code>Limit  : {e.description}</code>\n"
                "<code>- - - - - - - - - - - - -</code>\n"
                "<code>Someone exceeded a rate limit.</code>"
            )

            payload = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "HTML"
            }

            try:
                requests.post(url, json=payload, timeout=5)
            except requests.RequestException:
                current_app.logger.exception(
                    "Failed to send Telegram notification"
                )

        return render_template('error/429.html'), 429
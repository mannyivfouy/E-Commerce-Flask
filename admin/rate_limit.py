from flask import render_template
from admin import admin_bp
from models.rate_limit_log import RateLimitLog
from admin.auth import login_required
from extensions import limiter
@admin_bp.get('/rate-limit')
@login_required
@limiter.limit("10 per minute")
def rate_limit_logs():
    module = 'rate_limit'

    logs = RateLimitLog.query.order_by(
        RateLimitLog.created_at.desc()
    ).all()

    return render_template(
        'admin/rate_limit/rate_limit.html',
        module=module,
        logs=logs
    )
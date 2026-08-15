from .models import VisitorMessage


def visitor_message_badge(request):
    """Provide the unread visitor-message count to admin templates."""
    if not request.session.get("admin"):
        return {"admin_visitor_count": 0}
    return {"admin_visitor_count": VisitorMessage.objects.filter(is_read=False).count()}

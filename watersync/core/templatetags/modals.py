from django import template

register = template.Library()


@register.inclusion_tag("shared/modal.html")
def render_modal(modal_id, form, action_url, title="Modal Title", submit_text="Submit"):
    return {
        "modal_id": modal_id,
        "form": form,
        "action_url": action_url,
        "title": title,
        "submit_text": submit_text,
    }

# myapp/templatetags/seo_tags.py
from django import template

register = template.Library()

@register.simple_tag
def site_name():
    return 'WildQuest Kenya'

@register.simple_tag
def default_meta_description():
    return 'Discover Kenya\'s best safaris, tours, and adventures with WildQuest Kenya.'

@register.simple_tag
def default_og_image():
    return 'https://wildquest.onrender.com/static/img/og-default.jpg'

@register.simple_tag
def twitter_handle():
    return '@WildQuestKE'

@register.simple_tag(takes_context=True)
def canonical_url(context):
    request = context['request']
    return request.build_absolute_uri()

@register.simple_tag
def site_url():
    return 'https://wildquest.onrender.com'
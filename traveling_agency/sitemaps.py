# myapp/sitemaps.py
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Event, Category

class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        return ['index', 'about', 'service', 'contact', 'events_list']

    def location(self, item):
        return reverse(item)

class EventSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9

    def items(self):
        return Event.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse('event_detail', args=[obj.slug])

class CategorySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Category.objects.all()

    def location(self, obj):
        return reverse('category_events', args=[obj.slug])
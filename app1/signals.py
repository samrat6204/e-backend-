from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Rating


@receiver([post_save, post_delete], sender=Rating)
def refresh_product_rating_stats(sender, instance, **kwargs):
    # Runs after every rating is saved or deleted.
    # Recalculates the product's average_rating and review_count.
    instance.product.update_rating_stats()
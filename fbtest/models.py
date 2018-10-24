from django.db import models

from django.db import models

class FacebookUser(models.Model):
    """A simple User model for Facebook users."""

    # We use the user's UID as the primary key in our database.
    id = models.IntegerField(primary_key=True)
    language = models.CharField(max_length=64, default='Python')

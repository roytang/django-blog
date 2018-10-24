from django.db import models

# Create your models here.
class Theme(models.Model):
    slug = models.SlugField()
    title = models.CharField(max_length=250)
    css_path = models.CharField(max_length=500)
    template_path = models.CharField(max_length=500, blank=True, null=True)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return self.title
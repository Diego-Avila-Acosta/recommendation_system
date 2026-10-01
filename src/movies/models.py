from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import datetime

# Create your models here.


class Movie(models.Model):
    title = models.CharField(max_length=255)
    genres = models.JSONField(default=list)
    country = models.CharField(max_length=100, blank=True, null=True)
    extra_data = models.JSONField(default=dict)
    release_year = models.IntegerField(
        validators=[
            MinValueValidator(1888),
            MaxValueValidator(datetime.date.today().year)
        ],
        blank=True,
        null=True
    )

    class Meta:
        unique_together = ('title', 'country', 'release_year')

    def __str__(self):
        return self.title

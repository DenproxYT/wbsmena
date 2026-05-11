from django.db import models
from django.conf import settings

class Schedule(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField()
    shifts = models.DecimalField(max_digits=4, decimal_places=2, default=0.0)
    comment = models.TextField(blank=True)
    pvz_address = models.CharField(max_length=255)

    class Meta:
        unique_together = ("user", "date")

    def __str__(self):
        return f"{self.user} - {self.date}"

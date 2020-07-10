from django.db import models

class Announcement(models.Model):
    BLUE = 'blue'
    GREEN = 'green'
    ORANGE = 'orange'
    YELLOW = 'yellow'
    COLOR_CHOICES = [
        (BLUE, 'Blue'),
        (GREEN, 'Green'),
        (ORANGE, 'Orange'),
        (YELLOW, 'Yellow'),
    ]
    display = models.BooleanField(default=False)
    text = models.CharField(max_length=500)
    link = models.URLField()
    link_text = models.CharField(max_length=100)
    color = models.CharField(max_length=6, choices=COLOR_CHOICES, default=ORANGE,)

    def __str__(self):
        return self.text




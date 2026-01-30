from django.db import models

class BetaSignup(models.Model):
    email = models.EmailField(unique=True)
    preferred_genre = models.CharField(max_length=50, choices=[
        ('idle', 'Idle Games'),
        ('rpg', 'RPG'),
        ('vn', 'Visual Novel'),
        ('puzzle', 'Puzzle'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
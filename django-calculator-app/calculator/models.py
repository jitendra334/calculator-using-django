from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Calculation(models.Model):
    OPERATION_CHOICES = [
        ('add', 'Addition'),
        ('subtract', 'Subtraction'),
        ('multiply', 'Multiplication'),
        ('divide', 'Division'),
        ('power', 'Power'),
        ('sqrt', 'Square Root'),
        ('sin', 'Sine'),
        ('cos', 'Cosine'),
        ('tan', 'Tangent'),
        ('log', 'Logarithm'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    operation = models.CharField(max_length=20, choices=OPERATION_CHOICES, default='other')
    expression = models.CharField(max_length=255)
    result = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.expression} = {self.result}"
from django.db import models
from django.contrib.postgres.fields import ArrayField

class Grantha(models.Model):
    title = models.CharField(max_length=500)
    file = models.FileField(upload_to='word_files/')
    commentaries = ArrayField(models.CharField(max_length=200), blank=True, default=list)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['title']),
        ]
    
    def __str__(self):
        return self.title

class Suggestion(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
        ('implemented', 'Implemented'),
    ]
    
    grantha = models.ForeignKey(Grantha, on_delete=models.CASCADE, related_name='suggestions')
    user_name = models.CharField(max_length=200, blank=True)  # Made optional
    user_email = models.EmailField(blank=True)
    suggestion = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-submitted_at']
    
    def __str__(self):
        name = self.user_name if self.user_name else 'Anonymous'
        return f"Suggestion for {self.grantha.title} by {name}"

import os
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.db import models
from django.contrib.postgres.fields import ArrayField

class Grantha(models.Model):
    title = models.CharField(max_length=500)
    file = models.FileField(upload_to='word_files/')
    commentaries = ArrayField(models.CharField(max_length=200), blank=True, default=list)
    tags = ArrayField(models.CharField(max_length=100), blank=True, default=list)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['title']),
        ]
    def save(self, *args, **kwargs):
        # Auto-fill title from filename if title is empty
        if not self.title and self.file:
            filename = os.path.basename(self.file.name)
            # Remove extension and clean up
            self.title = os.path.splitext(filename)[0]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

@receiver(pre_delete, sender=Grantha)
def delete_grantha_file(sender, instance, **kwargs):
    """Delete the file when Grantha instance is deleted"""
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)

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

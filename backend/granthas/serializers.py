from rest_framework import serializers
from .models import Grantha, Suggestion

class GranthaSerializer(serializers.ModelSerializer):
    file = serializers.SerializerMethodField()
    
    class Meta:
        model = Grantha
        fields = ['id', 'title', 'file', 'commentaries', 'uploaded_at', 'last_modified']
    
    def get_file(self, obj):
        # Return relative URL instead of absolute
        if obj.file:
            return obj.file.url  # This already gives relative path like /media/...
        return None

class GranthaUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grantha
        fields = ['id', 'title', 'file', 'commentaries']

class SuggestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Suggestion
        fields = ['id', 'grantha', 'user_name', 'user_email', 'suggestion', 'status', 'submitted_at']

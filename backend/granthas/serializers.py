from rest_framework import serializers
from .models import Grantha, Suggestion

class GranthaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grantha
        fields = '__all__'
        read_only_fields = ['uploaded_at', 'last_modified']

class GranthaUploadSerializer(serializers.ModelSerializer):
    commentaries_input = serializers.CharField(write_only=True)
    
    class Meta:
        model = Grantha
        fields = ['title', 'file', 'commentaries_input']
    
    def create(self, validated_data):
        # Parse comma-separated commentaries
        commentaries_str = validated_data.pop('commentaries_input', '')
        commentaries = [c.strip() for c in commentaries_str.split(',') if c.strip()]
        
        grantha = Grantha.objects.create(
            commentaries=commentaries,
            **validated_data
        )
        return grantha

class SuggestionSerializer(serializers.ModelSerializer):
    grantha_title = serializers.CharField(source='grantha.title', read_only=True)
    
    class Meta:
        model = Suggestion
        fields = '__all__'
        read_only_fields = ['submitted_at']

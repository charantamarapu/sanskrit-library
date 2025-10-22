from django.contrib import admin
from django import forms
from .models import Grantha, Suggestion
import os

class GranthaAdminForm(forms.ModelForm):
    commentaries_input = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 2, 'cols': 80}),
        help_text='Enter commentary names separated by commas (exactly as they appear in document headings)'
    )

    tags_input = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 2, 'cols': 80}),
        help_text='Enter tags separated by commas'
    )
    
    class Meta:
        model = Grantha
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].required = False
        self.fields['title'].help_text = 'Leave empty to auto-fill from filename'
        if self.instance and self.instance.commentaries:
            self.fields['commentaries_input'].initial = ', '.join(self.instance.commentaries)
        if self.instance and self.instance.tags:
            self.fields['tags_input'].initial = ', '.join(self.instance.tags)

    def save(self, commit=True):
        instance = super().save(commit=False)
        commentaries_str = self.cleaned_data.get('commentaries_input', '')
        if commentaries_str:
            instance.commentaries = [c.strip() for c in commentaries_str.split(',') if c.strip()]
        else:
            instance.commentaries = []
        tags_str = self.cleaned_data.get('tags_input', '')
        if tags_str:
            instance.tags = [t.strip() for t in tags_str.split(',') if t.strip()]
        else:
            instance.tags = []
        if commit:
            instance.save()
        return instance

@admin.register(Grantha)
class GranthaAdmin(admin.ModelAdmin):
    form = GranthaAdminForm
    list_display = ['title', 'get_commentaries', 'get_tags', 'uploaded_at']
    search_fields = ['title', 'tags']
    readonly_fields = ['uploaded_at', 'last_modified']
    exclude = ['commentaries', 'tags']
    
    def get_commentaries(self, obj):
        return ', '.join(obj.commentaries) if obj.commentaries else 'None'
    get_commentaries.short_description = 'Commentaries'

    def get_tags(self, obj):
        return ', '.join(obj.tags) if obj.tags else 'None'
    get_tags.short_description = 'Tags'

@admin.register(Suggestion)
class SuggestionAdmin(admin.ModelAdmin):
    list_display = ['grantha', 'user_name', 'status', 'submitted_at']
    list_filter = ['status', 'submitted_at']
    search_fields = ['grantha__title', 'user_name', 'suggestion']
    readonly_fields = ['submitted_at']

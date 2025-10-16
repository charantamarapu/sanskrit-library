from django.contrib import admin
from django import forms
from .models import Grantha, Suggestion

class GranthaAdminForm(forms.ModelForm):
    commentaries_input = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 2, 'cols': 80}),
        help_text='Enter commentary names separated by commas (exactly as they appear in document headings)'
    )
    
    class Meta:
        model = Grantha
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.commentaries:
            self.fields['commentaries_input'].initial = ', '.join(self.instance.commentaries)
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        commentaries_str = self.cleaned_data.get('commentaries_input', '')
        if commentaries_str:
            instance.commentaries = [c.strip() for c in commentaries_str.split(',') if c.strip()]
        else:
            instance.commentaries = []
        if commit:
            instance.save()
        return instance

@admin.register(Grantha)
class GranthaAdmin(admin.ModelAdmin):
    form = GranthaAdminForm
    list_display = ['title', 'get_commentaries', 'uploaded_at']
    search_fields = ['title']
    readonly_fields = ['uploaded_at', 'last_modified']
    exclude = ['commentaries']
    
    def get_commentaries(self, obj):
        return ', '.join(obj.commentaries) if obj.commentaries else 'None'
    get_commentaries.short_description = 'Commentaries'

@admin.register(Suggestion)
class SuggestionAdmin(admin.ModelAdmin):
    list_display = ['grantha', 'user_name', 'status', 'submitted_at']
    list_filter = ['status', 'submitted_at']
    search_fields = ['grantha__title', 'user_name', 'suggestion']
    readonly_fields = ['submitted_at']

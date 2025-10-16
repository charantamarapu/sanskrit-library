from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import FileResponse
from .models import Grantha, Suggestion
from .serializers import GranthaSerializer, GranthaUploadSerializer, SuggestionSerializer
from .utils import filter_docx_by_commentaries
import os

class GranthaViewSet(viewsets.ModelViewSet):
    queryset = Grantha.objects.all()
    serializer_class = GranthaSerializer
    
    def get_serializer_class(self):
        if self.action == 'create':
            return GranthaUploadSerializer
        return GranthaSerializer
    
    @action(detail=True, methods=['post'])
    def filter(self, request, pk=None):
        """Filter document by selected commentaries"""
        grantha = self.get_object()
        selected = request.data.get('commentaries', [])
        
        print(f"\n{'='*70}")
        print(f"Grantha: {grantha.title}")
        print(f"All commentaries: {grantha.commentaries}")
        print(f"Selected: {selected}")
        print(f"{'='*70}\n")
        
        try:
            # Pass both ALL commentaries and SELECTED ones
            filter_data = {
                'all_commentaries': grantha.commentaries,
                'selected': selected  # Can be empty list
            }
            
            filtered_buffer = filter_docx_by_commentaries(grantha.file.path, filter_data)
            
            response = FileResponse(
                filtered_buffer,
                content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            )
            
            # Set filename based on selection
            if not selected or len(selected) == 0:
                filename = f"{grantha.title}_no_commentaries.docx"
            elif 'all' in selected:
                filename = f"{grantha.title}_complete.docx"
            else:
                filename = f"{grantha.title}_filtered.docx"
                
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
            
        except Exception as e:
            print(f"ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SuggestionViewSet(viewsets.ModelViewSet):
    queryset = Suggestion.objects.all()
    serializer_class = SuggestionSerializer

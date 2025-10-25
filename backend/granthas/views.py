from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.http import FileResponse, HttpResponse
from .models import Grantha, Suggestion
from .serializers import GranthaSerializer, GranthaUploadSerializer, SuggestionSerializer
from .utils import filter_docx_by_commentaries
import os


class GranthaViewSet(viewsets.ModelViewSet):
    queryset = Grantha.objects.all().order_by('-uploaded_at')
    serializer_class = GranthaSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return GranthaUploadSerializer
        return GranthaSerializer

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Download original document without filtering"""
        grantha = self.get_object()
        
        if not grantha.file:
            return Response(
                {'error': 'File not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        response = FileResponse(
            open(grantha.file.path, 'rb'),
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        response['Content-Disposition'] = f'attachment; filename="{grantha.title}.docx"'
        
        return response

    @action(detail=True, methods=['post'])
    def filter(self, request, pk=None):
        """Filter document by selected commentaries"""
        grantha = self.get_object()
        
        if not grantha.file:
            return Response(
                {'error': 'File not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        selected_commentaries = request.data.get('commentaries', [])
        
        # If "all" is selected, return original file directly without filtering
        if 'all' in selected_commentaries:
            response = FileResponse(
                open(grantha.file.path, 'rb'),
                content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            )
            response['Content-Disposition'] = f'attachment; filename="{grantha.title}.docx"'
            return response
        
        # Perform filtering
        try:
            filtered_buffer = filter_docx_by_commentaries(
                grantha.file.path,
                {
                    'all_commentaries': grantha.commentaries,
                    'selected': selected_commentaries
                }
            )
            
            response = HttpResponse(
                filtered_buffer.read(),
                content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            )
            # Removed "_filtered" suffix
            response['Content-Disposition'] = f'attachment; filename="{grantha.title}.docx"'
            
            return response
            
        except Exception as e:
            print(f"Error filtering document: {str(e)}")
            return Response(
                {'error': f'Failed to filter document: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SuggestionViewSet(viewsets.ModelViewSet):
    queryset = Suggestion.objects.all().order_by('-submitted_at')
    serializer_class = SuggestionSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        grantha_id = self.request.query_params.get('grantha', None)
        if grantha_id:
            queryset = queryset.filter(grantha_id=grantha_id)
        return queryset

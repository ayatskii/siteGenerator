from rest_framework import serializers
from .models import MediaFolder, MediaAsset, MediaAssetSiteData
from sites.models import Site

class MediaFolderSerializer(serializers.ModelSerializer):
    subfolders = serializers.SerializerMethodField()
    
    class Meta:
        model = MediaFolder
        fields = ['id', 'name', 'parent', 'owner', 'site', 'created_at', 'subfolders']
        read_only_fields = ['owner', 'created_at', 'subfolders']

    def get_subfolders(self, obj):
        serializer = MediaFolderSerializer(obj.subfolders.all(), many=True)
        return serializer.data

class MediaAssetSiteDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaAssetSiteData
        fields = ['id', 'site', 'alt_text', 'title', 'custom_filename']

class MediaAssetSerializer(serializers.ModelSerializer):
    site_data = MediaAssetSiteDataSerializer(many=True, read_only=True)
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = MediaAsset
        fields = ['id', 'file', 'filename', 'folder', 'owner', 'size', 'width', 'height', 'format', 'fingerprint_hash', 'created_at', 'site_data', 'file_url']
        read_only_fields = ['owner', 'size', 'width', 'height', 'format', 'fingerprint_hash', 'created_at', 'file_url']

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and hasattr(obj.file, 'url'):
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None

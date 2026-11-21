from rest_framework import serializers
from pathlib import Path


#validating incoming data from frontend
class ChatRequestSerializer(serializers.Serializer):
    participant = serializers.CharField(max_length = 100)
    message = serializers.CharField(
        allow_blank = False,
        trim_whitespace = True
    )

#validating file uploading by user from frontend
class ChatUploadSerializer(serializers.Serializer):
    file = serializers.FileField()

    def validate_file(self, file):
        #check extension
        if Path(file.name).suffix.lower() != '.txt':
            raise serializers.ValidationError(
                "Only whatsapp .txt exports are supported"
            )

        #check file size
        if file.size > 5 * 1024 * 1024:
            raise serializers.ValidationError(
                "File must be smaller than 5MB"
            )

        #check encoding
        try:
            file.seek(0)
            content = file.read().decode("utf-8-sig")
        except UnicodeDecodeError:
            raise serializers.ValidationError(
                "File must contain UTF-8 text."
            )
        finally:
            file.seek(0) #moving file pointer to the start

        #check if file is empty
        if not content.strip():
            raise serializers.ValidationError(
                "File cannot be empty."
            )
        
        return file
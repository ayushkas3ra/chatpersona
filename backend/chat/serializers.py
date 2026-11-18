from rest_framework import serializers

#validating incoming data from frontend
class ChatRequestSerializer(serializers.Serializer):
    participant = serializers.CharField(max_length = 100)
    message = serializers.CharField(
        allow_blank = False,
        trim_whitespace = True
    )
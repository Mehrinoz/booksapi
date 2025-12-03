from rest_framework import serializers

from .models import Topic, QuizQuestion


class QuizQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizQuestion
        fields = [
            "id",
            "question",
            "option_a",
            "option_b",
            "option_c",
            "option_d",
            "correct_option",
        ]


class TopicSerializer(serializers.ModelSerializer):
    questions = QuizQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Topic
        fields = ["id", "title", "pdf", "quiz_file", "status", "questions"]


class TopicStatusSerializer(serializers.ModelSerializer):
    """Serializer used faqat status ni o'zgartirish uchun."""

    class Meta:
        model = Topic
        fields = ["status"]


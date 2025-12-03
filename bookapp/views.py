from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .models import Topic, QuizQuestion
from .serializers import TopicSerializer, TopicStatusSerializer


class TopicViewSet(viewsets.ModelViewSet):
    """
    Provides read/write operations over Topic resources and handles
    quiz completion logic.
    """

    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    http_method_names = ["get", "put", "patch", "head", "options"]

    def get_serializer_class(self):
        # Detail update (PUT/PATCH) sahifasida faqat status maydonini ko'rsatamiz.
        if self.action in ["update", "partial_update"]:
            return TopicStatusSerializer
        return TopicSerializer

    def perform_create(self, serializer):
        # Yangi topic har doim boshlang'ich holatda (status=0) yaratiladi.
        serializer.save(status=0)

    def perform_update(self, serializer):
        topic = serializer.instance
        requested_status = serializer.validated_data.get("status", topic.status)

        # Faqat status maydonini boshqaramiz (TopicStatusSerializer)
        # Agar oldingi topiclar tugallanmagan bo'lsa, xato qaytarmaymiz,
        # shunchaki statusni o'zgartirmaymiz.
        if requested_status == 1 and topic.status != 1:
            can_complete = self._ensure_previous_topics_completed(topic)
            if not can_complete:
                # Oldingi topiclar hali 1 emas – holatni o'zgartirmaymiz.
                serializer.validated_data["status"] = topic.status
                serializer.save()
                return

        serializer.save()

    @action(detail=True, methods=["post"], url_path="complete_quiz")
    def complete_quiz(self, request, pk=None):
        topic = self.get_object()

        if not topic.has_quiz:
            raise ValidationError({"detail": "This topic does not contain a quiz."})

        # Agar oldingi topiclar hali tugallanmagan bo'lsa, xato emas,
        # faqat bu topicni ham tugallangan deb belgilamaymiz.
        if not self._ensure_previous_topics_completed(topic):
            return Response(
                {
                    "detail": "Previous topics are not completed yet.",
                    "can_complete": False,
                },
                status=status.HTTP_200_OK,
            )

        score = self._calculate_score(topic, request.data)
        if score < 60:
            return Response(
                {"detail": "Score is below the 60% threshold.", "score": score},
                status=status.HTTP_400_BAD_REQUEST,
            )

        topic.status = 1
        topic.save(update_fields=["status"])
        serializer = self.get_serializer(topic)
        return Response({"topic": serializer.data, "score": score}, status=status.HTTP_200_OK)

    def _ensure_previous_topics_completed(self, topic: Topic) -> bool:
        """
        Oldingi topiclar (id < current.id) hammasi status=1 bo'lgan-bo'lmaganini
        tekshiradi. True – hammasi tugallangan, False – hali tugallanmaganlari bor.
        """
        has_incomplete = Topic.objects.filter(id__lt=topic.id, status__lt=1).exists()
        return not has_incomplete

    def _calculate_score(self, topic: Topic, payload: dict) -> float:
        answers = payload.get("answers")
        questions = QuizQuestion.objects.filter(topic=topic).order_by("id")

        if not questions.exists():
            raise ValidationError({"detail": "No quiz questions found for this topic."})

        if answers is None:
            score = payload.get("score")
            if score is None:
                raise ValidationError({"detail": "Provide answers or score to validate quiz."})
            try:
                score_value = float(score)
            except (TypeError, ValueError) as exc:
                raise ValidationError({"detail": "Score must be a number."}) from exc
            return score_value

        if not isinstance(answers, list):
            raise ValidationError({"detail": "Answers must be provided as a list."})

        total_questions = questions.count()
        correct_answers = 0
        for idx, question in enumerate(questions):
            if idx < len(answers) and str(answers[idx]).lower() == question.correct_option:
                correct_answers += 1

        if total_questions == 0:
            raise ValidationError({"detail": "Quiz is not properly configured."})

        return (correct_answers / total_questions) * 100

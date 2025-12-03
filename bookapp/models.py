from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Topic(models.Model):
    """
    Topic represents a single learning unit inside the Voice platform.
    """

    title = models.CharField(max_length=255)
    pdf = models.FileField(upload_to="pdfs/", blank=True, null=True)
    quiz_file = models.FileField(
        upload_to="quizzes/",
        blank=True,
        null=True,
        help_text="Matn fayl (txt) formatida: savol, A) ..., B) ..., C) ..., D) ..., Javob: X",
    )
    status = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        help_text="0 - not completed, 1 - completed",
    )

    class Meta:
        ordering = ["id"]

    def __str__(self) -> str:
        return self.title

    @property
    def has_quiz(self) -> bool:
        return self.questions.exists()

    def import_quiz_from_file(self) -> None:
        """
        quiz_file dan savollarni o'qib, QuizQuestion obyektlarini yaratadi.

        Kutilgan format (har blok 6 qatordan iborat):

        Qaysi HTML teg Veb sahifaga tashqi CSS faylini ulash uchun ishlatiladi?
        A) <style>
        B) <link>
        C) <script>
        D) <meta>
        Javob: B
        """
        if not self.quiz_file:
            return

        filename = (self.quiz_file.name or "").lower()
        content = ""

        # DOCX fayl
        if filename.endswith(".docx"):
            try:
                from docx import Document
            except ImportError:
                # Kutubxona o'rnatilmagan bo'lsa, admin 500 bermasin
                # Shunchaki hech narsa qilmaymiz.
                return

            doc = Document(self.quiz_file)
            content = "\n".join(p.text for p in doc.paragraphs)
        # Oddiy matn fayl (TXT va boshqalar)
        else:
            self.quiz_file.open("rb")
            try:
                raw = self.quiz_file.read()
            finally:
                self.quiz_file.close()

            # Avval UTF-8, keyin Windows kodirovkasi (cp1251) bilan urinib ko'ramiz
            try:
                content = raw.decode("utf-8")
            except UnicodeDecodeError:
                content = raw.decode("cp1251", errors="ignore")

        # Eski savollarni o'chiramiz
        self.questions.all().delete()

        lines = [line.strip() for line in content.splitlines() if line.strip()]
        i = 0

        while i + 5 < len(lines):
            question_text = lines[i]
            option_a_line = lines[i + 1]
            option_b_line = lines[i + 2]
            option_c_line = lines[i + 3]
            option_d_line = lines[i + 4]
            answer_line = lines[i + 5]

            def clean_option(line):
                # "A) <style>" -> "<style>"
                if ")" in line:
                    return line.split(")", 1)[1].strip()
                return line.strip()

            option_a = clean_option(option_a_line)
            option_b = clean_option(option_b_line)
            option_c = clean_option(option_c_line)
            option_d = clean_option(option_d_line)

            # "Javob: B" -> "b"
            correct = None
            if ":" in answer_line:
                correct = answer_line.split(":", 1)[1].strip().lower()[:1]

            if correct not in {"a", "b", "c", "d"}:
                # Agar format xato bo'lsa, bu blokni tashlab ketamiz
                i += 6
                continue

            QuizQuestion.objects.create(
                topic=self,
                question=question_text,
                option_a=option_a,
                option_b=option_b,
                option_c=option_c,
                option_d=option_d,
                correct_option=correct,
            )

            i += 6


class QuizQuestion(models.Model):
    """
    Single quiz question with 4 options bound to a Topic.
    """

    OPTION_CHOICES = [
        ("a", "A"),
        ("b", "B"),
        ("c", "C"),
        ("d", "D"),
    ]

    topic = models.ForeignKey(
        Topic, related_name="questions", on_delete=models.CASCADE
    )
    question = models.TextField()
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    correct_option = models.CharField(max_length=1, choices=OPTION_CHOICES)

    class Meta:
        ordering = ["id"]

    def __str__(self) -> str:
        return f"{self.topic.title} - {self.question[:50]}"

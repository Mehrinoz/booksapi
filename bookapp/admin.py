from django.contrib import admin

from .models import Topic, QuizQuestion


class QuizQuestionInline(admin.TabularInline):
    model = QuizQuestion
    extra = 1


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "status")
    search_fields = ("title",)
    list_filter = ("status",)
    ordering = ("id",)
    inlines = [QuizQuestionInline]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Agar quiz_file yuklangan bo'lsa, undan savollarni import qilamiz
        if obj.quiz_file:
            obj.import_quiz_from_file()


@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "topic", "question", "correct_option")
    search_fields = ("question", "topic__title")
    list_filter = ("correct_option",)

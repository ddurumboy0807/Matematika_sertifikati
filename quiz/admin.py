from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Avg
from .models import Question, QuizResult


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['id', 'level_badge', 'short_text', 'correct_letter_display', 'created_at']
    list_filter = ['level']
    search_fields = ['text', 'option_a', 'option_b', 'option_c', 'option_d']
    list_per_page = 30
    ordering = ['level', 'id']

    fieldsets = (
        ('Savol', {
            'fields': ('level', 'text')
        }),
        ('Variantlar', {
            'fields': ('option_a', 'option_b', 'option_c', 'option_d', 'correct_answer'),
            'description': 'To\'g\'ri javobni quyida tanlang'
        }),
    )

    def level_badge(self, obj):
        colors = {
            'C': '#ffc470', 'CP': '#ffb450', 'B': '#7ab2f2',
            'BP': '#5599ee', 'A': '#6bc99a', 'AP': '#4caf82'
        }
        color = colors.get(obj.level, '#aaa')
        return format_html(
            '<span style="background:{};color:#111;padding:2px 10px;border-radius:12px;font-weight:700;">{}</span>',
            color, obj.get_level_display().split('—')[0].strip()
        )
    level_badge.short_description = 'Daraja'

    def short_text(self, obj):
        return obj.text[:70] + '...' if len(obj.text) > 70 else obj.text
    short_text.short_description = 'Savol'

    def correct_letter_display(self, obj):
        letters = {0: 'A', 1: 'B', 2: 'C', 3: 'D'}
        letter = letters.get(obj.correct_answer, '?')
        opts = [obj.option_a, obj.option_b, obj.option_c, obj.option_d]
        answer_text = opts[obj.correct_answer] if obj.correct_answer < len(opts) else ''
        return format_html(
            '<strong style="color:#4caf82">{}</strong>: {}',
            letter, answer_text[:40]
        )
    correct_letter_display.short_description = "To'g'ri javob"


@admin.register(QuizResult)
class QuizResultAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_name_display', 'level_badge', 'score_display', 'grade_badge', 'percentage_display', 'created_at']
    list_filter = ['level', 'grade', 'created_at']
    search_fields = ['user_name', 'session_key', 'ip_address']
    readonly_fields = ['session_key', 'created_at', 'ip_address']
    list_per_page = 25
    ordering = ['-created_at']

    def user_name_display(self, obj):
        if obj.user_name:
            return obj.user_name
        return format_html('<em style="color:#888">{}</em>', obj.session_key[:8] + '...')
    user_name_display.short_description = 'Foydalanuvchi'

    def level_badge(self, obj):
        colors = {
            'C': '#ffc470', 'CP': '#ffb450', 'B': '#7ab2f2',
            'BP': '#5599ee', 'A': '#6bc99a', 'AP': '#4caf82'
        }
        color = colors.get(obj.level, '#aaa')
        return format_html(
            '<span style="background:{};color:#111;padding:2px 10px;border-radius:12px;font-weight:700;">{}</span>',
            color, obj.level.replace('CP','C+').replace('BP','B+').replace('AP','A+')
        )
    level_badge.short_description = 'Daraja'

    def score_display(self, obj):
        pct = obj.percentage
        color = '#4caf82' if pct >= 80 else '#ffb450' if pct >= 60 else '#e05555'
        return format_html(
            '<span style="color:{};font-weight:700">{}/{}</span>',
            color, obj.score, obj.total
        )
    score_display.short_description = "Natija"

    def grade_badge(self, obj):
        colors = {
            'A+': '#4caf82', 'A': '#6bc99a', 'B+': '#5599ee',
            'B': '#7ab2f2', 'C+': '#ffb450', 'C': '#ffc470', '—': '#e05555'
        }
        color = colors.get(obj.grade, '#888')
        return format_html(
            '<span style="background:{};color:#fff;padding:3px 12px;border-radius:12px;font-weight:700;">{}</span>',
            color, obj.grade
        )
    grade_badge.short_description = 'Baho'

    def percentage_display(self, obj):
        return f"{obj.percentage:.1f}%"
    percentage_display.short_description = 'Foiz'

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        from django.db.models import Count, Avg
        stats = QuizResult.objects.aggregate(
            total=Count('id'),
            avg_score=Avg('percentage'),
        )
        extra_context['stats'] = stats
        return super().changelist_view(request, extra_context=extra_context)

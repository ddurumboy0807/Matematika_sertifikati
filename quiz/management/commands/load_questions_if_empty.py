"""
Savollar bo'sh bo'lsa yuklaydi (Railway deploy uchun).
Ishlatish: python manage.py load_questions_if_empty
"""
import json
import os
from django.core.management.base import BaseCommand
from quiz.models import Question


class Command(BaseCommand):
    help = 'Agar savollar yo\'q bo\'lsa, yuklaydi'

    def handle(self, *args, **options):
        if Question.objects.exists():
            self.stdout.write(self.style.WARNING(
                f'Savollar allaqachon mavjud ({Question.objects.count()} ta). O\'tkazib yuborildi.'
            ))
            return

        json_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'questions_data.json'
        )

        if not os.path.exists(json_path):
            self.stdout.write(self.style.ERROR(f'Fayl topilmadi: {json_path}'))
            return

        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        total_created = 0
        for level_key, questions in data.items():
            created = 0
            for q in questions:
                opts = q['opts']
                while len(opts) < 4:
                    opts.append('')
                Question.objects.create(
                    level=level_key,
                    text=q['q'],
                    option_a=opts[0],
                    option_b=opts[1],
                    option_c=opts[2],
                    option_d=opts[3],
                    correct_answer=q['ans'],
                )
                created += 1
            self.stdout.write(self.style.SUCCESS(f'✓ {level_key}: {created} ta savol'))
            total_created += created

        self.stdout.write(self.style.SUCCESS(f'🎉 Jami {total_created} ta savol yuklandi!'))

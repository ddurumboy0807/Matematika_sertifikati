"""
Savollarni ma'lumotlar bazasiga yuklash buyrug'i.
Ishlatish: python manage.py load_questions
"""
import json
import os
from django.core.management.base import BaseCommand
from quiz.models import Question


class Command(BaseCommand):
    help = 'Matematika savollarini ma\'lumotlar bazasiga yuklaydi'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Avvalgi savollarni o\'chirish',
        )

    def handle(self, *args, **options):
        if options['clear']:
            count = Question.objects.all().count()
            Question.objects.all().delete()
            self.stdout.write(self.style.WARNING(f'{count} ta savol o\'chirildi'))

        json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'questions_data.json')
        
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
            
            self.stdout.write(
                self.style.SUCCESS(f'✓ {level_key} darajasi: {created} ta savol yuklandi')
            )
            total_created += created

        self.stdout.write(
            self.style.SUCCESS(f'\n🎉 Jami {total_created} ta savol muvaffaqiyatli yuklandi!')
        )

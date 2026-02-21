from django.db import models
from django.contrib.auth.models import User
import json


LEVEL_CHOICES = [
    ('C', 'C — Asosiy daraja'),
    ('CP', 'C+ — Kengaytirilgan C'),
    ('B', 'B — O\'rta daraja'),
    ('BP', 'B+ — Kengaytirilgan B'),
    ('A', 'A — Yuqori daraja'),
    ('AP', 'A+ — Mukammal daraja'),
]


class Question(models.Model):
    level = models.CharField(max_length=2, choices=LEVEL_CHOICES, verbose_name="Daraja")
    text = models.TextField(verbose_name="Savol matni")
    option_a = models.CharField(max_length=200, verbose_name="Variant A")
    option_b = models.CharField(max_length=200, verbose_name="Variant B")
    option_c = models.CharField(max_length=200, verbose_name="Variant C")
    option_d = models.CharField(max_length=200, verbose_name="Variant D")
    correct_answer = models.IntegerField(
        choices=[(0,'A'),(1,'B'),(2,'C'),(3,'D')],
        verbose_name="To'g'ri javob"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Savol"
        verbose_name_plural = "Savollar"
        ordering = ['level', 'id']

    def __str__(self):
        return f"[{self.level}] {self.text[:60]}"

    def get_options(self):
        return [self.option_a, self.option_b, self.option_c, self.option_d]

    def correct_letter(self):
        return ['A','B','C','D'][self.correct_answer]


class QuizResult(models.Model):
    session_key = models.CharField(max_length=40, verbose_name="Sessiya")
    user_name = models.CharField(max_length=100, blank=True, verbose_name="Foydalanuvchi ismi")
    level = models.CharField(max_length=2, choices=LEVEL_CHOICES, verbose_name="Daraja")
    score = models.IntegerField(verbose_name="To'g'ri javoblar")
    total = models.IntegerField(default=45, verbose_name="Jami savollar")
    grade = models.CharField(max_length=10, verbose_name="Baho")
    percentage = models.FloatField(verbose_name="Foiz")
    time_taken = models.IntegerField(default=0, verbose_name="Sarflangan vaqt (soniya)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Sana")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP manzil")

    class Meta:
        verbose_name = "Natija"
        verbose_name_plural = "Natijalar"
        ordering = ['-created_at']

    def __str__(self):
        name = self.user_name or self.session_key[:8]
        return f"{name} — [{self.level}] {self.score}/{self.total} ({self.grade})"

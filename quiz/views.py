from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
import random
from .models import Question, QuizResult

LEVEL_MAP = {
    '0': 'C', '1': 'CP', '2': 'B', '3': 'BP', '4': 'A', '5': 'AP'
}

LEVEL_DISPLAY = {
    'C': 'C', 'CP': 'C+', 'B': 'B', 'BP': 'B+', 'A': 'A', 'AP': 'A+'
}

def get_grade(score, total=45):
    if score >= 43: return 'A+'
    elif score >= 40: return 'A'
    elif score >= 36: return 'B+'
    elif score >= 32: return 'B'
    elif score >= 27: return 'C+'
    elif score >= 23: return 'C'
    else: return '-'


def home(request):
    return render(request, 'quiz/home.html')


def level_select(request):
    levels_data = {}
    for level_key, level_display in LEVEL_DISPLAY.items():
        count = Question.objects.filter(level=level_key).count()
        levels_data[level_key] = {
            'display': level_display,
            'count': count,
        }
    return render(request, 'quiz/level_select.html', {'levels_data': levels_data})


def start_quiz(request, level_num):
    level_key = LEVEL_MAP.get(str(level_num))
    if not level_key:
        return redirect('home')

    questions_qs = list(Question.objects.filter(level=level_key).values(
        'id', 'text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer'
    ))

    selected = random.sample(questions_qs, min(45, len(questions_qs)))

    quiz_questions = []
    for q in selected:
        opts = [q['option_a'], q['option_b'], q['option_c'], q['option_d']]
        correct_text = opts[q['correct_answer']]
        shuffled = opts[:]
        random.shuffle(shuffled)
        new_correct = shuffled.index(correct_text)
        quiz_questions.append({
            'id': q['id'],
            'text': q['text'],
            'opts': shuffled,
            'correct': new_correct,
        })

    request.session['quiz_questions'] = quiz_questions
    request.session['quiz_level'] = level_key
    request.session['quiz_score'] = 0
    request.session['quiz_current'] = 0
    request.session['quiz_answers'] = []
    request.session.modified = True

    return redirect('quiz')


def quiz_view(request):
    questions = request.session.get('quiz_questions')
    level_key = request.session.get('quiz_level')
    current = request.session.get('quiz_current', 0)

    if not questions or not level_key:
        return redirect('home')

    if current >= len(questions):
        return redirect('result')

    q = questions[current]
    total = len(questions)
    labels = ['A', 'B', 'C', 'D']

    context = {
        'question': q,
        'current': current + 1,
        'total': total,
        'progress': round((current / total) * 100),
        'level': LEVEL_DISPLAY.get(level_key, level_key),
        'level_key': level_key,
        'labels': labels,
        'opts_with_labels': list(zip(labels, q['opts'])),
    }
    return render(request, 'quiz/quiz.html', context)


@csrf_exempt
@require_POST
def answer_question(request):
    try:
        data = json.loads(request.body)
        selected = int(data.get('selected', -1))
    except Exception:
        selected = -1

    questions = request.session.get('quiz_questions', [])
    current = request.session.get('quiz_current', 0)
    score = request.session.get('quiz_score', 0)
    answers = request.session.get('quiz_answers', [])

    if current >= len(questions):
        return JsonResponse({'redirect': '/result/'})

    q = questions[current]
    correct = q['correct']
    is_correct = (selected == correct)

    if is_correct:
        score += 1

    answers.append({
        'question_id': q['id'],
        'selected': selected,
        'correct': correct,
        'is_correct': is_correct,
    })

    request.session['quiz_score'] = score
    request.session['quiz_current'] = current + 1
    request.session['quiz_answers'] = answers
    request.session.modified = True

    next_current = current + 1
    is_last = next_current >= len(questions)

    return JsonResponse({
        'is_correct': is_correct,
        'correct_index': correct,
        'is_last': is_last,
        'score': score,
    })


def result_view(request):
    score = request.session.get('quiz_score', 0)
    level_key = request.session.get('quiz_level')
    total = len(request.session.get('quiz_questions', []))

    if not level_key or total == 0:
        return redirect('home')

    grade = get_grade(score, total)
    pct = round((score / total) * 100, 1)
    wrong = total - score

    user_name = request.session.get('user_name', '')
    result = QuizResult.objects.create(
        session_key=request.session.session_key or 'anon',
        user_name=user_name,
        level=level_key,
        score=score,
        total=total,
        grade=grade,
        percentage=pct,
        ip_address=request.META.get('REMOTE_ADDR'),
    )

    grade_colors = {
        'A+': '#4caf82', 'A': '#6bc99a', 'B+': '#5599ee',
        'B': '#7ab2f2', 'C+': '#ffb450', 'C': '#ffc470', '-': '#e05555'
    }

    grade_messages = {
        'A+': ('Ajoyib! Mukammal natija!', 'Siz ushbu darajani toliq egallagan ekansiz!'),
        'A': ('Zor! A darajasi!', 'Bilimingiz juda yuqori.'),
        'B+': ('Yaxshi! B+ natijasi!', 'A darajasiga yetish uchun mavzularni takrorlang.'),
        'B': ('B natijasi', 'Orta-yuqori daraja.'),
        'C+': ('C+ natijasi', 'Mavzularni chuqurroq organing.'),
        'C': ('C natijasi', 'Asosiy bilimlar bor, lekin koproq mashq kerak.'),
        '-': ('Davom eting!', 'Pastroq darajadan boshlang.'),
    }

    title, message = grade_messages.get(grade, ('Natija', ''))

    context = {
        'score': score,
        'wrong': wrong,
        'total': total,
        'pct': pct,
        'grade': grade,
        'grade_color': grade_colors.get(grade, '#888'),
        'level': LEVEL_DISPLAY.get(level_key, level_key),
        'level_key': level_key,
        'title': title,
        'message': message,
        'result_id': result.id,
    }

    for key in ['quiz_questions', 'quiz_score', 'quiz_current', 'quiz_answers', 'quiz_level']:
        request.session.pop(key, None)

    return render(request, 'quiz/result.html', context)


def leaderboard(request):
    results = QuizResult.objects.order_by('-percentage', '-score', 'created_at')[:50]
    return render(request, 'quiz/leaderboard.html', {'results': results})
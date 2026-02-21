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
    pct = (score / total) * 100
    if score >= 43: return 'A+'
    elif score >= 40: return 'A'
    elif score >= 36: return 'B+'
    elif score >= 32: return 'B'
    elif score >= 27: return 'C+'
    elif score >= 23: return 'C'
    else: return '—'


def home(request):
    return render(request, 'quiz/home.html')


def level_select(request):
    from django.db.models import Count
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

    if len(questions_qs) < 45:
        # fallback: repeat if not enough
        pass

    selected = random.sample(questions_qs, min(45, len(questions_qs)))

    # Shuffle options for each question
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


@require_POST
def answer_question(request):
    try:
        data = json.loads(request.body)
        selected = int(data.get('selected', -1))
    except Exception:
        return JsonResponse({'error': 'Invalid'}, status=400)

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
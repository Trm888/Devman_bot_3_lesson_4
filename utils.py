import os
import pathlib


def get_questions_answers():
    path = pathlib.Path.cwd() / 'quiz-questions'
    files = os.listdir(path)
    questions = []
    answers = []
    for file in files:
        with open(path / file, 'r', encoding='KOI8-R') as f:
            file_content = f.read()
        blocks = file_content.split('\n\n')
        for block in blocks:
            block = block.strip()
            if block.startswith('Вопрос'):
                question_lines = block.split('\n')[1:]
                questions.append(' '.join(question_lines))
            elif block.startswith('Ответ'):
                answer_lines = block.split('\n')[1:]
                answers.append(' '.join(answer_lines))

    questions_answers = dict(zip(questions, answers))
    return questions_answers

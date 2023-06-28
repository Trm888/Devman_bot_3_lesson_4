import os
import pathlib


def get_questions_answers():
    files = os.listdir(pathlib.PurePath.joinpath(pathlib.Path.cwd(), 'quiz-questions'))
    print(files)
    questions = []
    answers = []
    for file in files:
        with open(pathlib.PurePath.joinpath(pathlib.Path.cwd(), 'quiz-questions', file), 'r', encoding='KOI8-R') as f:
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

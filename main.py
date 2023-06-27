import os

files = os.listdir(os.path.join(os.getcwd(), 'quiz-questions'))
for file in files:
    with open(os.path.join(os.getcwd(), 'quiz-questions', file), 'r', encoding='KOI8-R') as f:
        file_content = f.read()

    blocks = file_content.split('\n\n')
    questions = []
    answers = []
    for block in blocks:
        if block.startswith('Вопрос'):
            question_lines = block.split('\n')[1:]
            questions.append(''.join(question_lines))
        elif block.startswith('Ответ'):
            answer_lines = block.split('\n')[1:]
            answers.append(''.join(answer_lines))

    questions_answers = dict(zip(questions, answers))
    print(questions_answers)


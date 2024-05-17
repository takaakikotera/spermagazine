from flask import Flask, render_template, request, redirect, url_for, session, flash
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'default_secret_key')

# Load the diagnostic data
file_path = 'diagnosis_tool.xlsx'
xls = pd.ExcelFile(file_path)
diagnostic_tool_df = pd.read_excel(xls, '診断ツール', header=None)

# 手動で列名を設定
diagnostic_tool_df.columns = ['Question', 'Choice', 'Score', 'Reference']

# データの抽出
questions = diagnostic_tool_df['Question']
choices = diagnostic_tool_df['Choice']
scores = diagnostic_tool_df['Score']
references = diagnostic_tool_df['Reference']

diagnostic_data = pd.DataFrame({
    'Question': questions,
    'Choice': choices,
    'Score': scores,
    'Reference': references
})

# デバッグ用の出力
print("Diagnostic Data:")
print(diagnostic_data)

@app.route('/')
def index():
    session.clear()
    return render_template('index.html')

@app.route('/question/<int:id>', methods=['GET', 'POST'])
def question(id):
    try:
        if id >= len(diagnostic_data):
            return "Question ID out of range", 404

        if request.method == 'POST':
            answer = request.form.get('choice')
            if answer is None:
                flash('Please select an option before proceeding.')
                return redirect(url_for('question', id=id))
            if 'answers' not in session:
                session['answers'] = []
            session['answers'].append(answer)
            print(f"Answers so far: {session['answers']}")  # デバッグ用の出力

            if id < len(diagnostic_data) - 1:
                return redirect(url_for('question', id=id + 1))
            else:
                return redirect(url_for('analysis'))

        question = diagnostic_data['Question'].iloc[id]
        choice_list = diagnostic_data['Choice'].iloc[id].split(',')
        reference = diagnostic_data['Reference'].iloc[id]
        progress = (id + 1) / len(diagnostic_data) * 100

        return render_template('question.html', question=question, choices=choice_list, reference=reference, progress=progress)
    except Exception as e:
        return str(e)

@app.route('/analysis')
def analysis():
    return render_template('analysis.html')

@app.route('/result')
def result():
    answers = session.get('answers', [])
    print(f"Final Answers: {answers}")  # デバッグ用の出力
    score = calculate_score(answers)
    return render_template('result.html', score=score)

def calculate_score(answers):
    total_score = 0
    for i, answer in enumerate(answers):
        choice_list = diagnostic_data['Choice'].iloc[i].split(',')
        score_list = diagnostic_data['Score'].iloc[i].split(',')
        score_dict = {c.strip(): s.strip() for c, s in zip(choice_list, score_list)}
        print(f"Question {i}:")
        print(f"Answer: {answer}")
        print(f"Choices: {choice_list}")
        print(f"Scores: {score_list}")
        print(f"Score Dict: {score_dict}")
        if answer in score_dict:
            total_score += float(score_dict[answer])
        else:
            print(f"Answer '{answer}' not found in choices.")
    print(f"Total Score: {total_score}")
    return total_score

if __name__ == '__main__':
    app.run(debug=True)

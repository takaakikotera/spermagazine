from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Load the diagnostic data
file_path = '/mnt/data/メディア＆診断ツール.xlsx'
xls = pd.ExcelFile(file_path)
diagnostic_tool_df = pd.read_excel(xls, '診断ツール')

# Clean and prepare the data
diagnostic_tool_clean_df = diagnostic_tool_df.dropna(how='all').reset_index(drop=True)
questions = diagnostic_tool_clean_df.iloc[2:, 1].dropna().reset_index(drop=True)
choices = diagnostic_tool_clean_df.iloc[2:, 2].dropna().reset_index(drop=True)
scores = diagnostic_tool_clean_df.iloc[2:, 3].dropna().reset_index(drop=True)
references = diagnostic_tool_clean_df.iloc[2:, 5].dropna().reset_index(drop=True)

# Combine into a single DataFrame for easier manipulation
diagnostic_data = pd.DataFrame({
    'Question': questions,
    'Choice': choices,
    'Score': scores,
    'Reference': references
})

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/question/<int:id>', methods=['GET', 'POST'])
def question(id):
    if request.method == 'POST':
        # Save the answer
        answer = request.form['choice']
        if 'answers' not in session:
            session['answers'] = []
        session['answers'].append(answer)
        
        # Redirect to the next question
        if id < len(diagnostic_data) - 1:
            return redirect(url_for('question', id=id + 1))
        else:
            return redirect(url_for('analysis'))

    question = diagnostic_data['Question'].iloc[id]
    choice_list = diagnostic_data['Choice'].iloc[id].split('、')
    reference = diagnostic_data['Reference'].iloc[id]
    progress = (id + 1) / len(diagnostic_data) * 100

    return render_template('question.html', question=question, choices=choice_list, reference=reference, progress=progress)

@app.route('/analysis')
def analysis():
    return render_template('analysis.html')

@app.route('/result')
def result():
    # Calculate the score
    answers = session.get('answers', [])
    score = calculate_score(answers)
    return render_template('result.html', score=score)

def calculate_score(answers):
    total_score = 0
    for i, answer in enumerate(answers):
        choice_list = diagnostic_data['Choice'].iloc[i].split('、')
        score_list = diagnostic_data['Score'].iloc[i].split('、')
        score_dict = dict(zip(choice_list, score_list))
        total_score += float(score_dict.get(answer, 0))
    return total_score

if __name__ == '__main__':
    app.run(debug=True)

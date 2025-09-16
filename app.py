from flask import Flask, render_template, request, redirect, url_for
import csv
from pathlib import Path
from datetime import datetime

app = Flask(__name__)

# Ensure data directory exists
Path("data").mkdir(parents=True, exist_ok=True)

# Quiz questions - edit here to change questions or options
QUESTIONS = [
    {
        'id': 'q1',
        'text': 'Do you prefer studying in the morning or evening?',
        'options': [
            {'value': 'morning', 'label': 'Morning'},
            {'value': 'evening', 'label': 'Evening'}
        ]
    },
    {
        'id': 'q2',
        'text': 'Do you prefer reading in silence or with background music?',
        'options': [
            {'value': 'silence', 'label': 'Silence'},
            {'value': 'music', 'label': 'Background Music'}
        ]
    },
    {
        'id': 'q3',
        'text': 'Do you prefer working alone or in a group?',
        'options': [
            {'value': 'alone', 'label': 'Alone'},
            {'value': 'group', 'label': 'In a Group'}
        ]
    }
]

# Result texts - edit here to change result messages
RESULT_TEXTS = {
    'introvert': 'You are more introvert.',
    'extrovert': 'You are more extrovert.'
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/quiz')
def quiz():
    return render_template('quiz.html', questions=QUESTIONS)

@app.route('/submit', methods=['POST'])
def submit():
    # Get answers from form
    answers = {}
    for question in QUESTIONS:
        answers[question['id']] = request.form.get(question['id'])
    
    # Calculate result based on majority rule
    first_option_count = 0
    for question in QUESTIONS:
        if answers[question['id']] == question['options'][0]['value']:
            first_option_count += 1
    
    # Determine result (tie defaults to introvert)
    if first_option_count >= 2:
        result = 'introvert'
    else:
        result = 'extrovert'
    
    # Save to CSV
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open('data/results.csv', 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            timestamp, 
            answers['q1'], 
            answers['q2'], 
            answers['q3'], 
            result
        ])
    
    return redirect(url_for('result', result=result))

@app.route('/result')
def result():
    result_type = request.args.get('result', 'introvert')
    result_text = RESULT_TEXTS.get(result_type, RESULT_TEXTS['introvert'])
    return render_template('result.html', result=result_text)

@app.route('/all')
def all_submissions():
    submissions = []
    csv_path = Path('data/results.csv')
    
    if csv_path.exists():
        with open(csv_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if len(row) == 5:  # Ensure valid row
                    submissions.append({
                        'timestamp': row[0],
                        'q1': row[1],
                        'q2': row[2],
                        'q3': row[3],
                        'result': row[4]
                    })
    
    # Sort by timestamp, newest first
    submissions.sort(key=lambda x: x['timestamp'], reverse=True)
    
    return render_template('all.html', submissions=submissions)

if __name__ == '__main__':
    app.run(debug=True)
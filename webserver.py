from flask import Flask, render_template, request, session, redirect, url_for
from app import BayesianMBTIApp
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Needed for session

# Initialize the MBTI app
mbti_app = BayesianMBTIApp()

@app.route('/')
def index():
    session.clear()
    return render_template('index.html')

@app.route('/test', methods=['GET', 'POST'])
def test():
    # Initialize test if it's the first visit
    if 'remaining_indices' not in session:
        session['remaining_indices'] = list(range(len(mbti_app.questions)))
        session['asked_questions'] = 0
        session['probabilities'] = {mbti_type: 1/16 for mbti_type in mbti_app.mbti_types}
        session['current_question_index'] = None

    if request.method == 'GET':
        try:
            name = request.args['name']
            email = request.args['email']
            mbti_app.set_email(email)
            mbti_app.set_name(name)
        except:
            pass

    # Process answer if POST
    if request.method == 'POST' and 'answer' in request.form:
        answer = int(request.form['answer'])
        question_index = session['current_question_index']

        # Get the question and likelihoods
        if question_index is None:
            return redirect(url_for('index'))
        question, likelihoods = mbti_app.questions[question_index]

        # Update probabilities based on the answer
        probabilities = session['probabilities']
        new_probabilities = {}

        # Apply Bayesian update
        for mbti_type in mbti_app.mbti_types:
            type_likelihood = 1.0
            answer_likelihoods = likelihoods[answer]

            for letter in mbti_type:
                if letter in answer_likelihoods:
                    type_likelihood *= answer_likelihoods[letter]

            new_probabilities[mbti_type] = type_likelihood * probabilities[mbti_type]

        # Normalize probabilities
        total = sum(new_probabilities.values())
        if total > 0:
            for mbti_type in mbti_app.mbti_types:
                new_probabilities[mbti_type] = new_probabilities[mbti_type] / total

        session['probabilities'] = new_probabilities

        # Update remaining questions and count
        remaining_indices = session['remaining_indices']
        remaining_indices.remove(question_index)
        session['remaining_indices'] = remaining_indices
        session['asked_questions'] = session['asked_questions'] + 1

        # Check if we should end the test
        if len(remaining_indices) == 0 or session['asked_questions'] >= 20:
            return redirect(url_for('results'))

    # Get next question
    if session['remaining_indices']:
        session['current_question_index'] = session['remaining_indices'][0]
        question, _ = mbti_app.questions[session['current_question_index']]

        return render_template(
                'test.html',
                question=question,
                question_num=session['asked_questions'] + 1,
                total_questions=min(20, len(mbti_app.questions)),
                )
    else:
        return redirect(url_for('results'))

@app.route('/results')
def results():
    if 'probabilities' not in session:
        return redirect(url_for('index'))

    # Get the personality type with highest probability
    probabilities = session['probabilities']
    personality_type = max(probabilities.items(), key=lambda x: x[1])[0]
    confidence = probabilities[personality_type] * 100

    # Calculate dimensional breakdown
    e_prob = sum(probabilities[t] for t in mbti_app.mbti_types if t[0] == 'E') * 100
    i_prob = sum(probabilities[t] for t in mbti_app.mbti_types if t[0] == 'I') * 100
    s_prob = sum(probabilities[t] for t in mbti_app.mbti_types if t[1] == 'S') * 100
    n_prob = sum(probabilities[t] for t in mbti_app.mbti_types if t[1] == 'N') * 100
    t_prob = sum(probabilities[t] for t in mbti_app.mbti_types if t[2] == 'T') * 100
    f_prob = sum(probabilities[t] for t in mbti_app.mbti_types if t[2] == 'F') * 100
    j_prob = sum(probabilities[t] for t in mbti_app.mbti_types if t[3] == 'J') * 100
    p_prob = sum(probabilities[t] for t in mbti_app.mbti_types if t[3] == 'P') * 100

    # Get sorted types for display
    sorted_types = sorted(probabilities.items(), key=lambda x: x[1], reverse=True)
    sorted_types = [(t, round(p*100, 1)) for t, p in sorted_types]

    return render_template(
            'results.html',
            personality_type=personality_type,
            confidence=round(confidence, 1),
            description=mbti_app.personality_descriptions.get(personality_type, ""),
            sorted_types=sorted_types,
            dimensions={
                'E': round(e_prob, 1), 'I': round(i_prob, 1),
                'S': round(s_prob, 1), 'N': round(n_prob, 1),
                'T': round(t_prob, 1), 'F': round(f_prob, 1),
                'J': round(j_prob, 1), 'P': round(p_prob, 1)
                },
            user_name=mbti_app.name,
            user_email=mbti_app.email,
            )

@app.route('/reset')
def reset():
    session.clear()
    return redirect(url_for('index'))

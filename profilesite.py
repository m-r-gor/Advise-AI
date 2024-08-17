from flask import Flask, render_template, request, redirect, url_for
import json
import os

app = Flask(__name__)

if os.path.exists('advisor_profile.json'):
    with open('advisor_profile.json', 'r') as f:
        advisor_profile = json.load(f)
else:
    advisor_profile = {
        "name": "Michael Goralski",
        "language": "English",
        "tone": "Conversational yet professional",
        "phrasing": "Use “we” to foster a sense of partnership, explain things simply, avoiding very technical financial terminology",
        "sign_off":"No preference",
        "locations": {
                "Office": "",
                "Dinner": "",
                "Lunch": ""
        },
        "other_preferences": [
            "If the email is related to the passing of a family member, simply offer to schedule a meeting instead of providing any advice in writing.",
            "If the email mentions a milestone or achievement (e.g., births, graduations) start the response by congratulating them."
        ],
    }

@app.route('/')
def index():
    return render_template('index.html', profile=advisor_profile)

@app.route('/edit', methods=['GET', 'POST'])
def edit_profile():
    if request.method == 'POST':
        # Update advisor profile with form data
        advisor_profile['name'] = request.form['name']
        advisor_profile['language'] = request.form['language']
        advisor_profile['tone'] = request.form['tone']
        advisor_profile['phrasing'] = request.form['phrasing']
        advisor_profile['sign_off'] = request.form['sign_off']
        advisor_profile['locations'] = request.form['locations'].strip().splitlines()
        advisor_profile['other_preferences'] = request.form['other_preferences']
       
        with open('advisor_profile.json', 'w') as f:
            json.dump(advisor_profile, f, indent=4)
       
        return redirect(url_for('index'))
    return render_template('edit.html', profile=advisor_profile)

if __name__ == '__main__':
    app.run(debug=True)
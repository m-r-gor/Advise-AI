from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

@app.route('/interactions')
def show_interactions():
    conn = sqlite3.connect('interaction_logs.db')
    cursor = conn.cursor()
    cursor.execute('SELECT sender, inquiry, interaction_time, processing_time, response_html FROM interactions')
    interactions = cursor.fetchall()
    
    # Calculate total number of interactions
    total_interactions = len(interactions)
    
    conn.close()
    return render_template('interactions.html', interactions=interactions, total_interactions=total_interactions)

if __name__ == '__main__':
    app.run(debug=True)

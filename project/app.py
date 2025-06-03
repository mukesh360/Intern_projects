from textblob import TextBlob
from flask import Flask, render_template, request, flash, redirect,url_for
from flask_mysqldb import MySQL

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# With these:
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '2006'
app.config['MYSQL_DB'] = 'sentiment_db'

mysql = MySQL(app)



@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        if 'delete_id' in request.form:
            # Handle deletion
            delete_id = request.form['delete_id']
            cur = mysql.connection.cursor()
            cur.execute("DELETE FROM sentiment_results WHERE id = %s", (delete_id,))
            mysql.connection.commit()
            cur.close()
            flash('Record deleted successfully!', 'success')
            return redirect(url_for('home'))
        else:
            # Handle sentiment analysis
            text_input = request.form['text']
            sentences = [s.strip() for s in text_input.split('.') if s.strip()]
            
            if not sentences:
                flash('Please enter some text to analyze', 'error')
            else:
                results = []
                for sentence in sentences:
                    polarity, sentiment, sentiment_category = analyze_sentiment(sentence)
                    results.append((sentence, polarity, sentiment, sentiment_category))
                
                # Store in MySQL
                cur = mysql.connection.cursor()
                for result in results:
                    cur.execute(
                        "INSERT INTO sentiment_results (text, polarity, sentiment, sentiment_category) VALUES (%s, %s, %s, %s)",
                        (result[0], result[1], result[2], result[3])
                    )
                mysql.connection.commit()
                cur.close()
                
                flash(f'Analyzed {len(results)} sentences and stored successfully!', 'success')
    
    # Get all historical results
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM sentiment_results ORDER BY created_at DESC")
    history = cur.fetchall()
    cur.close()
    
    return render_template('index.html', history=history)

@app.route('/delete_all', methods=['POST'])
def delete_all():
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM sentiment_results")
    mysql.connection.commit()
    cur.close()
    flash('All records deleted successfully!', 'success')
    return redirect(url_for('home'))

def analyze_sentiment(text):
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity
    
    if polarity > 0:
        sentiment = "positive"
    elif polarity < 0:
        sentiment = "negative"
    else:
        sentiment = "neutral"
    if polarity > 0.5:
        sentiment_category = "Excellent"
    elif polarity > 0.1:
        sentiment_category = "Good"
    elif polarity > -0.1:
        sentiment_category = "Neutral"
    elif polarity > -0.5:
        sentiment_category = "Bad"
    else:
        sentiment_category = "Terrible"
    
    return polarity, sentiment, sentiment_category

if __name__ == '__main__':
    app.run(debug=True, port=3000)
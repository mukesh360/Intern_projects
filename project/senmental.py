from textblob import TextBlob
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        text = request.form['text']
        polarity, sentiment = analyze_sentiment(text)
        if polarity > 0.5:
            sentiment_category = "Excellent "
        elif polarity > 0.1:
            sentiment_category = "Good "
        elif polarity > -0.1:
            sentiment_category = "Neutral "
        elif polarity > -0.5:
            sentiment_category = "Bad "
        else:
            sentiment_category = "Terrible "
            
        return render_template('a.html', 
                             text=text,
                             polarity=f"{polarity:.2f}",
                             sentiment=sentiment,
                             sentiment_category=sentiment_category)
    
    return render_template('a.html')

def analyze_sentiment(text):
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity
    if polarity > 0:
        sentiment = "positive"
    elif polarity < 0:
        sentiment = "negative"
    else:
        sentiment = "neutral"
    return polarity, sentiment

if __name__ == '__main__':
    app.run(debug=True, port=3000)
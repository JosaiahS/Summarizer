#This is for writing the output of openai to page

from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index(fileInput):    
    with open(fileInput, 'r') as file:
        content = file.read()

    return render_template('template.html', content=content)

if __name__ == 'main':
    app.run(debug=True)

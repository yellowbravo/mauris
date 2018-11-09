from flask import Flask, render_template, flash, request, session, jsonify


app = Flask(__name__)


@app.route('/')
def consumer():
    return render_template('consumer.html')


if __name__ == '__main__':
    app.run()

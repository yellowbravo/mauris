from flask import Flask, render_template, flash, request, session, jsonify


app = Flask(__name__)
app.secret_key = 'IsYRsz62EKhfWRKHEP2dyPIKGx55CD3G'


@app.route('/')
def consumer():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return render_template('consumer.html')


@app.route('/login/', methods=['POST'])
def login():
    password = '1234'
    if request.form['password'] == password and request.form['username'] == 'config':
        session['logged_in'] = True
    else:
        flash('wrong password!')
    return consumer()


@app.route("/logout/")
def logout():
    print('yeah')
    session['logged_in'] = False
    return consumer()


if __name__ == '__main__':
    app.run(debug=True)

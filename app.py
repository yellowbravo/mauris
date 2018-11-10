from flask import Flask, render_template, flash, request, session, jsonify


app = Flask(__name__)
app.secret_key = 'IsYRsz62EKhfWRKHEP2dyPIKGx55CD3G'


@app.route('/consumer/')
def consumer():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return render_template('consumer.html')


@app.route('/admin/')
def admin_view():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return render_template('admin.html')


@app.route('/admin/add_pod_meter/')
def add_existing_meter_view():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return render_template('add_pod_meter.html')


@app.route('/login/', methods=['POST'])
def login():
    admin = 'frank.grassi@monthey.ch'
    consumer_user = 'consumer@mail.com'

    password = '1234'

    if request.form['password'] == password and request.form['username'] == consumer_user:
        session['user'] = consumer_user
        session['logged_in'] = True

        return consumer()

    elif request.form['password'] == password and request.form['username'] == admin:
        session['user'] = admin
        session['logged_in'] = True

        return admin_view()

    else:
        flash('wrong password!')


@app.route("/logout/")
def logout():
    session['logged_in'] = False
    return consumer()


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)

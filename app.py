from flask import Flask, render_template, flash, request, session, jsonify
from pymongo import MongoClient

client = MongoClient('mongodb://mauris:mauris2018@ds259253.mlab.com:59253/mauris')
db = client['mauris']

app = Flask(__name__)

app.secret_key = 'IsYRsz62EKhfWRKHEP2dyPIKGx55CD3G'


@app.route('/')
def index():
    return admin_view()

@app.route('/consumer/')
def consumer():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return render_template('consumer.html')


@app.route("/meter/<pod>", methods=['GET', 'POST'])
def meter(pod):
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        template_data = dict()
        if request.method == 'POST':
            template_data = {'has_data': True}

        template_data['pod'] = pod
        my_pod = db.meters.find_one({'pod': pod})
        template_data['agg_meters'] = my_pod.get('agg_meters', list())

        return render_template('meter.html', **template_data)


@app.route('/admin/')
def admin_view():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        meters = list(db.meters.find())

        template_data = {'meters': meters}

        return render_template('admin.html', **template_data)


@app.route('/admin/add_pod_meter/', methods=['GET', 'POST'])
def add_existing_meter_view():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        if request.method == 'POST':
            meter = {'name': request.form['name'],
                     'pod': request.form['pod'],
                     'address': request.form['address'],
                     'city': request.form['city']
                     }

            db.meters.insert(meter)

            return admin_view()

        return render_template('add_pod_meter.html')


@app.route('/admin/add_virtual_meter/', methods=['GET', 'POST'])
def add_virtual_meter_view():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        if request.method == 'POST':
            meter = {'name': request.form['name'],
                     'pod': request.form['pod'],
                     'address': request.form['address'],
                     'city': request.form['city'],
                     'agg_meters': request.form.getlist('meters')
                     }

            db.meters.insert(meter)

            return admin_view()

        meters = list(db.meters.find())

        template_data = {'meters': meters}

        return render_template('add_virtual_meter.html', **template_data)


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


if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)


from flask import Flask, render_template, flash, request, session, jsonify
from pymongo import MongoClient
import requests
import pandas as pd
from operator import itemgetter
import datetime
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
        template_data['has_data'] = False

        if request.method == 'POST':
            start = datetime.datetime.strptime(request.form['start'], '%Y-%m-%d')
            end = datetime.datetime.strptime(request.form['end'], '%Y-%m-%d') + datetime.timedelta(days=1)

            # print(request.form)
            # url = "http://217.70.191.86:8080/mauris-mdw-0.0.1-SNAPSHOT/pods/{0}/data?from={1}&to={2}".format(pod, '01-04-2018', '01-04-2018')
            #
            # r = requests.get(url)
            #
            # print(r.text)

            raw_data = list(db.energy.find({'pod': pod, 'datetime': {'$gt': start, '$lte': end}}))
            raw_data = sorted(raw_data, key=itemgetter('datetime'))

            obis_codes = db.meters.find_one({'pod': pod})['obis']
            obis_infos = list(db.obis_codes.find())
            df = pd.DataFrame(raw_data)
            sums = df.sum()
            data = dict()
            for o in obis_codes:
                ob = next((item for item in obis_infos if item["code"] == o))
                o = o.replace('.', '_')
                data[o] = {'data': list(df[o].values),
                           'sum': sums[o],
                           'pmax': df[o].max(),
                           'name': ob['name'],
                           'color': ob.get('color', 'rgb(180,97,30)')
                           }

            index = list()

            for d in raw_data:
                ts = d['datetime']
                date_str = "{0}/{1}".format(ts.day, ts.month)


                index.append(date_str)

            template_data = {
                'data': data,
                'has_data': True,
                'index': index,
                'obis_codes': obis_codes,
                'start': start.strftime("%d-%m-%Y"),
                'end': end.strftime("%d-%m-%Y"),
                }

        template_data['pod'] = pod
        template_data['name'] = db.meters.find_one({'pod': pod})['name']
        my_pod = db.meters.find_one({'pod': pod})
        template_data['agg_meters'] = my_pod.get('agg_meters', list())

        return render_template('meter.html', **template_data)


@app.route("/meter/<pod>/live/")
def live(pod):
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        template_data = dict()

        return render_template('live.html', **template_data)

@app.route('/admin/')
def admin_view():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        meters = list(db.meters.find())

        template_data = {'meters': meters}

        return render_template('admin.html', **template_data)


@app.route('/admin/obis_codes/')
def obis_view():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        obis_codes = list(db.obis_codes.find())

        template_data = {'obis_codes': obis_codes}

        return render_template('obis_codes.html', **template_data)


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


@app.route('/admin/edit_pod_meter/<pod>', methods=['GET', 'POST'])
def edit_existing_meter_view(pod):
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        my_meter = db.meters.find_one({'pod': pod})

        template_data = dict()
        template_data['my_meter'] = my_meter
        template_data['obis_code'] = list(db.obis_codes.find())

        if request.method == 'POST':
            new = {'name': request.form['name'],
                   'pod': request.form['pod'],
                   'address': request.form['address'],
                   'city': request.form['city'],
                   'obis': request.form.getlist('obis')
                   }

            db.meters.update_one({'_id': my_meter['_id']}, {'$set': new})

            return admin_view()

        return render_template('edit_pod_meter.html', **template_data)


@app.route('/admin/add_obis_code/', methods=['GET', 'POST'])
def add_obis_code():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        if request.method == 'POST':
            obis_code = {'name': request.form['name'],
                         'code': request.form['code'],
                         'comment': request.form['comment'],
                         'unit': request.form['unit'],

                         }

            db.obis_codes.insert(obis_code)

            return obis_view()

        return render_template('add_obis.html')


@app.route('/admin/edit_obis_codes/<obis>', methods=['GET', 'POST'])
def edit_obis_code(obis):
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        my_obis = obis
        my_obis = db.obis_codes.find_one({'code': my_obis})
        template_data = dict()
        template_data['my_obis'] = my_obis

        if request.method == 'POST':
            obis_code = {'name': request.form['name'],
                         'code': request.form['code'],
                         'comment': request.form['comment'],
                         'unit': request.form['unit'],
                         'color': '#' + request.form['color'],
                         }

            db.obis_codes.update_one({'_id': my_obis['_id']}, {'$set': obis_code})

            return obis_view()

        return render_template('edit_obis.html', **template_data)


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
    app.run(debug=False)


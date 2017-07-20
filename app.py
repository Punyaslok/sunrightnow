import flask
from flask import Flask, flash
from flask_bootstrap import Bootstrap
#from flask_wtf import Form
#from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy

import datetime

import astropy.units as u


# add imperial units to list of known units.
from astropy.units import imperial
imperial.enable()


# Local imports
from hmi import plot_hmi_for_range

app = flask.Flask(__name__)
import os
basedir = os.path.abspath(os.path.dirname(__file__))
database_name = 'app.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, database_name)
db = SQLAlchemy(app)
#app.config['SECRET_KEY'] ='\xe7X\x8e\xc6L-\xf5\xf7\xdfY/P<\x8eM\x82\x8cc\x92\xfaJU\x12H'
#csrf = CSRFProtect(app)

class BaseClass(db.Model):
    __tablename__ = 'baseclass'
    id = db.Column(db.Integer, primary_key=True)
    plot_date = db.Column(db.DateTime)
    image_path = db.Column(db.String(120))

    def __init__(self, plot_date, image_path):
        self.plot_date = plot_date
        self.image_path = image_path

    def __repr__(self):
        return '< date = %r image_path = %r >' % (self.plot_date, self.image_path)

class Magnetogram(BaseClass):
    __tablename__ = 'magnetogram'
    id = db.Column(db.Integer, db.ForeignKey('baseclass.id'), primary_key=True)
    client_name = 'magnetogram'
    def __init__(self, plot_date, image_path):
        BaseClass.__init__(self, plot_date, image_path)

class Continuum(BaseClass):
    __tablename__ = 'continuum'
    id = db.Column(db.Integer, db.ForeignKey('baseclass.id'), primary_key=True)
    client_name = 'continuum'
    def __init__(self, plot_date, image_path):
        BaseClass.__init__(self, plot_date, image_path)



Bootstrap(app)


DEFAULT_IN_UNIT = 'mile/hr'
DEFAULT_IN_VALUE = 100
DEFAULT_OUT_UNIT = 'm/s'

@app.route('/')
def index():
    args = flask.request.args
    _input_unit = str(args.get('_input_unit', DEFAULT_IN_UNIT))
    _input_value = float(args.get('_input_value', DEFAULT_IN_VALUE))
    _output_unit = str(args.get('_output_unit', DEFAULT_OUT_UNIT))

    try:
        _output_value = u.Quantity(_input_value, _input_unit).to(_output_unit)
    except ValueError:
        _output_value = 'Invalid equivalence entry'

    html = flask.render_template(
        'index.html',
        _input_value=_input_value,
        _input_unit=_input_unit,
        _output_value=_output_value,
        _output_unit=_output_unit,
    )
    return html


# DEFAULT_INPUT_DATE = str((datetime.date.today()- datetime.timedelta(1)).strftime('%Y-%m-%d'))    # Yesterday's date
DEFAULT_INPUT_DATE = None

@app.route('/magnetogram', methods=['GET', 'POST'])
def magnetogram():
    args = flask.request.args
    _input_date = str(args.get('_input_date', DEFAULT_INPUT_DATE))
    print(_input_date)

    try:
        _image_path = search_in_db('magnetogram', _input_date)
    except Exception as e:
        print("Except Called")
        import traceback
        traceback.print_exc()
        print(e)
        _image_path = None

    html = flask.render_template(
        'baseclass.html',
        _input_date=_input_date,
        _image_path=_image_path,
        _client_name='magnetogram'
    )
    return html

@app.route('/continuum', methods=['GET', 'POST'])
def continuum():
    args = flask.request.args
    _input_date = str(args.get('_input_date', DEFAULT_INPUT_DATE))
    print(_input_date)

    try:
        _image_path = search_in_db('continuum', _input_date)
    except Exception as e:
        print("Except Called")
        import traceback
        traceback.print_exc()
        print(e)
        _image_path = None

    html = flask.render_template(
        'baseclass.html',
        _input_date=_input_date,
        _image_path=_image_path,
        _client_name='continuum',
    )
    return html

def create_new_db():
    import os
    if os.path.exists(database_name):
        os.remove(database_name)
    db.create_all()
    return


def save_to_db(client=None, input_date=None, image_path=None):
    if client is None or input_date is None or image_path is None:
        raise ValueError('No argument cannot be None')

    if 'magnetogram' in client:
        db.session.add(Magnetogram(input_date, image_path))
    elif 'continuum' in client:
        db.session.add(Continuum(input_date, image_path))

    db.session.commit()
    return


def search_in_db(client=None, input_date=None):
    if client is None:
        raise ValueError('client argument cannot be None')
    if input_date is None:
        raise ValueError('date argument cannot be None')

    input_date = datetime.datetime.strptime(input_date, '%Y-%m-%d')
    print('searching for ' + str(input_date))
    entry = None
    if 'magnetogram' in client:
        entry = Magnetogram.query.filter_by(plot_date=input_date).first()
    elif 'continuum' in client:
        entry = Continuum.query.filter_by(plot_date=input_date).first()
    print(entry)
    if entry is None:
        print("Image not found")
        return None
    else:
        return entry.image_path

def populate_db():
    start_date = '2017-03-05'
    end_date = '2017-03-05'
    plot_hmi_for_range(start_date, end_date, 'magnetogram')
    #plot_hmi_for_range(start_date, end_date, 'continuum')
    return

create_new_db()
populate_db()

if __name__ == '__main__':
    print(__doc__)
    app.run(debug=True)
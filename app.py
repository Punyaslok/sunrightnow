import flask
from flask import Flask, flash
from flask_bootstrap import Bootstrap
#from flask_wtf import Form
#from flask_wtf.csrf import CSRFProtect
import datetime

import astropy.units as u


# add imperial units to list of known units.
from astropy.units import imperial
imperial.enable()


# Local imports
from magnetogram import plot_magnetogram

app = flask.Flask(__name__)
#app.config['SECRET_KEY'] ='\xe7X\x8e\xc6L-\xf5\xf7\xdfY/P<\x8eM\x82\x8cc\x92\xfaJU\x12H'
#csrf = CSRFProtect(app)

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
        _image_path = plot_magnetogram(_input_date)
    except Exception as e:
        print("Except Called")
        import traceback
        traceback.print_exc()
        print(e)
        _image_path = None

    html = flask.render_template(
        'magnetogram.html',
        _input_date=_input_date,
        _image_path=_image_path,
    )
    return html

if __name__ == '__main__':
    print(__doc__)
    app.run(debug=True)

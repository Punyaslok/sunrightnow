# If you get the following error while running the flask app:
# Error: The file/path provided (app) does not appear to exist.  Please verify the path is correct.  If app is not on PYTHONPATH, ensure the extension is .py
# Then check the .py files for Import errors. Ensure all correct branches are in use if 
# you have sunpy-dev or any other module. To see exact import errors, run "python app.py"

import flask
from flask import Flask, flash, make_response
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
from plot_client import plot_client_for_range, clear_download_directory
from commonfunctions import get_text_for_imaging, get_text_for_timeseries

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

class Aia(BaseClass):
    __tablename__ = 'aia'
    id = db.Column(db.Integer, db.ForeignKey('baseclass.id'), primary_key=True)
    client_name = 'aia'
    def __init__(self, plot_date, image_path):
        BaseClass.__init__(self, plot_date, image_path)

class StereoA(BaseClass):
    __tablename__ = 'stereoa'
    id = db.Column(db.Integer, db.ForeignKey('baseclass.id'), primary_key=True)
    client_name = 'stereoa'
    def __init__(self, plot_date, image_path):
        BaseClass.__init__(self, plot_date, image_path)

class StereoB(BaseClass):
    __tablename__ = 'stereob'
    id = db.Column(db.Integer, db.ForeignKey('baseclass.id'), primary_key=True)
    client_name = 'stereob'
    def __init__(self, plot_date, image_path):
        BaseClass.__init__(self, plot_date, image_path)

class Goes(db.Model):
    __tablename__ = 'goes'

    id = db.Column(db.Integer, primary_key=True)

    index = db.Column(db.DateTime)
    xrsa = db.Column(db.Float)
    xrsb = db.Column(db.Float)
    time_str = db.Column(db.String(20))

    def __init__(self, index, xrsa, xrsb, time_str):
        self.index = index
        self.xrsa = xrsa
        self.xrsb = xrsb
        self.time_str = time_str

    def __repr__(self):
        return '< index = %r xrsa = %r xrsb = %r time_str = %r>' % (self.index, self.xrsa, self.xrsb, self.time_str)

class Eve(db.Model):
    __tablename__ = 'eve'

    id = db.Column(db.Integer, primary_key=True)

    index = db.Column(db.DateTime)
    xrsa_proxy = db.Column(db.Float)
    xrsb_proxy = db.Column(db.Float)
    sem_proxy = db.Column(db.Float)
    ESPquad017 = db.Column(db.Float)    # 0.1-7ESPquad
    ESP171 = db.Column(db.Float)        # 17.1ESP
    ESP257 = db.Column(db.Float)        # 25.7ESP
    ESP304 = db.Column(db.Float)        # 30.4ESP
    ESP366 = db.Column(db.Float)        # 36.6ESP
    darkESP = db.Column(db.Float)       # darkESP
    MEGS_P1216 = db.Column(db.Float)    # 121.6MEGS-P
    darkMEGS_P = db.Column(db.Float)    # darkMEGS-P
    q0ESP = db.Column(db.Float)
    q1ESP = db.Column(db.Float)
    q2ESP = db.Column(db.Float)
    q3ESP = db.Column(db.Float)
    CMLat = db.Column(db.Float)
    CMLon = db.Column(db.Float)
    x_cool_proxy= db.Column(db.Float)
    oldXRSB_proxy = db.Column(db.Float)
    time_str = db.Column(db.String(20))

    def __init__(self,**kwargs):
        self.index = kwargs.pop('index')
        self.xrsa_proxy = kwargs.pop('xrsa_proxy')
        self.xrsb_proxy = kwargs.pop('xrsb_proxy')
        self.sem_proxy = kwargs.pop('sem_proxy')
        self.ESPquad017 = kwargs.pop('ESPquad017')    # 0.1-7ESPquad
        self.ESP171 = kwargs.pop('ESP171')        # 17.1ESP
        self.ESP257 = kwargs.pop('ESP257')        # 25.7ESP
        self.ESP304 = kwargs.pop('ESP304')        # 30.4ESP
        self.ESP366 = kwargs.pop('ESP366')        # 36.6ESP
        self.darkESP = kwargs.pop('darkESP')       # darkESP
        self.MEGS_P1216 = kwargs.pop('MEGS_P1216')    # 121.6MEGS-P
        self.darkMEGS_P = kwargs.pop('darkMEGS_P')    # darkMEGS-P
        self.q0ESP = kwargs.pop('q0ESP')
        self.q1ESP = kwargs.pop('q1ESP')
        self.q2ESP = kwargs.pop('q2ESP')
        self.q3ESP = kwargs.pop('q3ESP')
        self.CMLat = kwargs.pop('CMLat')
        self.CMLon = kwargs.pop('CMLon')
        self.x_cool_proxy= kwargs.pop('x_cool_proxy')
        self.oldXRSB_proxy = kwargs.pop('oldXRSB_proxy')
        self.time_str = kwargs.pop('time_str')

    def __repr__(self):
        return '< index = %r xrsa_proxy = %r xrsb_proxy = %r time_str = %r>' % (self.index, self.xrsa_proxy, self.xrsb_proxy, self.time_str)

Bootstrap(app)





DEFAULT_INPUT_DATE = str((datetime.datetime.utcnow()- datetime.timedelta(1)).strftime('%Y-%m-%d'))    # Yesterday's date
# DEFAULT_INPUT_DATE = None

@app.route('/', methods=['GET', 'POST'])
def index():
    args = flask.request.args
    
    _input_date = str(args.get('_input_date', DEFAULT_INPUT_DATE))
    print(_input_date)

    clients = [
            'magnetogram',
            'continuum',
            'aia',
            'stereoa',
            'stereob',
    ]
    _image_paths = {}
    for client in clients:
        _image_paths[client] = search_in_db(client, _input_date)

    html = flask.render_template(
        'index.html',
        clients=clients,
        _input_date=_input_date,
        _image_paths=_image_paths
    )
    return html

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

@app.route('/aia', methods=['GET', 'POST'])
def aia():
    args = flask.request.args
    _input_date = str(args.get('_input_date', DEFAULT_INPUT_DATE))
    print(_input_date)

    try:
        _image_path = search_in_db('aia', _input_date)
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
        _client_name='aia',
    )
    return html

@app.route('/stereoa', methods=['GET', 'POST'])
def stereoa():
    args = flask.request.args
    _input_date = str(args.get('_input_date', DEFAULT_INPUT_DATE))
    print(_input_date)

    try:
        _image_path = search_in_db('stereoa', _input_date)
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
        _client_name='stereoa',
    )
    return html

@app.route('/stereob', methods=['GET', 'POST'])
def stereob():
    args = flask.request.args
    _input_date = str(args.get('_input_date', DEFAULT_INPUT_DATE))
    print(_input_date)

    try:
        _image_path = search_in_db('stereob', _input_date)
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
        _client_name='stereob',
    )
    return html

@app.route('/goes', methods=['GET', 'POST'])
def goes():
    """
    Very simple embedding of a lightcurve chart
    """
    # FLASK
    # Grab the inputs arguments from the URL
    # This is automated by the button

    import pandas

    from bokeh.embed import components
    from bokeh.plotting import figure
    from bokeh.resources import INLINE
    from bokeh.util.string import encode_utf8
    from bokeh.layouts import Column
    from bokeh.models.formatters import DatetimeTickFormatter
    from bokeh.models import ColumnDataSource, CustomJS, HoverTool

    from sunpy.time import TimeRange, parse_time

    # set some defaults
    #DEFAULT_TR = TimeRange(['2011-06-07 00:00', '2011-06-07 12:00'])
    DEFAULT_TR = TimeRange(['2016-06-07 00:00', '2016-06-07 12:00'])
    PLOT_HEIGHT = 800
    PLOT_WIDTH = 1400
    TOOLS = 'pan,box_zoom,wheel_zoom,box_select,crosshair,undo,redo,save,reset'
    ONE_HOUR = datetime.timedelta(seconds=60*60)
    ONE_DAY = datetime.timedelta(days=1)

    formatter = DatetimeTickFormatter(hours="%F %H:%M")

    data = search_in_timeseries_db(DEFAULT_TR.start, DEFAULT_TR.end, client='goes')
    
    source = ColumnDataSource(data=data)
    source_static = ColumnDataSource(data=data)


    args = flask.request.args

    _from = str(args.get('_from', str(DEFAULT_TR.start)))
    _to = str(args.get('_to', str(DEFAULT_TR.end)))

    tr = TimeRange(parse_time(_from), parse_time(_to))

    if 'next' in args:
        tr = tr.next()

    if 'prev' in args:
        tr = tr.previous()

    if 'next_hour' in args:
        tr = TimeRange(tr.start + ONE_HOUR, tr.end + ONE_HOUR)

    if 'next_day' in args:
        tr = TimeRange(tr.start + ONE_DAY, tr.end + ONE_DAY)

    if 'prev_hour' in args:
        tr = TimeRange(tr.start - ONE_HOUR, tr.end - ONE_HOUR)

    if 'prev_day' in args:
        tr = TimeRange(tr.start - ONE_DAY, tr.end - ONE_DAY)

    _from = str(tr.start)
    _to = str(tr.end)

    data = search_in_timeseries_db(tr.start, tr.end, client='goes')

    source = ColumnDataSource(data=data)
    source_static = ColumnDataSource(data=data)

    fig1 = figure(title="GOES", tools=TOOLS,
                  plot_height=PLOT_HEIGHT, width=PLOT_WIDTH,
                  x_axis_type='datetime', y_axis_type="log",
                  y_range=(10**-9, 10**-2), toolbar_location="right")

    fig1.xaxis.formatter = formatter

    names_and_legends = {
                            'xrsa' : ["blue", "xrsa 0.5-4.0 Angstrom"],
                            'xrsb' : ["red", "xrsa 1-8 Angstrom"]
                        }
    for key in names_and_legends:
        fig1.line('index', key, source=source_static, color=names_and_legends[key][0],line_width=2, legend=names_and_legends[key][1])

    fig = Column(fig1)

    source_static.callback = CustomJS(code="""
        var inds = cb_obj.selected['1d'].indices;
        var d1 = cb_obj.data;
        var m = 0;
        if (inds.length == 0) { return; }
        for (i = 0; i < inds.length; i++) {
            d1['color'][inds[i]] = "red"
            if (d1['y'][inds[i]] > m) { m = d1['y'][inds[i]] }
        }
        console.log(m);
        cb_obj.trigger('change');
    """)

    hover = HoverTool()
    hover.tooltips  = [
        ("time", "@time_str"),
        ("xrsb", "@xrsb"),
        ("xrsa", "@xrsa")
    ]

    fig1.add_tools(hover)

    # Configure resources to include BokehJS inline in the document.
    # For more details see:
    #   http://bokeh.pydata.org/en/latest/docs/reference/resources_embedding.html#bokeh-embed
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    # For more details see:
    #   http://bokeh.pydata.org/en/latest/docs/user_guide/embedding.html#components
    script, div = components(fig, INLINE)
    html = flask.render_template(
        'timeseries.html',
        plot_script=script,
        plot_div=div,
        js_resources=js_resources,
        css_resources=css_resources,
        _from=_from,
        _to=_to,
        _client_name='GOES'
    )
    return encode_utf8(html)


@app.route('/eve', methods=['GET', 'POST'])
def eve():
    """
    Very simple embedding of a lightcurve chart
    """
    # FLASK
    # Grab the inputs arguments from the URL
    # This is automated by the button

    import pandas

    from bokeh.embed import components
    from bokeh.plotting import figure
    from bokeh.resources import INLINE
    from bokeh.util.string import encode_utf8
    from bokeh.layouts import Column
    from bokeh.models.formatters import DatetimeTickFormatter
    from bokeh.models import ColumnDataSource, CustomJS, HoverTool

    from sunpy.time import TimeRange, parse_time

    # set some defaults
    DEFAULT_TR = TimeRange(['2016-06-07 00:00', '2016-06-07 12:00'])
    PLOT_HEIGHT = 800
    PLOT_WIDTH = 1400
    TOOLS = 'pan,box_zoom,wheel_zoom,box_select,crosshair,undo,redo,save,reset'
    ONE_HOUR = datetime.timedelta(seconds=60*60)
    ONE_DAY = datetime.timedelta(days=1)

    formatter = DatetimeTickFormatter(hours="%F %H:%M")

    data = search_in_timeseries_db(DEFAULT_TR.start, DEFAULT_TR.end, client='eve')
    
    source = ColumnDataSource(data=data)
    source_static = ColumnDataSource(data=data)


    args = flask.request.args

    _from = str(args.get('_from', str(DEFAULT_TR.start)))
    _to = str(args.get('_to', str(DEFAULT_TR.end)))

    tr = TimeRange(parse_time(_from), parse_time(_to))

    if 'next' in args:
        tr = tr.next()

    if 'prev' in args:
        tr = tr.previous()

    if 'next_hour' in args:
        tr = TimeRange(tr.start + ONE_HOUR, tr.end + ONE_HOUR)

    if 'next_day' in args:
        tr = TimeRange(tr.start + ONE_DAY, tr.end + ONE_DAY)

    if 'prev_hour' in args:
        tr = TimeRange(tr.start - ONE_HOUR, tr.end - ONE_HOUR)

    if 'prev_day' in args:
        tr = TimeRange(tr.start - ONE_DAY, tr.end - ONE_DAY)

    _from = str(tr.start)
    _to = str(tr.end)

    data = search_in_timeseries_db(tr.start, tr.end, client='eve')

    source = ColumnDataSource(data=data)
    source_static = ColumnDataSource(data=data)

    fig1 = figure(title="EVE", tools=TOOLS,
                  plot_height=PLOT_HEIGHT, width=PLOT_WIDTH,
                  x_axis_type='datetime', #y_axis_type="log",
                  y_range=(-60, 100), toolbar_location="right")

    fig1.xaxis.formatter = formatter

    names_and_legends = {   #colname : [color, legend_name]
                            'xrsa_proxy' : [],
                            'xrsb_proxy' : [],
                            'sem_proxy' : [],
                            'ESPquad017' : [],    # 0.1-7ESPquad
                            'ESP171' : [],        # 17.1ESP
                            'ESP257' : [],        # 25.7ESP
                            'ESP304' : [],        # 30.4ESP
                            'ESP366' : [],        # 36.6ESP
                            'darkESP' : [],       # darkESP
                            'MEGS_P1216' : [],    # 121.6MEGS-P
                            'darkMEGS_P' : [],    # darkMEGS-P
                            'q0ESP' : [],
                            'q1ESP' : [],
                            'q2ESP' : [],
                            'q3ESP' : [],
                            'CMLat' : [],
                            'CMLon' : [],
                            'x_cool_proxy' : [],
                            'oldXRSB_proxy' : []
                        }

    # select a palette
    from bokeh.palettes import viridis as palette
    # create a color iterator
    colors = palette(len(names_and_legends))
    for key, color in zip(names_and_legends, colors):
        names_and_legends[key].append(color)
        names_and_legends[key].append(str(key))

    for key in names_and_legends:
        color = names_and_legends[key][0]
        legend_name = names_and_legends[key][1] + '.'   # legend name cant se same as col name. See https://github.com/bokeh/bokeh/issues/5365
        fig1.line('index', key, source=source_static, color=color,line_width=2, legend=legend_name)

    fig = Column(fig1)

    source_static.callback = CustomJS(code="""
        var inds = cb_obj.selected['1d'].indices;
        var d1 = cb_obj.data;
        var m = 0;
        if (inds.length == 0) { return; }
        for (i = 0; i < inds.length; i++) {
            d1['color'][inds[i]] = "red"
            if (d1['y'][inds[i]] > m) { m = d1['y'][inds[i]] }
        }
        console.log(m);
        cb_obj.trigger('change');
    """)

    hover = HoverTool()
    hover.tooltips  = [
        ("time", "@time_str"),
    ]

    for key in names_and_legends:
        hover.tooltips.append((key, '@'+str(key)))

    fig1.add_tools(hover)

    # Configure resources to include BokehJS inline in the document.
    # For more details see:
    #   http://bokeh.pydata.org/en/latest/docs/reference/resources_embedding.html#bokeh-embed
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    # For more details see:
    #   http://bokeh.pydata.org/en/latest/docs/user_guide/embedding.html#components
    script, div = components(fig, INLINE)
    html = flask.render_template(
        'timeseries.html',
        plot_script=script,
        plot_div=div,
        js_resources=js_resources,
        css_resources=css_resources,
        _from=_from,
        _to=_to,
        _client_name='EVE'
    )
    return encode_utf8(html)

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
    elif 'aia' in client:
        db.session.add(Aia(input_date, image_path))
    elif 'stereoa' in client:
        db.session.add(StereoA(input_date, image_path))
    elif 'stereob' in client:
        db.session.add(StereoB(input_date, image_path))

    db.session.commit()
    return

def search_in_timeseries_db(start_time, end_time, client=None):
    import pandas
    if client is None:
        raise ValueError('client argument cannot be None')
    entry=None

    if client == 'goes':
        entry = Goes.query.filter(start_time <= Goes.index).filter(end_time >= Goes.index).all()

        zz = {
                'xrsa': [],
                'xrsb': [],
                'time_str': []
             }
        for e in entry:
            for key in zz:
                zz[key].append(getattr(e, key))
        print(zz)
        ret = pandas.DataFrame(data=zz)
        return ret

    elif client == 'eve':
        entry = Eve.query.filter(start_time <= Eve.index).filter(end_time >= Eve.index).all()

        zz = {
                'index': [],
                'xrsa_proxy' : [],
                'xrsb_proxy' : [],
                'sem_proxy' : [],
                'ESPquad017' : [],    # 0.1-7ESPquad
                'ESP171' : [],        # 17.1ESP
                'ESP257' : [],        # 25.7ESP
                'ESP304' : [],        # 30.4ESP
                'ESP366' : [],        # 36.6ESP
                'darkESP' : [],       # darkESP
                'MEGS_P1216' : [],    # 121.6MEGS-P
                'darkMEGS_P' : [],    # darkMEGS-P
                'q0ESP' : [],
                'q1ESP' : [],
                'q2ESP' : [],
                'q3ESP' : [],
                'CMLat' : [],
                'CMLon' : [],
                'x_cool_proxy' : [],
                'oldXRSB_proxy' : [],
                'time_str' : []
        }
        for e in entry:
            for key in zz:
                zz[key].append(getattr(e, key))

        ret = pandas.DataFrame(data=zz)

        return ret

    if entry is None:
        print("Timeseries data not found")
        return None

def search_in_db(client=None, input_date=None):
    if client is None:
        raise ValueError('client argument cannot be None')
    if input_date is None:
        raise ValueError('date argument cannot be None')

    input_date = datetime.datetime.strptime(input_date, '%Y-%m-%d')
    print('searching for ' + client + str(input_date))
    entry = None
    if 'magnetogram' in client:
        entry = Magnetogram.query.filter_by(plot_date=input_date).first()
    elif 'continuum' in client:
        entry = Continuum.query.filter_by(plot_date=input_date).first()
    elif 'aia' in client:
        entry = Aia.query.filter_by(plot_date=input_date).first()
    elif 'stereoa' in client:
        entry = StereoA.query.filter_by(plot_date=input_date).first()
    elif 'stereob' in client:
        entry = StereoB.query.filter_by(plot_date=input_date).first()
    print(entry)
    if entry is None:
        print("Image not found")
        return 'static/images/no_image.svg'
    else:
        return entry.image_path

def populate_db(start_date=None, end_date=None):
    
    if start_date is None or end_date is None:
        raise ValueError('Arguments cant be None')

    clients = [
            'magnetogram',
            'continuum',
            'aia',
            'stereoa',
            #'stereob',
    ]
    for client in clients:
        plot_client_for_range(start_date, end_date, client)
    return

def populate_timeseries_db(start_date=None, end_date=None):
    
    if start_date is None or end_date is None:
        raise ValueError('Arguments cant be None')

    import pandas
    import sunpy.timeseries
    from sunpy.net import Fido, attrs as a
    from sunpy.time import TimeRange, parse_time

    tr = TimeRange([start_date, end_date])

    clients = [
            'goes',
            'eve',
    ]
    
    st = tr.start
    en = tr.end
    delta = datetime.timedelta(days=1)
    en += delta
    while st <= tr.end:   # do it day by day to minimize load on PC

        for client in clients:
            if client == 'goes':
                results = Fido.search(a.Time(st, en), a.Instrument('goes'))
            elif client == 'eve':
                results = Fido.search(a.Time(st, en), a.Instrument('eve'), a.Level(0))

            downresp = Fido.fetch(results)
            source_name = {
                            'goes': 'XRS',
                            'eve': 'eve'
                          }
            ts = sunpy.timeseries.TimeSeries(downresp, source=source_name[client], concatenate=True)
            ts.data = ts.data.resample("1T").mean()

            # add time string for display of hover tool
            ts.data['time_str'] = ts.data.index.strftime('%F %H:%M:%S')

            add_list = []

            if client == 'goes':
                for row in ts.data.itertuples():    #itertuples faster than iterrows, duh
                    add_list.append(Goes(row.Index.to_pydatetime(), float(row.xrsa), float(row.xrsb), str(row.time_str)))
            elif client == 'eve':
                #print(list(ts.data.columns.values))
                for row in ts.data.itertuples():
                    add_list.append(Eve(
                                            index = row.Index.to_pydatetime(),
                                            xrsa_proxy = float(row._1),
                                            xrsb_proxy = float(row._2),
                                            sem_proxy = float(row._3),
                                            ESPquad017 = float(row._4),    # 0.1-7ESPquad
                                            ESP171 = float(row._5),        # 17.1ESP
                                            ESP257 = float(row._6),        # 25.7ESP
                                            ESP304 = float(row._7),        # 30.4ESP
                                            ESP366 = float(row._8),        # 36.6ESP
                                            darkESP = float(row.darkESP),       # darkESP
                                            MEGS_P1216 = float(row._10),    # 121.6MEGS-P
                                            darkMEGS_P = float(row._11),    # darkMEGS-P
                                            q0ESP = float(row.q0ESP),
                                            q1ESP = float(row.q1ESP),
                                            q2ESP = float(row.q2ESP),
                                            q3ESP = float(row.q3ESP),
                                            CMLat = float(row.CMLat),
                                            CMLon = float(row.CMLon),
                                            x_cool_proxy= float(row._18),
                                            oldXRSB_proxy = float(row._19),
                                            time_str = str(row.time_str))
                                        )

            db.session.add_all(add_list)
            db.session.commit()
            
            clear_download_directory()

        st += delta
        en += delta

    return


# This route will prompt a file download with the script lines
@app.route('/download')
def download():
    _client_name = flask.request.args.get('_client_name')

    if _client_name in ['magnetogram', 'continuum', 'aia', 'stereoa','stereob',]:
        _input_date = flask.request.args.get('_input_date')
        ret = get_text_for_imaging(_client_name, _input_date)
    elif _client_name in ['GOES', 'EVE']:
        _client_name = _client_name.lower()
        _from = flask.request.args.get('_from')
        _to = flask.request.args.get('_to')
        print('from to  = ')
        print(_from, _to)
        ret = get_text_for_timeseries(_client_name, _from, _to)
        # for naming file
        _from = str(_from).replace(':', '-')
        _from = str(_from).replace(' ', '-')
        _to = str(_to).replace(':', '-')
        _to = str(_to).replace(' ', '-')
        _input_date = str(_from) + "-" + str(_to)

    # We need to modify the response, so the first thing we 
    # need to do is create a response out of the python script string
    response = make_response(ret)

    # This is the key: Set the right header for the response
    # to be downloaded, instead of just printed on the browser
    response.headers["Content-Disposition"] = "attachment; filename="+_client_name + "_" + _input_date +".py"
    return response

create_new_db()
#populate_db(start_date = '2017-03-05', end_date = '2017-03-05')
#populate_timeseries_db(start_date = '2016-06-07 00:00', end_date = '2016-06-08 12:00')

tmp_date = str((datetime.datetime.utcnow() - datetime.timedelta(days=4)).strftime('%Y-%m-%d'))
tmp_date_2 = str((datetime.datetime.utcnow() - datetime.timedelta(days=3)).strftime('%Y-%m-%d'))
print(tmp_date, tmp_date_2)
#populate_db(start_date = tmp_date, end_date = tmp_date_2)


#################################################################################################
# Scheduler

# import atexit
# from apscheduler.schedulers.background import BackgroundScheduler

# cron = BackgroundScheduler(daemon=True)
# # Explicitly kick off the background thread
# # Be wary of this in debug mode : https://stackoverflow.com/questions/14874782/apscheduler-in-flask-executes-twice
# cron.start()


# def job_function():
#     yesterday_date = str((datetime.date.today()- datetime.timedelta(1)).strftime('%Y-%m-%d'))    # Yesterday's date
#     print(yesterday_date)
#     print((datetime.datetime.utcnow() - datetime.timedelta(1)).strftime('%Y-%m-%d'))
#     #populate_db(start_date = '2017-03-05', end_date = '2017-03-05')
#     #populate_timeseries_db(start_date = '2016-06-07 00:00', end_date = '2016-06-08 12:00')
#     return

# job = cron.add_job(job_function, 'interval', minutes=1)


# # Shutdown your cron thread if the web process is stopped
# atexit.register(lambda: cron.shutdown(wait=False))

# Scheduler ends
#######################################################################################################
if __name__ == '__main__':
    print(__doc__)
    app.run(debug=True)
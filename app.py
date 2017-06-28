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

def plot_magnetogram( input_date ):

    if input_date is None:
        return None

    """
    =========================================================
    Overplotting Active Region locations on magnetogram Plots
    =========================================================

    This example shows how to overplot Active Region location on magnetogram plots.
    """

    ##############################################################################
    # Start by importing the necessary modules.

    import datetime

    import matplotlib as mpl
    mpl.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    from astropy import units as u
    from astropy.coordinates import SkyCoord

    from sunpy.io.special import srs
    import sunpy.coordinates
    from sunpy.net import Fido, attrs as a
    import sunpy.map
    from sunpy.time import parse_time



    ##############################################################################
    # Let's select a date (yyyy-mm-dd) for which we will be downloading files.

    day = parse_time(input_date)

    ##############################################################################
    # We will select a small time range to avoid downloading too many files.

    start_time = day + datetime.timedelta(minutes=1)
    end_time = day + datetime.timedelta(minutes=2)

    ##############################################################################
    # Send the search query.
    srs_results = Fido.search(a.Time(start_time, end_time), a.Instrument('SOON'))
    srs_downloaded_files = Fido.fetch(srs_results)
    print(srs_downloaded_files)


    results = Fido.search(a.Time(start_time, end_time),
                                              a.Instrument('HMI') & a.vso.Physobs("LOS_magnetic_field"),
                                              a.vso.Sample(60* u.second))

    ##############################################################################
    # Download the files.

    downloaded_files = Fido.fetch(results)

    ##############################################################################
    # We will plot only one file in this example.

    file_name = downloaded_files[0]
    print(file_name)

    ##############################################################################
    # Now to download and read the SRS file.
    # Download the SRS file.

    

    ##############################################################################
    # We get one SRS file per day. So we pass the filename into the SRS reader. So
    # now `srs_table` contains an astropy table.

    srs_table = srs.read_srs(srs_downloaded_files[0])
    print(srs_table)

    ##############################################################################
    # We only need the rows which have 'ID' = 'I' or 'IA'.

    srs_table = srs_table[np.logical_or(srs_table['ID'] == 'I', srs_table['ID'] == 'IA')]

    ##############################################################################
    # Now we extract the latitudes, longitudes and the region numbers.
    lats = srs_table['Latitude']
    lngs = srs_table['Longitude']
    numbers = srs_table['Number']

    ##############################################################################
    # Now we make the plot.

    ##############################################################################
    # Create the magnetogram plot using the FITS file.

    smap = sunpy.map.Map(file_name)

    im = smap.plot()
    ax = plt.gca()
    ax.set_autoscale_on(False)

    ##############################################################################
    # We make a SkyCoord object and plot the active points on the map.

    c = SkyCoord(lngs, lats, frame="heliographic_stonyhurst")
    ax.plot_coord(c, 'o')

    ##############################################################################
    # Add the numbers as labels for each point.

    for i, num in enumerate(numbers):
            ax.annotate(num, (lngs[i].value, lats[i].value),
                                    xycoords=ax.get_transform('heliographic_stonyhurst'))

    ##############################################################################
    # Now we display the combined plot.

    smap.plot(vmin=-120, vmax=120)
    smap.draw_limb()

    if not os.path.exists('static/images/magnetogram/'):
        os.makedirs('static/images/magnetogram/')
    image_path = "static/images/magnetogram/"+str(start_time.strftime('%Y-%m-%d'))+"_magnetogram.svg"
    import os
    dir_path = os.path.dirname(os.path.realpath(__file__))
    plt.savefig(str(os.path.join(dir_path, image_path)))
    return image_path

if __name__ == '__main__':
    print(__doc__)
    app.run(debug=True)

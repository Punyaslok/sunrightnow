import datetime
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import os

import numpy as np
from astropy import units as u

from sunpy.net import Fido, attrs as a
from sunpy.time import parse_time
from sunpy.io.special import srs
from astropy.coordinates import SkyCoord
import sunpy.coordinates
import sunpy.map


def get_srs_info(start_time, end_time):
    """
    Get latitude, longitude and number info for ARs
    """

    srs_results = Fido.search(
        a.Time(start_time, end_time), a.Instrument('SOON'))
    srs_downloaded_files = Fido.fetch(srs_results)
    print(srs_downloaded_files)

    srs_table = srs.read_srs(srs_downloaded_files[0])
    print(srs_table)

    if 'I' in srs_table['ID'] or 'IA' in srs_table['ID']:
        srs_table = srs_table[np.logical_or(srs_table['ID'] == 'I',
                                            srs_table['ID'] == 'IA')]
    else:
        print("Warning : No I or IA entries for this date.")
        srs_table = None

    if srs_table is not None:
        lats = srs_table['Latitude']
        lngs = srs_table['Longitude']
        numbers = srs_table['Number']
    else:
        lats = lngs = numbers = None

    print(lats, lngs, numbers)

    return lats, lngs, numbers, srs_downloaded_files


def fetch_client_file(start_time, end_time, client_name):

    #return '/home/punya/sunpy/data/hmi_m_45s_2017_03_05_00_02_15_tai_magnetogram.1.fits', ['/home/punya/sunpy/data/hmi_m_45s_2017_03_05_00_02_15_tai_magnetogram.1.fits']

    if client_name == 'magnetogram':
        results = Fido.search(a.Time(start_time, end_time),
                              a.Instrument('HMI') & a.vso.Physobs("LOS_magnetic_field"),
                              a.vso.Sample(60 * u.second))
    elif client_name == 'continuum':
    	results = Fido.search(a.Time(start_time, end_time),
                              a.Instrument('HMI') & a.vso.Physobs("intensity"),
                              a.vso.Sample(60 * u.second))

    downloaded_files = Fido.fetch(results)

    file_name = downloaded_files[0]
    print(file_name)

    return file_name, downloaded_files


def get_time_range(input_date):

    day = parse_time(input_date)

    start_time = day + datetime.timedelta(minutes=0)
    end_time = day + datetime.timedelta(minutes=1)

    return start_time, end_time

def plot_and_save(start_time, file_name, lats, lngs, numbers, client_name):

    smap = sunpy.map.Map(file_name)

    im = smap.plot()
    ax = plt.gca()
    ax.set_autoscale_on(False)

    c = SkyCoord(lngs, lats, frame="heliographic_stonyhurst")
    ax.plot_coord(c, 'o')

    for i, num in enumerate(numbers):
            ax.annotate(num, (lngs[i].value, lats[i].value),
                                    xycoords=ax.get_transform('heliographic_stonyhurst'))

    if 'magnetogram' in client_name:
    	smap.plot(vmin=-120, vmax=120)

    smap.draw_limb()

    if not os.path.exists('static/images/' + client_name + '/'):
        os.makedirs('static/images/' + client_name + '/')
    image_path = "static/images/" + client_name + "/" + str(start_time.strftime('%Y-%m-%d')) + "_" + client_name + ".svg"

    dir_path = os.path.dirname(os.path.realpath(__file__))
    plt.savefig(str(os.path.join(dir_path, image_path)), format='svg')

    # Free memory
    plt.clf()
    plt.cla()
    plt.close('all')

    return image_path
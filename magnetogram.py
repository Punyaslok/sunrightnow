def plot_magnetogram( input_date ):

    if input_date is None:
        return None

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

    day = parse_time(input_date)

    start_time = day + datetime.timedelta(minutes=1)
    end_time = day + datetime.timedelta(minutes=2)

    srs_results = Fido.search(a.Time(start_time, end_time), a.Instrument('SOON'))
    srs_downloaded_files = Fido.fetch(srs_results)
    print(srs_downloaded_files)


    results = Fido.search(a.Time(start_time, end_time),
                                              a.Instrument('HMI') & a.vso.Physobs("LOS_magnetic_field"),
                                              a.vso.Sample(60* u.second))

    downloaded_files = Fido.fetch(results)

    file_name = downloaded_files[0]
    print(file_name)

    srs_table = srs.read_srs(srs_downloaded_files[0])
    print(srs_table)

    if 'I' in srs_table['ID'] or 'IA' in srs_table['ID']:
        srs_table = srs_table[np.logical_or(
            srs_table['ID'] == 'I', srs_table['ID'] == 'IA')]
    else:
        print("Warning : No I or IA entries for this date.")
        srs_table = None

    if srs_table is not None:
        lats = srs_table['Latitude']
        lngs = srs_table['Longitude']
        numbers = srs_table['Number']
    else:
        lats = lngs = numbers = None

    smap = sunpy.map.Map(file_name)

    im = smap.plot()
    ax = plt.gca()
    ax.set_autoscale_on(False)

    c = SkyCoord(lngs, lats, frame="heliographic_stonyhurst")
    ax.plot_coord(c, 'o')

    for i, num in enumerate(numbers):
            ax.annotate(num, (lngs[i].value, lats[i].value),
                                    xycoords=ax.get_transform('heliographic_stonyhurst'))

    smap.plot(vmin=-120, vmax=120)
    smap.draw_limb()

    import os
    if not os.path.exists('static/images/magnetogram/'):
        os.makedirs('static/images/magnetogram/')
    image_path = "static/images/magnetogram/"+str(start_time.strftime('%Y-%m-%d'))+"_magnetogram.svg"

    dir_path = os.path.dirname(os.path.realpath(__file__))
    plt.savefig(str(os.path.join(dir_path, image_path)), format='svg')

    from app import save_to_db
    save_to_db(client='magnetogram', input_date=day, image_path=image_path)

    # Job done, delete downloaded files
    for f in downloaded_files:
        os.remove(f)
    for f in srs_downloaded_files:
        os.remove(f)

    # Free memory
    plt.close('all')

    return image_path

def plot_magnetogram_for_range(start_date, end_date):
    import datetime
    start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    delta = datetime.timedelta(days=1)

    d = start_date
    while d <= end_date:
        plot_magnetogram(str(d))
        d += delta

    return
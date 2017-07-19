from commonfunctions import get_srs_info, fetch_client_file, get_time_range

def plot_magnetogram( input_date ):

    if input_date is None:
        return None

    import matplotlib as mpl
    mpl.use('Agg')
    import matplotlib.pyplot as plt

    from astropy.coordinates import SkyCoord
    import sunpy.coordinates
    import sunpy.map

    start_time, end_time = get_time_range(input_date)

    lats, lngs, numbers, srs_downloaded_files = get_srs_info(start_time, end_time)

    file_name, downloaded_files = fetch_client_file(start_time, end_time, 'magnetogram')

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
    save_to_db(client='magnetogram', input_date=start_time, image_path=image_path)

    # Job done, delete downloaded files
    for f in downloaded_files:
        os.remove(f)
    for f in srs_downloaded_files:
        os.remove(f)

    # Free memory
    plt.clf()
    plt.cla()
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
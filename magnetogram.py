import os

from commonfunctions import get_srs_info, fetch_client_file, get_time_range, plot_and_save

def plot_hmi( input_date, client_name ):
    # client_name can be either 'magnetogram' or 'continuum'

    if input_date is None:
        return None

    start_time, end_time = get_time_range(input_date)

    #lats, lngs, numbers, srs_downloaded_files = get_srs_info(start_time, end_time)
    srs_results = Fido.search(a.Time(start_time, end_time), a.Instrument('SOON'))
    srs_downloaded_files = Fido.fetch(srs_results)
    print(srs_downloaded_files)

    with open(srs_downloaded_files[0], 'r') as fin:
        print fin.read()
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

    file_name, downloaded_files = fetch_client_file(start_time, end_time, client_name)

    image_path = plot_and_save(start_time, file_name, lats, lngs, numbers, client_name)

    from app import save_to_db
    save_to_db(client=client_name, input_date=start_time, image_path=image_path)

    # Job done, delete downloaded files
    for f in downloaded_files:
        os.remove(f)
    for f in srs_downloaded_files:
        os.remove(f)

    return image_path

def plot_hmi_for_range(start_date, end_date, client_name):
    
    import datetime
    start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    delta = datetime.timedelta(days=1)

    d = start_date
    while d <= end_date:
        plot_hmi(str(d), client_name)
        d += delta

    return
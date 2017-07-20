import os

from commonfunctions import get_srs_info, get_srs_files, fetch_client_file, get_time_range, plot_and_save

def plot_hmi( input_date, client_name ):
    # client_name can be either 'magnetogram' or 'continuum'

    if input_date is None:
        return None

    start_time, end_time = get_time_range(input_date)

    # VERY IMPORTANT NOTE
    # get_srs_info() call should be made after fetch_client_file() call.
    # On dokku, if you call get_srs_info() immediately after get_srs_files(),
    # then it probably tries to read the srs file before it has fully downloaded
    # and fails. fetch_client_file() gives the srs file time to download completely
    # and get_srs_info() can read it successfully.

    srs_downloaded_files = get_srs_files(start_time, end_time)

    file_name, downloaded_files = fetch_client_file(start_time, end_time, client_name)

    lats, lngs, numbers = get_srs_info(srs_downloaded_files)

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
# Sample script for a _client_name plot

import sunpy.timeseries
from sunpy.net import Fido, attrs as a
import matplotlib.pyplot as plt

# Declare the start and end times
start_time = "_from"
end_time = "_to"

# Search in the timerange
results = _search_line_here

# Download files for the timerange
downresp = Fido.fetch(results)

# Make a timeseries object
combined_goes_ts = sunpy.timeseries.TimeSeries(downresp, source='_client_name', concatenate=True)

# Plot the timeseries object
im = combined_goes_ts.plot()

# Show the plot
plt.show()

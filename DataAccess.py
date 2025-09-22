import xarray as xr
import nwmurl
import joblib
import pandas as pd

def data_access(start_date, end_date, fcst_cycle, lead_time, feature_ids):
    ''' Access NWM data from cloud storage using kerchunk and xarray.
    Args:
        start_date: Start date in YYYYMMDDHHMM format.
        end_date: End date in YYYYMMDDHHMM format.
        fcst_cycle: List of forecast cycles to access (e.g., [0, 6, 12, 18]).
        feature_ids: List of feature IDs to extract streamflow data for.
    Returns:
        time_stream_df = A pandas DataFrame containing the extracted streamflow data with timestamps as the index.
    '''
    
    varinput = 1
    geoinput = 1
    runinput = 1
    urlbaseinput = 9
    meminput = 0


    url_list = nwmurl.generate_urls_operational(start_date, end_date, fcst_cycle, lead_time, varinput, geoinput, runinput, urlbaseinput, meminput)
    
    def process_file(file_url, feature_id):
        ds = xr.open_dataset(
            file_url,
            engine="kerchunk",
            storage_options={},
        )
        return ds['streamflow'].sel(feature_id=feature_id).values, ds.time.values

    with joblib.Parallel(n_jobs=10, backend="loky") as parallel:
        result_values = parallel(joblib.delayed(process_file)(file_url, feature_ids) for file_url in url_list)

    result_values = sorted(result_values, key=lambda x: x[1][0])
    streamflow = [item[0] for item in result_values]
    time = [item[1] for item in result_values]

    
    time_streamflow_df = pd.DataFrame(streamflow,columns=feature_ids)
    time_streamflow_df['time'] = time
    time_streamflow_df = time_streamflow_df.set_index('time')
    return time_streamflow_df
    # return time, streamflow
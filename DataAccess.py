import tempfile
import xarray as xr
import nwmurl
import joblib
import pandas as pd
from data_processing.forcings import compute_zonal_stats
import os
import geopandas as gpd
import random
import pathlib
import shutil


def data_access_streamflow(
    start_date, end_date, feature_ids, range_type, fcst_cycle=[0], lead_time=[1]
):
    """Access NWM data from cloud storage using kerchunk and xarray.
    Args:
        start_date: Start date in YYYYMMDDHHMM format.
        end_date: End date in YYYYMMDDHHMM format.
        fcst_cycle: List of forecast cycles to access (e.g., [0, 6, 12, 18]).
        lead_time: List of lead times to access (e.g., [1, 2, 3, ..., 36]).
        feature_ids: List of feature IDs to extract streamflow data for.
    Returns:
        A pandas DataFrame containing the extracted streamflow data with timestamps as the index.
    """

    varinput = 1
    geoinput = 1
    if range_type == "short_range":
        runinput = 1
    elif range_type == "medium_range":
        runinput = 2
    elif range_type == "long_range":
        runinput = 4
    else:
        print(
            "Please provide a valid range type: short_range, medium_range, or long_range"
        )
        return
    urlbaseinput = 9
    meminput = 0

    url_list = nwmurl.generate_urls_operational(
        start_date,
        end_date,
        fcst_cycle,
        lead_time,
        varinput,
        geoinput,
        runinput,
        urlbaseinput,
        meminput,
    )

    def process_file(file_url, feature_id):
        ds = xr.open_dataset(
            file_url,
            engine="kerchunk",
            storage_options={},
        )
        return ds["streamflow"].sel(feature_id=feature_id).values, ds.time.values

    with joblib.Parallel(n_jobs=joblib.cpu_count(), backend="loky") as parallel:
        result_values = parallel(
            joblib.delayed(process_file)(file_url, feature_ids) for file_url in url_list
        )

    result_values = sorted(result_values, key=lambda x: x[1][0])
    streamflow = [item[0] for item in result_values]
    time = [item[1][0] for item in result_values]

    time_streamflow_df = pd.DataFrame(streamflow, columns=feature_ids)
    time_streamflow_df["time"] = time
    time_streamflow_df = time_streamflow_df.set_index("time")
    return time_streamflow_df


def data_access_forcing(
    start_date,
    end_date,
    cat_ids,
    hydrofabric,
    range_type,
    fcst_cycle=[0],
    lead_time=[1],
):
    if not os.path.exists(hydrofabric):
        print("The hydrofabric doesn't exist")
        return

    print("Opening hydrofabric and subsetting the given catchments")
    gdf = gpd.read_file(hydrofabric, layer="divides")
    gdf = gdf.loc[gdf["divide_id"].isin(cat_ids)]

    varinput = 5
    geoinput = 1
    if range_type == "short_range":
        runinput = 1
    elif range_type == "medium_range":
        runinput = 2
    elif range_type == "long_range":
        runinput = 4
    else:
        print(
            "Please provide a valid range type: short_range, medium_range, or long_range"
        )
        return
    urlbaseinput = 9
    meminput = 0

    url_list = nwmurl.generate_urls_operational(
        start_date,
        end_date,
        fcst_cycle,
        lead_time,
        varinput,
        geoinput,
        runinput,
        urlbaseinput,
        meminput,
    )
    gridded_data = xr.open_mfdataset(
        url_list,
        combine="nested",
        concat_dim="time",
        engine="kerchunk",
        storage_options={},
    )
    gridded_data = gridded_data.drop_vars(["crs"])

    # make a temporary directory to store the forcings using .mkdtemp()
    forcing_dir = tempfile.mkdtemp()
    forcing_dir_temp = os.path.join(forcing_dir, "temp")
    try:
        os.makedirs(forcing_dir_temp)
        compute_zonal_stats(gdf, gridded_data, pathlib.Path(forcing_dir))
        ds = xr.open_dataset(forcing_dir + "/" + "forcings.nc")
    finally:
        shutil.rmtree(forcing_dir)
    return ds

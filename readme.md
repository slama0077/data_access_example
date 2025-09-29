# Forecast Data Access Example

This repository demonstrates how to use the `DataAccess` library to retrieve two primary types of forecast outputs: **streamflow forecasts** and **forcing values**. The provided code examples show how to access these datasets efficiently from cloud storage using `xarray`, `kerchunk`, and related tools.

### Streamflow Forecasts

To obtain streamflow forecasts, use the `data_access_streamflow` function. This function requires:

- `start_date` and `end_date`: The date range for the forecast (format: `YYYYMMDDHHMM`).
- `feature_ids`: List of feature IDs (e.g., river reach IDs) to extract streamflow data for.
- `range_type`: Forecast range (`short_range`, `medium_range`, or `long_range`).
- Optional: `fcst_cycle` (forecast cycles, e.g., `[0, 6, 12, 18]`) and `lead_time` (lead times, e.g., `[1, 2, ..., 36]`).

The function returns a pandas DataFrame with streamflow values indexed by time for the specified features.

### Forcing Values

To access forcing values (e.g., precipitation, temperature), use the `data_access_forcing` function. This function requires:

- `start_date` and `end_date`: The date range for the forecast.
- `cat_ids`: List of catchment IDs to extract forcing data for.
- `hydrofabric`: Path to the hydrofabric file (must contain the relevant catchment geometries).
- `range_type`: Forecast range (`short_range`, `medium_range`, or `long_range`).
- Optional: `fcst_cycle` and `lead_time`.

The function subsets the hydrofabric, retrieves gridded forecast data, computes zonal statistics for the specified catchments, and returns an xarray Dataset with the processed forcing values.

These examples are designed to help contributors understand how to access, process, and utilize forecast datasets in their own projects using the `DataAccess` library.

If you do not have the hydrofabric, you can download the hydrofabric from here:
https://communityhydrofabric.s3.us-east-1.amazonaws.com/hydrofabrics/community/conus_nextgen.gpkg



## Getting Started

1. **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/Contribute_Forecast.git
    cd data_access_example
    ```

2. **Install dependencies:**
> **Note:** This library depends on `NGIAB_data_preprocess`, which currently requires older versions of `xarray` and `zarr`. However, this project needs newer versions. As a temporary workaround, first install `NGIAB_data_preprocess`:
> ```bash
> pip install NGIAB_data_preprocess
> ```
> Then install the remaining dependencies:
> ```bash
> pip install -r requirements.txt
> ```
> This order avoids version conflicts. A permanent fix is pending in a submitted PR to `NGIAB_data_preprocess`.
    ```bash
    pip install -r requirements.txt
    ```

3. **Run the example:**
    Run the cells in DataAccessExample_V1.ipynb to see how to use the API

## Folder Structure

```
data_access_example/
├── DataAccessExample_V1.ipynb
├── requirements.txt
└── readme.md
```

## Contributing

Contributions are welcome! Please open issues or submit pull requests for improvements.

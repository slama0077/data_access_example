#!/usr/bin/env python3
import warnings
import argparse
from datetime import datetime

from DataAccess import data_access_streamflow
from DataAccess import data_access_forcing
import os

def parse_args():
    parser = argparse.ArgumentParser(
        description="Retrieve streamflow forecasts or forcing values using DataAccess."
    )

    parser.add_argument("--start_date", required=True, type=str,
                               help="Start date (YYYYMMDDHHMM)")
    parser.add_argument("--end_date", required=True, type = str,
                               help="End date (YYYYMMDDHHMM)")

    subparsers = parser.add_subparsers(dest="command", required=True)

    stream_parser = subparsers.add_parser(
        "streamflow", help="Retrieve streamflow forecast values"
    )

    stream_parser.add_argument("--feature_ids", nargs="+", type = int, required=True,
                               help="List of feature (reach) IDs")



    force_parser = subparsers.add_parser(
        "forcing", help="Retrieve forcing datasets (precip, temp, etc.)"
    )

    force_parser.add_argument("--cat_ids", nargs="+", required=True,
                              help="Catchment IDs to read forcing data for")

    force_parser.add_argument("--hydrofabric", required=True,
                              help="Path to hydrofabric geopackage or dataset")


    parser.add_argument("--range_type", required=True,
                              choices=["short_range", "medium_range", "long_range"],
                              help="Forecast range type")

    parser.add_argument("--fcst_cycle", nargs="+", type=int, default = [0],
                              help="Forecast cycles (0 6 12 18)")
    parser.add_argument("--lead_time", nargs="+", type=int, default = [1],
                              help="Lead times")

    return parser.parse_args()


def main():
    if not os.path.exists("Output"):
        os.mkdir("Output")
    args = parse_args()

    # STREAMFLOW MODE
    if args.command == "streamflow":
        df = data_access_streamflow(
            start_date=args.start_date,
            end_date=args.end_date,
            feature_ids=args.feature_ids,
            range_type=args.range_type,
            fcst_cycle=args.fcst_cycle,
            lead_time=args.lead_time,
        )
        output_file = "Streamflow" + args.start_date +".csv"
        df.to_csv(os.path.join("Output", output_file))
        print(f"\n Streamflow data retrieved and saved to Output directory as {output_file}")

        

    # FORCING MODE
    elif args.command == "forcing":
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            ds = data_access_forcing(
                start_date=args.start_date,
                end_date=args.end_date,
                cat_ids=args.cat_ids,
                hydrofabric=args.hydrofabric,
                range_type=args.range_type,
                fcst_cycle=args.fcst_cycle,
                lead_time=args.lead_time,
            )
            output_file = "Forcing" + args.start_date +".nc"
            ds.to_netcdf(os.path.join("Output", output_file))
            print(f"\n Forcing data retrieved and saved to Output directory as {output_file}")


if __name__ == "__main__":
    main()

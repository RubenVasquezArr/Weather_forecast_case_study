#!/bin/bash
# Script to convert the control forecast grib files into netcdf files
# therefore using CDO (Climate Data Operator), so make sure this is installed

# folder with GRIB files (please change for own directory)
input_dir="/home/jupyter-lreske/ESDP_project/GRIB_files"
# folder, where the netcdf files should be saved
output_dir="/home/jupyter-lreske/ESDP_project/netcdf_files"

# make sure, this directories exist
if [ ! -d "$input_dir" ]; then
  echo "Inputdirectorie does not exist: $input_dir"
  exit 1
fi

if [ ! -d "$output_dir" ]; then
  mkdir -p "$output_dir"
fi

# loop over all files in the input directory
for grib_file in "$input_dir"/*.nc; do
  if [ -f "$grib_file" ]; then
    #extract the filename 
    base_name=$(basename "$grib_file" .nc)
    #output filename
    netcdf_file="$output_dir/$base_name.nc4"
    #convert the grib files into netcdf format
    cdo -f nc copy "$grib_file" "$netcdf_file"
    echo "Converted: $grib_file -> $netcdf_file"
  else
    echo "No GRIB files in directory: $input_dir"
  fi
done


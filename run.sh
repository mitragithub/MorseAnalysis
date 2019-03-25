#!/bin/bash
#$ -cwd
# -l himem
# -l shortjob
#$ -l m_mem_free=32G

# image size
l=8557
w=11377
persistence_threshold=0.01   # can be larger for efficiency
remove_branch_threshold=2250   # default value is 1
GAUSSIAN=0		    # Gaussian smoothing sigma, 0 means no smoothing

# lots of file paths.
filename="SAMIK_ORIGIN"
image_path="dataset/${filename}/input_image.tif"
input_folder="dataset/${filename}"
output_folder="result/${filename}"

# first, convert image to a grid file, stored under output_folder
echo "Running image2grid......"
python image2grid.py $image_path $output_folder

# Then run jiayuan's triangulation code, get vert, edge, tri after removing
# zero-value pixels. There could a third parameter (Gaussian_sigma, default=1).
echo "Running triangulation......"
python threshold_triangulation.py $image_path $input_folder $GAUSSIAN

# Run discrete morse with vert, edge, tri files
echo "Running discrete morse......"
python graphRecon.py $filename -t 2 $persistence_threshold

# Remove redundant edges of discrete morse output, in new_vert, new_edge.txt
echo "Running RemoveBranch2D......"
./RemoveBranch2D $output_folder $l $w $remove_branch_threshold

# convert new_vert, new_edge to an image
echo "Running graph2image.py......"
python graph2image.py $output_folder $l $w

# output geojson
echo "Running geojson_2D.py......"
# python geojson_2D.py $output_folder

echo "Done:)"
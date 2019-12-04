#! /bin/bash

root_path="$( cd "$(dirname "$0")" ; pwd -P )/.."

which parallel
if [ $? == 1 ]; then
	echo "Please install parallel"
	exit 1
fi

num_jobs=4
prefix=""
first=1
while [[ $# -gt 0 ]]
do
key="$1"

case $key in
	-j|--jobs)
		num_jobs="$2"
		shift # past argument
		shift # past value
	;;
	-p|--prefix)
		prefix="$2"
		shift # past argument
		shift # past value
	;;
	-h|--help)
		echo "usage: chunk-import.sh <pbf-path> [OPTIONS]"
		echo "Imports every chunk into own db"
		echo ""
		echo "OPTIONS"
		echo "  -j, --jobs     Number of parallel jobs. Default: 4"
		echo "  -p, --prefix   Database prefix to be used"
		echo "  -h, --help     Shows this help and exit"
		exit 0
	;;

	*)
		if [ $first == "1" ]; then
			pbf_path="$1"
			shift # past pbf-path
			first=0
		else
			echo "Unknown option $key"
			exit 1
		fi
	;;
esac
done

if [ -z "$pbf_path" ]; then
	echo "No pbf path was given. See clear-cache-files -h for details"
	exit 1
fi

ls "$pbf_path/*.osm.pbf" | sed "s/.osm.pbf//" | parallel -j$num_jobs --eta "$root_path/create-db $prefix{} && $root_path/read-pbf $prefix{} {}.osm.pbf"

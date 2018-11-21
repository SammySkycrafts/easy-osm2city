# easy-osm2city
And wrapper around [osm2city](https://gitlab.com/fg-radi/osm2city) inspired by easy-rsa.

## Usage
### Getting started
* Clone the repo (or download the as zip/tar file and unpack it).
* Then go into the directory, run `./install` and follow the instructions.
* Run `./create-venv`. This will create a virtual environment and installs all needed python packages.
* Create a database using `./create-db -d <database>`.
* Download the .pbf file for the area you want to build and put it into the `pbf` directory.  
  I recommend to download from [GeoFabrik](http://download.geofabrik.de/).
* Read the .pbf file into the database by running `./read-pbf -d <database> -f <pbf-file>`
* If you want to speed up further opperation on the database, index it by running `./index-db -d <database>`.  
  I highly recommend to do so.
* Next step is to create a project by running `./create-project -p <project>` and following the instructions.
* Now you can build your first scenery by running `./build -p project`. You will find the scenery under `projects/<your-project>/scenery`.
* If you don't know, what a program does, simply run it with the `-h` parameter to get help.

### Other programs
Programs that were not covered by `Getting started`:
* `update-programs`: Will update easy-osm2city, osm2city it self and osm2city-data
* `clear-cache-files -p <project>`: Will delete cache files created by osm2city.
* `edit-settings -p <project>`: Is a simple way to edit your `params.ini`file (which is used by osm2city to know what and how to generate the scenery).  
  It will make sure, that everything is in the correct format and in the correct datatype.
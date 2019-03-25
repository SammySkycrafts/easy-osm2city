# easy-osm2city
And wrapper around [osm2city](https://gitlab.com/fg-radi/osm2city) inspired by easy-rsa.

## Usage
### Getting started
* Clone the repo (or download the as zip/tar file and unpack it).
* Then go into the directory, run `./install` and follow the instructions.
* Create a database using `./create-db <database>`.
* Download the .pbf file for the area you want to build and put it into the `pbf` directory.  
  I recommend to download from [GeoFabrik](http://download.geofabrik.de/).
* Read the .pbf file into the database by running `./read-pbf <database> <pbf-file>`
* If you want to speed up further opperation on the database, index it by running `./index-db <database>`.  
  I highly recommend to do so.
* Next step is to create a project by running `./create-project <project>` and following the instructions.
* Now you can build your first scenery by running `./build project`. You will find the scenery under `projects/<your-project>/scenery`.
* If you don't know, what a program does, simply run it with the `-h` parameter to get help.

### Other programs
Programs that were not covered by `Getting started`:
* `update-programs`: Will update easy-osm2city, osm2city it self and osm2city-data
* `clear-cache-files <project>`: Will delete cache files created by osm2city.
* `./create-venv`. This will create a virtual environment and installs all needed python packages. NOTE: This is run for you by the installer.
* `edit-settings <project>`: Is a simple way to edit your `params.ini`file (which is used by osm2city to know what and how to generate the scenery).  
  It will make sure, that everything is in the correct format and in the correct datatype.
* `./delete-db <database>`: Deletes the database.

## User scripts
User scripts in the `scripts/` directory are help scripts contributed by users. They Do not belong to the easy-osm2city concept but extend it. Use only if you know what you do.

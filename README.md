# README #

Python script for exporting gemini 2.2-compliant metadata from a csv file to individual xml files.

### How do I get set up? ###

* Create a virtual environment in the root directory
* Activate the virtual environment
* Install dependencies by running pip install -r requirements,txt
* See the sample csv file for the correct layout- alternatively change the column mappings in metadata_import.py to match your layout
* Place your csv file in the input folder
* Change to the python directory
* Count the total number of rows in your CSV including the header row and edit the numrows line (28) in metadata_import_ea.py to match
* Run python metadata_import_ea.py
* Your xml files will miraculously appear in the output folder

### Who do I talk to? ###

* jocook@astuntechnology.com
* Other Astun personnel
* Based on code originally written by Brian O'Hare
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

### Data Specifics ###

* Creation Date and Revision Date must be in the form YYYY-MM-DD
* Descriptive Keywords can be a comma-separated list
* AfA Element must be one of the following (case-sensitive):
* Open Data Risk Assessment
  * Not AfA (To be Assessed)
  * Not AfA (To be Assessed with Guidance)
  * AfA (Publication Scheme and Information for Re-Use Register)
  * AfA (Public Register)
  * AfA (Publication Scheme)
  * AfA (Information Requests only)
  * Not Applicable - third party dataset
* AfA Number must be a decimal or 0, not blank
* Topic Category must be one of the following (case-sensitive), but can be a comma-separated list:
  * Farming
  * Biota
  * Boundaries
  * Climatology, meteorology, atmosphere
  * Economy
  * Elevation
  * Environment
  * Geoscientific information
  * Health
  * Imagery base maps earth cover
  * Intelligence military
  * Inland waters
  * Location
  * Oceans
  * Planning cadastre
  * Structure
  * Utilities communication
* West, East, North, South bounding coordinates must be in WGS84 format (lat/lon)
* Temporal Extent can be a comma-separated list (begin date, end date) but dates must be in form YYYY-MM-DD
* Data Fromat and Version must come from provided lists of formats and versions
* Data Quality Info must be one of datset or nonGeographicDataset (case-sensitive)
* Inspire theme must come from the INSPIRE Themes Thesaurus in Geonetwork (choose one only)

### Who do I talk to? ###

* jocook@astuntechnology.com
* Other Astun personnel
* Based on code originally written by Brian O'Hare
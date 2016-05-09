# foia-online
Bulk downloading from FOIA online, given a URL. Designed for requests made through [foiaonline.regulations.gov](foiaonline.regulations.gov) that come back with several hundreds or thousands of records and cannot be easily downloaded through the user interface.

To use: 

* Download required libraries
    pip install -r /path/to/requirements.txt

* Run the script (python 3)
    python downloader.py

* Paste in your URL when prompted
    Example: https://foiaonline.regulations.gov/foia/action/public/view/request?objectId=090004d280b6c05e

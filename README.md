# rec-activity-scraper
Automated Github Actions workflow that runs web scraper to get Cal Poly Rec Center Space Activity data

## Setup
source venv/bin/activate
pip install -r requirements.txt

## Running the scraper
python scraper.py

* ignore preprocessing.py

## Model A (Activity) + Model B (Duration) Code
Refer to Colab notebook links

## Running the GUI
`
python app.py
`

View at: http://127.0.0.1:7860/

## Misc
certifi.where()

export REQUESTS_CA_BUNDLE=".../rec-activity-scraper/venv/lib/python3.9/site-packages/certifi/cacert.pem"

export SSL_CERT_FILE="$REQUESTS_CA_BUNDLE"

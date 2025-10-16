# rec-activity-scraper
Automated Github Actions workflow that runs web scraper to get Cal Poly Rec Center Space Activity data

pip install -r requirements.txt
source venv/bin/activate

certifi.where()
export REQUESTS_CA_BUNDLE=".../rec-activity-scraper/venv/lib/python3.9/site-packages/certifi/cacert.pem"
export SSL_CERT_FILE="$REQUESTS_CA_BUNDLE"

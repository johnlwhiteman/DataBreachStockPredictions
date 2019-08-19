# Security Data Breaches

*A simple project to track and predict stock prices after a data breach is publicly announced.*

| ID | Name | Symbol | Date |
|----|------|--------|------|
| COF | Capital One | COF | 2019-07-29 |
| TGT | Target | TGT | 2018-12-19 |
| MAR | Marriott | MAR | 2018-11-30 |
| FB-2018 | Facebook | FB | 2018-09-28 |
| TMUS | T-Mobile | TMUS | 2018-08-24 |
| DGX | Quest Diagnostics | DGX | 2018-05-03 |
| UAA | Under Armour | UAA | 2018-03-29 |
| EFX | Equifax | EFX | 2017-09-07 |
| ANTM | Anthem | ANTM | 2015-02-04 |
| EBAY | Ebay | EBAY | 2014-5-21 |

## Add Alpha Vantage API Key
* This application uses the Alpha Vantage API to download historical stock prices. You will need to get your own free API key. Go to their [website](https://www.alphavantage.co/documentation/) for instructions.
* Once you have the key, do the following:
* Open *setEnv* and add your key ALPHA_VANTAGE_API_KEY='YOUR KEY GOES HERE'
* Save the file and close ...

## Execution
Run in a terminal (Plots won't work here):
* *$ runClient*

Run in a browser:
* *$ runJupyter* 

## Add a New Breach
* Open *breaches.json*
* Enter new breach information
        `{
            "ID": "UNIQUE ID ... LIKE STOCK TICKER",
            "name": "COMPANY NAME",
            "symbol": "STOCK TICKER",
            "date": "DATE OF THE BREACH",
            "ignore": false
        },`
* Save file and close
* Execute as previously instructed

## Update All CSV Data Files
* When calling the *b.open(path="breaches.json", forceRemote=False)* function simply override the *forceRemote=False* parameter to *forceRemote=True*. 
* All files will automatically be updated. 
* Sometimes Alpha Vantage will throw an error after doing a handful of downloads. 
** Simply set the restart where the error occurred. The previous breaches can be ignored by setting the *"ignore": false* parameter to *"ignore": true* in the breaches.json file.

## Installation (Ubuntu)
* *$ sudo add-apt-repository ppa:jonathonf/python-3.7*
* *$ sudo apt-get update*
* *$ sudo apt-get install python3.7 -y*
* *$ sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.7 1*
* *$ sudo update-alternatives --list python*
* *$ sudo apt-get install python3-pip -y*
* *$ sudo update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 1*
* *$ pip install pystan*
* *$ pip install fbprophet*
* *$ pip install plotly*
* *$ pip install quandl*
* *$ pip install jupyter*
* *$ pip install matplotlib*
* *$ pip install alpha_vantage*

## Data Breach Resources
* [California's Breach Database](https://oag.ca.gov/privacy/databreach/list)
* [Fraud.org](https://www.fraud.org/latest_breaches)
* [Identity Theft Resource Center](https://www.idtheftcenter.org/2019-data-breaches/)
* [I Have Been Pawned](https://haveibeenpwned.com/)
* [Information is Beautiful](https://www.informationisbeautiful.net/visualizations/worlds-biggest-data-breaches-hacks/)
* [Oregon's Consumer Databreach Database](https://justice.oregon.gov/consumer/databreach/)
* [Privacy Rights ORG](https://www.privacyrights.org/)
* [SelfKey.org](https://selfkey.org/data-breaches-in-2019/)

## Developer Links
* [Alpha Advantage](https://www.alphavantage.co/documentation/)
* [Facebook's Profit](https://github.com/facebook/prophet)
* [Matplotlib](https://matplotlib.org/)
* [Pandas](https://pandas.pydata.org/)
* [Quandl](https://www.quandl.com/)

## Developers
* John L. Whiteman

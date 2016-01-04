
import scraperwiki
import lxml.html
import bs4


def prepare_counties():
    states = ["AL","AK","AZ","AR","CA","CO","CT","DC","DE","FL","GA","GU","HI","ID","IL","IN","IA","KS","KY","LA","ME","MD","MA","MI","MN","MO","MP","MS","MT","NE","NV","NH","NJ","NM","NY","NC","ND","OH","OK","OR","PA","PR","RI","SC","SD","TN","TX","UT","VT","VA","WA","WV","WI","WY"]
    county_directory_url = 'http://explorer.naco.org/ciccfm/'
    
    for state in states:
        url = county_directory_url + 'state.cfm?statecode=' + state;
        get_counties(url, state);
    

def get_counties(url, state):
    html = scraperwiki.scrape(url)
    soup = bs4.BeautifulSoup(html, "lxml")
    count = 0;

    if soup.select('table#stateResponse-table') and soup.select('table#stateResponse-table')[0].select("tr"):
        for row in soup.select('table#stateResponse-table')[0].select("tr"):
            
            if (count > 0):
                county_id = row.select('a')[0].attrs.get('id')
                county_data_url = 'http://explorer.naco.org/ciccfm/county.cfm?id=' + county_id
                county_name = row.select('a')[0].get_text()
                
                get_county_data(state, county_name, county_data_url)

            count = count + 1


def get_county_data(state, county_name, county_data_url):
    html = scraperwiki.scrape(county_data_url)
    soup = bs4.BeautifulSoup(html, "lxml")
    count = 0;

    profile = {}
    
    address_count = 0;

    for rows in soup.select('div#countyResponse-countyDetails')[0].select("table.table")[0].select("tr"):

        if (rows.select('th')[0].get_text().strip() == 'Website:'):
            profile['url'] = rows.select('td')[0].get_text()
    
    for rows in soup.select('div#countyResponse-countyDetails')[0].select("table.table")[1].select("tr"):

        if (rows.select('th')[0].get_text().strip() == 'Phone:'):
            profile['phone'] = rows.select('td')[0].get_text()

        if (rows.select('th')[0].get_text().strip() == 'Address:'):
            profile['address_1'] = rows.select('td')[0].get_text()
            address_count = address_count + 1

        if (rows.select('th')[0].get_text().strip() == ''):

            if address_count == 1: 
                profile['address_2'] = rows.select('td')[0].get_text()

            if address_count == 2: 
                profile['address_locality'] = rows.select('td')[0].get_text()

            if address_count == 3: 
                profile['address_postcode'] = rows.select('td')[0].get_text()

            address_count = address_count + 1

    profile['name'] = county_name
    profile['address_region'] = state
    profile['cite_source'] = county_data_url

    scraperwiki.sqlite.save(unique_keys=['name', 'address_region'], data=profile, table_name = "jurisdictions")

    for rows in soup.select('div#countyResponse-electedOfficials')[0].select('div#countyResponse-electedOfficials')[0].select("table.table")[0].select("tr"):
        
        official = {}

        official['state'] = state
        official['government_name'] = county_name
        official['name'] = rows.select('th')[0].get_text().strip()
        official['position'] = rows.select('td')[0].get_text().strip()
        official['cite_source'] = county_data_url

        scraperwiki.sqlite.save(unique_keys=['name', 'government_name'], data=official, table_name = "officials")

prepare_counties()
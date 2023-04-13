# Import All the require libraries
from selenium import webdriver
from time import sleep
import requests
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st
from selenium.webdriver.chrome.options import Options
from PIL import Image
import zipfile

# Function to fetch Global Times data
def global_times_data(query):
    # Request the url by driver
    url='https://search.globaltimes.cn/QuickSearchCtrl'
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    # driver = webdriver.Chrome()
    driver.get(url)
    driver.implicitly_wait(30)
    sleep(3)

    # find the searchbox and get him the action command
    search_box = driver.find_element('name','search_txt')
    search_box.send_keys(query)
    search_box.submit()

    # create all headers list to append the data
    links=[]
    ids=[]
    titles=[]
    descs=[]
    dates=[]
    authors=[]

    # get the soup to scrap
    htmlcontent=driver.page_source
    soup = BeautifulSoup(htmlcontent, 'html.parser')

    # Hit the main class to get the elements
    t = soup.find('div', class_='row-fluid body-fluid')

    # Get the all elements one by one and append it into the lists
    for row in t.find_all('div',class_='row-fluid'):
        row_ = row.find('div', class_="span9")
        if row_ is not None:
            link = row_.find('a')
            if link is not None:
                links.append(link.get('href'))
                ids.append(link.get('href').split('/')[-1].split('.')[0])
        if row_ is not None:
            desc = row_.find('p')
            if desc is not None:
                descs.append(desc.text)
        if row_ is not None:
            title = row_.find('h4')
            if title is not None:
                titles.append(title.text)
        if row_ is not None:
            auth_date=row_.find('small')
            if auth_date is not None:
                dates.append(auth_date.text.split('|')[0].split(' ')[8].split('\t')[1])
                authors.append(auth_date.text.split('|')[-2].split(':')[1])

    # create a data frame of this data

    df = pd.DataFrame()
    df = pd.DataFrame({'Id':ids,'Title':titles,'Description':descs,'Author':authors,'Date':dates,'Link':links})
    return df

# Function to fetch Wall Street Journal data
def wall_street_data(query):
    # Configure the webdriver with headless options
    # Request the url by driver
    url='https://www.wsj.com/search?query='+query
    driver = webdriver.Chrome()
    driver.get(url)
    driver.implicitly_wait(30)
    sleep(30)
    # create all headers list to append the data
    data_id=[]
    link_data=[]
    title_data=[]
    desc_data=[]
    auth_data=[]
    date_data=[]
    # get the soup to scrap
    htmlcontent=driver.page_source
    soup = BeautifulSoup(htmlcontent, 'html.parser')
    t=soup.find('div',class_="style--column--1p190TxH style--column-top--3Nm75EtS style--column-12--1x6zST_y")
    div=t.find('div',class_="style--column--1p190TxH style--column-top--3Nm75EtS style--column-8--2_beVGlu style--border-right--3pLIaDzb")
    for article_ in div.find_all('article',class_="WSJTheme--story--XB4V2mLz WSJTheme--overflow-visible--3OB31tWq WSJTheme--border-bottom--s4hYCt0s"):
        link_data.append(article_.find('a').get('href'))
        title_data.append(article_.find('span',class_='WSJTheme--headlineText--He1ANr9C').text)
        # Check if the element exists before calling the find() method
        desc = article_.find('span',class_='WSJTheme--summaryText--2LRaCWgJ')
        if desc is not None:
            desc_data.append(desc.text)
        else:
            desc_data.append("")
        auth = article_.find('p',class_="WSJTheme--byline--1oIUvtQ3")
        if auth is not None:
            auth_data.append(auth.text)
        else:
            auth_data.append("")
        date_ = article_.find('div',class_="WSJTheme--timestamp--2zjbypGD")
        if date_ is not None:
            date_data.append(date_.text)
        else:
            date_data.append("")
    df = pd.DataFrame()
    df = pd.DataFrame({'Title':title_data,'Description':desc_data,'Author':auth_data,'Date':date_data,'Link':link_data})
    return df

# Function to fetch New York Post data
def nyp_data(query):
    url = "https://nypost.com/search/" + query
    # Send a GET request to the URL
    response = requests.get(url)
    # Create a Beautiful Soup object from the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')
    stories = soup.find('div', class_="search-results__stories")
    link_list = []
    heading_list = []
    author_list = []
    date_list = []
    description_list = []
    # Looping through every story
    for story in stories.find_all('div', class_="search-results__story"):
        # Finding story div
        story_div = story.find('div', class_="story__text")
        # Scraping link of the post
        try:
            post_link = story_div.find('a').get('href')
        except:
            post_link = None
        # Scraping headline of the post
        try:
            heading = story_div.find('a').text.strip()
        except:
            heading = ""
        # Scraping date of the post
        date = story_div.find('span', class_="meta--byline").text.strip()
        author_date_div = date.replace('\xa0\t\t\t', '')
        # Scraping author of the post
        try:
            author = author_date_div.split('\t')[0].split('By ')[1]
        except:
            author = ""
        # Scraping date of the post
        try:
            date = author_date_div.split('\t')[1].split('|')[0]
        except:
            date = ""
        # Scraping description of the post
        try:
            description = story_div.find('p', class_="story__excerpt").text.strip()
        except:
            description = ""

        # Appending all values to respective lists
        link_list.append(post_link)
        heading_list.append(heading)
        author_list.append(author)
        date_list.append(date)
        description_list.append(description)

    df = pd.DataFrame({'Title' : heading_list, 'Description' : description_list, 'Author' : author_list, 'Date' : date_list, 'Link' : link_list})
    return df

# Function to fetch New York Times data
def nyt_data(query):
    url = "https://www.nytimes.com/search?query=" + query
    # Send a GET request to the URL
    response = requests.get(url)
    # Create a Beautiful Soup object from the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')
    stories = soup.find('ol', {'data-testid': 'search-results'})
    
    link_list = []
    heading_list = []
    author_list = []
    description_list = []

    for story in stories.find_all('li', {'data-testid': 'search-bodega-result'}):
        # Scraping headline of the post
        try:
            heading = story.find('h4').text.strip()
        except:
            heading = ""
        # Scraping link of the post
        try:
            post_link = "https://www.nytimes.com/" + str(story.find('a').get('href'))
        except:
            post_link = None
        # Scraping heading of the post
        try:
            description = story.find('p', class_='css-16nhkrn').text.strip()
        except:
            description = ""
        # Scraping author of the post
        try:
            author = story.find('p', class_="css-15w69y9").text.strip()
            author = author.split('By ')[1]
        except:
            author = ""
        # Appending all values to respective lists
        link_list.append(post_link)
        heading_list.append(heading)
        author_list.append(author)
        description_list.append(description)


    df = pd.DataFrame({'Title' : heading_list, 'Description' : description_list, 'Author' : author_list, 'Link' : link_list})
    return df

# Function to fetch BBC data
def bbc_data(query):
    # Configure the webdriver with headless options
    # Request the url by driver
    url="https://www.bbc.co.uk/search?q="+query
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    # driver = webdriver.Chrome()
    driver.get(url)
    driver.implicitly_wait(30)
    sleep(15)
    # create all headers list to append the data
    data_id=[]
    link_data=[]
    title_data=[]
    desc_data=[]
    programmes=[]
    date_data=[]
    # get the soup to scrap all elements
    htmlcontent = driver.page_source
    soup = BeautifulSoup(htmlcontent, 'html.parser')
    m = soup.find('div', class_="ssrcss-181c4hk-SectionWrapper eustbbg3")
    for div in m.find_all('div', class_="ssrcss-1v7bxtk-StyledContainer enjd40x0"):
        for title in div.find_all('a', class_="ssrcss-rl2iw9-PromoLink e1f5wbog1"):
            title_data.append(title.text)
        for link in div.find_all('a'):
            link_data.append(link.get('href'))
        for desc in div.find_all('p', class_="ssrcss-1q0x1qg-Paragraph eq5iqo00"):
            desc_data.append(desc.text)
        for elements in div.find_all('div', class_="ssrcss-13nu8ri-GroupChildrenForWrapping e1ojgjhb2"):
            date_data.append(elements.text.split('Site')[0].split('Published')[-1])
            programmes.append(elements.text.split('Site')[1].split('Programmes')[-1])
        for id in div.find_all('a'):
            data_id.append(id.get('href').split('/')[-1].split('-')[-1])
    df = pd.DataFrame()
    df = pd.DataFrame({'Id':data_id,'Title':title_data,'Description':desc_data,'Programmes':programmes,'Date':date_data,'Link':link_data})
    return df

# Define function to create CSV and download zip folder
def download_csv_zip(dataframes):
    zip_file = zipfile.ZipFile('data.zip', mode='w')
    for name, dataframe in dataframes.items():
        # Create CSV file
        csv_file = dataframe.to_csv(index=False)
        # Add CSV file to zip folder
        zip_file.writestr(name + '.csv', csv_file)
    # Close zip folder
    zip_file.close()
    
    # Create link to download zip folder
    with open('data.zip', 'rb') as f:
        bytes_data = f.read()
    # Downloading the zip file
    st.download_button(label='Download Zip Folder', data=bytes_data, file_name='Reports.zip', mime='application/zip')

# Creating a Streamlit app
banner_img = Image.open('images/banner 1.png')
st.image(banner_img)
st.title('Welcome To News Scraper')
st.write("This tool helps to search news articles using keywords and scraps them from popular news websites like, Global Times, BBC, New York Post and New York Times.")
st.write('----')
# Creating a multiselect dropdown to select news sites
selected_sites = st.multiselect("News Sites", ['Global Times', 'New York Post', 'New York Times', 'BBC'])

# Creating a text input field and submit button in the Streamlit app
query = st.text_input("Search Query:")
submit_button = st.button("Submit")

# Displaying the results based on the search query and selected news sites
if submit_button:
    if query:
        if len(selected_sites) > 0:
            dataframes = {}
            for site in selected_sites:
                if site == 'Global Times':
                    with st.spinner('Fetching Global times Data...'):
                        # sleep(30)
                        gt_df = global_times_data(query)
                    gt_image = Image.open('images/GlobalTimesLogo.svg.png')
                    st.image(gt_image)
                    st.title('Global Times Data')
                    st.write(gt_df)
                    # Adding the dataframe in dict
                    dataframes['Global Times'] = gt_df
                    st.write("___________________________")
                    # Download button to download data in CSV format
                    csv = gt_df.to_csv(index=False).encode()
                    st.download_button(
                        label="Download Global Times data as CSV",
                        data=csv,
                        file_name='global_times_data.csv',
                        mime='text/csv',
                    )
                elif site == 'Wall Street Journey':
                    st.title('Wall Street Journal Data')
                    with st.spinner('Fetching Wall Street Journey Data...'):
                        wsj_df = wall_street_data(query)
                    st.write(wsj_df)
                    
                    # Download button to download data in CSV format
                    csv = wsj_df.to_csv(index=False).encode()
                    st.download_button(
                        label="Download Wall Street Journal data as CSV",
                        data=csv,
                        file_name='wall_street_journal_data.csv',
                        mime='text/csv',
                    )
                elif site == 'New York Post':
                    with st.spinner("Fetching Reports of New York Post!"):
                        nyp_df = nyp_data(query)
                    nyp_image = Image.open('images/New_York_Post_logo_logotype.png')
                    st.image(nyp_image)
                    st.title('New York Post Data')
                    st.write(nyp_df)
                    # Adding the dataframe in dict
                    dataframes['New York Post'] = nyp_df
                    st.write("___________________________")
                elif site == "New York Times":
                    with st.spinner("Fetching Reports of New York Times!"):
                        nyt_df = nyt_data(query)
                    nyt_image = Image.open('images/NewYorkTimes.svg.png')
                    st.image(nyt_image)
                    st.title('New York Times Data')
                    st.write(nyt_df)
                    # Adding the dataframe in dict
                    dataframes['New York Times'] = nyt_df
                    st.write("___________________________")
                elif site == "BBC":
                    with st.spinner("Fetching Reports of BBC!"):
                        bbc_df = bbc_data(query)
                    bbc_image = Image.open('images/BBC.svg.png')
                    st.image(bbc_image)
                    st.title('BBC Data')
                    st.write(bbc_df)
                    # Adding the dataframe in dict
                    dataframes['BBC'] = bbc_df
                    st.write("___________________________")
            download_csv_zip(dataframes)
        else:
            st.error("Please select any news site to scrap data from.")

    else:
        st.error("Please enter a query to search!")
'''
This script scrapes the lineup of each match in a given round of the English Premier League from the BDFutbol website.
BDFutbol EPL Match Lineup Scraper: 102 lines of code ~ ibrahimdavid24.dev'''

import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_date_hyperlinks(url):
    '''Extract the hyperlinks from the Date column in the first table on the page.'''
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Check if the request was successful

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the first table on the page
        table = soup.find('table', class_='taula_estil taula_estil-16')

        if table is not None:
            # Extract the hyperlinks from the Date column
            match_hyperlinks = []
            for row in table.find_all('tr', class_='jornadai ij1'):
                date_cell = row.find('td', class_='14')
                if date_cell:
                    link = date_cell.find('a')  
                    if link and link['href']: # Check if the link exists and has an 'href' attribute
                        match_hyperlinks.append(link['href'][2:]) # Remove the first two characters '..'
            
            return match_hyperlinks
        else:
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None
    
    

# URL of the Season and Round page:
season = input("Enter the season (2019-20, 2020-21, 2021-22, etc.): ") 
round_number = input("Enter the round number (1-38): ")
url = f'https://www.bdfutbol.com/en/t/teng{season}.html?tab=results&jornada={round_number}'


# Get the hyperlinks from the Date column in the first table
match_links = get_date_hyperlinks(url)


def extract_lineup():
    if match_links is not None:  # Check if the match_links list is not empty

        for match_link in match_links:
            '''Extract the lineup from the match link.'''

            match_url = f"https://www.bdfutbol.com/en{match_link}" # Create the full match URL
            
            # Extract the match ID from the match link
            match_id = match_url.split('=')[-1]

            # Send a GET request to the Match_URL
            response = requests.get(match_url)
            response.raise_for_status()  # Check if the request was successful

            # Parse the HTML content
            soup = BeautifulSoup(response.content, 'html.parser')

            ''' Get Team Names and store them in a list'''
            # Element containing team name:
            teamName_block = soup.find_all('div', class_='d-none d-md-block')
            team_names = [] # List to store team names

            for teamName in teamName_block:
                row =  teamName.find('div', class_='row mt-3 mb-2')
                if row:
                    # Extract Home & Away team names:
                    home_team = row.find('div', class_='col partit-equip')
                    if home_team:
                        home_name = home_team.find('a').text

                    away_team = row.find('div', class_='col partit-equip text-left')
                    if away_team:
                        away_name = away_team.find('a').text
                    
                    team_names.append({'Home':home_name, 'Away':away_name})
                    
            
            ''' Get Home & Away Lineups and store them in lists'''
            # Extract list of home players:
            home_player_columns = soup.find_all('div', class_='col-6 pl-0 pl-md-3 pr-0 pr-md-3')
            home_players = []

            for h_player in home_player_columns:
                h_tables = h_player.find_all('table', class_='taula_estil text-left')

                if h_tables:
                    for table in h_tables:
                        h_rows = table.find_all('tr')
                        for row in h_rows:
                            player = row.find_all('td')[:-1]
                            if len(player) >= 4:
                                hp_name = player[3].get_text(strip=True)

                                home_players.append(hp_name)


            # Extract list of away players:
            away_player_columns = soup.find_all('div', class_='col-6 pr-0 pr-md-3 pl-0 pl-md-3')
            away_players = []

            for a_player in away_player_columns:
                a_tables = a_player.find_all('table', class_='taula_estil text-left')

                if a_tables:
                    for table in a_tables:
                        a_rows = table.find_all('tr')
                        for row in a_rows:
                            player = row.find_all('td')[:-1]
                            if len(player) >= 4:
                                ap_name = player[3].get_text(strip=True)

                                away_players.append(ap_name)

            # Return the team names and lineups as dictionaries:
            home_dict = {home_name:home_players} 
            away_dict = {away_name:away_players}
            match_dict = {'match_id':[match_id for i in range(len(home_players))]} # Create a dictionary with the match_id

            home_df = pd.DataFrame({**match_dict, **home_dict}) # Merge the match_id with the home team players
            away_df = pd.DataFrame({**match_dict, **away_dict}) # Merge the match_id with the away team players

            home_df.to_csv(f'{home_name}_S{season}_R{round_number}_home.csv', index=False)
            away_df.to_csv(f'{away_name}_S{season}_R{round_number}_away.csv', index=False) 

    else:
        print("No table found on the season page.") # Print an error message if the match_links list is empty 




# Call the function to extract the lineup
extract_lineup()              
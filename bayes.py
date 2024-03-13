# This script scrapes the partial URL of every box
# score in the team schedule and then reconstructs
# the full URL. The idea is that you could then go
# to each of these box score URLs and scrape further
# data.

import requests, re, math
from bs4 import BeautifulSoup
import time

# Site to begin scraping
url = "https://www.basketball-reference.com/teams/MIA/2006_games.html"

# Scrape start page into tree
page = requests.get(url)
soup = BeautifulSoup(page.content, "html.parser")

# Isolate the schedule table by id, and grab every row
schedule_table = soup.find(id="games")
rows = schedule_table.findChildren('tr')

wins = 0.0
above_avg = 0
above_avg_w = 0

# Loop through every row
for row in rows:
   # Isolate the box score cell using the data-stat attribute
   boxscore_td = row.findChildren('td', {"data-stat": "box_score_text"})
   if len(boxscore_td) == 0:
       continue

   # Isolate the link and grab its href field
   game_href = boxscore_td[0].find('a', href=True)['href']

   # Find the game_result cell using the data-stat attribute
   game_result = row.findChildren('td', {"data-stat": "game_result"})
   if len(game_result) == 0:
       continue

   # Extract the win/loss result (W or L)
   result = game_result[0].text.strip()

   # Get the root url of the page variable
   regex = r'.*\.com'
   url_root = re.findall(regex, url)[0]

   # Formulate the final game base_url
   game_url = '{}{}'.format(url_root, game_href)
   game_url_shot_chart = game_url.replace('/boxscores/', '/boxscores/shot-chart/')

   # Print the win/loss result
   print(result)

   # Count wins
   if result == 'W':
       wins += 1

   # Make a request to the shot chart URL
   shot_chart_page = requests.get(game_url_shot_chart)
   shot_chart_soup = BeautifulSoup(shot_chart_page.content, "html.parser")

   # Find the "shooting-MIA" table
   shooting_table = shot_chart_soup.find('table', id='shooting-MIA')

   if shooting_table:
       # Find the final row in the table
       final_row = shooting_table.find_all('tr')[-1]

       # Extract the "fg_ast_pct" from the final row
       fg_ast_pct_element = final_row.find('td', {"data-stat": "fg_ast_pct"})
       if fg_ast_pct_element:
           fg_ast_pct_value = float(fg_ast_pct_element.text.strip())
           print(f'FG Ast Percentage: {fg_ast_pct_value}')
           if fg_ast_pct_value > 0.557:
               above_avg += 1
               if result == 'W':
                   above_avg_w += 1
      
       else:
           print("assist pct not found")
     
   time.sleep(2)



print(f'Total above average: {above_avg}')
above_avg_pct = above_avg / 82
print(f'Above Average Percentage: {above_avg_pct}')

print(f'Total Wins: {wins}')
win_percentage = wins / 82
print(f'Win Percentage: {win_percentage}')

print(f'Total Wins and Above Average: {above_avg_w}')
above_avg_w_pct = above_avg_w / wins
print(f'Above Average given Win: {above_avg_w_pct}')

result = above_avg_w_pct * win_percentage
result = result / above_avg_pct
print(f'Likelihood the Miami Heat win a game given that they have an above average assist percentage: {result}')




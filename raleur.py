import requests
from bs4 import BeautifulSoup
from random import randint

searchstring = '&taxonomy[course][]=hoofdgerechten'
baseURL = 'https://www.leukerecepten.nl/'

def getResultPage(pageNr : int):
    url = baseURL + 'page/' + str(pageNr) + '/?s=' + searchstring
    r = requests.get(url)
    if r.status_code != 200:
        print(f"Error in requests.get({url}): status code {r.status_code}")
        exit()
    return BeautifulSoup(r.content, 'html.parser')

def getNumberofResultPages(page : BeautifulSoup):
    s = page.find('div', class_='column button-holder')
    # use index -2 to get the penultimate box in the column button-holder class
    # since the last box (index -1) is the 'volgende' box
    lastPage = s.find_all('a')[-2]
    return int(lastPage.text)

def getRecipe(page : BeautifulSoup, recipeIndex : int):
    if recipeIndex > 24:
        print(f'Error in getRecipe(recipeIndex={recipeIndex}): Only up to 24 recipes per page')
        exit()
    recipe = page.find('div', id='receptnummer_' + str(recipeIndex))
    return recipe.find('a')

initialPage = getResultPage(1)

# find out how many pages of results there are
nrofPages = getNumberofResultPages(initialPage)
print(f"It seems like there are {nrofPages} pages of recipes for this search")

# let's print the title and link to the first recipe
recipe = getRecipe(initialPage, 1)
print(f"The first recipe I found is called '{recipe.get('title')}'")

# now let's get a random recipe
pageNr = randint(1, nrofPages)
page = getResultPage(pageNr)
# todo: on the last page, nr of recipes may be fewer than 24. So ideally scrape nrOfRecipesPerPage from page itself
nrOfRecipesPerPage = 24
recipeNr = randint(1, nrOfRecipesPerPage)
recipe = getRecipe(page, recipeNr)
print(f"My randomly chosen recipe is the following: '{recipe.get('title')}'")
print(f"Find it at {recipe.get('href')}")

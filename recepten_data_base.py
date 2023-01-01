import pandas as pd
from hashable_df import hashable_df
from os.path import exists
from datetime import datetime
import numpy as np
import random

time_weight = 10.0
ingredient_weight = 30.0
type_of_kitchen_weight = 20.0
season_weight = 20.0
url_weight = 100.0

def getUrlScore(url1, url2):
    return (url1 is url2)

def getTimeScore(time1, time2):
    try:
        time_difference = np.abs(time1-time2)
        if (time_difference > 60):
            return 0.0
        
        return 10.0 - 1.0/6.0*float(time_difference)
    except:
        print("times are not valid")
        return 0.0


def getTypeOfKitchenScore(kitchen1, kitchen2):
    try:
        if kitchen1 == kitchen2:
            return 10.0
        
        return 0.0
    except:
        print("kitchen types are not valid")
        return 0.0

def stringToList(ingredients_string):
    if type(ingredients_string) is not str:
        return []

    ingredients_list = ingredients_string.split(", ")
    for index, ingredient in enumerate(ingredients_list):
        ingredient = ingredient.replace('[', '')
        ingredient = ingredient.replace(']', '')
        ingredient = ingredient.replace("'", "")
        ingredients_list[index] = ingredient

    return ingredients_list

def getIngredientScore(ingredients1, ingredients2):
    if type(ingredients1) is not str:
        return 0.0

    number_of_the_same_ingredients = 0

    ingredient_list_1 = stringToList(ingredients1)
    ingredient_list_2 = stringToList(ingredients2)
    
    for ingredient in ingredient_list_1:
        if ingredient in ingredient_list_2:
            number_of_the_same_ingredients = number_of_the_same_ingredients + 1
            # todo: check for capitals/noncapitals

    percentage_the_same = float(number_of_the_same_ingredients)/float(len(ingredient_list_1))

    return (percentage_the_same/10.0)

def isInSeason(season):
    month = datetime.now().month
    
    winter_list = ["winter", "Winter"]
    if (season in winter_list):
        return (month < 3 or month == 12)

    spring_list = ["spring", "Sprint", "lente", "Lente"]
    if (season in spring_list):
        return (month > 2 and month < 6)

    summer_list = ["Summer", "summer", "Zomer", "zomer"]
    if (season in summer_list):
        return (month > 5 and month < 9)

    autum_list = ["Autum", "autum", "Herfst", "herfst"]
    if (season in autum_list):
        return (month > 8 and month < 12)

    else:
        print("invalid season " + season)
        return True

def getSeasonScore(season):
    if isInSeason(season):
        return 0.0
    return 10.0*season_weight

def getSimilarityScore(recipe1, recipe2):
    time_score = getTimeScore(recipe1["time"],  recipe2["time"])
    ingredient_score = getIngredientScore(recipe1["ingredients"], recipe2["ingredients"])
    type_of_kitchen_score = getTypeOfKitchenScore(recipe1["type_of_kitchen"], recipe2["type_of_kitchen"])
    # url_score = getUrlScore(recipe1["url_or_bookpage"], recipe2["url_or_bookpage"])
    url_score = 0.0

    total_score = time_weight * time_score + ingredient_weight * ingredient_score + type_of_kitchen_score * type_of_kitchen_score + url_weight * url_score

    return total_score

class RecipesDataBase:
    data_base = pd.DataFrame([])
    save_path = "data_base.csv"

    def __init__(self):
        if exists(self.save_path):
            self.data_base = pd.read_csv(self.save_path)

    def getDataBase(self):
        return self.data_base

    def add(self, title, url_or_bookpage, ingredients, season, time, type_of_kitchen):
        self.data_base = self.data_base.append({'title':title, 'url_or_bookpage':url_or_bookpage, 'ingredients':ingredients, 
        'season': season, 'time': time, 'type_of_kitchen': type_of_kitchen}, ignore_index=True)

    def saveToCSV(self):
        self.data_base.to_csv(self.save_path, index=False)

    def removeDuplicates(self):
        self.data_base = hashable_df(self.data_base).drop_duplicates()

    def getUniqueRecipes(self, number_of_recipes):
        print("Get unique recipes")
        selected_recipes = pd.DataFrame() 
        first_recipe_idx = random.randrange(self.data_base.index[0], self.data_base.index[-1], 1)
        selected_recipes = selected_recipes.append(self.data_base.loc[first_recipe_idx])

        # todo: take into account what was already cooked

        recipe_scores = {}
        while (len(selected_recipes) < number_of_recipes):
            already_selected_idx = selected_recipes.index[-1]
           
            for recipe_idx in self.data_base.index:
                already_selected_recipe = selected_recipes.loc[already_selected_idx]

                if recipe_idx in selected_recipes.index:
                    recipe_scores[recipe_idx] = float('inf')
                    continue

                similarity_score = getSimilarityScore(self.data_base.loc[recipe_idx], selected_recipes.loc[already_selected_idx])
                season_score = getSeasonScore(self.data_base.loc[recipe_idx]["season"])
                total_score = similarity_score + season_score

                if (recipe_idx in recipe_scores):
                    recipe_scores[recipe_idx] = total_score + recipe_scores[recipe_idx]
                else:
                    recipe_scores[recipe_idx] = total_score
            
            sorted_scores = sorted(recipe_scores.items(), key=lambda kv:(kv[1], kv[0]))
            least_similar_recipe = self.data_base.loc[sorted_scores[0][0]]
            
            selected_recipes = selected_recipes.append(least_similar_recipe)

        return selected_recipes

    def getIngredients(self, recipe_indices):
        ingredients = []

        for recipe_index in recipe_indices:
            recipe_ingredients = self.data_base.loc[recipe_index]["ingredients"]
            recipe_ingredients = stringToList(recipe_ingredients)
            for ingredient in recipe_ingredients:
                ingredients.append(ingredient)

        return ingredients


recipe_data_base = RecipesDataBase()
ingredients = ["bread", "spaghetti"]
recipe_data_base.add("Tosti", "https://url.test", ingredients, "spring", 10, "Dutch")
recipe_data_base.removeDuplicates()

print("\n get full database\n")
print(recipe_data_base.getDataBase())

print("\nget unique database")
unique_recipes =recipe_data_base.getUniqueRecipes(5)
print(unique_recipes)

print("\ningredients of unique recipes")
ingredients = recipe_data_base.getIngredients(unique_recipes.index)
print(ingredients)

# todo: get ingredients with appropriate amounts of all recipes and make sure they are added
# todo: print all selected recipes, urls etc
# todo: save which recipes are going to be cooked
# todo: count how many times the recipes were cooked before and add a cost

recipe_data_base.saveToCSV()

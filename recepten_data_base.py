import pandas as pd
from hashable_df import hashable_df
from os.path import exists
from datetime import datetime
import numpy as np

# todo: similarity score!

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

def getSeasonScore(season):
    month = datetime.now().month
    if (season == "winter"):
        return (month < 3 or month == 12)
    if (season == "spring"):
        return (month > 2 and month < 6)
    if (season == "summer"):
        return (month > 5 and month < 9)
    if (season == "autum"):
        return (month > 8 and month < 12)
    else:
        print("invalid season " + season)
        # Check for capitals
        return True

def getSimilarityScore(recipe1, recipe2):
    # season_score = getSeasonScore(recipe1["season"])
    time_score = getTimeScore(recipe1["time"],  recipe2["time"])
    ingredient_score = getIngredientScore(recipe1["ingredients"], recipe2["ingredients"])
    type_of_kitchen_score = getTypeOfKitchenScore(recipe1["type_of_kitchen"], recipe2["type_of_kitchen"])

    # season_weight = 40
    time_weight = 10
    ingredient_weight = 30
    type_of_kitchen_weight = 20

    total_score = time_weight * time_score + ingredient_weight * ingredient_score + type_of_kitchen_score * type_of_kitchen_score

    return total_score

    # todo: implement this after the proper data base is there
    # return recipe1["url_or_bookpage"] == recipe2["url_or_bookpage"] 

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
        selected_recipes = selected_recipes.append(self.data_base.loc[0])
        # todo: in the future we want to get a random selection and therefore we don't want to
        # initialize based on the first one, but maybe on the one that was cooked already the least

        similarity_scores = {}
        while (len(selected_recipes) < number_of_recipes):
            already_selected_idx = selected_recipes.index[-1]
           
            for recipe_idx in self.data_base.index:
                already_selected_recipe = selected_recipes.loc[already_selected_idx]

                if recipe_idx in selected_recipes.index:
                    similarity_scores[recipe_idx] = float('inf')
                    continue

                score = getSimilarityScore(self.data_base.loc[recipe_idx], selected_recipes.loc[already_selected_idx])

                if (recipe_idx in similarity_scores):
                    similarity_scores[recipe_idx] = score + similarity_scores[recipe_idx]
                else:
                    similarity_scores[recipe_idx] = score
            
            sorted_scores = sorted(similarity_scores.items(), key=lambda kv:(kv[1], kv[0]))
            least_similar_recipe = self.data_base.loc[sorted_scores[0][0]]
            
            selected_recipes = selected_recipes.append(least_similar_recipe)

        return selected_recipes



recipe_data_base = RecipesDataBase()
ingredients = ["bread", "spaghetti"]
recipe_data_base.add("Tosti", "https://url.test", ingredients, "spring", 10, "Dutch")
recipe_data_base.removeDuplicates()

print("\n get full database\n")
print(recipe_data_base.getDataBase())

print("get unique database")
print(recipe_data_base.getUniqueRecipes(5))




recipe_data_base.saveToCSV()

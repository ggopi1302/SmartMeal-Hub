# recommendations.py

from meal.models import Meal
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


#INGREDIENT SUBSTITUTION DICTIONARY
SUBSTITUTIONS = {
    # --- Dairy & Milk ---
    "milk": ["yogurt", "buttermilk", "cream", "curd", "soy milk", "almond milk"],
    "buttermilk": ["milk + lemon", "curd", "yogurt"],
    "cream": ["milk", "curd", "evaporated milk"],
    "cheese": ["paneer", "tofu", "nutritional yeast"],
    "butter": ["ghee", "oil", "margarine", "coconut oil"],
    "yogurt": ["curd", "sour cream", "buttermilk"],

    # --- Eggs ---
    "egg": ["banana", "chia seeds", "flaxseed", "applesauce"],
    "egg yolk": ["butter", "cream"],
    "egg white": ["aquafaba"],  # chickpea water foam

    # --- Grains ---
    "rice": ["quinoa", "couscous", "broken wheat (dalia)", "millets"],
    "oats": ["quinoa", "rava", "millets"],
    "bread": ["chapati", "tortilla", "pita"],
    "flour": ["atta", "oat flour", "almond flour"],

    # --- Proteins ---
    "chicken": ["tofu", "paneer", "mushrooms"],
    "fish": ["tofu", "mushrooms"],
    "beef": ["mushrooms", "jackfruit"],
    "mutton": ["beef", "mushrooms"],
    "paneer": ["tofu", "mushrooms"],
    "dal": ["chickpeas", "kidney beans", "black beans"],

    # --- Vegetables ---
    "potato": ["sweet potato", "yam"],
    "tomato": ["tomato paste", "ketchup", "puree"],
    "spinach": ["methi", "amaranth leaves"],
    "onion": ["spring onion", "leek"],
    "garlic": ["garlic powder", "hing (asafoetida)"],
    "ginger": ["ginger paste", "galangal"],
    "carrot": ["pumpkin", "sweet potato"],
    "cabbage": ["lettuce", "bok choy"],

    # --- Fruits ---
    "banana": ["applesauce", "pumpkin puree"],
    "apple": ["pear", "banana"],
    "lemon": ["vinegar", "lime"],
    "lime": ["lemon", "vinegar"],

    # --- Oils & Fats ---
    "oil": ["ghee", "butter"],
    "olive oil": ["any vegetable oil", "avocado oil"],
    "coconut oil": ["butter", "ghee"],

    # --- Sauces & Condiments ---
    "soy sauce": ["tamari", "fish sauce"],
    "vinegar": ["lemon", "lime"],
    "ketchup": ["tomato sauce", "tomato paste"],
    "mayonnaise": ["yogurt", "hung curd"],
    "mustard": ["dijon", "kasundi"],

    # --- Indian Ingredients ---
    "atta": ["maida", "oat flour"],
    "rava": ["oats", "cornmeal"],
    "curd": ["yogurt", "buttermilk"],
    "ghee": ["butter", "oil"],
    "besan": ["corn flour", "oat flour"],

    # --- Spices ---
    "cumin": ["jeera powder", "caraway seeds"],
    "chilli powder": ["paprika", "peri-peri"],
    "turmeric": ["saffron (small amount)", "dry mustard"],
    "coriander powder": ["cumin powder"],
}


#SUBSTITUTE MATCHING ENGINE
def substitution_match(leftovers, ingredient_text):
    """
    Count substitution matches.
    If a meal requires ingredient (A) but user has substitute (B), 
    count it as a partial match.
    """
    ingredient_text = ingredient_text.lower()
    leftovers = [i.lower() for i in leftovers]

    count = 0

    for key, substitutes in SUBSTITUTIONS.items():

        # If the meal contains this ingredient
        if key in ingredient_text:

            # Check if user has any substitute available
            for sub in substitutes:
                if sub.lower() in leftovers:
                    count += 1  # Partial match found

    return count


#TF-IDF CONTENT-BASED RECOMMENDATION
def meal_recommend_tfidf(leftover_list):
    meals = Meal.objects.all()
    if not meals:
        return []

    leftover_query = " ".join(leftover_list).lower()
    ingredient_texts = [meal.ingredients.lower() for meal in meals]
    corpus = ingredient_texts + [leftover_query]

    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(corpus)

    similarity_scores = cosine_similarity(
        tfidf_matrix[-1], tfidf_matrix[:-1]
    ).flatten()

    ranked_indexes = np.argsort(similarity_scores)[::-1]

    recommended = []
    for idx in ranked_indexes:
        if similarity_scores[idx] > 0:
            meal = meals[int(idx)]
            meal.similarity_score = float(similarity_scores[idx])
            recommended.append(meal)

    return recommended


#RULE-BASED BOOSTING (COOKING LOGIC)
def rule_based_ranking(meals, leftover_list):
    boosted = []

    for meal in meals:
        score = getattr(meal, "similarity_score", 0)

        ingredient_text = meal.ingredients.lower()
        match_count = sum(1 for x in leftover_list if x in ingredient_text)

        score += match_count * 0.2  # direct match reward

        if meal.cooking_time and meal.cooking_time <= 20:
            score += 0.1  # reward fast recipes

        meal.final_score = round(score, 3)
        boosted.append(meal)

    return sorted(boosted, key=lambda x: x.final_score, reverse=True)


#FINAL HYBRID RECOMMENDER (WITH SUBSTITUTION ENGINE)
def find_meals_from_leftovers(leftover_list):
    meals = Meal.objects.all()
    ranked = []

    leftovers = [x.lower() for x in leftover_list]

    for meal in meals:
        ingredients = meal.ingredients.lower()

        # DIRECT MATCHES + Record names for HTML
        direct_match_list = [item for item in leftovers if item in ingredients]
        direct_match = len(direct_match_list)

        # SUBSTITUTION MATCHES (count + detailed list)
        substitute_match, substitute_match_list = substitution_match(leftovers, ingredients)

        total_match = direct_match + substitute_match

        if total_match > 0:

            # Weighted score (direct > substitute)
            final_score = (direct_match * 1.0) + (substitute_match * 0.6)

            # Attach info to meal object (for HTML)
            meal.direct_match = direct_match
            meal.direct_match_list = direct_match_list

            meal.substitute_match = substitute_match
            meal.substitute_match_list = substitute_match_list

            meal.score = round(final_score, 2)

            ranked.append(meal)

    # Sort by hybrid score DESCENDING
    ranked.sort(key=lambda x: x.score, reverse=True)

    return ranked
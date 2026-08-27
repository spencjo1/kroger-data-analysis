import pandas as pd

from functions import (
    milk_converter,
    cheese_converter,
    eggs_converter,
    oz_converter,
)

# =========================================================
# LOAD DATA
# =========================================================

data = pd.read_excel('filtered file.xlsx')

# =========================================================
# FILTER DATA BY CATEGORY
# =========================================================

milk_data = data[data['category'] == 'milk']
cheese_data = data[data['category'] == 'cheese']
eggs_data = data[data['category'] == 'eggs']
cereal_data = data[data['category'] == 'cereal']
coffee_data = data[data['category'] == 'coffee']


# Keep only the columns needed for the analysis
milk_data = milk_data[['description', 'price', 'size']].copy()
cheese_data = cheese_data[['description', 'price', 'size']].copy()
eggs_data = eggs_data[['description', 'price', 'size']].copy()
cereal_data = cereal_data[['description', 'price', 'size']].copy()
coffee_data = coffee_data[['description', 'price', 'size']].copy()

# =========================================================
# CALCULATE PRICE PER SIZE
# =========================================================

milk_data['price/size'] = (milk_data['price'] / milk_converter(milk_data)['size'])
cheese_data['price/size'] = (cheese_data['price'] / cheese_converter(cheese_data)['size'])
eggs_data['price/size'] = (eggs_data['price'] / eggs_converter(eggs_data)['size'])
cereal_data['price/size'] = (cereal_data['price'] / oz_converter(cereal_data)['size'])
coffee_data['price/size'] = (coffee_data['price'] / oz_converter(coffee_data)['size'])

# =========================================================
# GROUP BY COMPARISON PAIRS
# =========================================================

milk_comparisons = [[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]
cheese_comparisons = [[0, 1], [2, 3], [4, 5], [6, 7, 8]]
eggs_comparisons = [[0, 1, 2], [3, 4], [5, 6, 7], [8, 9]]
cereal_comparisons = [[0, 1, 2], [3, 4], [5, 6], [7, 8]]
coffee_comparisons = [[0, 1], [2, 3, 4], [5, 6], [7, 8]]


# =========================================================
# ASSIGN CATEGORY TO CONVERTERS
# =========================================================

converters = {
    'milk': milk_converter,
    'cheese': cheese_converter,
    'eggs': eggs_converter,
    'cereal': oz_converter,
    'coffee': oz_converter
}

# =========================================================
# ASSIGN CATEGORY TO DATA AND COMPARISONS
# =========================================================

categories = {
    'milk': (milk_data, milk_comparisons),
    'cheese': (cheese_data, cheese_comparisons),
    'eggs': (eggs_data, eggs_comparisons),
    'cereal': (cereal_data, cereal_comparisons),
    'coffee': (coffee_data, coffee_comparisons)
}


# =========================================================
# Set comparisons for each category. So, we will compare a person buying the largest item in category once a week,
# against a person who buys the smaller category during the week.
# =========================================================


purchase_ratios = {

    'milk': {
        1: {'large': 1, 'small': 5},
        2: {'large': 1, 'small': 1},
        3: {'large': 1, 'small': 1},
        4: {'large': 1, 'small': 5},
        5: {'large': 1, 'small': 2}
    },

    'cheese': {
        1: {'large': 1, 'small': 3},
        2: {'large': 1, 'small': 3},
        3: {'large': 1, 'small': 4},
        4: {'large': 1, 'small': 3}
    },

    'eggs': {
           1: {'large': 1, 'small': 2},
           2: {'large': 1, 'small': 1},
           3: {'large': 1, 'small': 1},
           4: {'large': 1, 'small': 1}
       },


    'cereal': {
               1: {'large': 1, 'small': 2},
               2: {'large': 1, 'small': 1},
               3: {'large': 1, 'small': 1},
               4: {'large': 1, 'small': 1}
           },   

     'coffee': {
                   1: {'large': 1, 'small': 1},
                   2: {'large': 1, 'small': 1},
                   3: {'large': 1, 'small': 1},
                   4: {'large': 1, 'small': 1}
               },   
}



# Arbitrary comparison
standardized_units = 100

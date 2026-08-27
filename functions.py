import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
import glob
from plotly.subplots import make_subplots


#----------------------------------------------------conversions----------------------------------------------------------------

# For these functions, we need to standardize the text after the size. Examples are 'oz', 'fl oz', 'ct', etc,
# and they need to be handled appropriately. For each function we do a similar process; extract the number before
# the size qualifier and uses said number. For some operations, we multiply the two numbers together, like 'ct, oz' to standardize to oz.


def milk_converter(dataframe):
    # Standardize to ounces
    conversions = {
        'oz': 1,
        'gal': 128
    }

    dataframe = dataframe.copy()

    # Replace 1/2 with 0.5
    dataframe['size'] = dataframe['size'].str.replace( '1/2', '0.5', regex=False)

    # Use Regex to extract the number from the format "'x' ct/'y' oz"
    ct_oz = dataframe['size'].str.extract(r'([\d.]+)\s*ct\s*/\s*([\d.]+)\s*(?:fl\s*)?oz', expand=True)

    # Extract number and unit: [0] = number, [1] = unit
    normal = dataframe['size'].str.extract(r'([\d.]+)\s*(?:fl\s*)?(oz|gal)', expand=True)

    # Extract numbers from the units. [0] corresponds to the number attached to the first unit,
    # while [1] corresponds to the number attached to the second.
    dataframe['size'] = (pd.to_numeric(ct_oz[0], errors='coerce') *pd.to_numeric(ct_oz[1], errors='coerce'))

    # Calculate the normal sizes
    normal_size = (pd.to_numeric(normal[0], errors='coerce') *normal[1].str.lower().map(conversions))

    # Fill in the missing values
    dataframe['size'] = dataframe['size'].fillna(normal_size)

    return dataframe


def cheese_converter(dataframe):
    #Standardize to ounces
    conversions = {
        'oz': 1,
        'lb': 16
    }

    dataframe = dataframe.copy()

    dataframe['size'] = dataframe['size'].str.replace('1/2', '0.5', regex=False)

    # First: 6 slices / 18 oz
    # We only want the oz amount
    slices_oz = dataframe['size'].str.extract(r'([\d.]+)\s*slices?\s*/\s*([\d.]+)\s*oz',expand=True)

    # Normal: 12 oz, 2 lb, etc.
    normal = dataframe['size'].str.extract( r'([\d.]+)\s*(oz|lb)',expand=True)

    # For slices / oz, take the second number (the oz)
    dataframe['size'] = pd.to_numeric(slices_oz[1],errors='coerce')

    # For normal sizes, convert everything to ounces
    normal_size = (pd.to_numeric(normal[0], errors='coerce') *normal[1].str.lower().map(conversions) )

    dataframe['size'] = dataframe['size'].fillna(normal_size)

    return dataframe


def eggs_converter(dataframe):
    dataframe = dataframe.copy()

    dataframe['size'] = dataframe['size'].str.replace( '1/2', '0.5', regex=False)

    # First: 6 ct / 12 oz
    # We only want the ct amount
    ct_oz = dataframe['size'].str.extract( r'([\d.]+)\s*ct\s*/\s*([\d.]+)\s*oz', expand=True)

    # Second: 1 dozen, 2 dozen
    dozen = dataframe['size'].str.extract(r'([\d.]+)\s*dozen',expand=True)

    # Third: normal 12 ct, 18 ct, etc.
    normal = dataframe['size'].str.extract( r'([\d.]+)\s*ct',expand=True )

    # For ct / oz, use the ct number
    dataframe['size'] = pd.to_numeric( ct_oz[0], errors='coerce')

    # For dozen, convert to individual eggs
    dozen_size = (pd.to_numeric(dozen[0], errors='coerce') * 12)

    # For normal ct, keep the count as-is
    normal_size = pd.to_numeric(normal[0],errors='coerce')

    dataframe['size'] = dataframe['size'].fillna(dozen_size)
    dataframe['size'] = dataframe['size'].fillna(normal_size)

    return dataframe


def oz_converter(dataframe):
    dataframe = dataframe.copy()

    # Extract the number from oz. Since its our only qualifier we need to just extract it to use it later.
    dataframe['size'] = dataframe['size'].str.extract(r'([\d.]+)\s*oz',expand=False)

    dataframe['size'] = pd.to_numeric(dataframe['size'],errors='coerce')

    return dataframe


#---------------------------------------------- analysis for comparing products ----------------------------------------------


def analyze_category(dataframe, comparisons, converter):

    results = []

    for comparison_number, indexes in enumerate(comparisons, start=1):

        # Get the products in this comparison
        group = dataframe.iloc[indexes]

        # Find the product with the cheapest sticker price
        cheapest_index = group['price'].idxmin()

        # Find the product with the lowest price/size
        best_value_index = group['price/size'].idxmin()

        # Find the largest package
        largest_index = converter(group)['size'].idxmax()

        # -----------------------------------------------------
        # VALUE MISMATCH
        # -----------------------------------------------------
        # True when the product with the cheapest sticker
        # price is NOT the product with the best price/size.

        value_mismatch = (cheapest_index != best_value_index)

        # -----------------------------------------------------
        # LARGER PACKAGE HAS BETTER VALUE
        # -----------------------------------------------------
        # True when the largest package also has the
        # lowest price/size.

        larger_package_has_better_value = (largest_index == best_value_index)

        # -----------------------------------------------------
        # CREATE PRODUCT INFORMATION
        # -----------------------------------------------------

        products = []

        # For every row in group, grab the products attributes
        # and save to a list

        for _, product in group.iterrows():


            products.append({
                'description': product['description'],
                'size': product['size'],
                'price': product['price'],
                'price/size': product['price/size']
            })

        # -----------------------------------------------------
        # SAVE RESULTS
        # -----------------------------------------------------

        results.append({

            'comparison': comparison_number,

            'cheapest_product': (
                group.loc[cheapest_index, 'description']
            ),

            'cheapest_size': (
                group.loc[cheapest_index, 'size']
            ),

            'cheapest_price': (
                group.loc[cheapest_index, 'price']
            ),

            'cheapest_price/size': (
                group.loc[cheapest_index, 'price/size']
            ),

            'best_value_product': (
                group.loc[best_value_index, 'description']
            ),

            'best_value_size': (
                group.loc[best_value_index, 'size']
            ),

            'best_value_price': (
                group.loc[best_value_index, 'price']
            ),

            'best_price/size': (
                group.loc[best_value_index, 'price/size']
            ),

            'value_mismatch': value_mismatch,

            'larger_package_has_better_value':
                larger_package_has_better_value,

            'products': products
        })

    return pd.DataFrame(results)


def analyze_package_size(dataframe, comparisons, converter):

    results = []

    for comparison_number, indexes in enumerate(comparisons,start=1):

        group = dataframe.iloc[indexes].copy()

        # Convert package sizes to a common unit
        group['converted_size'] = converter(group)['size']

        # Sort by normalized numeric size
        sorted_group = group.sort_values('converted_size')

        # Since they are sorted from smallest to largest, we get the first (smallest) using index 0
        # and the last (largest) using index -1 (counting backwards)

        # Smallest
        smallest = sorted_group.iloc[0]

        # Largest
        largest = sorted_group.iloc[-1]

        # Medium
        if len(sorted_group) >= 3:
            medium = sorted_group.iloc[len(sorted_group) // 2]
        else:
            medium = None

        # Best value
        best_value_index = group['price/size'].idxmin()
        best_value = group.loc[best_value_index]

        # Determine which size is the best value and displays it,
        # can either be small, large, or medium
        
        if best_value_index == smallest.name:
            best_value_package = (f"smaller, {best_value['description']}")

        elif best_value_index == largest.name:
            best_value_package = (f"larger, {best_value['description']}")

        elif (medium is not None and best_value_index == medium.name):
            best_value_package = (f"middle, {best_value['description']}")

        else:
            best_value_package = (f"middle, {best_value['description']}")

        result = {
            'comparison': comparison_number,

            'smallest_product':
                smallest['description'],

            'smallest_size':
                smallest['size'],
        }

        # Only include a medium product when there are at least 3 producs.
        # Produces 'nan' if medium does not exist in the group.
        result = {
    'comparison': comparison_number,

    'smallest_product':
        smallest['description'],

    'smallest_size':
        smallest['size'],

    'medium_product':
        medium['description'] if medium is not None else None,

    'medium_size':
        medium['size'] if medium is not None else None,

    'largest_product':
        largest['description'],

    'largest_size':
        largest['size'],

    'best_value_product':
        best_value['description'],

    'best_value_size':
        best_value['size'],

    'best_value_package':
        best_value_package
}

        results.append(result)

    return pd.DataFrame(results)

# Calculates how much more expensive the cheapest sticker price product is, price/size wise, compared to the best value prodect.

def analyze_value_difference(dataframe, comparisons):

    results = []

    for comparison_number, indexes in enumerate(comparisons, start=1):

        group = dataframe.iloc[indexes]

        cheapest_index = group['price'].idxmin()
        best_value_index = group['price/size'].idxmin()

        cheapest_unit_price = group.loc[
            cheapest_index, 'price/size'
        ]

        best_unit_price = group.loc[
            best_value_index, 'price/size'
        ]

        percent_difference = ((cheapest_unit_price - best_unit_price)/ best_unit_price) * 100

        results.append({
            'comparison': comparison_number,

            'cheapest_product': group.loc[
                cheapest_index, 'description'
            ],

            'cheapest_price': group.loc[
                cheapest_index, 'price'
            ],

            'cheapest_price/size': cheapest_unit_price,

            'best_value_product': group.loc[
                best_value_index, 'description'
            ],

            'best_value_price': group.loc[
                best_value_index, 'price'
            ],

            'best_price/size': best_unit_price,

            'percent_difference': percent_difference
        })

    return pd.DataFrame(results)


def run_analysis(analysis_function, categories, converters=None, category=None, filename=None):

    if category is not None:

        if category not in categories:
            raise ValueError(
                f"Category '{category}' not found."
            )

        selected_categories = {
            category: categories[category]
        }

    else:

        selected_categories = categories

    results = {}

    for category_name, (dataframe, comparisons) in selected_categories.items():

        # Package-size analysis needs the 3 arguments, so handle its special case.
        # Otherwise, pass the 2 arguments as usual.
        if analysis_function == analyze_package_size or analysis_function == analyze_category:

            if converters is None:
                raise ValueError(
                    "Converters are required for "
                    "package size analysis."
                )

            converter = converters[category_name]

            results[category_name] = analysis_function(
                dataframe,
                comparisons,
                converter
            )

        else:

            results[category_name] = analysis_function(
                dataframe,
                comparisons
            )

    if filename is not None:

        write_results(
            results,
            filename,
            analysis_function.__name__
        )

    return results


def count_larger_package_value(results):

    larger_package_value_results = pd.DataFrame({
        'category': results.keys(),
        'larger_package_has_better_value': [
            result['larger_package_has_better_value'].sum()
            for result in results.values()
        ]
    })

    return larger_package_value_results


def write_results(results, filename, analysis_name=None):

    with open(filename, 'w', encoding='utf-8') as file:

        # -----------------------------------------------------
        # TITLE
        # -----------------------------------------------------

        file.write('=' * 70 + '\n')

        if analysis_name:
            file.write(
                f'ANALYSIS: {analysis_name}\n'
            )

        file.write('=' * 70 + '\n\n')

        # -----------------------------------------------------
        # EACH CATEGORY
        # -----------------------------------------------------

        for category, dataframe in results.items():

            file.write(
                f'CATEGORY: {category}\n'
            )

            file.write('-' * 70 + '\n\n')

            # -------------------------------------------------
            # EACH COMPARISON
            # -------------------------------------------------

            for _, row in dataframe.iterrows():

                file.write(
                    f"COMPARISON {row['comparison']}\n"
                )

                file.write('-' * 50 + '\n')

                # -------------------------------------------------
                # WRITE ANALYSIS RESULTS
                # -------------------------------------------------

                for column in dataframe.columns:

                    # Products are handled separately
                    if column == 'products':
                        continue

                    value = row[column]

                    # Format prices
                    if (
                        'price' in column.lower()
                        and isinstance(
                            value,
                            (int, float, np.number)
                        )
                    ):
                        value = f'${value:.4f}'

                    # Format percentages
                    elif (
                        'percent' in column.lower()
                        and isinstance(
                            value,
                            (int, float, np.number)
                        )
                    ):
                        value = f'{value:.2f}%'

                    file.write(
                        f'{column}: {value}\n'
                    )

                # -------------------------------------------------
                # PRODUCTS FROM analyze_category()
                # -------------------------------------------------

                if 'products' in dataframe.columns:

                    file.write(
                        '\nProducts compared:\n'
                    )

                    for product in row['products']:

                        file.write(
                            f"\n    {product['description']}\n"
                        )

                        file.write(
                            f"        Sticker price: "
                            f"${product['price']:.2f}\n"
                        )

                        file.write(
                            f"        Size: "
                            f"{product['size']}\n"
                        )

                        file.write(
                            f"        Price/size: "
                            f"${product['price/size']:.4f}\n"
                        )

                file.write('\n')
                file.write('-' * 50 + '\n\n')


def test_analysis(analysis_function, categories, category=None):

    # Delete old test files
    old_test_files = glob.glob('TEST_*.txt')

    for filename in old_test_files:
        os.remove(filename)

    if category is not None:

        if category not in categories:
            raise ValueError(
                f"Category '{category}' not found."
            )

        selected_categories = {
            category: categories[category]
        }

    else:

        selected_categories = categories

    for category_name, (dataframe, comparisons) in selected_categories.items():

        results = analysis_function(
            dataframe,
            comparisons
        )

        filename = (
            f'TEST_{analysis_function.__name__}'
            f'_{category_name}.txt'
        )

        write_results(
            {category_name: results},
            filename,
            analysis_function.__name__
        )


def person_a_vs_person_b(
    dataframe,
    comparisons,
    converter,
    category,
    purchase_ratios,
    standardized_units
):

    results = []

    weeks_per_year = 52

    for comparison_number, indexes in enumerate(
        comparisons,
        start=1
    ):

        group = dataframe.iloc[indexes].copy()

        # -------------------------------------------------
        # CONVERT PACKAGE SIZES
        # -------------------------------------------------

        group['converted_size'] = (
            converter(group)['size']
        )

        # -------------------------------------------------
        # CALCULATE PRICE PER UNIT
        # -------------------------------------------------

        group['price/size'] = (
            group['price'] /
            group['converted_size']
        )

        # -------------------------------------------------
        # FIND LARGEST AND SMALLEST PRODUCTS
        # -------------------------------------------------

        largest_index = (
            group['converted_size'].idxmax()
        )

        smallest_index = (
            group['converted_size'].idxmin()
        )

        largest = group.loc[largest_index]
        smallest = group.loc[smallest_index]

        # -------------------------------------------------
        # PURCHASE RATIO
        # -------------------------------------------------

        ratio = purchase_ratios[category][
            comparison_number
        ]

        large_purchases = ratio['large']
        small_purchases = ratio['small']

        # -------------------------------------------------
        # WEEKLY COST
        # -------------------------------------------------

        # Person A buys the largest product.
        person_a_weekly_cost = (
            largest['price'] *
            large_purchases
        )

        # Person B buys the smallest product
        # according to the comparison ratio.
        person_b_weekly_cost = (
            smallest['price'] *
            small_purchases
        )

        # -------------------------------------------------
        # YEARLY COST
        # -------------------------------------------------

        person_a_yearly_cost = (
            person_a_weekly_cost *
            weeks_per_year
        )

        person_b_yearly_cost = (
            person_b_weekly_cost *
            weeks_per_year
        )

        # -------------------------------------------------
        # AVERAGE PRICE PER UNIT
        # -------------------------------------------------

        person_a_price_per_unit = (
            largest['price/size']
        )

        person_b_price_per_unit = (
            smallest['price/size']
        )

        # -------------------------------------------------
        # STANDARDIZED 100-UNIT COST
        # -------------------------------------------------

        person_a_cost_per_100_units = (
            person_a_price_per_unit *
            standardized_units
        )

        person_b_cost_per_100_units = (
            person_b_price_per_unit *
            standardized_units
        )

        # -------------------------------------------------
        # B ADDITIONAL COST PER 100 UNITS
        # -------------------------------------------------

        b_additional_cost_per_100_units = (
            person_b_cost_per_100_units
            -
            person_a_cost_per_100_units
        )

        # -------------------------------------------------
        # YEARLY DIFFERENCE
        # -------------------------------------------------

        yearly_difference = (
            person_b_yearly_cost
            -
            person_a_yearly_cost
        )

        # -------------------------------------------------
        # B VS A YEARLY COST DIFFERENCE
        # -------------------------------------------------

        if person_a_yearly_cost > 0:

            percent_difference = (
                yearly_difference /
                person_a_yearly_cost
            ) * 100

        else:

            percent_difference = 0

        # -------------------------------------------------
        # SAVE RESULTS
        # -------------------------------------------------

        results.append({

            'comparison':
                comparison_number,

            'person_a_yearly_cost':
                person_a_yearly_cost,

            'person_b_yearly_cost':
                person_b_yearly_cost,

            'person_a_price_per_unit':
                person_a_price_per_unit,

            'person_b_price_per_unit':
                person_b_price_per_unit,

            'person_a_cost_per_100_units':
                person_a_cost_per_100_units,

            'person_b_cost_per_100_units':
                person_b_cost_per_100_units,

            'b_additional_cost_per_100_units':
                b_additional_cost_per_100_units,

            'yearly_difference':
                yearly_difference,

            'percent_difference':
                percent_difference
        })

    return pd.DataFrame(results)





#-------------------------------------------------------------- plotting ----------------------------------------------------------------

# Plots categories and compares them side-by-side, graphing subplots for each pair
# of either price or price/size

def plot_pair(categories, converters, category=None):

    # ---------------------------------------------------------
    # SELECT CATEGORIES
    # ---------------------------------------------------------

    if category is not None:

        if category not in categories:
            raise ValueError(
                f"Category '{category}' not found in categories."
            )

        selected_categories = {
            category: categories[category]
        }

    else:

        selected_categories = categories

    # ---------------------------------------------------------
    # COLORS
    # ---------------------------------------------------------

    colors = [
        'steelblue',
        'orange',
        'green',
        'red',
        'purple',
        'brown',
        'pink',
        'gray'
    ]

    # ---------------------------------------------------------
    # CREATE ONE WINDOW PER CATEGORY
    # ---------------------------------------------------------

    for category_name, (dataframe, comparisons) in selected_categories.items():

        converter = converters[category_name]

        rows = len(comparisons)

        # -----------------------------------------------------
        # SUBPLOTS
        # -----------------------------------------------------

        fig = make_subplots(
            rows=rows,
            cols=2,

            subplot_titles=[
                title
                for comparison_number in range(1, rows + 1)
                for title in [
                    f'Comparison {comparison_number} - Sticker Price',
                    f'Comparison {comparison_number} - Price per oz'
                ]
            ],

            # Keep the horizontal gap from before
            horizontal_spacing=0.06,

            # Small gap between comparison rows
            vertical_spacing=0.04
        )

        # -----------------------------------------------------
        # EACH COMPARISON
        # -----------------------------------------------------

        for comparison_number, indexes in enumerate(
            comparisons,
            start=1
        ):

            # Get all products in this comparison
            pair = dataframe.iloc[indexes].copy()

            # Convert package sizes
            pair['converted_size'] = converter(pair)['size']

            # Calculate price per size
            pair['price/size'] = (
                pair['price'] /
                pair['converted_size']
            )

            # -------------------------------------------------
            # PRODUCT NUMBERS
            # -------------------------------------------------

            product_numbers = [
                f'Product {i + 1}'
                for i in range(len(pair))
            ]

            # -------------------------------------------------
            # HOVER DATA
            # -------------------------------------------------

            customdata = pair[
                [
                    'description',
                    'size',
                    'converted_size',
                    'price',
                    'price/size'
                ]
            ].values

            # -------------------------------------------------
            # COLORS
            # -------------------------------------------------

            bar_colors = [
                colors[i % len(colors)]
                for i in range(len(pair))
            ]

            # -------------------------------------------------
            # STICKER PRICE GRAPH
            # -------------------------------------------------

            fig.add_trace(

                go.Bar(
                    x=product_numbers,
                    y=pair['price'],

                    marker_color=bar_colors,

                    customdata=customdata,

                    hovertemplate=
                        '<b>%{customdata[0]}</b><br><br>'

                        '<b>Sticker Price:</b> '
                        '$%{customdata[3]:.2f}<br>'

                        '<b>Package Size:</b> '
                        '%{customdata[1]}<br>'

                        '<b>Converted Size:</b> '
                        '%{customdata[2]:.2f} oz<br>'

                        '<b>Price per oz:</b> '
                        '$%{customdata[4]:.4f}'

                        '<extra></extra>'
                ),

                row=comparison_number,
                col=1
            )

            # -------------------------------------------------
            # PRICE PER OZ GRAPH
            # -------------------------------------------------

            fig.add_trace(

                go.Bar(
                    x=product_numbers,
                    y=pair['price/size'],

                    marker_color=bar_colors,

                    customdata=customdata,

                    hovertemplate=
                        '<b>%{customdata[0]}</b><br><br>'

                        '<b>Sticker Price:</b> '
                        '$%{customdata[3]:.2f}<br>'

                        '<b>Package Size:</b> '
                        '%{customdata[1]}<br>'

                        '<b>Converted Size:</b> '
                        '%{customdata[2]:.2f} oz<br>'

                        '<b>Price per oz:</b> '
                        '$%{customdata[4]:.4f}'

                        '<extra></extra>'
                ),

                row=comparison_number,
                col=2
            )

        # -----------------------------------------------------
        # AXIS LABELS
        # -----------------------------------------------------

        for row in range(1, rows + 1):

            # Left graph
            fig.update_xaxes(
                title_text='Product',
                row=row,
                col=1
            )

            fig.update_yaxes(
                title_text='Sticker Price ($)',
                row=row,
                col=1
            )

            # Right graph
            fig.update_xaxes(
                title_text='Product',
                row=row,
                col=2
            )

            fig.update_yaxes(
                title_text='Price per oz ($)',
                row=row,
                col=2
            )

        # -----------------------------------------------------
        # FIGURE SIZE
        # -----------------------------------------------------

        fig.update_layout(

            title=f'{category_name.title()} Product Comparisons',

            # Keep the graphs tall.
            #
            # Increasing this number makes each comparison
            # vertically taller.
            height=900 * rows,

            # Keep the two graphs wide enough to fill
            # the screen evenly.
            width=1800,

            showlegend=False,

            hovermode='closest',

            margin=dict(
                l=50,
                r=50,
                t=80,
                b=50
            )
        )

        fig.show()

# Plots comparisons where the larger package value is best

def plot_larger_package_value(results):

    dataframe = results.copy()

    fig = px.bar(
        dataframe,
        x='category',
        y='larger_package_has_better_value',
        color='category'
    )

    fig.update_traces(
        hovertemplate=
            '<b>%{x}</b><br>'
            'Larger package has better value: %{y}<br>'
            '<extra></extra>'
    )

    fig.update_layout(
        title='Comparisons Where the Larger Package Has Better Value',
        xaxis_title='Category',
        yaxis_title='Number of Comparisons',
        showlegend=False
    )

    fig.show()

# Plots the percentage difference between the cheapest product and the best value product.

def plot_value_difference(results, category=None):

    colors = {
        'milk': 'steelblue',
        'cheese': 'orange',
        'eggs': 'green',
        'cereal': 'red',
        'coffee': 'purple'
    }

    # ---------------------------------------------------------
    # ONE CATEGORY
    # ---------------------------------------------------------

    if category is not None:

        dataframe = results[category].copy()

        fig = px.bar(
            dataframe,
            x='comparison',
            y='percent_difference',
            color_discrete_sequence=[colors[category]]
        )

        # Custom hover information
        fig.update_traces(
            customdata=dataframe[
                [
                    'cheapest_product',
                    'cheapest_price',
                    'cheapest_price/size',
                    'best_value_product',
                    'best_value_price',
                    'best_price/size'
                ]
            ].values,

            hovertemplate=
                '<b>Comparison %{x}</b><br><br>'

                '<b>Cheapest Sticker Price</b><br>'
                '%{customdata[0]}<br>'
                'Price: $%{customdata[1]:.2f}<br>'
                'Price/size: $%{customdata[2]:.4f}<br><br>'

                '<b>Best Value</b><br>'
                '%{customdata[3]}<br>'
                'Price: $%{customdata[4]:.2f}<br>'
                'Price/size: $%{customdata[5]:.4f}<br><br>'

                '<b>Difference: %{y:.1f}%</b>'

                '<extra></extra>'
        )

        fig.update_layout(
            title=(
                f'{category.title()}: '
                'Percentage Difference Between Cheapest and Best Value'
            ),
            xaxis_title='Product Comparison',
            yaxis_title='Percentage Difference (%)',
            hovermode='closest'
        )

        fig.show()

    # ---------------------------------------------------------
    # ALL CATEGORIES
    # ---------------------------------------------------------

    else:

        for category, dataframe in results.items():

            dataframe = dataframe.copy()

            fig = px.bar(
                dataframe,
                x='comparison',
                y='percent_difference',
                color_discrete_sequence=[colors[category]]
            )

            fig.update_traces(
                customdata=dataframe[
                    [
                        'cheapest_product',
                        'cheapest_price',
                        'cheapest_price/size',
                        'best_value_product',
                        'best_value_price',
                        'best_price/size'
                    ]
                ].values,

                hovertemplate=
                    '<b>%s - Comparison %%{x}</b><br><br>'

                    '<b>Cheapest Sticker Price</b><br>'
                    '%%{customdata[0]}<br>'
                    'Price: $%%{customdata[1]:.2f}<br>'
                    'Price/size: $%%{customdata[2]:.4f}<br><br>'

                    '<b>Best Value</b><br>'
                    '%%{customdata[3]}<br>'
                    'Price: $%%{customdata[4]:.2f}<br>'
                    'Price/size: $%%{customdata[5]:.4f}<br><br>'

                    '<b>Difference: %%{y:.1f}%%</b>'

                    '<extra></extra>'
                    % category.title()
            )

            fig.update_layout(
                title=(
                    f'{category.title()}: '
                    'Percentage Difference Between Cheapest and Best Value'
                ),
                xaxis_title='Product Comparison',
                yaxis_title='Percentage Difference (%)',
                hovermode='closest'
            )

            fig.show()


#-------------------------------------------------------------- summary -----------------------------------------------------------------

# Uses the above functions to answer interesting research questions.

def create_research_summary(categories, converters):

    # =====================================================
    # RUN THE EXISTING ANALYSES
    # =====================================================

    comparison_results = run_analysis(
        analyze_category,
        categories,
        converters
    )

    value_results = run_analysis(
        analyze_value_difference,
        categories
    )

    summary_rows = []

    # =====================================================
    # CREATE ONE ROW PER CATEGORY
    # =====================================================

    for category in categories:

        comparison = comparison_results[category]
        value = value_results[category]

        total = len(comparison)

        # =================================================
        # 1. CHEAPEST STICKER PRICE VS BEST VALUE
        # =================================================

        mismatch_count = comparison[
            'value_mismatch'
        ].sum()

        mismatch_fraction = (
            f'{mismatch_count}/{total}'
        )

        # Only comparisons where cheapest sticker
        # price was NOT the best value.
        mismatches = value[
            comparison['value_mismatch'].values
        ]

        if len(mismatches) > 0:

            extra_per_unit = (
                mismatches['cheapest_price/size']
                -
                mismatches['best_price/size']
            )

            average_extra_per_unit = (
                extra_per_unit.mean()
            )

            average_percent_difference = (
                mismatches['percent_difference'].mean()
            )

        else:

            average_extra_per_unit = 0
            average_percent_difference = 0

        # =================================================
        # 2. LARGEST PACKAGE VS BEST VALUE
        # =================================================

        largest_best_count = comparison[
            'larger_package_has_better_value'
        ].sum()

        largest_best_fraction = (
            f'{largest_best_count}/{total}'
        )

        # =================================================
        # CREATE SUMMARY ROW
        # =================================================

        summary_rows.append({

            'Category':
                category.title(),

            # Q1
            'Cheapest ≠ Best Value':
                mismatch_fraction,

            # Q1
            'Avg % More Expensive':
                round(
                    average_percent_difference,
                    2
                ),

            # Q1
            'Avg Extra Cost per Unit':
                round(
                    average_extra_per_unit,
                    4
                ),

            # Q2
            'Largest Package = Best Value':
                largest_best_fraction
        })

    # =====================================================
    # CREATE DATAFRAME
    # =====================================================

    summary = pd.DataFrame(summary_rows)

    return summary


def create_person_a_vs_person_b_summary(
    categories,
    converters,
    purchase_ratios,
    standardized_units
):

    summary_rows = []

    # =====================================================
    # CREATE ONE ROW PER CATEGORY
    # =====================================================

    for category in categories:

        dataframe = categories[category][0]
        comparisons = categories[category][1]
        converter = converters[category]

        yearly_results = person_a_vs_person_b(
            dataframe,
            comparisons,
            converter,
            category,
            purchase_ratios,
            standardized_units
        )

        # =================================================
        # YEARLY COST
        # =================================================

        person_a_yearly_cost = (
            yearly_results[
                'person_a_yearly_cost'
            ].sum()
        )

        person_b_yearly_cost = (
            yearly_results[
                'person_b_yearly_cost'
            ].sum()
        )

        # =================================================
        # B VS A YEARLY COST DIFFERENCE
        # =================================================

        yearly_difference = (
            person_b_yearly_cost
            -
            person_a_yearly_cost
        )

        if person_a_yearly_cost > 0:

            percent_difference = (
                yearly_difference /
                person_a_yearly_cost
            ) * 100

        else:

            percent_difference = 0

        # =================================================
        # AVERAGE PRICE PER UNIT
        # =================================================

        person_a_price_per_unit = (
            yearly_results[
                'person_a_price_per_unit'
            ].mean()
        )

        person_b_price_per_unit = (
            yearly_results[
                'person_b_price_per_unit'
            ].mean()
        )

        # =================================================
        # STANDARDIZED 100-UNIT COST
        # =================================================

        person_a_cost_per_100_units = (
            person_a_price_per_unit *
            standardized_units
        )

        person_b_cost_per_100_units = (
            person_b_price_per_unit *
            standardized_units
        )

        # =================================================
        # B ADDITIONAL COST PER 100 UNITS
        # =================================================

        b_additional_cost_per_100_units = (
            person_b_cost_per_100_units
            -
            person_a_cost_per_100_units
        )

        # =================================================
        # SAVE CATEGORY
        # =================================================

        summary_rows.append({

            'Category':
                category.title(),

            'Person A Yearly Cost':
                round(
                    person_a_yearly_cost,
                    2
                ),

            'Person B Yearly Cost':
                round(
                    person_b_yearly_cost,
                    2
                ),

            'B vs A Yearly Cost Difference (%)':
                round(
                    percent_difference,
                    2
                ),

            'Person A Price/Size (Avg)':
                round(
                    person_a_price_per_unit,
                    4
                ),

            'Person B Price/Size (Avg)':
                round(
                    person_b_price_per_unit,
                    4
                ),

            'Person A Cost per 100 Units':
                round(
                    person_a_cost_per_100_units,
                    2
                ),

            'Person B Cost per 100 Units':
                round(
                    person_b_cost_per_100_units,
                    2
                ),

            'B Additional Cost per 100 Units':
                round(
                    b_additional_cost_per_100_units,
                    2
                )
        })

    # =====================================================
    # CREATE DATAFRAME
    # =====================================================

    summary = pd.DataFrame(summary_rows)

    return summary



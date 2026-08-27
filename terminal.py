# terminal.py

from data import (
    categories,
    converters,
    purchase_ratios,
    standardized_units
)

from functions import (
    analyze_category,
    analyze_package_size,
    analyze_value_difference,
    create_research_summary,
    create_person_a_vs_person_b_summary,
    run_analysis,
    count_larger_package_value,
    plot_pair,
    plot_larger_package_value,
    plot_value_difference,
    create_research_summary
)


# =========================================================
# GENERAL INPUT
# =========================================================

def get_input(prompt):
    """
    Get user input.

    b or back = return to previous menu
    q or quit = exit the entire program
    """

    while True:

        answer = input(prompt).strip().lower()

        # Quit program
        if answer in ('q', 'quit'):

            print('\nGoodbye!')
            raise SystemExit

        # Go back
        if answer in ('b', 'back'):

            return 'back'

        # Normal input
        if answer:

            return answer

        print(
            'Please enter a choice, '
            'b to go back, or q to quit.'
        )


# =========================================================
# NUMBER SELECTION
# =========================================================

def get_number(prompt, minimum, maximum):
    """
    Ask the user to select a number.

    b = go back
    q = quit
    """

    while True:

        answer = get_input(prompt)

        # Go back
        if answer == 'back':

            return 'back'

        try:

            number = int(answer)

        except ValueError:

            print(
                f'Please select a number from '
                f'{minimum}-{maximum}, '
                f'b to go back, or q to quit.'
            )

            continue

        if minimum <= number <= maximum:

            return number

        print(
            f'Please select a number from '
            f'{minimum}-{maximum}, '
            f'b to go back, or q to quit.'
        )


# =========================================================
# CATEGORY SELECTION
# =========================================================

def select_category():
    """
    Ask the user to select one category.

    b = go back
    q = quit
    """

    category_names = list(categories.keys())

    print('\n' + '=' * 60)
    print('SELECT CATEGORY')
    print('=' * 60)

    for number, category in enumerate(
        category_names,
        start=1
    ):

        print(
            f'{number}. {category.title()}'
        )

    print('b. Back')
    print('q. Quit')

    choice = get_number(
        f'\nSelect a number (1-{len(category_names)}), '
        f'b to go back, or q to quit: ',
        1,
        len(category_names)
    )

    if choice == 'back':

        return 'back'

    return category_names[choice - 1]


# =========================================================
# ALL OR ONE CATEGORY
# =========================================================

def select_category_scope():
    """
    Ask whether the user wants all categories
    or one specific category.

    b = go back
    q = quit
    """

    print('\n' + '=' * 60)
    print('SELECT CATEGORIES')
    print('=' * 60)

    print('1. All categories')
    print('2. One category')
    print('b. Back')
    print('q. Quit')

    choice = get_number(
        '\nSelect a number (1-2), '
        'b to go back, or q to quit: ',
        1,
        2
    )

    # Go back
    if choice == 'back':

        return 'back'

    # All categories
    if choice == 1:

        return None

    # One category
    category = select_category()

    if category == 'back':

        return 'back'

    return category


# =========================================================
# VIEW FINAL RESEARCH TABLE
# =========================================================

# =========================================================
# VIEW FINAL RESEARCH TABLE
# =========================================================

def view_final_table():

    print('\n' + '=' * 123)
    print('RESEARCH QUESTIONS SUMMARY')
    print('=' * 123)

    # =====================================================
    # CREATE BOTH SUMMARIES
    # =====================================================

    summary = create_research_summary(
        categories,
        converters
    )

    person_summary = create_person_a_vs_person_b_summary(
        categories,
        converters,
        purchase_ratios,
        standardized_units
    )

    # =====================================================
    # FIRST TABLE
    # =====================================================

    headers = [
        'Category',
        'Cheapest ≠ Best Value',
        'Avg % More Expensive',
        'Avg Extra Cost per Unit',
        'Largest Package = Best Value'
    ]

    widths = [
        max(15, len(header))
        for header in headers
    ]
    

    separator = '+' + '+'.join(
        '-' * (width + 2)
        for width in widths
    ) + '+'

    header = '|'

    for header_text, width in zip(
        headers,
        widths
    ):

        header += (
            f' {header_text:<{width}} |'
        )

    rows = []

    for _, row in summary.iterrows():

        rows.append([

            row['Category'],

            row['Cheapest ≠ Best Value'],

            f"{row['Avg % More Expensive']:.2f}%",

            f"${row['Avg Extra Cost per Unit']:.4f}",

            row['Largest Package = Best Value']
        ])

    table_lines = []

    table_lines.append(separator)
    table_lines.append(header)
    table_lines.append(separator)

    for row in rows:

        line = '|'

        for value, width in zip(
            row,
            widths
        ):

            line += (
                f' {str(value):<{width}} |'
            )

        table_lines.append(line)

    table_lines.append(separator)

    first_table = '\n'.join(table_lines)

    print()
    print(first_table)

    # =====================================================
    # PERSON A VS PERSON B TABLE
    # =====================================================

    print('\n')
    print('=' * 251)
    print('PERSON A VS PERSON B — YEARLY SPENDING AND UNIT COST')
    print('=' * 251)

    person_headers = [
        'Category',
        'Person A Yearly Cost',
        'Person B Yearly Cost',
        'B vs A Yearly Cost Difference (%)',
        'Person A Price/Size (Avg)',
        'Person B Price/Size (Avg)',
        'Person A Cost per 100 Units',
        'Person B Cost per 100 Units',
        'B Additional Cost per 100 Units'
    ]

    person_widths = [
    max(15, len(header))
    for header in person_headers
]

    person_separator = (
        '+' +
        '+'.join(
            '-' * (width + 2)
            for width in person_widths
        ) +
        '+'
    )

    person_header = '|'

    for header_text, width in zip(
        person_headers,
        person_widths
    ):

        person_header += (
            f' {header_text:<{width}} |'
        )

    person_table_lines = []

    person_table_lines.append(
        person_separator
    )

    person_table_lines.append(
        person_header
    )

    person_table_lines.append(
        person_separator
    )

    # =====================================================
    # CATEGORY ROWS
    # =====================================================

    for _, row in person_summary.iterrows():

        person_row = [

            row['Category'],

            f"${row['Person A Yearly Cost']:.2f}",

            f"${row['Person B Yearly Cost']:.2f}",

            f"{row['B vs A Yearly Cost Difference (%)']:.2f}%",

            f"${row['Person A Price/Size (Avg)']:.4f}",

            f"${row['Person B Price/Size (Avg)']:.4f}",

            f"${row['Person A Cost per 100 Units']:.2f}",

            f"${row['Person B Cost per 100 Units']:.2f}",

            f"${row['B Additional Cost per 100 Units']:.2f}"
        ]

        line = '|'

        for value, width in zip(
            person_row,
            person_widths
        ):

            line += (
                f' {str(value):<{width}} |'
            )

        person_table_lines.append(line)

    # =====================================================
    # TOTALS
    # =====================================================

    total_person_a = (
        person_summary[
            'Person A Yearly Cost'
        ].sum()
    )

    total_person_b = (
        person_summary[
            'Person B Yearly Cost'
        ].sum()
    )

    # -----------------------------------------------------
    # TOTAL YEARLY PERCENT DIFFERENCE
    # -----------------------------------------------------

    total_difference = (
        total_person_b -
        total_person_a
    )

    if total_person_a > 0:

        total_percent_difference = (
            total_difference /
            total_person_a
        ) * 100

    else:

        total_percent_difference = 0

    # -----------------------------------------------------
    # TOTAL AVERAGE PRICE/SIZE
    # -----------------------------------------------------

    total_person_a_price_per_unit = (
        person_summary[
            'Person A Price/Size (Avg)'
        ].mean()
    )

    total_person_b_price_per_unit = (
        person_summary[
            'Person B Price/Size (Avg)'
        ].mean()
    )

    # -----------------------------------------------------
    # TOTAL COST PER 100 UNITS
    # -----------------------------------------------------

    total_person_a_cost_per_100_units = (
        total_person_a_price_per_unit *
        standardized_units
    )

    total_person_b_cost_per_100_units = (
        total_person_b_price_per_unit *
        standardized_units
    )

    # -----------------------------------------------------
    # TOTAL B ADDITIONAL COST PER 100 UNITS
    # -----------------------------------------------------

    total_b_additional_cost_per_100_units = (
        total_person_b_cost_per_100_units
        -
        total_person_a_cost_per_100_units
    )

    # -----------------------------------------------------
    # TOTAL ROW
    # -----------------------------------------------------

    total_row = [

        'TOTAL',

        f"${total_person_a:.2f}",

        f"${total_person_b:.2f}",

        f"{total_percent_difference:.2f}%",

        f"${total_person_a_price_per_unit:.4f}",

        f"${total_person_b_price_per_unit:.4f}",

        f"${total_person_a_cost_per_100_units:.2f}",

        f"${total_person_b_cost_per_100_units:.2f}",

        f"${total_b_additional_cost_per_100_units:.2f}"
    ]

    person_table_lines.append(
        person_separator
    )

    line = '|'

    for value, width in zip(
        total_row,
        person_widths
    ):

        line += (
            f' {str(value):<{width}} |'
        )

    person_table_lines.append(line)

    person_table_lines.append(
        person_separator
    )

    person_table = '\n'.join(
        person_table_lines
    )

    print()
    print(person_table)

    # =====================================================
    # SAVE BOTH TABLES
    # =====================================================

    with open(
        'research_question_summary.txt',
        'w',
        encoding='utf-8'
    ) as file:

        file.write(
            '=' * 123 + '\n'
        )

        file.write(
            'RESEARCH QUESTIONS SUMMARY\n'
        )

        file.write(
            '=' * 123 + '\n\n'
        )

        file.write(first_table)

        file.write('\n\n')

        file.write(
            '=' * 251 + '\n'
        )

        file.write(
            'PERSON A VS PERSON B — '
            'YEARLY SPENDING AND UNIT COST\n'
        )

        file.write(
            '=' * 251 + '\n\n'
        )

        file.write(person_table)

        file.write('\n')

        file.write(
            '=' * 251 + '\n'
        )

    print(
        '\nSummary saved to '
        'research_question_summary.txt'
    )




# =========================================================
# ANALYSIS MENU
# =========================================================

def analysis_menu():

    print('\n' + '=' * 60)
    print('SELECT ANALYSIS')
    print('=' * 60)

    print('1. Product comparison analysis')
    print('2. Package size analysis')
    print('3. Value difference analysis')
    print('b. Back')
    print('q. Quit')

    choice = get_number(
        '\nSelect a number (1-3), '
        'b to go back, or q to quit: ',
        1,
        3
    )

    # -----------------------------------------------------
    # BACK
    # -----------------------------------------------------

    if choice == 'back':

        return

    # -----------------------------------------------------
    # PRODUCT COMPARISON
    # -----------------------------------------------------

    if choice == 1:

        category = select_category_scope()

        if category == 'back':

            return

        # All categories
        if category is None:

            run_analysis(
                analyze_category,
                categories,
                filename='comparison_results.txt'
            )

        # One category
        else:

            selected_categories = {
                category: categories[category]
            }

            run_analysis(
                analyze_category,
                selected_categories,
                filename='comparison_results.txt'
            )

        print(
            '\nAnalysis complete.'
        )

        print(
            'Results saved to comparison_results.txt'
        )

    # -----------------------------------------------------
    # PACKAGE SIZE
    # -----------------------------------------------------

    elif choice == 2:

        category = select_category_scope()

        if category == 'back':

            return

        # All categories
        if category is None:

            run_analysis(
                analyze_package_size,
                categories,
                converters,
                filename='package_size_results.txt'
            )

        # One category
        else:

            selected_categories = {
                category: categories[category]
            }

            run_analysis(
                analyze_package_size,
                selected_categories,
                converters,
                filename='package_size_results.txt'
            )

        print(
            '\nAnalysis complete.'
        )

        print(
            'Results saved to package_size_results.txt'
        )

    # -----------------------------------------------------
    # VALUE DIFFERENCE
    # -----------------------------------------------------

    elif choice == 3:

        category = select_category_scope()

        if category == 'back':

            return

        # All categories
        if category is None:

            run_analysis(
                analyze_value_difference,
                categories,
                filename='value_difference_results.txt'
            )

        # One category
        else:

            selected_categories = {
                category: categories[category]
            }

            run_analysis(
                analyze_value_difference,
                selected_categories,
                filename='value_difference_results.txt'
            )

        print(
            '\nAnalysis complete.'
        )

        print(
            'Results saved to value_difference_results.txt'
        )


# =========================================================
# PLOTTING MENU
# =========================================================

def plotting_menu():

    print('\n' + '=' * 60)
    print('SELECT PLOT')
    print('=' * 60)

    print('1. Product comparison plots')
    print('2. Larger package value plot')
    print('3. Value difference plot')
    print('b. Back')
    print('q. Quit')

    choice = get_number(
        '\nSelect a number (1-3), '
        'b to go back, or q to quit: ',
        1,
        3
    )

    # -----------------------------------------------------
    # BACK
    # -----------------------------------------------------

    if choice == 'back':

        return

    # -----------------------------------------------------
    # PRODUCT COMPARISON PLOTS
    # -----------------------------------------------------

    if choice == 1:

        print('\n' + '=' * 60)
        print('SELECT CATEGORIES')
        print('=' * 60)

        print('1. All categories')
        print('2. One category')
        print('b. Back')
        print('q. Quit')

        scope = get_number(
            '\nSelect a number (1-2), '
            'b to go back, or q to quit: ',
            1,
            2
        )

        if scope == 'back':

            return

        # All categories
        if scope == 1:

            plot_pair(
                categories,
                converters
            )

        # One category
        else:

            category = select_category()

            if category == 'back':

                return

            plot_pair(
                categories,
                converters,
                category=category
            )

    # -----------------------------------------------------
    # LARGER PACKAGE VALUE
    # -----------------------------------------------------

    elif choice == 2:

        results = run_analysis(
            analyze_category,
            categories,
            converters
        )

        count_results = count_larger_package_value(
            results
        )

        plot_larger_package_value(
            count_results
        )

    # -----------------------------------------------------
    # VALUE DIFFERENCE
    # -----------------------------------------------------

    elif choice == 3:

        print('\n' + '=' * 60)
        print('SELECT CATEGORIES')
        print('=' * 60)

        print('1. All categories')
        print('2. One category')
        print('b. Back')
        print('q. Quit')

        scope = get_number(
            '\nSelect a number (1-2), '
            'b to go back, or q to quit: ',
            1,
            2
        )

        if scope == 'back':

            return

        # Run analysis once
        results = run_analysis(
            analyze_value_difference,
            categories
        )

        # All categories
        if scope == 1:

            plot_value_difference(
                results
            )

        # One category
        else:

            category = select_category()

            if category == 'back':

                return

            plot_value_difference(
                results,
                category=category
            )


# =========================================================
# MAIN MENU
# =========================================================

def main():

    print('\n' + '=' * 60)
    print('PRODUCT ANALYSIS PROGRAM')
    print('=' * 60)

    print(
        '\nType "b" to go back.'
    )

    print(
        'Type "q" to quit the program.'
    )

    while True:

        print('\n' + '=' * 60)
        print('MAIN MENU')
        print('=' * 60)

        print('1. Run an analysis')
        print('2. Create a plot')
        print('3. View final research table')
        print('q. Quit')

        choice = get_number(
            '\nSelect a number (1-3), '
            'or q to quit: ',
            1,
            3
        )

        # -------------------------------------------------
        # RUN ANALYSIS
        # -------------------------------------------------

        if choice == 1:

            analysis_menu()

        # -------------------------------------------------
        # CREATE PLOT
        # -------------------------------------------------

        elif choice == 2:

            plotting_menu()

        # -------------------------------------------------
        # VIEW FINAL RESEARCH TABLE
        # -------------------------------------------------

        elif choice == 3:

            view_final_table()


# =========================================================
# START PROGRAM
# =========================================================

if __name__ == '__main__':

    main()
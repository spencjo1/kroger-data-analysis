# Kroger Data Analysis

## Summary:
Does a larger package actually provide better value? This project is a small, user-friendly data analysis program
that explores this question. It analyzes product prices across five Kroger categories and compares sticker price
with price per unit. The project also examines how choosing smaller packages can affect total spending over time,
even when the smaller package has a lower sticker price. The primary goal is to investigate whether sticker price 
accurately reflects value and whether choosing the seemingly cheaper option can actually result in higher costs
over time.


## Workflow:
I obtained product data through the Kroger API and selected approximately 50 products across five categories for analysis. 
I specifically selected comparable products, including different package sizes of the same or similar products, to investigate 
the relationship between sticker price and price per unit. The raw product data returned by the Kroger API is stored in 
`products.csv`. I selected approximately 50 comparable products and stored the filtered dataset in `filtered file.xlsx`. 
I then used pandas to process the product data and organize the selected products into the dictionaries and structures used 
by the analysis.

The analysis is divided into 4 main components:

- **Size Conversion** -- Standardizes product sizes for comparison.
- **Data Analysis** -- Analyzes sticker prices and price-per-unit relationships.
- **Plotting** -- Generates visualizations of the comparisons.
- **Final Analysis** -- Answers the key questions outlined in `QUESTIONS_TO_ANSWER.txt`.


## Limitations:
I attempted to select the same products in different package sizes whenever possible in order to 
minimize variables other than package size and isolate its effect on price and value. Despite this, 
there are still a few comparisons where the products aren't the exact same.

The data also represents a snapshot rather than a live pricing timeline. The Kroger data used in this 
project was collected on July 2nd, 2026 from a store in Ohio. Prices can change over time, so these results represent
the prices available at the time the data was collected rather than current or historical average prices. Finally, 
the analysis is limited to approximately 50 products across five categories. A full Kroger category may contain 
thousands of products, so the results should not be interpreted as representative of Kroger's entire catalog.


## How to run:
To run this program, all you have to do is run `terminal.py` and follow the steps outlined.


## Results:
The analysis found that across all five categories, the cheapest product by sticker price was not necessarily 
the best value. In this project, "best value" is defined as the product with the lowest price per unit within
a comparison group. I found that the cheapest sticker price is almost never the lowest price per unit, and that
the larger product generally provided better value per unit.

I also created a hypothetical scenario involving two people with different spending habits, Person A and Person B.

Person A buys the largest product from a category once per week, while Person B buys the smallest product according
to the purchasing ratios outlined in `data.py`, following the rules within `exceptions.txt`. These ratios are designed to have Person B purchase approximately
the same amount of product as Person A while spending approximately the same amount or less per week. 

Under these assumptions, Person A spent more money over the course of a year, while Person B paid a higher average 
price per unit. This demonstrates that a lower yearly expenditure does not necessarily mean that a consumer is 
receiving better value for their money. To further illustrate this difference, I applied each person's average
price per unit to 100 units of an arbitrary product. Under this scenario, Person B paid an average of $6.00 more
per 100 units than Person A.

I have attached `research_question_summary.txt`, although it can also be produced by running `terminal.py` if you so choose.

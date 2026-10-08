# Resume content

**Title:** Smart Expense Tracker with Spending Prediction

**Description:** Full-stack Django web application for tracking expenses, managing monthly budgets and visualising spending. Includes a REST API and a scikit-learn Linear Regression model that estimates next month's spending.

**Bullets**
- Built a full-stack expense tracker with Django, MySQL, Bootstrap 5 and JavaScript, with secure registration and login and per-user data isolation.
- Designed a REST API with Django REST Framework covering expense CRUD, dashboard summary, monthly and category spending, and predictions.
- Implemented a Pandas and scikit-learn Linear Regression pipeline that predicts next-month spending from historical data and reports error when enough data exists.
- Created an interactive dashboard with Chart.js (doughnut, bar, line) plus budget alerts and rule-based spending insights.
- Wrote automated tests for authentication, expense CRUD, budgets, user isolation and prediction.

**Technologies:** Python, Django, Django REST Framework, MySQL, HTML, CSS, Bootstrap 5, JavaScript, Chart.js, Pandas, NumPy, scikit-learn.

## 60-second explanation
"I built a Smart Expense Tracker in Django with MySQL. Users register, log in, add expenses by category, set a monthly budget and get alerts as they approach it. A dashboard shows charts made with Chart.js, and there is a REST API. For prediction I aggregate expenses by month and train a Linear Regression model with scikit-learn to estimate next month's spending. It needs at least three months of data, and it is a simple trend estimate, not a guarantee. All data is filtered per user, and I wrote tests for the main features."

## 3-minute explanation
Start with the problem: people lose track of spending. Then walk through: (1) the stack and why, (2) the two models, Expense and Budget, and their relationships, (3) authentication and how every query filters by the logged-in user, (4) the services layer that keeps views small, (5) the ML pipeline step by step (monthly aggregation, cleaning, month index as the feature, train, predict, hold-out MAE when there are 6+ months), (6) the limitations of a straight-line model, (7) the API and charts, (8) testing, and (9) what you would improve next. Practise this in your own words, and only mention features you have run yourself.

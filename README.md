# XYZ IT Company– Monthly Billing & Sales Forecasting

## Project Overview

This project focuses on analyzing historical monthly billing data and forecasting future sales, network capacity, and active customer connections for **XYZ IT**, an Internet Service Provider (ISP).

The main objective is to help the marketing and business departments understand monthly business performance, identify customer connection trends, and estimate future business growth using historical billing information.

The system uses two different forecasting approaches:

1. **Exponential Smoothing (ETS):** A time-series forecasting technique that identifies historical trends and estimates future monthly sales and network capacity.
2. **Gradient Boosting Regressor:** A machine learning algorithm that learns from previous monthly values and uses historical patterns to predict future sales and capacity.

In addition to forecasting, the project analyzes customer connection movements, including new connections, terminations, upgrades, and downgrades.

Users can enter a specific month and year to retrieve actual historical results or future predictions directly through the terminal.

## Project Objectives

- Analyze historical monthly billing and sales data.
- Forecast future monthly sales in Bangladeshi Taka (BDT).
- Predict total network capacity requirements in Mbps.
- Estimate the number of active customer connections.
- Identify newly connected and terminated customer links.
- Analyze customer connection upgrades and downgrades.
- Calculate monthly changes in sales and network capacity.
- Compare forecasting results from ETS and Gradient Boosting.
- Provide useful business insights for marketing and planning activities.

## Technologies and Libraries Used

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| Pandas | Data processing and analysis |
| NumPy | Numerical calculations |
| Scikit-learn | Machine learning utilities |
| Gradient Boosting Regressor | Monthly sales and capacity forecasting |
| Statsmodels | Exponential Smoothing (ETS) |
| Calendar | Month and year handling |

## Dataset Information

**Dataset:** `billing_part.csv`

The dataset contains monthly billing records and customer connection information.

### Important Dataset Columns

| Column | Description |
|---|---|
| Month | Billing month |
| Link ID | Unique customer connection identifier |
| Quantity | Internet connection capacity in Mbps |
| MRC | Monthly Recurring Charge |
| Billing End Date | Billing period ending date |
| Billing Remarks | Additional billing information |

### Data Preprocessing

Before performing the analysis and forecasting, the dataset goes through several preprocessing steps:

- Remove unnecessary spaces from column names.
- Convert billing months into datetime format.
- Remove records with invalid months or missing Link IDs.
- Remove empty and invalid Link IDs.
- Convert Quantity and MRC into numerical values.
- Replace missing numerical values with zero.
- Convert Billing End Date into datetime format.
- Clean missing billing remarks.

These operations help maintain a consistent dataset for monthly billing analysis and forecasting.

## Project Methodology

### 1. Monthly Billing Summary

The system generates a monthly summary from the customer billing records.

Three main business parameters are calculated:

| Parameter | Description |
|---|---|
| Sales | Total monthly MRC |
| Capacity | Total active connection capacity in Mbps |
| Active Links | Number of active customer connections |

For each customer connection, the latest billing record is used to determine its monthly status, while MRC values are summed across that customer's monthly records.

This summary provides the historical monthly information required for forecasting.

### 2. Customer Link Movement Analysis

The system compares consecutive months to identify changes in customer connections.

Four major categories of customer movement are analyzed:

| Category | Description |
|---|---|
| New Links | Customer connections appearing for the first time compared with the previous month |
| Terminations | Customer connections disappearing compared with the previous month |
| Upgrades | Existing connections with increased network capacity |
| Downgrades | Existing connections with decreased network capacity |

**Special Handling:**

Connections marked with the billing remark `Shift to LH` are excluded from termination counts.

This analysis helps understand monthly customer growth, customer exits, and changes in existing connection packages.

### 3. Capacity and Sales Change Analysis

The system calculates both absolute and percentage changes in sales and network capacity.

**Absolute Change**

Current month's value minus previous month's value.

\[
\text{Absolute Change} =
\text{Current Month} - \text{Previous Month}
\]

**Percentage Change**

\[
\text{Change \%} =
\frac{\text{Absolute Change}}{\text{Previous Month Total}}
\times 100
\]

These calculations are performed separately for capacity and sales.

The results help identify how much business performance has increased or decreased compared with the previous month.

### 4. Forecasting Models

The project implements two forecasting models to estimate future monthly sales and network capacity.

#### Model 1: Exponential Smoothing (ETS)

Exponential Smoothing is a time-series forecasting technique that uses historical observations to estimate future values.

It gives more importance to recent observations while considering historical trends.

**Model Configuration:**

- Trend: Additive
- Damped Trend: Enabled
- Initialization Method: Estimated

ETS is applied separately to forecast:

- Monthly Sales (BDT).
- Total Network Capacity (Mbps).

#### Model 2: Gradient Boosting Regressor

Gradient Boosting is a machine learning algorithm that combines multiple decision trees to improve prediction performance.

The model learns from historical monthly values and identifies patterns that can be used to estimate future sales and network capacity.

**Input Features:**

- Month number.
- Previous month's value.
- Value from two months earlier.
- Value from three months earlier.

The model predicts future monthly sales and capacity using these historical features.

For multi-month forecasting, previous predictions are used as inputs for subsequent months. This approach is known as recursive forecasting.

### 5. Active Customer Link Forecasting

The number of future active customer connections is estimated using historical average monthly new connections and terminations.

The calculation is:

\[
\text{Future Active Links} =
\text{Current Active Links}
+
(\text{Average New Links} - \text{Average Terminations})
\times \text{Forecast Steps}
\]

This provides an estimated number of active customer connections for the requested month.

Unlike sales and capacity, active links are estimated using historical customer movement rather than the ETS and Gradient Boosting models.

## Sample Forecasting Results

**Forecast Month: August 2026**

The following table shows example predictions from the current model execution.

| Parameter | Exponential Smoothing (ETS) | Gradient Boosting |
|---|---:|---:|
| Sales (BDT) | 8,088,040 | 8,021,819 |
| Capacity (Mbps) | 341,236 | 331,128 |
| Active Links | 264 | 264 |

The results allow users to compare two different forecasting approaches and understand how their predictions differ.

### Customer Movement Analysis

The following historical average monthly changes were calculated:

| Category | Average Monthly Links |
|---|---:|
| New Users | 263 |
| Users Who May Exit | 263 |
| Upgrades | 0 |
| Downgrades | 0 |

These values provide an overview of historical customer connection movements.

### Capacity and Sales Changes

| Category | Capacity Change | Sales Change |
|---|---:|---:|
| New Links | +99.8% | +99.8% |
| Terminations | -99.6% | -99.6% |
| Upgrades | +0.1% | +0.1% |
| Downgrades | -0.2% | -0.2% |

*Note: These figures represent sample execution results and are not guaranteed future business outcomes.*

## Installation and Usage

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/Amber-IT-Billing-Forecasting.git
```

### 2. Navigate to the Project Directory

```bash
cd Amber-IT-Billing-Forecasting
```

### 3. Install Required Libraries

```bash
pip install pandas numpy scikit-learn statsmodels
```

### 4. Add the Dataset

Place the billing dataset inside the project directory:

```text
billing_part.csv
```

### 5. Run the Program

```bash
python billing_forecasting.py
```

### 6. Enter Forecast Information

The program will ask the user to enter a month and year.

**Example:**

```text
Enter month (Aug / August): aug
Enter year (2026 / 26): 26
```

The program supports:

- Short month names (Jan, Feb, Mar, Aug, etc.).
- Full month names (January, February, March, August, etc.).
- Two-digit years (26).
- Four-digit years (2026).

### Example Terminal Output

```text
Forecast for Aug 2026

ETS
Sales (BDT)        : 8,088,040
Capacity (Mbps)    : 341,236
Active links       : 264

Gradient boosting
Sales (BDT)        : 8,021,819
Capacity (Mbps)    : 331,128
Active links       : 264
```

For a month already available in the dataset, the program displays actual historical results instead of generating a forecast.

## Project Structure

```text
Amber-IT-Billing-Forecasting/
│
├── billing_forecasting.py
├── billing_part.csv
├── README.md
└── requirements.txt
```

## Business Applications

This forecasting system can support the marketing and business departments in several ways.

| Business Area | Application |
|---|---|
| Sales Planning | Estimate upcoming monthly revenue and identify possible sales trends. |
| Capacity Planning | Understand expected network capacity requirements. |
| Customer Analysis | Monitor new connections, terminations, and customer movements. |
| Marketing Strategy | Identify customer growth and retention trends. |
| Business Forecasting | Compare different forecasting approaches before making business decisions. |

By combining billing analysis with forecasting, the system can help businesses understand historical performance and prepare for upcoming operational requirements.

## Limitations

There are some limitations in the current implementation:

- Forecasting accuracy depends on the quality and length of historical billing data.
- Gradient Boosting uses the month index and three previous monthly values as input features.
- Multi-month predictions are recursive, meaning earlier predictions influence later predictions.
- Active link predictions use historical average customer movements.
- Unexpected changes in pricing, customer demand, or business operations are not directly modeled.
- The current implementation does not calculate forecasting accuracy against a separate test dataset.
- The models do not currently account for external business factors such as marketing campaigns, competitor pricing, or major changes in customer behavior.

## Future Improvements

Some possible improvements for this project include:

- Implementing additional models such as XGBoost and Random Forest.
- Comparing forecasting accuracy using MAE, RMSE, and MAPE.
- Introducing customer churn prediction.
- Including seasonal billing patterns and additional time-based features.
- Adding customer-level revenue analysis.
- Developing an interactive dashboard using Streamlit.
- Introducing automated monthly billing reports.
- Adding historical vs predicted sales comparison graphs.
- Incorporating external business factors to improve forecasting performance.

## AI Assistance & Acknowledgement

During the planning and development of this project, I used AI tools as a supporting resource for research, learning, and exploring different technical approaches.

AI assistance helped me with:

- Exploring and refining the initial project idea.
- Finding and identifying suitable CSV datasets for monthly billing and sales forecasting.
- Understanding the structure of billing data and identifying relevant features for analysis.
- Researching different machine learning and time-series forecasting approaches.
- Comparing models such as Linear Regression, Random Forest, Gradient Boosting, XGBoost, and Exponential Smoothing to understand which approaches were more suitable for this project.
- Understanding forecasting concepts, data preprocessing techniques, and model configurations.
- Exploring possible improvements to the forecasting workflow.

AI was used as a learning and research assistant, not as a replacement for understanding and implementing the project.
The implementation, data processing, model execution, experimentation, and analysis of the results were part of my own project development and learning process.

*This project demonstrates the practical application of Python, data analysis, machine learning, time-series forecasting, and business analytics to monthly billing and sales data in the ISP industry.*

# XYZ IT – Monthly Billing & Sales Forecasting

## Project Overview

This project is designed to analyze historical monthly billing data and forecast future sales, network capacity, and active customer connections for **Amber IT**, an internet service provider (ISP).

The system uses historical billing records to identify monthly business trends and predict future performance using two forecasting approaches:

1. **Exponential Smoothing (ETS):** A time-series forecasting method that captures trends in historical billing data.
2. **Gradient Boosting Regressor:** A machine learning model that learns from previous monthly values to predict future sales and capacity.

In addition to forecasting, the system analyzes customer connection changes, including new connections, terminations, upgrades, and downgrades.

Users can enter a month and year to retrieve actual historical results or future predictions directly in the terminal.

## Project Objectives

- Analyze historical monthly billing data.
- Forecast future monthly sales in Bangladeshi Taka (BDT).
- Predict total network capacity in Mbps.
- Estimate the number of active customer connections.
- Identify newly connected and terminated customer links.
- Analyze customer upgrades and downgrades.
- Measure monthly changes in sales and network capacity.
- Compare predictions from ETS and Gradient Boosting.

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| Pandas | Data processing and analysis |
| NumPy | Numerical calculations |
| Scikit-learn | Machine learning |
| Gradient Boosting | Sales and capacity forecasting |
| Statsmodels | Exponential Smoothing (ETS) |
| Calendar | Month and year handling |

## Dataset Information

**Dataset:** `billing_part.csv`

The dataset contains monthly billing records and customer connection information.

### Important Columns

| Column | Description |
|---|---|
| Month | Billing month |
| Link ID | Unique customer connection identifier |
| Quantity | Internet connection capacity (Mbps) |
| MRC | Monthly recurring charge |
| Billing End Date | Billing period ending date |
| Billing Remarks | Additional billing information |

### Data Preprocessing

The following preprocessing operations are performed:

- Remove unnecessary spaces from column names.
- Convert billing months into datetime format.
- Remove records with invalid months or missing Link IDs.
- Remove empty and invalid Link IDs.
- Convert Quantity and MRC into numerical values.
- Replace missing numerical values with zero.
- Convert Billing End Date into datetime format.
- Clean missing billing remarks.

## Project Methodology

### 1. Monthly Billing Summary

The system generates a monthly summary using customer billing records.

The following parameters are calculated:

- **Sales:** Total monthly MRC.
- **Capacity:** Total active connection capacity in Mbps.
- **Active Links:** Number of active customer connections.

For each customer connection, the latest billing record is used to determine its monthly status, while MRC values are summed across that customer's monthly records.

### 2. Customer Link Movement Analysis

The system compares consecutive months to identify changes in customer connections.

It identifies four major categories:

| Category | Description |
|---|---|
| New Links | Customer connections appearing for the first time compared with the previous month |
| Terminations | Customer connections disappearing compared with the previous month |
| Upgrades | Existing connections with increased capacity |
| Downgrades | Existing connections with decreased capacity |

Connections marked with the billing remark `Shift to LH` are excluded from termination counts.

### 3. Capacity and Sales Change Analysis

The system calculates both absolute and percentage changes for each category.

**Absolute Change:**

Current month's value minus previous month's value.

**Percentage Change:**

\[
\text{Change \%} =
\frac{\text{Absolute Change}}{\text{Previous Month Total}}
\times 100
\]

This calculation is performed separately for capacity and sales.

### 4. Forecasting Models

The system uses two forecasting models to estimate future monthly sales and capacity.

**Model 1: Exponential Smoothing (ETS)**

Exponential Smoothing is a time-series forecasting technique that uses historical observations to estimate future values.

Configuration:

- Additive trend
- Damped trend
- Estimated initialization method

It is used to forecast monthly sales and total capacity.

**Model 2: Gradient Boosting Regressor**

Gradient Boosting is a machine learning algorithm that builds multiple decision trees to improve prediction accuracy.

The model uses the following input features:

- Month number
- Previous month's value
- Value from two months earlier
- Value from three months earlier

The model predicts future sales and capacity using historical monthly patterns.

For multi-month forecasts, previous predictions are used as inputs for subsequent months.

### 5. Active Link Forecasting

Active customer connections are estimated using the historical average monthly number of new connections and terminations.

The calculation is:

\[
\text{Future Active Links} =
\text{Current Active Links}
+
(\text{Avg New Links} - \text{Avg Terminations})
\times \text{Forecast Steps}
\]

This provides an estimated number of active connections for the requested month.

## Sample Forecasting Results

**Forecast Month:** August 2026

<text>Example output from the current model execution.</text>

| Parameter | ETS | Gradient Boosting |
|---|---:|---:|
| Sales (BDT) | 8,088,040 | 8,021,819 |
| Capacity (Mbps) | 341,236 | 331,128 |
| Active Links | 264 | 264 |

### Customer Movement Analysis

The following historical average monthly changes were calculated:

| Category | Average Monthly Links |
|---|---:|
| New Users | 263 |
| Users Who May Exit | 263 |
| Upgrades | 0 |
| Downgrades | 0 |

### Capacity and Sales Changes

| Category | Capacity Change | Sales Change |
|---|---:|---:|
| New Links | +99.8% | +99.8% |
| Terminations | -99.6% | -99.6% |
| Upgrades | +0.1% | +0.1% |
| Downgrades | -0.2% | -0.2% |

*These figures represent the sample execution output and are not guaranteed future business results.*

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

The program will ask for a month and year.

Example:

```text
Enter month (Aug / August): aug
Enter year (2026 / 26): 26
```

The program supports both short and full month names, as well as two-digit and four-digit years.

### Example Output

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

This forecasting system can help the marketing and business departments with:

- **Sales Planning:** Estimate upcoming monthly revenue.
- **Capacity Planning:** Understand expected network capacity requirements.
- **Customer Analysis:** Monitor new connections and possible customer exits.
- **Marketing Strategy:** Identify customer growth and retention trends.
- **Business Forecasting:** Compare different forecasting approaches before making decisions.

## Limitations

- Forecasting accuracy depends on the quality and length of historical billing data.
- Gradient Boosting uses only three previous monthly values and the month index as input features.
- Multi-month predictions are recursive, meaning earlier predictions influence later predictions.
- Active link predictions use historical average customer movements.
- Unexpected changes in pricing, customer demand, or business operations are not directly modeled.
- The current implementation does not calculate forecasting accuracy against a separate test dataset.

## Future Improvements

- Add XGBoost and Random Forest forecasting models.
- Compare forecasting accuracy using MAE, RMSE, and MAPE.
- Introduce customer churn prediction.
- Include seasonal billing patterns.
- Add customer-level revenue analysis.
- Develop an interactive dashboard using Streamlit.
- Introduce automated monthly billing reports.

*This project demonstrates the practical application of time-series forecasting, machine learning, billing data analysis, customer connection monitoring, and business revenue prediction in the ISP industry.*

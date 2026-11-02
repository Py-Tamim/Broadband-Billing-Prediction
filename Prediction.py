import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score, StratifiedKFold


raw = pd.read_csv("Billing_part.csv", header=None)                # Read and clean the Data
all_rows = []
block = 0
reading = False
qty_first = True
for i in range(len(raw)):
    row = raw.iloc[i].tolist()
 
    if row[0] == "From Location":
        block = block + 1
        reading = True
        qty_first = str(row[3]).startswith("Quantity")
        continue
    if row[0] == "Total":
        reading = False
        continue
 
    # skip empty rows and the small info rows
    if reading == False or pd.isna(row[2]):
        continue
 
    if qty_first:
        qty, rate, comm = row[3], row[4], row[5]
    else:
        comm, qty, rate = row[3], row[4], row[5]
 
    all_rows.append({
        "block": block,
        "link_id": row[2],
        "location": row[1],
        "qty": qty,
        "rate": rate,
        "comm_date": comm,
        "bill_end": row[7],
        "days": row[8],
        "mrc": row[9],
        "remark": row[11],
    })
bill = pd.DataFrame(all_rows)
for col in ["link_id", "location", "remark"]:          # Fill the empty cells
    bill[col] = bill[col].replace("", float("nan"))
for col in ["qty", "rate", "days", "mrc"]:
    bill[col] = pd.to_numeric(bill[col], errors="coerce")
    bill[col] = bill[col].fillna(0)

bill["comm_date"] = pd.to_datetime(bill["comm_date"])
bill["bill_end"] = pd.to_datetime(bill["bill_end"])

block_end = bill.groupby("block")["bill_end"].max()
first_end = block_end.min()
block_month = ((block_end.dt.year - first_end.year) * 12
               + block_end.dt.month - first_end.month + 1)
bill["month"] = bill["block"].map(block_month)
month_last_day = bill.groupby("month")["bill_end"].max()
sales = bill.groupby("month")["mrc"].sum()
end_of_month = bill["month"].map(month_last_day)
same_month = ((bill["bill_end"].dt.year == end_of_month.dt.year)
              & (bill["bill_end"].dt.month == end_of_month.dt.month))
bill = bill[same_month]

mrc_of_link = bill.groupby(["month", "link_id"])["mrc"].sum()
bill = bill.sort_values("bill_end")
links = bill.groupby(["month", "link_id"]).tail(1).copy()
links = links.set_index(["month", "link_id"])
links["mrc"] = mrc_of_link
links = links.reset_index()

month_end = links["month"].map(month_last_day)
links["age_months"] = (month_end - links["comm_date"]).dt.days / 30
links["stopped_early"] = (links["bill_end"] < month_end).astype(int)

months = sorted(links["month"].unique())             #Monthly summarization
summary = []
for i in range(len(months)):
    m = months[i]
    now = links[links["month"] == m].set_index("link_id")
    row = {
        "month_no": m,
        "sales": sales[m],
        "capacity": now["qty"].sum(),
        "active_links": len(now),
        "new_links": None,
        "terminations": None,
        "upgrades": None,
        "downgrades": None,
    }
    if i > 0:
        before = links[links["month"] == months[i - 1]].set_index("link_id")
        new_ids = now.index.difference(before.index)
        gone_ids = before.index.difference(now.index)
        both_ids = now.index.intersection(before.index)
 
        # "shift to LH" means the link was moved to another service,
        # the customer did not leave, so we do not count it as termination
        moved = before.loc[gone_ids, "remark"] == "shift to LH"
        gone_ids = gone_ids[~moved.values]
 
        change = now.loc[both_ids, "qty"] - before.loc[both_ids, "qty"]
 
        row["new_links"] = len(new_ids)
        
        row["terminations"] = len(gone_ids)
        row["upgrades"] = (change > 0).sum()
        row["downgrades"] = (change < 0).sum()
    summary.append(row)

summary = pd.DataFrame(summary)

x= summary[["month_no"]]                                   #Train the model
sales_model = LinearRegression().fit(x, summary["sales"])  # LinearRegression ML Model
capacity_model = LinearRegression().fit(x, summary["capacity"])
avg_new= summary["new_links"].mean()
avg_term= summary["terminations"].mean()
avg_up= summary["upgrades"].mean()
avg_down= summary["downgrades"].mean()

data=[]
for i in range(len(months) - 1):
    this_month = links[links["month"] == months[i]].copy()
    next_month_ids = links[links["month"] == months[i + 1]]["link_id"].values
    this_month["left"] = (~this_month["link_id"].isin(next_month_ids)).astype(int)
 
    # links moved to LH did not really leave, so we remove them
    moved = (this_month["left"] == 1) & (this_month["remark"] == "shift to LH")
    data.append(this_month[~moved])
 
data = pd.concat(data)
 
features = ["qty", "age_months", "days", "stopped_early"]
churn_model = RandomForestClassifier(n_estimators=200, max_depth=4,          # RandomForestClassifier ML Model
                                     min_samples_leaf=3,
                                     class_weight="balanced", 
                                     random_state=1)

churn_model.fit(data[features], data["left"]) 
folds = StratifiedKFold(n_splits=4, shuffle=True, random_state=1)
score = cross_val_score(churn_model, data[features], data["left"],
                        cv=folds, scoring="roc_auc").mean()

month_list = ["jan", "feb", "mar", "apr", "may", "jun",                    # For output part
              "jul", "aug", "sep", "oct", "nov", "dec"]

month_text = input("Enter month (Aug / aug / August / august): ").strip().lower()
year_text = input("Enter year (2026 / 26): ").strip()
if month_text[:3] not in month_list or not year_text.isdigit():
    print("Wrong month or year, please try again.")
    exit()
month = month_list.index(month_text[:3]) + 1
year = int(year_text)
if year < 100:
    year = year + 2000
target = (year - first_end.year) * 12 + month - first_end.month + 1
title = month_list[month - 1].capitalize() + " " + str(year)
last_month_no = int(summary["month_no"].max())   # last month in the file
if target < 1:
    print("Our data starts from", month_list[first_end.month - 1].capitalize(),
          first_end.year, ", please enter a later date.")
    exit()
print()
if target <= last_month_no:
    # this month is already in the billing file, so show the real numbers
    r = summary[summary["month_no"] == target].iloc[0]
    print("Actual data for", title)
    p_sales, p_capacity, p_active = r["sales"], r["capacity"], r["active_links"]
    p_new, p_term, p_up, p_down = r["new_links"], r["terminations"], r["upgrades"], r["downgrades"]
else:
    print("Prediction for", title)
    t = pd.DataFrame({"month_no": [target]})
    p_sales = sales_model.predict(t)[0]
    p_capacity = capacity_model.predict(t)[0]
    p_new, p_term, p_up, p_down = avg_new, avg_term, avg_up, avg_down
 
    # active links = links in the last month + (new - leaving) for every month after it
    months_ahead = target - last_month_no
    p_active = summary["active_links"].iloc[-1] + (avg_new - avg_term) * months_ahead
print("-----------------------------------------")
print("Sales (BDT)        :", round(p_sales))
print("Capacity (Mbps)    :", round(p_capacity))
print("Active links       :", round(p_active))
if pd.isna(p_new):
    print("(This is the first month in the file, so there is nothing to compare with.)")
else:
    print("New users (links)  :", round(p_new))
    print("Users who may exit :", round(p_term))
    print("Upgradation        :", round(p_up))
    print("Downgradation      :", round(p_down))
print("-----------------------------------------")

last_end = month_last_day[last_month_no]
last_title = month_list[last_end.month - 1].capitalize() + " " + str(last_end.year)
latest = links[links["month"] == last_month_no].copy()
latest["risk"] = churn_model.predict_proba(latest[features])[:, 1]
top5 = latest.sort_values("risk", ascending=False).head(5)
print()
print("Top 5 users with high risk of leaving (based on", last_title, "billing):")
print("(Risk score is only for ranking. Model score", round(score, 2),
      "- very few links left in the data, so use it as a guide.)")
number = 1
for i in range(len(top5)):
    u = top5.iloc[i]
    print(number, ".", u["link_id"], "|", u["location"])
    print("    Speed:", u["qty"], "Mbps | Monthly bill:", round(u["mrc"]),
          "BDT | Link age:", round(u["age_months"]), "months | Risk score:",
          round(u["risk"] * 100), "/ 100")
    number = number
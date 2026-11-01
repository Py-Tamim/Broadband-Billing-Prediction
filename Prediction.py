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
sales_model = LinearRegression().fit(x, summary["sales"])
capacity_model = LinearRegression().fit(x, summary["capacity"])
avg_new= summary["new_links"].mean()

import pandas as pd
from sklearn.linear_model import LinearRegression

A = pd.read_csv("Billing_part.csv", header=None)                # Read and clean the Data
all_rows = []
block = 0
reading = False
qty_first = True
for i in range(len(A)):
    row = A.iloc[i].tolist()

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

#============================================================================

#Rest of the code Update Soon.............................

#============================================================================

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
    vals = {c: r[c] for c in pct_cols + abs_cols}
else:
    print("Prediction for", title)
    t = pd.DataFrame({"month_no": [target]})
    p_sales = sales_model.predict(t)[0]
    p_capacity = capacity_model.predict(t)[0]
    p_new, p_term, p_up, p_down = avg_new, avg_term, avg_up, avg_down
    vals = avg_vals

    # active links = links in the last month + (new - leaving) for every month after it
    months_ahead = target - last_month_no
    p_active = summary["active_links"].iloc[-1] + (avg_new - avg_term) * months_ahead


def show(label, count, g):
    print(label, ":", round(count))
    print("      Capacity (Mbps) change :",
          f"{vals[g + '_cap_pct']:+.1f} %", "or", f"{vals[g + '_cap_abs']:+,.0f} Mbps")
    print("      Sales (BDT) change     :",
          f"{vals[g + '_sales_pct']:+.1f} %", "or", f"BDT {vals[g + '_sales_abs']:+,.0f}")


print("-----------------------------------------")
print("Sales (BDT)        :", round(p_sales))
print("Capacity (Mbps)    :", round(p_capacity))
print("Active links       :", round(p_active))
if pd.isna(p_new):
    print("(This is the first month in the file, so there is nothing to compare with.)")
else:
    show("New users (links)  ", p_new, "new")
    show("Users who may exit ", p_term, "term")
    show("Upgradation        ", p_up, "up")
    show("Downgradation      ", p_down, "down")
print("-----------------------------------------")
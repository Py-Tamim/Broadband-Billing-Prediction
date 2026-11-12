import calendar
import sys
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from statsmodels.tsa.holtwinters import ExponentialSmoothing

def load_billing():
    df = pd.read_csv("billing_part.csv")
    df.columns = df.columns.str.strip()
    df["month_date"] = pd.to_datetime(df["Month"], format="%y-%b", errors="coerce")
    df = df[df["month_date"].notna() & df["Link ID"].notna()].copy()
    df["Link ID"] = df["Link ID"].astype(str).str.strip()
    df = df[df["Link ID"].ne("") & df["Link ID"].ne("Link ID")]
    for col in ["Quantity", "MRC"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    df["Billing End Date"] = pd.to_datetime(df["Billing End Date"], errors="coerce")
    df["Billing Remarks"] = df["Billing Remarks"].fillna("").astype(str).str.strip()
    return df

def make_monthly_summary(df):
    mrc_by_link = df.groupby(["month_date", "Link ID"])["MRC"].sum()
    latest = (df.sort_values("Billing End Date")
                .groupby(["month_date", "Link ID"], sort=False)
                .tail(1).copy().set_index(["month_date", "Link ID"]))
    latest["MRC"] = mrc_by_link
    links = latest.reset_index()
    months = pd.date_range(df["month_date"].min(), df["month_date"].max(), freq="MS")
    sales = df.groupby("month_date")["MRC"].sum().reindex(months, fill_value=0)
    rows = []
    change_cols = [f"{g}_{metric}_{kind}" for g in ["new", "term", "up", "down"]
                   for metric in ["cap", "sales"] for kind in ["abs", "pct"]]

    for i, month in enumerate(months):
        now = links[links["month_date"].eq(month)].set_index("Link ID")
        row = {"month_no": i + 1, "sales": sales.loc[month],
               "capacity": now["Quantity"].sum(), "active_links": len(now),
               "new_links": np.nan, "terminations": np.nan,
               "upgrades": np.nan, "downgrades": np.nan}
        row.update({col: np.nan for col in change_cols})
        if i:
            previous = links[links["month_date"].eq(months[i - 1])].set_index("Link ID")
            new_ids = now.index.difference(previous.index)
            gone_ids = previous.index.difference(now.index)
            both_ids = now.index.intersection(previous.index)
            moved = previous.loc[gone_ids, "Billing Remarks"].str.casefold().eq("shift to lh")
            gone_ids = gone_ids[~moved.to_numpy()]
            cap_change = now.loc[both_ids, "Quantity"] - previous.loc[both_ids, "Quantity"]
            mrc_change = now.loc[both_ids, "MRC"] - previous.loc[both_ids, "MRC"]
            up_ids = cap_change[cap_change > 0].index
            down_ids = cap_change[cap_change < 0].index
            row.update({"new_links": len(new_ids), "terminations": len(gone_ids),
                        "upgrades": len(up_ids), "downgrades": len(down_ids),
                        "new_cap_abs": now.loc[new_ids, "Quantity"].sum(),
                        "new_sales_abs": now.loc[new_ids, "MRC"].sum(),
                        "term_cap_abs": -previous.loc[gone_ids, "Quantity"].sum(),
                        "term_sales_abs": -previous.loc[gone_ids, "MRC"].sum(),
                        "up_cap_abs": cap_change[up_ids].sum(),
                        "up_sales_abs": mrc_change[up_ids].sum(),
                        "down_cap_abs": cap_change[down_ids].sum(),
                        "down_sales_abs": mrc_change[down_ids].sum()})
            base_cap, base_sales = previous["Quantity"].sum(), previous["MRC"].sum()
            for group in ["new", "term", "up", "down"]:
                row[f"{group}_cap_pct"] = row[f"{group}_cap_abs"] / (base_cap or 1) * 100
                row[f"{group}_sales_pct"] = row[f"{group}_sales_abs"] / (base_sales or 1) * 100
        rows.append(row)
    return pd.DataFrame(rows)

# -_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_ Continue -_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_
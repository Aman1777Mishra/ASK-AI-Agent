import pandas as pd
import os

def npc(time_period: str, file_path: str):
    print(f"Running NPC with time_period: {time_period} and file_path: {file_path}")
    vfs = pd.read_csv("v_fact_sales_mock.csv")
    
    try:
        time_period = int(time_period)
    except ValueError:
        return "Can you please provide explicit time period for analysis in months"

    if file_path:
        filepath = os.path.join("uploads", file_path)
        prices = pd.read_csv(filepath)

    else:
        return "No_Price_File_Uploaded"

    vfs["Average Discount"] = vfs.groupby(["Item Number", "Customer"])["Discount %"].transform("mean")
#print(vfs)

    curr_date = pd.Timestamp.today()
    try:
        revision_period = int(time_period)
    except ValueError:
        return "Invalid_Time_Period_Input"

    last_date = curr_date - pd.DateOffset(months=revision_period)
    #print(type(last_date))

    vfs["Date"] = pd.to_datetime(vfs["Date"])

    vfs.drop(vfs[vfs["Date"] < last_date].index, inplace=True)

    prices.rename(columns={"Price" : "Future Price"}, inplace=True)

    df = vfs.merge(prices, on=["Item Number"], how="left")
    df.dropna(inplace=True)
    #print(df)

    df["Prev_Revenue"] = df.apply(lambda x: x["Quantity"] * x["List Price"] * (1-x["Average Discount"]), axis=1)
    df["Future_Revenue"] = df.apply(lambda x: x["Quantity"] * x["Future Price"] * (1-x["Average Discount"]), axis=1)

    previous_revenue = df["Prev_Revenue"].sum()
    future_revenue = df["Future_Revenue"].sum()

    return f"Previous Revenue: {previous_revenue}, Future Revenue: {future_revenue}."
#print(f"Previous Revenue: {previous_revenue}")
#print(f"Future Revenue: {future_revenue}")

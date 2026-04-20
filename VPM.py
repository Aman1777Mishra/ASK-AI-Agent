import pandas as pd 
from pandas.tseries.offsets import DateOffset

def vpm(time_period: str):
    df = pd.read_csv("v_fact_sales_mock.csv")
    #df = df.copy()
    curr_date = pd.Timestamp.today()

    try:
        time_period = int(time_period)
    except ValueError:
        return "Invalid_Time_Period_Input"
    
    df.rename(columns={"Item Number" : "item_number", "Customer" : "customer", "Date" : "txn_date", "Quantity" : "quantity", "List Price" : "list_price", "Net Price" : "net_price"}, inplace=True)

    period_curr = curr_date - DateOffset(months=time_period)
    period_prev = period_curr - DateOffset(months=time_period)
    df['txn_date'] = pd.to_datetime(df['txn_date'])
    
    df['include_indicator'] = df.groupby(['item_number', 'customer'])['txn_date'].transform(lambda x: 1 if (x.between(period_prev, period_curr).any() and x.between(period_curr, curr_date).any()) else 0)

    df_1 = df[df['txn_date'].between(period_prev, period_curr) & (df['include_indicator'] == 1)]
    df_prev = df_1.groupby(['item_number', 'customer']).agg({'quantity' : 'sum', 'list_price' : 'mean', 'net_price' : 'mean'})
    df_prev['revenue_prev'] = df_prev.apply(lambda x: x['quantity'] * x['net_price'], axis=1)
    df_prev.rename(columns={'quantity': 'quantity_prev', 'list_price': 'list_price_prev', 'net_price': 'net_price_prev'}, inplace=True)
    
    df_2 = df[df['txn_date'].between(period_curr, curr_date) & (df['include_indicator'] == 1)]
    df_curr = df_2.groupby(['item_number', 'customer']).agg({'quantity' : 'sum', 'list_price' : 'mean', 'net_price' : 'mean'})
    df_curr['revenue_curr'] = df_curr.apply(lambda x: x['quantity'] * x['net_price'], axis=1)
    df_curr.rename(columns={'quantity': 'quantity_curr', 'list_price': 'list_price_curr', 'net_price': 'net_price_curr'}, inplace=True)
    
    df_final = pd.merge(df, df_curr, on=['item_number', 'customer'], how='left').merge(df_prev, on=['item_number', 'customer'], how='left')
    
    df_final.fillna(0, inplace=True)
    
    df_final['price_change'] = df_final.apply(lambda x: x['net_price_curr'] - x['net_price_prev'], axis= 1)
    df_final['volume_change'] = df_final.apply(lambda x: x['quantity_curr'] - x['quantity_prev'], axis=1)
    
    df_final['price_effect'] = df_final.apply(lambda x: (x['price_change'] * x['quantity_curr'])*x['include_indicator'], axis=1)
    df_final['volume_effect'] = df_final.apply(lambda x: (x['volume_change'] * x['net_price_curr']) * x['include_indicator'], axis=1)
    df_final['mix_effect'] = df_final.apply(lambda x: (x['price_change'] * x['volume_change']) * x['include_indicator'], axis=1)
    return f"Price Effect: {df_final['price_effect'].sum()}, Volume Effect: {df_final['volume_effect'].sum()}, Mix Effect: {df_final['mix_effect'].sum()}."

#df_final = vpm(df, period_curr, period_prev, curr_date)
#df_final.to_csv('vpm_output.csv', index=False)
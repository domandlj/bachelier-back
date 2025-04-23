import pandas as pd
import numpy as np
from cohen import cohen

# Sheet info
sheet_id = "1MxsnnAW9yErCX2ZvuwgM-FtHWJMivA4ZTYEZt-P7nPs"
sheet_name = "Sheet1"  # Replace if necessary

# CSV export link
csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"

# Load into DataFrame
df = pd.read_csv(csv_url)

# Clean column names
df.columns = df.columns.str.replace('"', '', regex=False).str.replace('\n', ' ', regex=True).str.strip()

# Drop columns where the name starts with 'Unnamed'
df = df.loc[:, ~df.columns.str.startswith('Unnamed')]

# Drop empty rows if needed
df = df.dropna(how='all')

rename = {
    "COMPRA LECAPS EN Ticker": "ticker",
    "Fecha Vencim.": "fechaVencim", 
    "Días":"dias",
    "Px":"precio",
    "Liqui Secu.": "liqui_secu",
    "Pago Final":"total",
    "TEM" : "tem",
    "TNA" : "tna",
    "TEA" : "tea",
    }

df = df.rename(columns=rename)

df = df[0:20]

# cleaning
df["tna"] = df["tna"].str.rstrip('%').astype(float).div(100).replace(np.nan, None)
df["tea"] = df["tea"].str.rstrip('%').astype(float).div(100).replace(np.nan, None)
df["tem"] = df["tem"].str.rstrip('%').astype(float).div(100).replace(np.nan, None)
df["Meses"] = df["Meses"].astype(float).replace(np.nan, None)

df = df.where(pd.notnull(df), None)


for ticker in df["ticker"]:
    print(ticker)
    day, year = cohen.fixed_income_price_var(ticker)
    df.loc[df["ticker"] == ticker, "price day %"] = day
    df.loc[df["ticker"] == ticker, "price ytd %"] = year

##df["price day %"] = df["ticker"].apply(lambda ticker: cohen.fixed_income_price_daily_var(ticker)*100)
##df["price ytd %"] = df["ticker"].apply(lambda ticker: cohen.fixed_income_price_ytd(ticker)*100)

def get_lecaps():
  return df.to_dict('records')
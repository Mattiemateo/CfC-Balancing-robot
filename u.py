import pandas as pd
df = pd.read_csv('balance_data.csv')
print(df.head(10))
print(df.describe())

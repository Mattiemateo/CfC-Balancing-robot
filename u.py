import pandas as pd
df = pd.read_csv('balance_data_extremes.csv')
print(df.describe())
print(f"\nlarge disturbance rows (|u| > 10): {len(df[abs(df['u']) > 10])}")
print(f"episode count: {df['episode'].nunique()}")

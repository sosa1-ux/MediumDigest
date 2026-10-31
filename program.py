import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

df = pd.read_csv("FY_2025_Disability_Compensation_Recipients_by_County_20261027.csv")
df.head()

rating_columns = [
    "SCD rating: 0% to 20%",
    "SCD rating: 30% to 40%",
    "SCD rating: 50% to 60%",
    "SCD rating: 70% to 90%",
    "SCD rating: 100%"
]

number_columns = rating_columns + ['Total: Disability Compensation Recipients']
for col in number_columns:
    df[col] = pd.to_numeric(df[col], errors='coerce')

clean_df = df.dropna(subset=number_columns).copy()
clean_df = clean_df[clean_df["Total: Disability Compensation Recipients"] > 0].copy()

percentages_columns = []
for col in rating_columns:
    new_col = col + "_percent"
    clean_df[new_col] = (clean_df[col] / clean_df["Total: Disability Compensation Recipients"]) * 100
    percentages_columns.append(new_col)
clean_df[percentages_columns]

inertia_values = []

for k in range(2, 8):
    model = KMeans(n_clusters=k, random_state=42, n_init=10)
    model.fit(clean_df[percentages_columns])
    inertia_values.append(model.inertia_)
    print(k, model.inertia_)

plt.plot(range(2, 8), inertia_values, marker="o")
plt.xlabel("Number of clusters (k)")
plt.ylabel("Inertia")
plt.title("Elbow Method")
plt.show()


kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
clean_df['cluster'] = kmeans.fit_predict(clean_df[percentages_columns])

clean_df['cluster'].value_counts().sort_index()
clean_df.groupby('cluster')[percentages_columns].mean().round(1)
clean_df.groupby("cluster")[["County Name", "State"]].head(2)
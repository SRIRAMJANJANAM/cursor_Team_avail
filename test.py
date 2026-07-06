import pandas as pd
import matplotlib.pyplot as plt


df = pd.read_excel("data.xlsx")

df_melted = df.melt(id_vars=["ID"], var_name="Date", value_name="Response")
df_melted = df_melted.dropna(subset=["Response"])


response_counts = df_melted["Response"].value_counts()

plt.figure(figsize=(8,8))
plt.pie(response_counts, labels=response_counts.index, autopct="%1.1f%%", startangle=90)
plt.title("Overall Response Code Distribution")
plt.show()


for email, group in df_melted.groupby("ID"):
    response_counts = group["Response"].value_counts()
    
    plt.figure(figsize=(8,8))
    plt.pie(response_counts, labels=response_counts.index, autopct="%1.1f%%", startangle=90)
    plt.title(f"Response Code Distribution for {email}")
    plt.show()

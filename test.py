airbnb_path = "/dbfs/databricks-datasets/learning-spark-v2/sf-airbnb/sf-airbnb.csv"

# ANSWER
import pandas as pd

df = pd.read_csv(airbnb_path)
df.head()

display(df)
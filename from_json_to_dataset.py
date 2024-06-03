import pandas as pd
import json
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import datasets
from transformers import AutoTokenizer
import sys
import os
from sanitizer import sanitize_text
from tqdm import tqdm

os.chdir(os.path.dirname(sys.argv[0]))

def count_tokens(text: str, model_name: str) -> int:
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    tokens = tokenizer.tokenize(text)
    num_tokens = len(tokens)
    return num_tokens

with open(r"../ready/wwwoksaluteit.json", 'r') as file:
  j = json.load(file)
df = pd.DataFrame(j["data"])

# Filter by length
def check_length(df, plot=True):
    lengths = df['content'].str.len()

    percentiles = np.percentile(lengths,range(100))
    sec_order_perc = np.gradient(np.gradient(percentiles))
    df_derivatives = pd.DataFrame({
        '1st derivative': np.gradient(percentiles),
        '2nd derivative': np.gradient(np.gradient(percentiles)),
        '3rd derivative': np.gradient(np.gradient(np.gradient(percentiles)))
        #'4rd derivative': np.gradient(np.gradient(np.gradient(np.gradient(percentiles))))
        })
    candidates = np.argsort(sec_order_perc)[-5:]
    proposed_thrs = min(candidates) #minimum percentile amongst the highest variations from percentile x to x+1
    proposed_value = percentiles[proposed_thrs]
    print(["<<"+str(x)+">>" if x==proposed_thrs else str(x) for x in candidates])
    print(proposed_value)

    if plot:
        ax=sns.lineplot(df_derivatives)
        ax.axvline(proposed_thrs, color='r', linestyle='--')
        plt.show()

    return proposed_value

def filter_and_push_to_hub(dataframe, dataset_name: str, length_filter):
    filtered_df = df[df['content'].str.len() > length_filter]
    filtered_df['content']=[sanitize_text(x) for x in tqdm(filtered_df['content'])]
    hf_dataset = datasets.Dataset(filtered_df.copy(deep=True))
    hf_dataset.push_to_hub("Detsutut/"+dataset_name, private=True)

#check_length(df)
filter_and_push_to_hub(df, "oksalute", 154)



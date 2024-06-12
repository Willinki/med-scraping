from pandas import DataFrame
import json
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datasets import Dataset, DatasetDict
from transformers import AutoTokenizer
import sys
import os
from webscraping.sanitizer import sanitize_text
from tqdm import tqdm

os.chdir(os.path.dirname(sys.argv[0]))


def load_json(path: str) -> dict:
    with open(path, 'r') as file:
        jsondict = json.load(file)
    return jsondict


def check_length(dataframe: DataFrame, plot=True, num_candidates=5, tokenizer=None):
    if tokenizer is not None:
        print("Using tokenizer")
        lengths = calc_tokens_len(dataframe, tokenizer)
    else:
        lengths = dataframe['content'].str.len()

    percentiles = np.percentile(lengths, range(100))
    sec_order_perc = np.gradient(np.gradient(percentiles))
    df_derivatives = DataFrame({
        '1st derivative': np.gradient(percentiles),
        '2nd derivative': np.gradient(np.gradient(percentiles)),
        '3rd derivative': np.gradient(np.gradient(np.gradient(percentiles)))
    })
    candidates = np.argsort(sec_order_perc)[-num_candidates:]
    proposed_thrs = min(candidates)  #minimum percentile amongst the highest variations from percentile x to x+1
    proposed_value = percentiles[proposed_thrs]
    print(["<<" + str(x) + ">>" if x == proposed_thrs else str(x) for x in candidates])
    print(proposed_value)

    if plot:
        ax1 = sns.lineplot(percentiles)
        ax1.axvline(proposed_thrs, color='r', linestyle='--')
        plt.show()

        ax2 = sns.lineplot(df_derivatives)
        ax2.axvline(proposed_thrs, color='r', linestyle='--')
        plt.show()

    return proposed_value


def calc_tokens_len(dataframe: DataFrame, tokenizer):
    dataset = Dataset.from_pandas(dataframe)

    def tokenize(batch):
        batch["length"] = [len(tokenizer(text)["input_ids"]) for text in batch["content"]]
        return batch

    dset_tokenized = dataset.map(tokenize, batched=True)
    return dset_tokenized["length"]


def calc_stats(array):
    # Print results
    print(f"Sum: {np.sum(array)}")
    print(f"Mean: {np.mean(array)}")
    print(f"Standard Deviation: {np.std(array)}")
    print(f"Minimum: {np.min(array)}")
    print(f"Maximum: {np.max(array)}")


def filter_and_push_to_hub(dataframe: DataFrame, dataset_name: str, length_filter):
    filtered_df = dataframe[dataframe['content'].str.len() > length_filter]
    sanitized_df = filtered_df.copy(deep=True)
    sanitized_df['content'] = [sanitize_text(x) for x in tqdm(filtered_df['content'])]
    calc_stats(calc_tokens_len(dataframe=sanitized_df, tokenizer=AutoTokenizer.from_pretrained("IVN-RIN/bioBIT")))
    hf_dataset = Dataset.from_pandas(sanitized_df)
    hf_dataset.push_to_hub("Detsutut/" + dataset_name, private=True)


j = load_json(r"../json/wwwmedicitaliait.json")
df = DataFrame(j["data"])

#check_length(df, num_candidates=20)
filter_and_push_to_hub(df, "medicitalia", 100)

from datasets import load_dataset
from dotenv import load_dotenv
from datasets import DatasetDict
import os
import pandas as pd
from typing import Optional
load_dotenv()
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(encoding='utf-8', level=logging.DEBUG)

HF_TOKEN = os.environ["HF_TOKEN"]


def load_data_hf(repo_name: str, data_files: str, is_public: bool) -> DatasetDict:
    if is_public:
        dataset = load_dataset(repo_name, split="train")
    else:
        dataset = load_dataset(repo_name, token=True, data_files=data_files)
    return dataset


def load_scores(category: str) -> pd.DataFrame | None:
    repository = os.environ.get("DATA_REPO")
    data_file = None
    match category:
        case "popularity":
            data_file = "computed/popularity/popularity_scores.csv"
        case "seasonality":
            data_file = "computed/seasonality/seasonality_scores.csv"
        case "emissions":
            data_file = "computed/emissions/emissions_merged.csv"
        case _:
            logger.info(f"Invalid category: {category}")
    if data_file:  # only for valid categories
        data = load_data_hf(repository, data_file, is_public=False)
        df = pd.DataFrame(data["train"][:])
        return df
    return None


def load_places(data_file: str) -> pd.DataFrame | None:
    repository = os.environ.get("DATA_REPO")

    if data_file:
        data = load_data_hf(repository, data_file, is_public=False)
        df = pd.DataFrame(data["train"][:])
        return df

    return None


import os
import logging
import pandas as pd
import lancedb
from datasets import load_dataset

from src.vectordb.schema import WikivoyageDocuments


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


HF_REPO = "ashmib/wikivoyage-eu-city-embeddings"
HF_FILE = "city_abstracts_embeddings.csv"
TABLE_NAME = "wikivoyage_documents"


def build_documents_df() -> pd.DataFrame:
    """
    Build a dataframe compatible with the WikivoyageDocuments LanceDB schema.

    Required schema fields:
    - city
    - country
    - section
    - text
    - vector, generated automatically by LanceDB from the source fields
    """
    logger.info("Loading Hugging Face dataset: %s / %s", HF_REPO, HF_FILE)

    dataset = load_dataset(
        HF_REPO,
        data_files=HF_FILE,
    )

    df = pd.DataFrame(dataset["train"][:])

    logger.info("Loaded %d rows", len(df))
    logger.info("Columns: %s", list(df.columns))

    required_columns = {"city", "country", "abstract"}
    missing = required_columns - set(df.columns)

    if missing:
        raise RuntimeError(f"Missing required columns from HF dataset: {missing}")

    docs_df = pd.DataFrame()
    docs_df["city"] = df["city"].astype(str)
    docs_df["country"] = df["country"].astype(str)
    docs_df["section"] = "Overview"
    docs_df["text"] = df["abstract"].fillna("").astype(str)

    docs_df = docs_df[docs_df["text"].str.len() > 0].reset_index(drop=True)

    logger.info("Prepared %d document rows", len(docs_df))

    return docs_df


def main():
    uri = os.environ.get("BUCKET_NAME")

    if not uri:
        raise RuntimeError(
            "BUCKET_NAME is not set. Example: "
            "export BUCKET_NAME=/home/maryyf/green-city-finder/database/wikivoyage"
        )

    os.makedirs(uri, exist_ok=True)

    docs_df = build_documents_df()

    logger.info("Connecting to LanceDB at %s", uri)
    db = lancedb.connect(uri)

    logger.info("Dropping old table if it exists: %s", TABLE_NAME)
    db.drop_table(TABLE_NAME, ignore_missing=True)

    logger.info("Creating table: %s", TABLE_NAME)
    table = db.create_table(TABLE_NAME, schema=WikivoyageDocuments)

    logger.info("Adding rows to table...")
    table.add(docs_df.to_dict("records"))

    logger.info("Done. Created %s with %d rows.", TABLE_NAME, len(docs_df))


if __name__ == "__main__":
    main()
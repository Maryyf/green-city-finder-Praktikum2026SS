import os
import re
import logging
from typing import Optional, Iterable

import numpy as np
import pandas as pd

from src.data_directories import cities_csv
from src.data_directories import *

logger = logging.getLogger(__name__)
logging.basicConfig(encoding="utf-8", level=logging.INFO)


DEFAULT_COST_FILES = [
    numbio_dir + "/cost-of-living/cost-of-living.csv",
    numbio_dir + "/cost-of-living/cost-of-living_v2.csv",
]
COUNTRY_ALIASES = {
    "czech republic": "czechia",
    "kosovo (disputed territory)": "kosovo",
    "north macedonia": "macedonia",
}

def _normalize_name(value: object) -> str:
    if pd.isna(value):
        return ""
    value = str(value).strip().lower()
    value = re.sub(r"\s+", " ", value)
    return value

def _normalize_country(value: object) -> str:
    country = _normalize_name(value)
    return COUNTRY_ALIASES.get(country, country)


def _read_cost_file(path: str, source_priority: int) -> pd.DataFrame:
    if not os.path.exists(path):
        logger.warning("Cost-of-living file not found: %s", path)
        return pd.DataFrame()

    df = pd.read_csv(path, low_memory=False)

    if "Unnamed: 0" in df.columns:
        df = df.drop(columns=["Unnamed: 0"])

    required = {"city", "country"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"{path} is missing required columns: {missing}")

    df["source_priority"] = source_priority
    return df


def load_allowed_cities(city_csv_path: str = cities_csv) -> pd.DataFrame:
    allowed = pd.read_csv(city_csv_path, low_memory=False)

    required = {"city", "country"}
    missing = required - set(allowed.columns)
    if missing:
        raise ValueError(
            f"{city_csv_path} must contain at least city and country columns."
        )

    allowed = allowed[["city", "country"]].copy()
    allowed["city"] = allowed["city"].fillna("").astype(str).str.strip()
    allowed["country"] = allowed["country"].fillna("").astype(str).str.strip()

    allowed["city_key"] = allowed["city"].apply(_normalize_name)
    allowed["country_key"] = allowed["country"].apply(_normalize_country)

    return allowed.drop_duplicates(["city_key", "country_key"])


def load_raw_cost_data(cost_files: Optional[list[str]] = None) -> pd.DataFrame:
    if cost_files is None:
        cost_files = DEFAULT_COST_FILES

    frames = []
    for priority, path in enumerate(cost_files):
        frame = _read_cost_file(path, source_priority=priority)
        if not frame.empty:
            frames.append(frame)

    if not frames:
        raise FileNotFoundError(
            "No cost-of-living files found. Please check DEFAULT_COST_FILES."
        )

    df = pd.concat(frames, ignore_index=True)

    df["city"] = df["city"].fillna("").astype(str).str.strip()
    df["country"] = df["country"].fillna("").astype(str).str.strip()
    df["city_key"] = df["city"].apply(_normalize_name)
    df["country_key"] = df["country"].apply(_normalize_country)

    numeric_cols = [
        c for c in df.columns
        if re.fullmatch(r"x\d+", c) or c == "data_quality"
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # 对重复城市，优先使用：
    # 1. data_quality 更高的数据
    # 2. source_priority 更高的数据，也就是 v2 优先
    df = df.sort_values(
        by=["city_key", "country_key", "data_quality", "source_priority"],
        ascending=[True, True, False, False],
    )

    df = df.drop_duplicates(["city_key", "country_key"], keep="first")
    return df.reset_index(drop=True)


def filter_to_embedding_cities(
    cost_df: pd.DataFrame,
    city_csv_path: str = cities_csv,
) -> pd.DataFrame:
    allowed = load_allowed_cities(city_csv_path)

    merged = allowed.merge(
        cost_df,
        on=["city_key", "country_key"],
        how="inner",
        suffixes=("_embedding", "_cost"),
    )

    # 使用 city_abstracts_embeddings.csv 里的标准城市名和国家名
    merged["city"] = merged["city_embedding"]
    merged["country"] = merged["country_embedding"]

    drop_cols = [
        "city_embedding",
        "country_embedding",
        "city_cost",
        "country_cost",
    ]
    merged = merged.drop(columns=[c for c in drop_cols if c in merged.columns])

    return merged.reset_index(drop=True)


def _fill_missing_prices(df: pd.DataFrame) -> pd.DataFrame:
    """
    缺失值处理：
    1. 先用同国家 median 填补
    2. 如果国家内也没有，再用全局 median
    """
    df = df.copy()
    price_cols = [c for c in df.columns if re.fullmatch(r"x\d+", c)]

    for col in price_cols:
        df[col] = df.groupby("country_key")[col].transform(
            lambda s: s.fillna(s.median())
        )
        df[col] = df[col].fillna(df[col].median())

    return df


def estimate_monthly_living_costs(
    cost_files: Optional[list[str]] = None,
    city_csv_path: str = cities_csv,
) -> pd.DataFrame:
    """
    根据 Numbeo-style cost-of-living columns 估计单人月生活成本。

    输出：
    - monthly_living_cost_usd: 估计月生活成本，USD
    - cost_index: 0-100，越高越贵
    - cost_score: 0-100，越高越适合推荐，也就是越便宜
    - cost_salary_ratio: 月生活成本 / 平均税后月工资
    """

    raw = load_raw_cost_data(cost_files)
    df = filter_to_embedding_cities(raw, city_csv_path)
    df = _fill_missing_prices(df)

    # ----------------------------
    # 1. Groceries / supermarket food
    # ----------------------------
    groceries_cost = (
        df["x9"] * 12      # Milk, 12 liters
        + df["x10"] * 16   # Bread, 16 loaves
        + df["x11"] * 5    # Rice, 5 kg
        + df["x12"] * 4    # Eggs, 4 packs of 12
        + df["x13"] * 1.5  # Cheese, 1.5 kg
        + df["x14"] * 4    # Chicken, 4 kg
        + df["x15"] * 1.5  # Beef, 1.5 kg
        + df["x16"] * 4    # Apples, 4 kg
        + df["x17"] * 4    # Bananas, 4 kg
        + df["x18"] * 4    # Oranges, 4 kg
        + df["x19"] * 4    # Tomato, 4 kg
        + df["x20"] * 5    # Potato, 5 kg
        + df["x21"] * 3    # Onion, 3 kg
        + df["x22"] * 6    # Lettuce, 6 heads
        + df["x23"] * 10   # Water, 10 bottles
    )

    # ----------------------------
    # 2. Restaurants / eating out
    # ----------------------------
    restaurant_cost = (
        df["x1"] * 6       # 6 inexpensive restaurant meals
        + df["x3"] * 4     # 4 McMeals or equivalent
        + df["x2"] * 0.5   # one mid-range dinner for two, half assigned to one person
        + df["x6"] * 8     # 8 cappuccinos
        + df["x7"] * 4     # 4 soft drinks
        + df["x8"] * 4     # 4 restaurant waters
    )

    # ----------------------------
    # 3. Transport
    # ----------------------------
    # 如果有 monthly pass，用 x29。
    # 如果没有，则用 40 次单程票估算。
    transport_cost = df["x29"].where(
        df["x29"].notna() & (df["x29"] > 0),
        df["x28"] * 40,
    )

    # ----------------------------
    # 4. Rent
    # ----------------------------
    # 单人生活默认使用 outside centre 的一居室 x49。
    # 如果缺失，再用 city centre 的一居室 x48。
    rent_cost = df["x49"].where(
        df["x49"].notna() & (df["x49"] > 0),
        df["x48"],
    )

    # ----------------------------
    # 5. Utilities and communication
    # ----------------------------
    # x37 是 1 minute prepaid mobile tariff，不是月费。
    # 这里假设每月 100 分钟。
    utilities_cost = (
        df["x36"]        # electricity, heating, cooling, water, garbage
        + df["x38"]      # internet
        + df["x37"] * 100
    )

    # ----------------------------
    # 6. Leisure
    # ----------------------------
    leisure_cost = (
        df["x39"]        # monthly fitness club
        + df["x41"] * 2  # two cinema visits
    )

    # ----------------------------
    # 7. Basic shopping, monthly amortized
    # ----------------------------
    # 衣服鞋子不是每月都买，所以做月摊销。
    # 假设每年购买：
    # - 1 jeans
    # - 2 summer dresses / equivalent chain-store clothes
    # - 1 running shoes
    # - 1 business shoes
    basic_shopping_cost = (
        df["x44"] / 12
        + df["x45"] * 2 / 12
        + df["x46"] / 12
        + df["x47"] / 12
    )

    df["groceries_cost_usd"] = groceries_cost.round(2)
    df["restaurant_cost_usd"] = restaurant_cost.round(2)
    df["transport_cost_usd"] = transport_cost.round(2)
    df["rent_cost_usd"] = rent_cost.round(2)
    df["utilities_cost_usd"] = utilities_cost.round(2)
    df["leisure_cost_usd"] = leisure_cost.round(2)
    df["basic_shopping_cost_usd"] = basic_shopping_cost.round(2)

    df["monthly_living_cost_usd"] = (
        df["groceries_cost_usd"]
        + df["restaurant_cost_usd"]
        + df["transport_cost_usd"]
        + df["rent_cost_usd"]
        + df["utilities_cost_usd"]
        + df["leisure_cost_usd"]
        + df["basic_shopping_cost_usd"]
    ).round(2)

    # ----------------------------
    # 8. Normalize to cost_index
    # ----------------------------
    min_cost = df["monthly_living_cost_usd"].min()
    max_cost = df["monthly_living_cost_usd"].max()

    if max_cost > min_cost:
        df["cost_index"] = (
            (df["monthly_living_cost_usd"] - min_cost)
            / (max_cost - min_cost)
            * 100
        ).round(2)
    else:
        df["cost_index"] = 50.0

    # 推荐分数：越便宜越高
    df["cost_score"] = (100 - df["cost_index"]).round(2)

    # ----------------------------
    # 9. Affordability
    # ----------------------------
    # x54 = Average Monthly Net Salary
    df["average_salary_usd"] = df["x54"]

    df["cost_salary_ratio"] = np.where(
        df["average_salary_usd"] > 0,
        (df["monthly_living_cost_usd"] / df["average_salary_usd"]).round(3),
        np.nan,
    )

    keep_cols = [
        "city",
        "country",
        "monthly_living_cost_usd",
        "cost_index",
        "cost_score",
        "cost_salary_ratio",
        "average_salary_usd",
        "groceries_cost_usd",
        "restaurant_cost_usd",
        "transport_cost_usd",
        "rent_cost_usd",
        "utilities_cost_usd",
        "leisure_cost_usd",
        "basic_shopping_cost_usd",
        "data_quality",
    ]

    return df[keep_cols].sort_values(
        by=["cost_score", "data_quality"],
        ascending=[False, False],
    ).reset_index(drop=True)


def get_cost_scores(
    destinations: Optional[Iterable[str]] = None,
    cost_files: Optional[list[str]] = None,
    city_csv_path: str = cities_csv,
) -> list[dict]:
    """
    给 info_retrieval.get_context() 使用。
    输入一组推荐城市，返回这些城市的 cost score。
    """
    df = estimate_monthly_living_costs(
        cost_files=cost_files,
        city_csv_path=city_csv_path,
    )

    if destinations is not None:
        destination_keys = {_normalize_name(city) for city in destinations}
        df = df[df["city"].apply(_normalize_name).isin(destination_keys)]

    results = []

    for _, row in df.iterrows():
        results.append({
            "city": row["city"],
            "country": row["country"],
            "monthly_living_cost_usd": float(row["monthly_living_cost_usd"]),
            "cost_index": float(row["cost_index"]),
            "cost_score": float(row["cost_score"]),
            "cost_salary_ratio": (
                None if pd.isna(row["cost_salary_ratio"])
                else float(row["cost_salary_ratio"])
            ),
            "average_salary_usd": (
                None if pd.isna(row["average_salary_usd"])
                else float(row["average_salary_usd"])
            ),
            "breakdown": {
                "groceries": float(row["groceries_cost_usd"]),
                "restaurants": float(row["restaurant_cost_usd"]),
                "transport": float(row["transport_cost_usd"]),
                "rent": float(row["rent_cost_usd"]),
                "utilities": float(row["utilities_cost_usd"]),
                "leisure": float(row["leisure_cost_usd"]),
                "basic_shopping": float(row["basic_shopping_cost_usd"]),
            },
            "data_quality": (
                None if pd.isna(row["data_quality"])
                else float(row["data_quality"])
            ),
        })

    return results


def save_cost_scores(
    output_path: str = "./european-city-data/computed/cost_of_living/cost_scores.csv",
    cost_files: Optional[list[str]] = None,
    city_csv_path: str = cities_csv,
) -> pd.DataFrame:
    df = estimate_monthly_living_costs(
        cost_files=cost_files,
        city_csv_path=city_csv_path,
    )

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)

    logger.info("Saved cost scores to %s", output_path)
    return df


if __name__ == "__main__":
    scores = save_cost_scores()
    print(scores.head(20))
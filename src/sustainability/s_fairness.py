import sys
import os
from typing import Optional, Dict, Any

import pandas as pd
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)
logging.basicConfig(encoding='utf-8', level=logging.DEBUG)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

def get_emission_scores(emissions_df: pd.DataFrame, starting_point: str, destination: str, ):
    """

    Returns the emission score for the connection with least co2e between two cities.
    :param emissions_df:
    :param starting_point:
    :param destination:
    :return:
    """
    df = emissions_df.loc[(emissions_df["city_1"] == starting_point) & (emissions_df["city_2"] == destination)]
    if len(df) == 0:
        logger.info(f"Connection not found between {starting_point} and {destination}")
        return 0, None
    df.loc[:, 'min_co2e'] = df[['fly_co2e_kg', 'drive_co2e_kg', 'train_co2e_kg']].min(axis=1)
    df.loc[:, 'min_co2e_colname'] = df[['fly_co2e_kg', 'drive_co2e_kg', 'train_co2e_kg']].idxmin(axis=1)
    min_co2e = df.min_co2e.values[0]
    mode_prefix = (df.min_co2e_colname.values[0]).split("_")[0]
    min_cost = df[mode_prefix + "_cost_EUR"].values[0]
    if mode_prefix == "train":
        min_travel_time = df[mode_prefix + "_time_mins"].values[0] / 60
    else:
        min_travel_time = df[mode_prefix + "_time_hrs"].values[0]
    emission_score = 0.352 * min_travel_time + 0.218 * min_co2e + 0.431 * min_cost
    return emission_score, mode_prefix


def _check_city_present(df: pd.DataFrame, starting_point: Optional[str] = None, destination: str = "",
                        category: str = "popularity"):
    if category == "emissions":
        if not ((df['city_1'] == starting_point) & (df['city_2'] == destination)).any():
            return False
        else:
            return True
    if not len(df[df['city'] == destination]):
        return False
    return True


def get_scores(df: pd.DataFrame, starting_point: Optional[str] = None, destination="",
               month: Optional[str] = None, category: str = "popularity"):
    """
    
    Returns the seasonality/popularity score for a particular destination.
    Seasonality is calculated for a particular month, while popularity is year-round.
    If no month is provided then
    the best month, i.e. month of lowest seasonality is returned.

    Args:
        - destination: str
        - month: str (default: None)
        - category: str (default: "popularity")
    
    """

    # Check if city is present in dataframe
    if not _check_city_present(df, starting_point, destination, category):
        logger.info(f"{destination} does not have {category} data")
        return None, None

    match category:
        case "popularity":
            return df[df['city'] == destination]['weighted_pop_score'].item()
        case "seasonality":
            dest_df = df.loc[df['city'] == destination]
            if month:
                m = month.capitalize()[:3]
            else:
                dest_df['lowest_col'] = dest_df.loc[:, dest_df.columns != 'city'].idxmin(axis="columns")
                m = dest_df[dest_df['city'] == destination]['lowest_col'].item()
            return m, dest_df[dest_df['city'] == destination][m].item()
        case "emissions":
            emissions = get_emission_scores(df, starting_point, destination)
            return emissions


def compute_sfairness_score(data: list[pd.DataFrame],
                            starting_point: str, destination: str,
                            month: Optional[str] = None) -> dict[str, Any] | dict[str, None]:
    """
    
    Returns the s-fairness score for a particular destination city and (optional) month. If the destination doesn't
    have popularity or seasonality scores, then the function returns None.

    Args:
        - data: list[pd.DataFrame]
        - starting_point: str
        - destination: str
        - month: str (default: None)
    
    """
    popularity_score = get_scores(df=data[0],
                                  starting_point=None,
                                  destination=destination, month=None, category="popularity")
    month, seasonality_score = get_scores(df=data[1],
                                          starting_point=None, destination=destination,
                                          month=month, category="seasonality")

    emission_score, mode = get_scores(df=data[2],
                                      starting_point=starting_point, destination=destination, category="emissions")
    if emission_score is None:
        emission_score = 0

    # RECHECK
    if seasonality_score is not None and popularity_score is not None:
        s_fairness = round(0.281 * emission_score + 0.334 * popularity_score + 0.385 * seasonality_score, 3)
        return {
            'month': month,
            'mode': mode,  # 'fly', 'drive', 'train'
            's-fairness': s_fairness
        }
    # elif popularity is not None: # => seasonality is None
    #     s_fairness = 0.281 * emissions + 0.334 * popularity
    # elif seasonality[1] is not None: # => popularity is None
    #     s_fairness = 0.281 * emissions + 0.385 * seasonality[1]
    # else: # => both are non
    #     s_fairness =  0.281 * emissions
    else:
        return {
            'month': None,
            'mode': None,  # 'fly', 'drive', 'train'
            's-fairness': None
        }


def test():
    popularity_data = load_data("popularity")
    seasonality_data = load_data("seasonality")
    emissions_data = load_data("emissions")
    data = [popularity_data, seasonality_data, emissions_data]
    print(compute_sfairness_score(data=data, starting_point="Munich", destination="Dijon"))
    print(compute_sfairness_score(data=data, starting_point="Munich", destination="Strasbourg", month="Dec"))


if __name__ == "__main__":
    test()

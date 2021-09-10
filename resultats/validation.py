import json
from typing import Dict

from pydantic import BaseModel, validator


class Results(BaseModel):
    inscrits: int
    votants: int
    exprimes: int
    resultats: Dict[str, int]

    @validator("votants")
    def less_votants_than_inscrits(cls, votants, values):
        if votants > values["inscrits"]:
            raise ValueError(
                f"Results: there are more votants than inscrits: expected less than {values['inscrits']}, found {votants}"
            )
        return votants

    @validator("exprimes")
    def less_exprimes_than_votants(cls, exprimes, values):
        if exprimes > values["votants"]:
            raise ValueError(
                f"Results: there are more experimes than votants: expected less than {values['votants']}, found {exprimes}"
            )
        return exprimes

    @validator("resultats")
    def votes_sum_to_exprimes(cls, resultats, values):
        """The sum of votes to each candidats must sum to to the number of votes exprimes."""
        sum_votes = sum(resultats.values())
        if sum_votes != values['exprimes']:
            raise ValueError(
                f"Results: the sum of votes to the respective candidates ({sum_votes}) is different from"
                f" the total number of votes {values['exprimes']}"
            )


class Presidentielles(BaseModel):
    premier_tour: Results
    second_tour: Results


class Regionales(BaseModel):
    premier_tour: dict[str, Results]
    second_tour: dict[str, Results]


def validate_presidentielles():
    with open("resultats/presidentielles.json", "r") as data:
        results = json.load(data)

    for year in results:
        try:
            Presidentielles(**results[year])
        except ValueError:
            print(f"Presidentielles {year}")
            raise


def validate_europeennes():
    with open("resultats/europeennes.json", "r") as data:
        results = json.load(data)

    for year in results:
        try:
            Results(**results[year])
        except ValueError:
            print(f"Européennes {year}")
            raise


def validate_regionales():
    with open("resultats/regionales.json", "r") as data:
        results = json.load(data)

    for year in results:
        try:
            Regionales(**results[year])
        except ValueError:
            print(f"Régionales {year}")
            raise


if __name__ == "__main__":
    validate_presidentielles()
    validate_europeennes()
    validate_regionales()

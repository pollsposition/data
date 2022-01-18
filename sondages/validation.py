import datetime
import json
from enum import Enum
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, PositiveInt, ValidationError, confloat, validator


POLLS_FILES = [
    "sondages/presidentielles_2022.json",
    "sondages/presidentielles_2017.json",
]


class Method(str, Enum):
    internet = "internet"
    internet_telephone = "internet & telephone"


class Pollster(str, Enum):
    bva = "BVA"
    elabe = "Elabe"
    harris = "Harris interactive"
    ifop = "Ifop"
    ipsos = "Ipsos"
    kantar = "Kantar"
    odoxa = "Odoxa"
    opinionway = "Opinionway"
    cluter17 = "Cluster 17"


class Base(str, Enum):
    """Population whose intentions are reported"""

    I = "I"  # interviewed
    SV = "SV"  # interviewed and certain to vote
    SVC = "SVC"  # interviewed, certain to vote and of their choice


class Certitude(BaseModel):
    ensemble: Optional[confloat(gt=0, lt=100)]
    detail: Optional[Dict[str, confloat(gt=0, lt=100)]]

    class Config:
        extra = "forbid"


class Scenario(BaseModel):
    hypothese: Optional[str]
    base: Base
    nspp: Optional[confloat(gt=0, lt=100)]
    intentions_exprimees: Optional[int]
    intentions: Dict[str, confloat(ge=0, lt=100)]  # % per candidate among answers
    certitude: Optional[Certitude]

    class Config:
        extra = "forbid"

    @staticmethod
    def intentions_sum_to_100(intentions):
        """The sum of voting intentions needs to be equal to 100.

        This means that in some cases we may have to set the percentage of
        votes of candidates with <0.5% of intentions to 0. It is easier to do
        this work upstream, and leave a comment in the Pull Request, than to do
        it closer to the visualizations or models.

        """
        sum_intentions = sum(intentions.values())
        if sum_intentions != 100:
            raise ValueError(
                f"Hypothesis: voting intentions must sum to 100, found {sum_intentions}"
            )

    @staticmethod
    def intentions_in_reasonable_range(intentions):
        """Voting intentions are assumed to be in a reasonable range.

        There may be a situation in which voting intentions for a candidate
        would be really large, but it is more likely to be a typing mistake.
        Feels free to ignore this error and change the threshold is a candidate
        indeed gets more than 70% of voting intentions.

        """
        for value in intentions.values():
            if value >= 70:
                raise ValueError(
                    f"Hypothesis: voting intentions abnormally large: {value}"
                )

    @validator("intentions")
    def validate_intentions(cls, intentions):
        """Performs all validations on the intentions."""
        cls.intentions_sum_to_100(intentions)
        cls.intentions_in_reasonable_range(intentions)
        return intentions


class Transfers(BaseModel):
    candidats_1er_tour: List[str]
    candidats_2nd_tour: List[str]
    reports: List[List[int]]

    @staticmethod
    def transfers_sum_to_100(matrix):
        """Total vote transference must be equal to 100.

        This may require enterig by hand the share of votes that would be "non
        exprimés" in the second round.

        """
        for scenario in matrix:
            sum_intentions = sum(scenario)
            if sum_intentions != 100:
                raise ValueError(
                    f"Transfers: the vote transfers must sum to 100 found {sum_intentions}"
                )

    @staticmethod
    def matrices_have_proper_size(matrix, values):
        """Vote transference matrix must have the right shape.

        The number of rows must be equal to the number of candidates in the
        first round (reported) and the number of columns equal to the number of
        candidates in the second round.

        """
        num_candidates_1st = len(values["candidats_1er_tour"])
        num_candidates_2nd = len(values["candidats_2nd_tour"])
        if len(matrix) != num_candidates_1st:
            raise ValueError(
                "Transfers: the number of rows in the matrix does not match the number of candidates:"
                f" expected {num_candidates_1st}, found {len(matrix)}"
            )

        for row in matrix:
            if len(row) != num_candidates_2nd:
                raise ValueError(
                    "Transfers: the number of columns in the matrix does not match the number of candidates:"
                    f" expected {num_candidates_2nd}, found {len(row)}"
                )

    @validator("reports")
    def validate_transfer_matrix(cls, matrix, values):
        """Performs all validations on the transfers."""
        cls.matrices_have_proper_size(matrix, values)
        cls.transfers_sum_to_100(matrix)
        return matrix


class Poll(BaseModel):
    candidates: List[str]  # passed as an argument

    institut: Pollster
    commanditaires: List[str]
    source: str
    date_debut: datetime.date
    date_fin: datetime.date
    methode: Method
    interroges: PositiveInt
    premier_tour: Optional[List[Scenario]] = None
    second_tour: Optional[List[Scenario]] = None
    reports: Optional[List[Transfers]] = None

    class Config:
        extra = "forbid"

    @validator("date_fin")
    def end_date_corectness(cls, end_dates, values):
        if end_dates < values["date_debut"]:
            raise ValueError(
                "Poll: the end of the poll must happen after the beggining"
            )
        return end_dates

    @staticmethod
    def check_candidate_names(allowed, candidates):
        for name in candidates:
            if name not in allowed:
                raise ValueError(
                    f"Hypothesis: the specified candidate name '{name}' is not valid"
                )

    @validator("premier_tour")
    def first_round(cls, first_round, values):
        possible_candidates = values["candidates"]
        for hypothesis in first_round:
            candidates = hypothesis.intentions.keys()
            cls.check_candidate_names(possible_candidates, candidates)

    @validator("second_tour")
    def second_round(cls, second_round, values):
        possible_candidates = values["candidates"]
        for hypothesis in second_round:
            candidates = hypothesis.intentions.keys()
            cls.check_candidate_names(possible_candidates, candidates)

    @validator("reports")
    def validate_reports(cls, reports, values):
        possible_candidates = values["candidates"]
        for hypothesis in reports:
            candidates = hypothesis.candidats_1er_tour
            cls.check_candidate_names(possible_candidates, candidates)

            candidates = hypothesis.candidats_2nd_tour
            cls.check_candidate_names(possible_candidates, candidates)


def validate_polls(path):
    """Validate all polls in file."""
    with open(path, "r") as data:
        sondages = json.load(data)

    candidates = sondages["candidats"]
    for id, sondage in sondages["sondages"].items():
        try:
            Poll(candidates=candidates, **sondage)
        except:
            print(id)
            raise


if __name__ == "__main__":
    for filename in POLLS_FILES:
        validate_polls(filename)

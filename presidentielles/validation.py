import datetime
import json
from typing import Dict, List, Optional

from pydantic import BaseModel, ValidationError, validator

BEGIN = datetime.date(2021, 1, 1)
END = datetime.date(2022, 4, 24)

candidates = [
    "Abstention/Blanc/Nul",
    "Extrême Gauche",
    "Nathalie Arthaud",
    "Philippe Poutou",
    "Fabien Roussel",
    "Jean-Luc Mélenchon",
    "Anne Hidalgo",
    "Arnaud Montebourg",
    "Yannick Jadot",
    "Emmanuel Macron",
    "Jean-Christophe Lagarde",
    "Xavier Bertrand",
    "Valérie Pécresse",
    "Laurent Wauquiez",
    "François Baroin",
    "Éric Ciotti",
    "Michel Barnier",
    "Jean-Frédéric Poisson",
    "Nicolas Dupont-Aignan",
    "François Asselineau",
    "Jean Lassalle",
    "Florian Philippot",
    "Marine Le Pen",
    "Éric Zemmour",
]

methods = ["internet"]

pollsters = ["Harris interactive", "Ifop", "Ipsos", "ELABE"]

populations = [
    "Inscrits sur les listes électorales",
    "Certains d'aller voter"

]


class Hypothesis(BaseModel):
    intentions_exprimees: Optional[int]
    intentions: Dict[str, float]

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

    @staticmethod
    def candidate_names_are_valid(intentions):
        """Check that candidate names belong to the list of possible candidates.

        This check prevents typos in names--which happens often--from provoking
        errors downstream.

        """
        for candidate in intentions.keys():
            if candidate not in candidates:
                raise ValueError(
                    f"Hypothesis: the specified candidate name '{candidate}' is not valid"
                )

    @validator("intentions")
    def validate_intentions(cls, intentions):
        """Performs all validations on the intentions."""
        cls.intentions_sum_to_100(intentions)
        cls.intentions_in_reasonable_range(intentions)
        cls.candidate_names_are_valid(intentions)
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

    @validator("candidats_1er_tour", "candidats_2nd_tour")
    def validate_candidate_names(cls, names):
        """Check that the name of candidates belongs to the list of possible candidates."""
        for candidate in names:
            if candidate not in candidates:
                raise ValueError(
                    f"Transfers: the specified candidate name '{candidate}' is not valid"
                )
        return names


class Poll(BaseModel):
    institut: str
    commanditaires: List[str]
    date_debut: datetime.date
    date_fin: datetime.date
    date_publication: datetime.date
    methode: str
    lien: str

    echantillon: int
    population: str

    hypotheses: Dict[str, str]
    premier_tour: Dict[str, Hypothesis]
    second_tour: Optional[Dict[str, Hypothesis]] = None
    reports: Optional[Dict[str, Transfers]] = None

    @validator("date_debut")
    def start_date_within_election_period(cls, start_date):
        if start_date > END or start_date < BEGIN:
            raise ValueError(f"Poll: the start date {start_date} is incorrect")
        return start_date

    @validator("date_fin")
    def end_date_corectness(cls, end_dates, values):
        if end_dates > END or end_dates < BEGIN:
            raise ValueError(f"Polls: the end date {end_dates} is incorrect")

        if end_dates < values["date_debut"]:
            raise ValueError(
                "Poll: the end of the poll must happen after the beggining"
            )
        return end_dates

    @validator("date_publication")
    def publication_date_ordering(cls, publication_date, values):
        if publication_date > END or publication_date < BEGIN:
            raise ValueError(
                f"Poll: The publication date {publication_date} is incorrect"
            )
        if publication_date < values["date_fin"]:
            raise ValueError(
                "Poll: the publication must happen after the end of the poll"
            )
        return publication_date

    @validator("institut")
    def pollster_name(cls, name):
        if name not in pollsters:
            raise ValueError(f"Pollster: Expected one of {pollsters}, got {name}")
        return name

    @validator("methode")
    def method_name(cls, name):
        if name not in methods:
            raise ValueError(f"Method: Expected one of {methods}, got {name}")
        return name

    @validator("population")
    def sample_name(cls, name):
        if name not in populations:
            raise ValueError(f"Sample type: Expected one of {populations}, got {name}")
        return name

    @validator("lien")
    def link_not_empty(cls, link):
        if link == "":
            raise ValueError("Expected a link, found none")
        return link

    @validator("premier_tour")
    def first_round(cls, first_round, values):
        hypotheses = set(values["hypotheses"].keys())
        hypotheses_1er_tour = set(first_round.keys())
        if len(hypotheses_1er_tour.difference(hypotheses)) != 0:
            raise ValueError(
                "The set of keys for the first round does not match the list of hypotheses:"
                f" expected {hypotheses}, got {hypotheses_1er_tour}"
            )
        return first_round


if __name__ == "__main__":
    # This will raise an error if the JSON is not properly formatted
    with open("presidentielles/sondages.json", "r") as data:
        sondages = json.load(data)

    for id, sondage in sondages.items():
        try:
            Poll(**sondage)
        except:
            print(id)
            raise

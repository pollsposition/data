import datetime
import json
from typing import List

from pydantic import BaseModel, ValidationError, validator


class Sondage(BaseModel):
    institut: str
    commanditaires: List[str]
    date_debut: datetime.date
    date_fin: datetime.date
    date_publication: datetime.date

    @validator('date_debut', 'date_fin', 'date_publication')
    def dates_ordering(cls, debut, fin, publication):
        if fin < debut:
            raise ValidationError("La date de fin du sondage doit être postérieur à celle du début")
        if publication < fin:
            raise ValidationError("La fin du sondage doit précéder la publication")


candidats = [
    "Nathalie Arthaud",
    "Philippe Poutou",
    "Fabien Roussel",
]

instituts = ["Harris interactive"]

compulsory_fields = ["premier_tour", "second_tour"]
optional_fields = ["reports_2017", "reports_premier_tour"]
fields = compulsory_fields + optional_fields


if __name__ == "__main__":
    # This will raise an error if the JSON is not properly formatted
    with open("sondages.json", "r") as data:
        sondages = json.load(data)

    for sondage in sondages.values():
        print(sondage)
        Sondage(**sondage)

    # Verifie que le % total sur la base des suffrages exprimés est égale
    # à 100
    # Vérifier le nom des candidats / config
    # Vérifier que le nom des hypothèses est cohérent à chaque fois
    # - toutes les hypotheses se retrouvent dans les intentions de vote
    # - les hypotheses des reports existent dans la liste d'hypotheses
    # Verifier la taille des matrices de report
    # - 2017 -> 2022
    # - depuis le premier tour
    # Verifier que valeurs au premier tour dans un range raisonnabele (<40)
    # Verifier que toutes les cles sont la, warning if extra (force schema)
    # vérifier date fin > date debut
    # verifier publication > debut
    # verifier range raisonnable (< today et > jan 2020)

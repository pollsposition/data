"""Clean and uniformize data given by the Ministère de l'Intérieur for the législatives.
"""
import re

import pandas as pd


dep_codes = {
    "ZA": "971",
    "ZB": "972",
    "ZC": "973",
    "ZD": "974",
    "ZM": "976",
    "ZN": "988",
    "ZP": "987",
    "ZS": "975",
    "ZW": "986",
    "ZX": "977_978",
    "ZZ": "fr_etranger",
    "ZT": "978",
    "ZY": "977",
}


def clean_elec(df):
    cols = df.columns
    keywords = [
        "code",
        "libellé",
        "nuance",
        "abstention",
        "blanc",
        "nuls",
        "nom",
        "voix",
        "commune",
        "département",
        "circonscription",
    ]
    new_cols = []
    for col in cols:
        if any(x in col.lower() for x in keywords) and "%" not in col:
            new_cols.append(col)
    df = df[new_cols]
    df.columns = [
        i.lower()
        .replace(" du ", "_")
        .replace(" de la ", "_")
        .replace("é", "e")
        .replace(" et ", "_")
        .strip()
        .replace(" ", "_")
        for i in df.columns
    ]

    if "code_departement" in df.columns:
        df["code_departement"] = df["code_departement"].replace(dep_codes)
        df["code_departement"] = (
            df["code_departement"].astype(str).str.pad(2, "left", "0")
        )

    if "libelle_commune" in df.columns:

        df.loc[
            (df["code_departement"].astype(str) == "977_978")
            & (df["code_commune"].astype(str) == "701"),
            ["code_departement", "libelle_departement"],
        ] = ["977", "Saint-Barthélémy"]
        df.loc[
            (df["code_departement"].astype(str) == "977_978")
            & (df["code_commune"].astype(str) == "801"),
            ["code_departement", "libelle_departement"],
        ] = ["978", "Saint-Martin"]

        df["code_commune"] = df["code_commune"].astype(str).str.pad(3, "left", "0")

    if "nom" in df.columns:
        name_present = True
    else:
        name_present = False

        if "code_b.vote" in df.columns:
            df = df.drop(columns=["libelle_commune"], axis=1)

    categories_candidats = list(
        pd.Series([i.split(".")[0] for i in df.columns if ".1" in i]).unique()
    )

    keywords = ["blanc", "nul", "abstention"]

    max_cand = [int(re.search(".(\d+)", i)[1]) for i in df.columns if "." in i]
    max_cand = max(max_cand) + 1

    n = max_cand
    for col in df.columns:
        if any(x in col.lower() for x in keywords):
            for cat in categories_candidats:

                is_name = len([i for i in categories_candidats if "nom" in i]) > 0

                if "voix" in cat:
                    df["voix." + str(n)] = df[col]

                elif ("nuance" in cat and is_name) or "prenom" in cat:
                    df[cat + "." + str(n)] = np.nan
                else:
                    df[cat + "." + str(n)] = col

            n += 1

    for cat in categories_candidats:
        for col in df.columns:
            if cat == col:
                df = df.rename(columns={col: col + ".0"})

    max_cand = [int(re.search(".(\d+)", i)[1]) for i in df.columns if "." in i]
    max_cand = max(max_cand) + 1

    temp_list = []
    for cand in range(max_cand):
        cols = [
            i for i in df.columns if "." in i and int(re.search(".(\d+)", i)[1]) == cand
        ]

        df_temp = df[cols].reset_index(drop=True)
        df_temp.columns = [i.split(".")[0] for i in df_temp.columns]
        temp_list.append(df_temp)

    geo_codes = [
        i
        for i in df.columns
        if (
            any(
                x in i.lower()
                for x in [
                    "code",
                    "libelle",
                    "departement",
                    "commune",
                    "circonscription",
                ]
            )
            and "nuance" not in i
            and "liste" not in i
        )
    ]
    len_cand = len(temp_list)
    codgeo = pd.concat([df[geo_codes] for i in range(len_cand)])
    temp_df = pd.concat(temp_list)
    df = pd.concat([codgeo, temp_df], axis=1)

    if "libelle_circonscription" in df.columns:
        df = df.drop(["libelle_circonscription"], axis=1)

    df.columns = [
        i.replace(" ", "_").replace("libelle_", "").replace("_candidat", "")
        for i in df.columns
    ]
    df = df[df["voix"].notna()]

    df = df.drop(columns={"etendu_liste"}, errors="ignore").rename(
        columns={"nom_tête_de_liste": "nom"}
    )

    return df

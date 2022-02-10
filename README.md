<p align="center">
  <img src="https://raw.githubusercontent.com/pollsposition/data/main/.github/logo.png" height=150>
</p>

**Sondages:** ![count2022](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/rlouf/51a78df74e3aeaa07fe17c83eb0608fb/raw/2022.json) 
![count2017](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/rlouf/51a78df74e3aeaa07fe17c83eb0608fb/raw/2017.json) 
![popularity](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/rlouf/51a78df74e3aeaa07fe17c83eb0608fb/raw/popularity.json)  
**Rejoignez-nous:** [![Discord](https://badgen.net/badge/icon/discord?icon=discord&label)](https://t.co/5imMnlOOY1?amp=1)

Ce dépôt compile les données utilisées par les modèles et les infographies de
[Pollsposition](https://twitter.com/pollsposition), et plus:

- Résultats des [élections présidentielles](https://raw.githubusercontent.com/pollsposition/data/main/resultats/presidentielles.json)
- Résultats des [élections européennes](https://raw.githubusercontent.com/pollsposition/data/main/resultats/europeennes.json)
- Résultats des [élections régionales](https://raw.githubusercontent.com/pollsposition/data/main/resultats/regionales.json)
- Sondages pour les présidentielles [2022](https://raw.githubusercontent.com/pollsposition/data/main/sondages/presidentielles_2022.json), [2017](https://raw.githubusercontent.com/pollsposition/data/main/sondages/presidentielles_2017.json)
- Sondages de [popularité des présidents](https://raw.githubusercontent.com/pollsposition/data/main/sondages/popularite.csv)

## Contribuer

Les contributions sont toujours les bienvenues !

### Présidentielles 2022

Le plus important en ce moment, c'est de rentrer les nombreux sondages des présidentielles 2022. 
Pour contribuer:

0. *Lire les spécifications* pour les [présidentielles](https://github.com/pollsposition/data/issues/35). Ne pas hésitez à commenter dans l'issue relative aux spécifications si quelque chose n'est pas clair ou s'il y a un problème.
1. Créez une nouvelle branche localement, de manière à pouvoir ouvrir une Pull Request (PR): `git branch -b my-branch-name`
2. Rentrez les sondages comme indiqué à l'étape 0
3. Faites tourner les scripts de validation, pour vous assurer que les données ne contiennent pas d'erreur:
``` python
pip install -r requirements.txt
pre-commit run --all
```
4. Une fois la validation faite, commitez vos changements avant de pusher:
```console
git add file-name.json
git commit -m "My changes summary"
git push
```
> NB: Si c'est la première fois que vous pushez sur cette branche, vous devrez le signaler au remote repo: `git push --set-upstream origin my-branch-name`. Les prochaines fois que vous pusherez sur cette branche, un simple `git push` suffira.

5. Ouvrez une PR sur ce repo.

Voici une version [vidéo de toutes ces étapes](https://drive.google.com/file/d/1q9wbM51n7pon_5V7SZla5KK6tXJGqZ38/view?usp=sharing), qui devrait accélérer votre capacité à contribuer.

### Reste

Hormis les sondages des présidentielles 2022, voici ce dont nous avons particulièrement besoin en ce moment:

- Report des électeurs de 2017 au premier tour 2022
- Sondages publiés moins d'un mois avant les présidentielles 2017 ([liste](https://github.com/pollsposition/data/issues/31))
- Sondages publiés moins d'un mois avant les européennes 2019 ([liste](https://github.com/pollsposition/data/issues/32))
- Sondages publiés moins d'un mois avant les régionales 2021

Les étapes sont les mêmes que pour les présidentielles 2022, avec l'addition des étapes suivantes:

1. Ouvrez une [issue](https://github.com/pollsposition/data/issues) pour signaler que vous ajoutez un jeu de données. Soyez précis dans la description du jeu de données ajouté;
2. Mieux, ouvrez une draft Pull Request dès que possible. Convertissez-la en Pull Request normale dès que le jeu de données est prêt à être ajouté;
3. Merci d'ajouter le lien vers la source de données dans la Pull Request pour faciliter la relecture.

De même, pensez bien à exécuter les scripts de validation.

## Nous contacter

Vous pouvez nous contacter sur [Twitter](https://twitter.com/pollsposition).

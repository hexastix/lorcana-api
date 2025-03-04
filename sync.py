import codecs
import json
import os
import pathlib
import urllib.request


def card_filename(card):
    parts = card["card_identifier"].replace("/", "_").split(" ")
    parts.reverse()
    return f"{'-'.join(parts)}.json"


def main():
    token_auth = codecs.decode(
        (
            b"42617369632062473979593246755953316863476b74636d56685a447046646b4a724d7a4a6"
            b"b5157746b4d7a6c756457743551564e494d4863325832464a63565a456348704a656e567253"
            b"306c7863446c424e58526c6232633552334a6b51314a484d55464261445653656e644d64455"
            b"26b596c527063326b3354484a5957446c325930466b535449345330393664773d3d"
        ),
        "hex",
    ).decode()
    token_request = urllib.request.Request(
        "https://sso.ravensburger.de/token",
        data=urllib.parse.urlencode({"grant_type": "client_credentials"}).encode(),
        headers={"Authorization": token_auth, "User-Agent": ""},
    )

    with urllib.request.urlopen(token_request) as f:
        token = json.loads(f.read().decode("utf-8"))

    catalog_dir = pathlib.Path(__file__).parent / "catalog"
    catalog_dir.mkdir(exist_ok=True)

    for lang in ("de", "en", "fr", "it"):
        print(f"Downloading {lang} catalog")

        catalog_auth = f"{token['token_type']} {token['access_token']}"
        catalog_request = urllib.request.Request(
            f"https://api.lorcana.ravensburger.com/v2/catalog/{lang}",
            headers={"Authorization": catalog_auth, "User-Agent": ""},
        )

        with urllib.request.urlopen(catalog_request) as f:
            contents = json.loads(f.read().decode("utf-8"))

        lang_dir = catalog_dir / lang
        lang_dir.mkdir(exist_ok=True)

        cards_dir = lang_dir / "cards"
        cards_dir.mkdir(exist_ok=True)

        for card_type in contents["cards"]:
            card_type_dir = cards_dir / card_type
            card_type_dir.mkdir(exist_ok=True)
            for card in contents["cards"][card_type]:
                if "abilities" in card:
                    card["abilities"].sort()

                with (card_type_dir / card_filename(card)).open("w") as out:
                    json.dump(card, out, indent=2, ensure_ascii=False)

        del contents["cards"]
        with (lang_dir / "catalog-no-cards.json").open("w") as out:
            json.dump(contents, out, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()

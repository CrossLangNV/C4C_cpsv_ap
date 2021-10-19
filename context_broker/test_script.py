import os

import requests

URL = "http://localhost:1026/ngsi-ld/v1/entities"

URL_V2 = "http://localhost:1026/v2/entities/"
EXAMPLE_ID = "Conceptbc83bfd3ad9b4690bbb1d3913420d320"
C4C = "c4c"
C4C_URL = "http://cefat4cities.crosslang.com/content/"
SKOS = "skos"
SKOS_URL = "http://www.w3.org/2004/02/skos/core#"

ID = f"{C4C}:{EXAMPLE_ID}"


def post_example():
    headers = {"Content-Type": "application/ld+json"}

    json_post = {
        "@id": ID,
        "@type": f"{SKOS}:Concept",
        "skos:prefLabel": [
            {
                "type": "Property",
                "value": "Finanzielles"
            }
        ],
        "@context": {
            f"{C4C}": C4C_URL,
            f"{SKOS}": SKOS_URL
        }
    }

    r = requests.post(URL,
                      headers=headers,
                      json=json_post)
    return r


def delete_example():
    r = requests.delete(os.path.join(URL_V2, ID))

    return r


def main():
    r = post_example()
    r.status_code
    r.content
    r.json()

    r = delete_example()
    r.status_code
    r.content
    r.json()

    print('Script has finished.')


if __name__ == '__main__':
    main()

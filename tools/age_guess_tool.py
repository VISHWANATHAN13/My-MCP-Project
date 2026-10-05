import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def guess_age_tool(name: str) -> dict:

    response = requests.get(
        "https://api.agify.io",
        params={"name": name},
        verify=False
    )

    data = response.json()

    return {
        "name": name,
        "predicted_age": data.get("age"),
        "sample_size": data.get("count")
    }
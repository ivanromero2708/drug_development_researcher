import requests


def images(setid):
    api_url = (
        f"https://dailymed.nlm.nih.gov/dailymed/services/v2/spls/{setid}/media.json"
    )
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        media_list = data.get("data", {}).get("media", [])

        if media_list:
            return media_list[1].get("url", "")
        else:
            return None

    except Exception as e:
        print(f"Error fetching image for setide {setid}: {e}")
        return None

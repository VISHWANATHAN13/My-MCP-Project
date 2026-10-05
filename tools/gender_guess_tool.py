import requests 

def guess_gender_tool(name : str) -> str:
    
    url = "https://api.genderize.io"
    
    response = requests.get(url, params={"name":name})
    
    response_json = response.json()
    
    gender = response_json.get("gender", "unknown")
    probability = response_json.get("probability", 0)

    return (
    f"Hey hi! Let me guess your gender.\n"
    f"My prediction is: {gender}\n"
    f"Confidence: {probability*100:.1f}%"
    )

if __name__ == "__main__":
    guess_gender_tool()
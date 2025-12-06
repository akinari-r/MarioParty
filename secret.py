import base64
import json
import requests
import streamlit as st

GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
REPO_OWNER = st.secrets["REPO_OWNER"]
REPO_NAME = st.secrets["REPO_NAME"]
FILE_PATH = st.secrets["FILE_PATH"]

API_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"

def load_games():
    r = requests.get(API_URL, headers={"Authorization": f"token {GITHUB_TOKEN}"})
    r.raise_for_status()
    data = r.json()
    content = base64.b64decode(data["content"]).decode("utf-8")
    sha = data["sha"]
    games = json.loads(content)
    return games, sha

def save_games(games, sha, message="Update games.json from Streamlit"):
    new_content = json.dumps(games, indent=2)
    b64_content = base64.b64encode(new_content.encode("utf-8")).decode("utf-8")

    payload = {
        "message": message,
        "content": b64_content,
        "sha": sha,
    }

    r = requests.put(
        API_URL,
        headers={"Authorization": f"token {GITHUB_TOKEN}"},
        json=payload,
    )
    r.raise_for_status()
    return r.json()

# Example Streamlit flow
games, sha = load_games()

st.write("Current games:", games)

if st.button("Add test game"):
    games.append({"name": "Test Game"})
    result = save_games(games, sha, "Add test game from Streamlit")
    st.success("games.json updated in GitHub")

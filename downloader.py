from os import makedirs
import requests
import json
from zipfile import ZipFile
import cloudscraper
import sys

if(len(sys.argv) != 2):
    print("Wrong arguments!\nUsage: python downloader.py [path=path/modpack/manifest.json | projectID=project id]")
    exit()

ID_URL = "https://addons-ecs.forgesvc.net/api/v2/addon/"
BASE_URL = "https://www.curseforge.com/minecraft/mc-mods/"

MANIFEST_PATH = sys.argv[1]

HEADER = { 'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36' }

PROJECTDATA = ''

if("projectID=" in MANIFEST_PATH):
    print("Using project id is currently not supported because of issues with cloudflare and ReCapthca v2"); exit()
    MANIFEST_PATH = str.replace(MANIFEST_PATH, 'projectID=', '')
    PROJECTDATA = requests.get(url=ID_URL + str(MANIFEST_PATH), headers=HEADER).json()
    defaultFile = PROJECTDATA["defaultFileId"]

    with open(PROJECTDATA["slug"] + ".zip", 'wb') as folder:
        scraper = cloudscraper.create_scraper()
        data = scraper.get(url="https://curseforge.com/minecraft/modpacks/" + PROJECTDATA["slug"] + "/download/" + str(defaultFile) + "/file", allow_redirects=True)
        folder.write(data.content)
    
    with ZipFile(PROJECTDATA["slug"] + ".zip", 'r') as zipped:
        zipped.extractall(PROJECTDATA["slug"])
    
    MANIFEST_PATH = PROJECTDATA["slug"] + "/manifest.json"
else:
    MANIFEST_PATH = str.replace(MANIFEST_PATH, 'path=', '') + "/manifest.json"

CWD = str.replace(MANIFEST_PATH, 'manifest.json', '')

with open(MANIFEST_PATH, 'r') as manifestfile:
    manifest = json.load(manifestfile)
    for file in manifest["files"]:
        id = file["projectID"]

        res = requests.get(url=ID_URL + str(id), headers=HEADER).json()

        makedirs(CWD + "overrides/mods/", exist_ok=True)
        makedirs(CWD + "overrides/resourcepacks/", exist_ok=True)

        download = requests.get(res["websiteUrl"] + "/download/" + str(file["fileID"]), allow_redirects=True)
        if("mc-mods" in res["websiteUrl"]):
            with open(CWD + "overrides/mods/" + str.replace(res["websiteUrl"], BASE_URL, '') + ".jar", 'wb') as modjar:
                modjar.write(download.content)
        elif("texture-packs" in res["websiteUrl"]):
            with open(CWD + "overrides/resourcepacks/" + str.replace(res["websiteUrl"], 'https://www.curseforge.com/minecraft/texture-packs/', '') + ".zip", 'wb') as texturepack:
                texturepack.write(download.content)

        print(res["websiteUrl"])
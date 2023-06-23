import json
import pandas as pd

with open("profs.json") as profsJSON:
    data = json.loads(profsJSON)
    df = pd.DataFrame()

from dotenv import load_dotenv
import json
import pandas as pd
import os
import psycopg2

load_dotenv()

with open("profs.json") as profsJSON:
    data = json.load(profsJSON)
    profs = data["data"]["search"]["teachers"]["edges"]

    # Select Data
    profNames, profIDs = [], []
    for prof in profs:
        profNames.append(prof["node"]["firstName"].strip() + " " + prof["node"]["lastName"].strip())
        profIDs.append(prof["node"]["legacyId"])
    
    # Create Dataframe
    df = pd.DataFrame({
        "professor_id" : profIDs,
        "professor_name" : profNames
        
    })

    # Write Dataframe to CSV
    with open("profCSV.csv", "w") as profCSV:
        df.to_csv(profCSV, sep="|", header=False,
                  index=False, lineterminator="\n")
    
    # Update DB
    # Load database connection data from env
    hostname = os.environ.get("DB_HOST_NAME")
    port = os.environ.get("DB_PORT")
    dbName = os.environ.get("DB_NAME")
    user = os.environ.get("DB_USER_NAME")
    password = os.environ.get("DB_PASSWORD")

    # Connect to DB
    conn = psycopg2.connect(
        host=hostname,
        port=port,
        database=dbName,
        user=user,
        password=password)

    # Verify connection
    curr = conn.cursor()
    curr.execute("SELECT version();")
    dbVersion = curr.fetchone()
    curr.close()
    print(f"\n{dbVersion[0]}\n")

    # Write to DB
    with open("profCSV.csv") as profCSV:
        curr = conn.cursor()
        curr.copy_from(profCSV, "Professor", sep="|")
        curr.close()

    # Close connection
    conn.commit()
    conn.close()

print("Complete!")


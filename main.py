# main.py

from nudger.ingestion import load_crm_data, load_email_threads
from nudger.reasoning import generate_nudges, write_nudges_to_file
from dotenv import load_dotenv
load_dotenv()

def main():
    # Here we're loading the data
    crm_data = load_crm_data("data/crm_events.csv")
    email_data = load_email_threads("data/emails.json")

    # We generate the nudges
    nudges = generate_nudges(crm_data, email_data)

    # And finally we write the nudges to a JSON file 
    write_nudges_to_file(nudges)

if __name__ == "__main__":
    main()

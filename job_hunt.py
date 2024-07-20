from ai import ask_ai
from db_operations import create_table, insert_job
from functions import save_to_json
from search_jobs import get_jobs

def job_hunt():
    # Obtenemos primeros 25 jobs
    jobs = get_jobs()

    for job in jobs["jobs"]:
        response = ask_ai(job['jobDescription'])
        job['relevant'] = response  # This adds a new key-value pair to the job dictionary

    for job in jobs["jobs"]:
        if job['relevant'].lower() == "no-relevante":
            continue

        # Try to insert the job into the database
        if insert_job(job):
            # Only print if the job was successfully inserted (i.e., it's new)
            print(job["title"] + " - " + job["companyName"])
            print(job["jobPostingUrl"])
            print("\n")

    # TODO. ver si guardamos o no quiza por parametro config.json podemos ver
    # save_to_json(jobs)
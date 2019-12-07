# model as a flask application

import numpy as np
from flask import Flask, request
from docusign_esign import ApiClient, EnvelopesApi, EnvelopeDefinition, Signer, SignHere, Tabs, Recipients, Document
import base64, os
import sqlite3

DEFAULT_PATH = os.path.join(os.path.dirname(__file__), 'database.sqlite3')

def db_connect(db_path=DEFAULT_PATH):
    con = sqlite3.connect(db_path)
    return con

def db_init():
    con = db_connect() # connect to the database
    cur = con.cursor() # instantiate a cursor obj

    sql = """
        CREATE TABLE envelops (
        id integer,
        name text,
        email text,
        envelopid text)"""
    cur.execute(sql)
    con.close()

def insert_envelop(con, loanid, name, email, envelopid):
    sql = """
        INSERT INTO envelops (id, name, email, envelopid)
        VALUES (?, ?,?,?)"""
    cur = con.cursor()
    cur.execute(sql, (loanid, name, email, envelopid))
    con.close()
    return cur.lastrowid


def send_document_for_signing(loan_id,signer_name, signer_email):
    APP_PATH = os.path.dirname(os.path.abspath(__file__))
    access_token='eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImtpZCI6IjY4MTg1ZmYxLTRlNTEtNGNlOS1hZjFjLTY4OTgxMjIwMzMxNyJ9.eyJUb2tlblR5cGUiOjUsIklzc3VlSW5zdGFudCI6MTU3NTY5MDA3NywiZXhwIjoxNTc1NzE4ODc3LCJVc2VySWQiOiI5YmM2MWNiZC1lMjA2LTQ4ZmYtOGE2OC1mZGM0ZGNlMWRhOWUiLCJzaXRlaWQiOjEsInNjcCI6WyJzaWduYXR1cmUiLCJjbGljay5tYW5hZ2UiLCJvcmdhbml6YXRpb25fcmVhZCIsImdyb3VwX3JlYWQiLCJwZXJtaXNzaW9uX3JlYWQiLCJ1c2VyX3JlYWQiLCJ1c2VyX3dyaXRlIiwiYWNjb3VudF9yZWFkIiwiZG9tYWluX3JlYWQiLCJpZGVudGl0eV9wcm92aWRlcl9yZWFkIiwiZHRyLnJvb21zLnJlYWQiLCJkdHIucm9vbXMud3JpdGUiLCJkdHIuZG9jdW1lbnRzLnJlYWQiLCJkdHIuZG9jdW1lbnRzLndyaXRlIiwiZHRyLnByb2ZpbGUucmVhZCIsImR0ci5wcm9maWxlLndyaXRlIiwiZHRyLmNvbXBhbnkucmVhZCIsImR0ci5jb21wYW55LndyaXRlIl0sImF1ZCI6ImYwZjI3ZjBlLTg1N2QtNGE3MS1hNGRhLTMyY2VjYWUzYTk3OCIsImF6cCI6ImYwZjI3ZjBlLTg1N2QtNGE3MS1hNGRhLTMyY2VjYWUzYTk3OCIsImlzcyI6Imh0dHBzOi8vYWNjb3VudC1kLmRvY3VzaWduLmNvbS8iLCJzdWIiOiI5YmM2MWNiZC1lMjA2LTQ4ZmYtOGE2OC1mZGM0ZGNlMWRhOWUiLCJhdXRoX3RpbWUiOjE1NzU2OTAwMDYsInB3aWQiOiIyZjA5MDc4Yy0yMzdiLTQ1ODMtYWI0MS1jOGM4NTg2MDllZmYifQ.wrcjGaFQTDAZ2NpYcT4i40hboJyc4s1NGNodhN0VEEWh-XuM5cmHJJQECEueGf3UA9taUjupFbI86JxMkpx9GqebBBNCT6UyHBq0GPbhy85nR2ktgYi6ZbcBJvxiLdWwd3IkrC0a-4GVAgqdp1pXVe79f4nPMmRzCvKMIsdlUUVcQCacPU7hgHNuZhwwPikQKO1WDEBCD8epv4qbil4_Er73It3-DNMNYa4yqaaQ64rb_xTOAwYZ4Ua3w6gW2Vot6zBIt-Gm1Go8GgDrzrAxES5W0e6DtQMUq48q9Kiba5YhdnZSXLC1yJIb2ma_p0j1NYW-Pu0WMjjK8Y_-4B6RpQ'
    account_id = '5959504'
    file_name_path = 'documents/approval_letter.pdf'
    base_path = 'https://demo.docusign.net/restapi'
    # Create the component objects for the envelope definition...
    with open(os.path.join(APP_PATH, file_name_path), "rb") as file:
        content_bytes = file.read()
    base64_file_content = base64.b64encode(content_bytes).decode('ascii')

    document = Document( # create the DocuSign document object
        document_base64 = base64_file_content,
        name = 'Approval Letter', # can be different from actual file name
        file_extension = 'pdf', # many different document types are accepted
        document_id = 1 # a label used to reference the doc
    )

    # Create the signer recipient model
    signer = Signer( # The signer
        email = signer_email, name = signer_name, recipient_id = "1", routing_order = "1")

    # Create a sign_here tab (field on the document)
    sign_here = SignHere( # DocuSign SignHere field/tab
        document_id = '1', page_number = '1', recipient_id = '1', tab_label = 'SignHereTab',
        x_position = '195', y_position = '147')

    # Add the tabs model (including the sign_here tab) to the signer
    signer.tabs = Tabs(sign_here_tabs = [sign_here]) # The Tabs object wants arrays of the different field/tab types

    # Next, create the top level envelope definition and populate it.
    envelope_definition = EnvelopeDefinition(
        email_subject = "Please sign this Approval Letter for your loan.",
        documents = [document], # The order in the docs array determines the order in the envelope
        recipients = Recipients(signers = [signer]), # The Recipients object wants arrays for each recipient type
        status = "sent" # requests that the envelope be created and sent.
    )

	# send envelope request
    api_client = ApiClient()
    api_client.host = base_path
    api_client.set_default_header("Authorization", "Bearer " + access_token)

    envelope_api = EnvelopesApi(api_client)
    results = envelope_api.create_envelope(account_id, envelope_definition=envelope_definition)
    return results


model = None
app = Flask(__name__)


@app.route('/')
def home_endpoint():
    return 'Hello World.'


@app.route('/test')
def home_test():
    return 'test'

@app.route('/sendesign', methods=['POST'])
def call_docusign():
    if request.method == 'POST':
        data = request.get_json()  # Get data posted as a json
        loan_id = data['loanid']
        signer_name = data['name']
        signer_email = data['email']
        print(signer_name, signer_email)
        results = send_document_for_signing(loan_id,signer_name, signer_email)
        print("\nEnvelope status: " + results.status + ". Envelope ID: " + results.envelope_id + "\n")
        dbres = insert_envelop(db_connect(),loan_id,signer_name, signer_email,str(results.envelope_id))
        print(dbres)
    return str(results.envelope_id)

if __name__ == '__main__':
    db_init()
    app.run(host='0.0.0.0', port=80)

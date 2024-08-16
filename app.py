import os
import csv
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse

from flask import Flask, render_template, request,  flash, session, logging, url_for, redirect, Response,  send_from_directory, jsonify, send_file
import psycopg2
import psycopg2.extras
from markupsafe import escape
from flask_sqlalchemy import SQLAlchemy
from wtforms import Form, StringField, TextAreaField, PasswordField, validators, SelectField, DecimalField, DateField, IntegerField, EmailField, TimeField, FileField,  SubmitField, FieldList, FormField, DateTimeField
from gevent.pywsgi import WSGIServer
from functools import wraps
from datetime import datetime, time, timedelta, date
from decimal import Decimal
from wtforms.validators import InputRequired,DataRequired
from werkzeug.utils import secure_filename
from psycopg2 import sql, extras
from flask_wtf import FlaskForm
import matplotlib.pyplot as plt
from collections import defaultdict
from io import BytesIO
import base64

from apscheduler.schedulers.background import BackgroundScheduler

import logging

from flask_babel import Babel

from babel.numbers import format_currency

from flask import make_response
import pandas as pd
from io import BytesIO
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer,Image,  PageBreak

import json
import re
import PyPDF2
import io

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

import plotly.graph_objs as go
import numpy as np
#from celery import Celery

app = Flask(__name__)


logging.basicConfig(level=logging.INFO)

@app.before_request
def before_request():
    # Código antes da requisição
    pass

@app.after_request
def after_request(response):
    # Código após a requisição
    return response

@app.teardown_request
def teardown_request(exception):
    if exception:
        app.logger.error(f"Erro: {exception}")
        usuario = session.get('username')
        #enviar_email('temoteo.tembe@cardinalt.com', 'Erro ao executar a transação', exception,usuario,'smatsinhe223@gmail.com' , 'adxr olgy gews evyo')
        return render_template('erro.html'), 500
    
# Tratamento global de exceções
@app.errorhandler(Exception)
def handle_exception(e):
    app.logger.error(f"Erro inesperado: {e}")
    usuario = session.get('username')
    #enviar_email('temoteo.tembe@cardinalt.com', 'Erro ao executar a transação', e,usuario,'smatsinhe223@gmail.com' , 'adxr olgy gews evyo')
    return render_template('erro.html'), 500   


SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

AUDIO_FOLDER = 'static/audios'
app.config['AUDIO_FOLDER'] = AUDIO_FOLDER
# Criação do diretório de uploads se não existir
if not os.path.exists(app.config['AUDIO_FOLDER']):
    os.makedirs(app.config['AUDIO_FOLDER'])


# Dummy survey data for demonstration
survey_questions = [
    'Question 1: How satisfied are you with our service?',
    'Question 2: Would you recommend our product to others?',
    'Question 3: How likely are you to purchase from us again?'
]

survey_responses = [
    {'question': 'Question 1', 'options': ['Very Satisfied', 'Satisfied', 'Neutral', 'Dissatisfied', 'Very Dissatisfied'], 'counts': [15, 25, 10, 5, 3]},
    {'question': 'Question 2', 'options': ['Yes', 'No'], 'counts': [30, 10]},
    {'question': 'Question 3', 'options': ['Very Likely', 'Likely', 'Neutral', 'Unlikely', 'Very Unlikely'], 'counts': [20, 15, 10, 8, 5]}
]




# Replace these values with your actual Twilio credentials
TWILIO_ACCOUNT_SID = "AC952933e9303a9c0021be3c0ce432caec"
TWILIO_AUTH_TOKEN = "5e14a5105201307f6d9a77af3fd81853"
TWILIO_PHONE_NUMBER = '+19495652625'


# URLs of audio files for each question
QUESTION_AUDIO_URLS = [
    "https://insightsap.com/audio/conjutiviteintro.mp3",
    
    "https://insightsap.com/audio/conjutivitep1.mp3",

    "https://insightsap.com/audio/conjutivitep2.mp3",

    "https://insightsap.com/audio/conjutiviteconc.mp3"]

CAMPANHA_AUDIO_URL = [
    
    "https://insightsap.com/audio/campanha_vacinacao_pt.mp3",

]

FORMACAO_AUDIO_URL = [
    
    "https://insightsap.com/audio/campanha_vacinacao_pt.mp3",

]

# Mock function to save survey responses to the database
def save_survey_response(phone_number, question_index, selected_option, campaign):
    # Connect to the database
    campaign ='campanha_32'

    conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')

    # Create a cursor object
    cur = conn.cursor()

    # Create survey_responses table if not exists
    cur.execute("""
        CREATE TABLE IF NOT EXISTS survey_responses (
            id SERIAL PRIMARY KEY,
            phone_number VARCHAR(20),
            question_index INT,
            selected_option INT,
            campaign VARCHAR(40),
            data timestamp without time zone   )
    """)
    
    # Insert survey response into the table
    cur.execute("""
        INSERT INTO survey_responses (phone_number, question_index, selected_option, campaign)
        VALUES (%s, %s, %s, %s)
    """, (phone_number, question_index, selected_option, campaign ))

    #print(campaign+"_"+"pergunta_"+question_index)    

    pergunta = "pergunta_"+str(question_index)

    ref = campaign+"_"+"pergunta_"+str(question_index)

    # Display ref
    cur.execute(f"SELECT opcao FROM {ref} where id='{selected_option}'")
    
    opcao = cur.fetchone()[0]

    # Insert survey response into the main table
    cur.execute(f"INSERT INTO {campaign} ({pergunta}) VALUES ('{opcao}')")

    # Update count_
    cur.execute(f"UPDATE {ref} SET count_=count_+1 where id='{selected_option}'")
    
   



    # Commit changes and close connection
    conn.commit()
    cur.close()
    conn.close()


def get_phone_numbers_from_database():
    conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')
   
    cursor = conn.cursor()
    cursor.execute("SELECT phone_number FROM phone_numbers_table")
    phone_numbers = [row[0] for row in cursor.fetchall()]
    conn.close()
    return phone_numbers

# Authentication function
def authenticate_twilio_request():
    if (request.values.get('AccountSid') != TWILIO_ACCOUNT_SID or
            request.values.get('AuthToken') != TWILIO_AUTH_TOKEN):
        return False
    return True

def criar_tabela():
    conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS respostas (
        nome TEXT PRIMARY KEY,
        pergunta1 TEXT,
        pergunta2 TEXT,
        pergunta3 TEXT,
        pergunta4 TEXT,
        pergunta5 TEXT,
        pergunta6 TEXT,
        pergunta7 TEXT,
        pergunta8 TEXT,
        pergunta9 TEXT,
        pergunta10 TEXT,
        pergunta11 TEXT,
        pergunta12 TEXT,
        pergunta13 TEXT,
        pergunta14 TEXT,
        pergunta15 TEXT
    )
    """)
    conn.commit()
    conn.close()

def obter_respostas():
    conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')
    cur = conn.cursor()
    cur.execute("SELECT * FROM respostas")
    respostas = cur.fetchall()
    conn.close()
    return respostas


# Display Ref
def display_ref(cursor,ref):
    
    
    # Display ref
    cursor.execute(f"SELECT ref FROM display_ref where id='{ref}'")
    print("teste:")
    print(f"SELECT ref FROM display_ref where id='{ref}'")
    #print(cursor.fetchone()[0])
    #conn.close()
    return cursor.fetchone()[0]


# Function to fetch survey title and column titles from the database
def get_survey_data(cursor, survey_name):
    # Fetch survey title
    cursor.execute("SELECT projecto FROM campanhas WHERE campanha_ref = %s", (survey_name,))
    survey_title = cursor.fetchone()[0]

    # Fetch column names starting with "pergunta"
    cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = %s AND column_name LIKE %s", (survey_name, 'pergunta%'))
    questions = [row[0] for row in cursor.fetchall()]

    questions2 = []
    for row in questions:
        ref=survey_name+"_"+row
        # Display ref
        cursor.execute(f"SELECT ref FROM display_ref where id='{ref}'")
        question = cursor.fetchone()
        
        

        # Query
        query = sql.SQL("SELECT opcao FROM {}").format(sql.Identifier(survey_name+"_"+row))

        # Execute query with parameterized value
        cursor.execute(query)


        #cursor.execute("SELECT opcao FROM %s_%s", (str(survey_name), row))
        options = cursor.fetchall()
        
        questions2.append({"question": question, "options": options})

    print(questions2)
    return survey_title, questions2


def create_table_for_column(cursor, table_name, column_name):
    # Create a new table with the name "actual_campaign_column_name"
    new_table_name = str(table_name+'_'+column_name)
    query = sql.SQL("""
        CREATE TABLE {} (
            id SERIAL PRIMARY KEY,
            orgid VARCHAR(50),
            opcao VARCHAR(100) DEFAULT 'Opcao de resposta',
            count_ Integer DEFAULT 0                      
        )
    """).format(sql.Identifier(new_table_name))
    print('dentro')
    cursor.execute(query)


def list_columns(cursor, table_name, column_prefix):
    try:
        # Get a list of column names for the specified table and column name prefix
        cursor.execute(
            "SELECT column_name FROM information_schema.columns WHERE table_name = %s AND column_name LIKE %s",
            (table_name, f'{column_prefix}%')
        )
        columns_list = [row[0] for row in cursor.fetchall()]

        print(columns_list)

        return columns_list

    except Exception as e:
        print(f"Error in list_columns: {e}")
        return None


def create_table(cursor, new_table_name):
    # Create a new table with an auto-incrementing ID column
    # Create a new table with specified columns and default values
    query = sql.SQL("""
        CREATE TABLE {} (
            id_campanha SERIAL PRIMARY KEY,
            orgid VARCHAR(50),
            t_name VARCHAR(50) DEFAULT %s,
            contact VARCHAR(50),
            data_hora TIMESTAMP DEFAULT NOW()                
        )
    """).format(sql.Identifier(new_table_name))
    
    default_value = new_table_name  # Example default value based on table name

    cursor.execute(query, (default_value,))


def add_column(cursor, table_name, column_name, column_type):
    # Add a new column to the specified table
    query = sql.SQL("ALTER TABLE {} ADD COLUMN {} {}").format(
        sql.Identifier(table_name),
        sql.Identifier(column_name),
        sql.SQL(column_type)
    )
    print(query) 
    cursor.execute(query)    
    

def get_next_column_name(cursor, base_column_name,table_name):
    # Get a list of existing column names
    cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = %s", (table_name,))
    existing_columns = [row[0] for row in cursor.fetchall()]

    # Find the next available column name by incrementing the suffix
    suffix = 1
    while f"{base_column_name}_{suffix}" in existing_columns:
        suffix += 1

    return f"{base_column_name}_{suffix}"


def table_exists(cursor, table_name):
    # Check if the specified table exists
    query = sql.SQL("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = %s)")
    cursor.execute(query, (table_name,))
    exists = cursor.fetchone()[0]

    return exists

def get_next_table_name(cursor, base_table_name):
    # Find the next available table name by incrementing the suffix
    suffix = 1
    while table_exists(cursor, f"{base_table_name}_{suffix}"):
        suffix += 1

    return f"{base_table_name}_{suffix}"


def get_gmail_service():
    with open('templates/client_secret_556945350236-q43vh7j4jefgc876hfnm7oag9kk6hc6f.apps.googleusercontent.com.json', 'r') as f:
        client_config = json.load(f)

    flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
    creds = flow.run_local_server(port=0)
    service = build('gmail', 'v1', credentials=creds)
    return service

def extract_text_and_numbers_from_pdf(attachment_data):
    try:
        # Create a PDF file reader object
        # Use pdfminer to extract text from the PDF
        extracted_text = io.BytesIO(attachment_data)

        # Use regex to find all text and numbers
        extracted_content = ' '.join(re.findall(r'\b\w+\b', extracted_text))

        return extracted_content
    except Exception as e:
        print(f"Error extracting content from PDF: {e}")
        return None

def read_specific_email(subject):
    service = get_gmail_service()

    results = service.users().messages().list(userId='me', q=f'subject:{subject}').execute()
    messages = results.get('messages', [])

    all_texts = []

    if not messages:
        flash(f'No emails found with subject: {subject}', 'warning')
        return all_texts

    for message in messages:
        msg = service.users().messages().get(userId='me', id=message['id']).execute()

        if 'parts' in msg['payload']:
            for part in msg['payload']['parts']:
                # Check for different keys in the part structure
                body = part.get('body', {})
                if 'data' in body:
                    attachment_data = base64.urlsafe_b64decode(body['data'])
                elif 'attachmentId' in body:
                    attachment = service.users().messages().attachments().get(
                        userId='me',
                        messageId=message['id'],
                        id=body['attachmentId']
                    ).execute()
                    attachment_data = base64.urlsafe_b64decode(attachment['data'])
                else:
                    continue

                extracted_text = extract_text_and_numbers_from_pdf(attachment_data)

                if extracted_text:
                    all_texts.append(extracted_text)

    return all_texts

@app.route('/phone_numbers', methods=['GET', 'POST'])
def phone_numbers():
    all_texts = []

    if request.method == 'POST':
        subject_to_search = request.form['subject']
        all_texts = read_specific_email(subject_to_search)

        if not all_texts:
            flash(f'No emails found with subject: {subject_to_search} or no PDF attachments with text', 'warning')

    return render_template('phone_numbers.html', all_texts=all_texts)






# A4 size in points (1 inch = 25.4 mm = 72 points)
A4_WIDTH, A4_HEIGHT = letter


# Function to retrieve the last 10 transactions with balances and evidence links
def get_last_10_transactions():
    conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')
    cur = conn.cursor()
    cur.execute("SELECT tipo, valor, saldo, evidencia FROM transacoes ORDER BY id DESC LIMIT 10")
    rows = cur.fetchall()
    cur.close()
    return rows

def calculate_total(tipo):
    conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')
    cur = conn.cursor()
    cur.execute("SELECT SUM(valor) FROM transacoes WHERE tipo = %s", (tipo,))
    total = cur.fetchone()[0] or 0.0
    cur.close()
    return total



# Function to create the 'transacoes' table if it doesn't exist
def create_transactions_table():
    conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS transacoes (
            id SERIAL PRIMARY KEY,
            tipo VARCHAR(10) NOT NULL,
            valor NUMERIC(10, 2) NOT NULL,
            saldo NUMERIC(10, 2),
            evidencia TEXT,
            data_hora TIMESTAMP DEFAULT NOW()    
        )
    """)
    conn.commit()
    cur.close()

# Function to calculate the balance
def calculate_balance():
    conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')
    total_entradas = calculate_total('Entrada')
    total_saidas = calculate_total('Saída')
    saldo = Decimal(total_entradas) - Decimal(total_saidas)

    return saldo


# Function to retrieve the last 10 transactions with balances and evidence links
def get_last_10_transactions():
    
    conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')

    
    cur = conn.cursor()
    cur.execute("SELECT tipo, valor, saldo, evidencia, data_hora FROM transacoes ORDER BY id DESC LIMIT 10")
    rows = cur.fetchall()
    cur.close()
    return rows

# Function to format values in MZN using pt_PT
def format_currency_mzn(value):
    if value is None:
        return "Invalid Amount"
    
    # Ensure that the value is a valid numeric string with the appropriate decimal separator
    try:
        decimal_value = Decimal(str(value))
        return format_currency(decimal_value, 'MZN', locale='pt_PT')
    except (ValueError, Decimal.InvalidOperation):
        return "Invalid Amount"


def initialize_sales_data():
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')

        cursor = conn.cursor()

        # Check if data for today already exists
        today = datetime.now().date()
        query = "SELECT COUNT(*) FROM sales_data WHERE date = 'CURRENT_DATE';"
        cursor.execute(query)
        count = cursor.fetchone()[0]

        if count == 0:
            # Insert data for "Tomas" and "Jennifer"
            agents_data = [
                (today, "Tomas", 30, 15, 2),
                (today, "Jennifer", 25, 10, 1)
            ]
            insert_query = "INSERT INTO sales_data (date, sales_agent, calls_contacts, new_customers, meetings_booked) VALUES (%s, %s, %s, %s, %s);"
            cursor.executemany(insert_query, agents_data)

            conn.commit()

        # Close the cursor and connection
        cursor.close()
        conn.close()

    except Exception as e:
        print("Error initializing sales data:", e)



dia_actual= datetime.now()
data1=dia_actual.strftime("%Y/%m/%d, %H:%M:%S")


conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')

# Create cursor
cursor = conn.cursor()

create_table_query = '''
    CREATE TABLE IF NOT EXISTS contacts (
        id SERIAL PRIMARY KEY,
        name VARCHAR(50) NOT NULL,
        location VARCHAR(100),
        phone VARCHAR(15),
        gender VARCHAR(10),
        org_id VARCHAR(10)
    );
    '''

cursor.execute(create_table_query)

conn.commit()
    
cmd = 'SELECT * from cliente ORDER by id_cliente'
        
cursor.execute(cmd)
    
dados=cursor.fetchall()

dados_cliente=[]
dados2_cliente=[]
dados3_cliente=[]
dados_usuarios=[]

for x in dados:
    dados_cliente.append((x[1],x[1]))
    dados2_cliente.append((x[2],x[2]))

cmd = 'SELECT * from usuarios'

cursor.execute(cmd)

dados=cursor.fetchall()


for y in dados:
    dados_usuarios.append((y[1],y[1]))


cmd = 'SELECT nome from cliente_vendas order by nome'
cursor.execute(cmd)  

dados=cursor.fetchall()

for z in dados:
    dados3_cliente.append((z[0],z[0]))

#selecionario usuarios para tabela comprovativo de pagamento
usu = 'SELECT * FROM usuarios ORDER BY id_usuarios'
     
cursor.execute(usu)

dados1=cursor.fetchall()

dados1_usuarios=[]
dados2_usuarios=[]



for y in dados1:
   dados1_usuarios.append((y[1],y[1]))


# Close connection
conn.close()

def relatorio_obra_db_connection():
    connection_string = "postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy"
    return psycopg2.connect(connection_string)

def create_table_if_not_exists(connection):
    cursor = connection.cursor()
    
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS tasks (
        id SERIAL PRIMARY KEY,
        title VARCHAR(100) NOT NULL,
        due_date DATE NOT NULL,
        accepted_time TIMESTAMP,
        completed_time TIMESTAMP,
        responsible VARCHAR(100),
        completed BOOLEAN DEFAULT FALSE
    );
    '''
    
    cursor.execute(create_table_query)

    connection.commit()


    


    cursor.close()

# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Não autorizado, faça login', 'danger')
            return redirect(url_for('login'))
    return wrap

class ItemForm(FlaskForm):
    description = TextAreaField('Item Description')
    quantity = StringField('Quantity')
    price = StringField('Price')

class AudioForm(FlaskForm):
    organization = SelectField('Idioma', choices=[], validators=[DataRequired()])
    project = StringField('Project', validators=[DataRequired()])
    audio_file = FileField('Audio File', validators=[DataRequired()])
    submit = SubmitField('Upload')    

@app.before_request
def before_request():
    choices = request_languge()
    AudioForm.organization.kwargs['choices'] = choices

def request_languge():
    org_id = session.get('last_org')
    conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM org_linguas where org_id = '{org_id}'")
    organizations = cur.fetchall()
    cur.close()
    conn.close()
    choices = [(org[2], org[1]) for org in organizations]
    return choices

class ProformaInvoiceForm(FlaskForm):
    invoice_number = StringField('Invoice Number')
    date = DateField('Date')
    customer_name = StringField('Customer Name')

    items = FieldList(FormField(ItemForm), min_entries=1)
    add_item = SubmitField('Add Item')
    generate_invoice = SubmitField('Generate Invoice')


@app.route('/add_contact', methods=['GET', 'POST'])
@is_logged_in
def add_contact():
    # Obtém o ID da organização da sessão do usuário
    org_id = session['last_org']
    
    try:
        # Conectar ao banco de dados PostgreSQL
        conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')
        cursor = conn.cursor()
        
        # Recuperar todos os contatos associados à organização
        cursor.execute(f"SELECT * FROM contacts JOIN contact_org ON contacts.id = contact_org.id_cont WHERE contact_org.org_id = '{org_id}';")
        contacts = cursor.fetchall()
        
        # Recuperar todos os grupos disponíveis
        cursor.execute("SELECT * FROM grupo;")
        grupo = cursor.fetchall()
        
        # Fechar a conexão com o banco de dados
        conn.close()
    
    except psycopg2.Error as e:
        # Em caso de erro, exibir uma página de erro
        error_msg = f"Erro ao fazer a transação: {e}"
        return render_template('erro.html', error=error_msg)
    
    # Verifica se o saldo é suficiente para prosseguir
    if session['saldo'] == '00.0':
        agent = 'Saldo insuficiente, Recarregue a sua conta!'
        return render_template('add_contat.html', contacts=contacts, grupo=grupo, agent=agent)
    
    if request.method == 'POST':
        file = request.files['file']
        
        if file:
            # Se um arquivo for enviado, processa o arquivo Excel
            df = pd.read_excel(file)
            conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')
            cur = conn.cursor()
            
            # Iterar sobre as linhas do DataFrame e inserir os dados no banco de dados
            for index, row in df.iterrows():
                valores = row.to_json()  # Converte a linha para formato JSON
                insert_query = "INSERT INTO contacts (dados_contactos) VALUES (%s) RETURNING id;"
                try:
                    cur.execute(insert_query, [valores])
                    inserted_id = cur.fetchone()[0]
                    conn.commit()
                    print(f"Inserido ID: {inserted_id}")
                    cur.execute("INSERT INTO contact_org VALUES (%s, %s);", (inserted_id, org_id))
                    conn.commit()
                except Exception as e:
                    print(f"Erro ao inserir a linha {index}: {e}")
            
            conn.close()
            return redirect(url_for('add_contact'))
        
        else:
            # Se não for um arquivo, trata a atualização de contatos
            grupo_id = request.form['grupo']
            conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')
            cursor = conn.cursor()
            
            # Recuperar o primeiro contato da organização
            cursor.execute(f"SELECT * FROM contacts JOIN contact_org ON contacts.id = contact_org.id_cont WHERE contact_org.org_id = '{org_id}' LIMIT 1;")
            contactos = cursor.fetchone()
            conn.close()
            
            dados = {}
            for contact in contactos[6]:  
                field = contact
                dados[field] = []

                if field:
                    # Atualiza o campo específico com o valor do formulário
                    field_to_update = request.form[field]
                    print(field_to_update)
                    dados[field] = field_to_update
            
            try:
                # Conectar ao banco de dados para verificação e inserção
                conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')
                cursor = conn.cursor()
                
                # Verifica se o contato já existe
                for field, values in dados.items():
                    cursor.execute(f"SELECT * FROM contacts WHERE phone = '{values[-1]}';")
                    cont = cursor.fetchone()
                    
                    # Verifica se o contato já existe na organização
                    cursor.execute(f"SELECT * FROM contacts JOIN contact_org ON contacts.id = contact_org.id_cont WHERE contacts.phone = '{values[-1]}' AND contact_org.org_id = '{org_id}';")
                    contactos = cursor.fetchone()
            
            except psycopg2.Error as e:
                # Em caso de erro, exibir uma página de erro
                error_msg = f"Erro ao fazer a transação: {e}"
                return render_template('erro.html', error=error_msg)
            
            # Verifica se o contato já existe na organização e exibe mensagem de erro se necessário
            if contactos:
                erro = 'Este número de telefone já está registrado.'
                return render_template('add_contat.html', contacts=contacts, grupo=grupo, erro=erro)
            else:
                # Insere um novo contato na base de dados
                insert_query1 = '''
                    INSERT INTO contacts (dados_contactos)
                    VALUES (%s) RETURNING id;
                '''
                insert_query2 = '''
                    INSERT INTO contact_org (id_cont, org_id)
                    VALUES (%s, %s);
                '''
                
                if not cont:
                    cursor.execute(insert_query1, (extras.Json(dados),))
                    contact_id = cursor.fetchone()[0]
                    conn.commit()
                else:
                    contact_id = cont[0]
                    cursor.execute(insert_query2, (contact_id, org_id))
                
                conn.commit()
                
                # Atualizar a lista de contatos após inserção
                cursor.execute(f"SELECT * FROM contacts WHERE id IN (SELECT id_cont FROM contact_org WHERE org_id = '{org_id}');")
                contacts = cursor.fetchall()
                conn.close()
                return render_template('add_contat.html', contacts=contacts, grupo=grupo)

    # Renderiza o template de contatos e grupos para GET requests e quando o POST não é um arquivo
    return render_template('add_contat.html', contacts=contacts, grupo=grupo)
  

# essa funcao deleta uma lista de contactos referentes as linhas selecionadas na tabela
@app.route('/delete', methods=['POST'])
def delete():
    delete_ids = request.form.getlist('delete_ids')
    if delete_ids:
        conn = relatorio_obra_db_connection()
        cursor = conn.cursor()
        delete_ids_str = ', '.join(cursor.mogrify("%s", (id,)).decode('utf-8') for id in delete_ids)
        cursor.execute(f"DELETE FROM contacts WHERE id IN ({delete_ids_str})")
        conn.commit()
        cursor.close()
        conn.close()
    return redirect(url_for('add_contact'))



# funcao para inserir dados pelo exccel
@app.route('/grupos', methods=['POST','GET'])
def grupos():
    org_id = session['last_org']
    

    if request.method == 'POST':
    # Ler o arquivo Excel enviado
      grupo = request.form['grupo']
      categoria = request.form['categoria']
      referencia = request.form['referencia']
      
      conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')
      cur = conn.cursor()
      # Iterar sobre as linhas do DataFrame e inserir os dados no banco de dados
      cur.execute(f"SELECT * FROM contacts join contact_org on contacts.id = contact_org.id_cont where  contact_org.org_id = '{org_id}';")
      contactos = cur.fetchall()
      dados = {}

      for contact in contactos:
          for key, value in contact[6].items():  
            # Pegando o nome do campo a ser atualizado
            print(key)
            dados[key] = [] 
            grupo_id = 3 
            # verificando se a coluna e a valor correspondem com a categoria e a referencia dada
            if key == categoria and value == referencia:
               cur.execute(f"SELECT * FROM grupo WHERE nome_grupo = '{grupo}';")
               grupos = cur.fetchone()
               insert_grupo = f"INSERT INTO grupo (nome_grupo) VALUES ('{grupo}') RETURNING id;"
                
               print(grupo_id)
               if not grupos: 
                cur.execute(insert_grupo)
                grupo_id = cur.fetchone()[0]
                conn.commit
               
               else:
                grupo_id = grupos[0]

               print(grupo_id)
   
               # Atualizando o campo específico com o valor do formulário
               insert_query = f"UPDATE contact_org SET grupo_id = {grupo_id} WHERE id_cont = {contact[0]};"
               cur.execute(insert_query) 
               conn.commit()
      conn.close()
      redirect(url_for('grupos'))
               

    conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')
    cursor = conn.cursor()
    # Iterar sobre as linhas do DataFrame e inserir os dados no banco de dados
    cursor.execute(f"SELECT * FROM contacts join contact_org on contacts.id = contact_org.id_cont where  contact_org.org_id = '{org_id}' LIMIT 1;")
    contacto = cursor.fetchone()
    
    conn.close()           
    print(contacto)
    return render_template('grupos.html', contact=contacto)


# funcao para editar dados do contacto
@app.route('/edit_contact/<int:id>', methods=['GET','POST'])
@is_logged_in
def edit_contact(id):
    org_id = session['last_org']
    conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')
    cur = conn.cursor() 
    cur.execute(f"SELECT * FROM contacts where id = {id};")
    contactos = cur.fetchone() 
    dados = {}
    for contact in contactos[6]:  
             # Pegando o nome do campo a ser atualizado
             field = contact
             print(field)
             dados[field] = []

             if field:
                # Atualizando o campo específico com o valor do formulário
                field_to_update = request.form[field]
                print(field_to_update)
               
                dados[field] = field_to_update
        
    cur.execute("UPDATE contacts SET dados_contactos = %s WHERE id = %s ;",(extras.Json(dados), id,))
    conn.commit()
    cur.close()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM contacts join contact_org on contacts.id = contact_org.id_cont where contact_org.org_id = '{org_id}';")
    contacts = cur.fetchall() 
    cur.execute("SELECT * FROM grupo ;")
    grupo = cur.fetchall()
    conn.close()
    sucesso = "Contacto Atualizado com sucesso"
    return render_template('add_contat.html', contacts=contacts,grupo = grupo,sucesso = sucesso)
   


@app.route('/delete_contact/<int:id>', methods=['GET','POST'])
@is_logged_in
def delete_contact(id):
   org_id = session['last_org']
   try:
    conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')
    cur = conn.cursor()  
    cur.execute("DELETE FROM contacts WHERE id = %s",(id,))
    conn.commit()
    cur.close()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM contacts join contact_org on contacts.id = contact_org.id_cont where contact_org.org_id = '{org_id}';")
    contacts = cur.fetchall() 
    cur.execute("SELECT * FROM grupo ;")
    grupo = cur.fetchall()
    conn.close()
    sucesso = "Contacto Removido com sucesso"
    return render_template('add_contat.html', contacts=contacts,grupo = grupo,sucesso = sucesso)
   except psycopg2.Error as e:
        error_msg = f"Erro ao fazer a transação: {e}"
        return render_template('erro.html', error=error_msg) 


@app.route('/contact_info/<int:id>', methods=['GET','POST'])
@is_logged_in
def contact_info(id):
   org_id = session['last_org']
   try:
    conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')
    cur = conn.cursor()  
    query = f"""
        SELECT *
        FROM contacts c
        JOIN contact_org r ON c.id = r.id_cont
        JOIN grupo g ON r.grupo_id = g.id
        WHERE c.id = {id};
         """
    cur.execute(query)
    contacts= cur.fetchone() 
    cur.execute(f"select * from grupo where id in (select grupo_id from contact_org where org_id = '{org_id}');")
    grupos= cur.fetchall() 
    cur.execute(f"select * from grupo where id in (select grupo_id from contact_org where id_cont = {id});")
    grupo= cur.fetchall()
    conn.close()
    print(contacts)
    return render_template('contact_info.html', contact=contacts, grupo=grupo, grupos=grupos)
   except psycopg2.Error as e:
        error_msg = f"Erro ao fazer a transação: {e}"
        return render_template('erro.html', error=error_msg) 

@app.route('/add_group/<int:id>', methods=['GET','POST'])
@is_logged_in
def add_group(id):
   grupo_id = request.form['group']
   org_id = session['last_org']
   try:
    conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')
    cursor = conn.cursor()
    insert_query = f"insert into contact_org values( {id},'{org_id}',{grupo_id});"

    cursor.execute(insert_query)
    conn.commit()
    conn.close()
    return redirect(url_for('contact_info',id=int(id)))
   except psycopg2.Error as e:
        error_msg = f"Erro ao fazer a transação: {e}"
        return render_template('erro.html', error=error_msg) 
   
@app.route('/remove_group/<int:id>', methods=['GET','POST'])
def remove_group(id):
   try:
    conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM contact_group WHERE id_cont=%s;', (id,))
    conn.commit()
    conn.close()
    sucesso = "Cliente Removido com sucesso"
    return redirect(url_for('contact_info',id=int(id)))
   except psycopg2.Error as e:
        error_msg = f"Erro ao fazer a transação: {e}"
        return render_template('erro.html', error=error_msg)    


# Proforma Invoice

@app.route('/proforma_invoice',methods=['GET', 'POST'])
def proforma_invoice():
     form = ProformaInvoiceForm()

     if request.method == 'POST' and form.validate_on_submit():
        invoice_data = {
            'invoice_number': form.invoice_number.data,
            'date': form.date.data,
            'customer_name': form.customer_name.data,
            'items': [
                {
                    'description': item['description'],
                    'quantity': item['quantity'],
                    'price': item['price'],
                }
                for item in form.items.data
            ],
        }

        pdf_content = generate_pdf(invoice_data)

        response = make_response(pdf_content)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'inline; filename=proforma_invoice.pdf'

        return response

     return render_template('proforma_invoice.html', form=form)


@app.route('/download')
def download():
    invoice_data = {
        'invoice_number': 'PRO-123',
        'date': '2023-10-10',
        'customer_name': 'John Doe',
        # Add more data as needed
    }

    pdf_content = generate_pdf(invoice_data)

    response = make_response(pdf_content)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=proforma_invoice.pdf'

    return response

def generate_pdf(invoice_data):
    buffer = BytesIO()

    # Create the PDF object, using BytesIO as its file
    pdf = SimpleDocTemplate(buffer, pagesize=letter)

    # Styles and content
    styles = getSampleStyleSheet()
    heading_style = ParagraphStyle(
        'Heading1',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=16,
        spaceAfter=12,
        textColor=colors.darkblue,
    )

    normal_style = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        spaceAfter=6,
    )

    # Content with table
    content = [
        Paragraph("Proforma Invoice", heading_style),
        Spacer(1, 12),
        Paragraph(f"Invoice Number: {invoice_data['invoice_number']}", normal_style),
        Paragraph(f"Date: {invoice_data['date']}", normal_style),
        Paragraph(f"Customer: {invoice_data['customer_name']}", normal_style),
        Table(
            data=[
                ['Item Description', 'Quantity', 'Price'],
                *[[
                    item['description'],
                    item['quantity'],
                    item['price'],
                ] for item in invoice_data['items']]
            ],
            style=[
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ],
        ),
    ]

    # Build PDF
    pdf.build(content)

    # Move the buffer's cursor to the beginning
    buffer.seek(0)

    return buffer.read()

@app.route('/tasks')
@is_logged_in

def tasks():
    
    connection = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')

    create_table_if_not_exists(connection)
    
    cursor = connection.cursor()
    
    query = "SELECT "+'"'+ "id"+'"'+" ,title, due_date, accepted_time, completed_time, responsible, completed, accepted FROM tasks where due_date = Current_date OR completed = false OR completed_time = Current_date ORDER BY responsible;"
    
    
   
    cursor.execute(query)
    tasks = cursor.fetchall() 

    # Get today's date
    today = datetime.now().date()

    cursor.execute('SELECT privileges FROM usuarios WHERE "user" = %s', (session['username'],))
    user = cursor.fetchone()
    session['privileges'] = user[0].split(',')
    print(session['privileges'])
    
    return render_template('tasks.html', tasks=tasks, today=today)

@app.route('/add_task', methods=['POST'])
@is_logged_in

def add_task():
    task_title = request.form.get('task_title')
    due_date = request.form.get('due_date')
    selected_agent = request.form.get('agent')

    connection = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')

    cursor = connection.cursor()

    insert_query = sql.SQL("INSERT INTO tasks (title, due_date, responsible) VALUES ({}, {}, {})")
    cursor.execute(insert_query.format(sql.Literal(task_title), sql.Literal(due_date), sql.Literal(selected_agent)))

    connection.commit()
    cursor.close()
    connection.close()

    return redirect(url_for('tasks'))


@app.route('/complete_task/<int:task_id>')
@is_logged_in

def complete_task(task_id):
    connection = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')

    cursor = connection.cursor()


    update_query = str("UPDATE tasks SET completed = TRUE, completed_time = now() WHERE "+'"'+ "id"+'"'+" = " + str(task_id))
    cursor.execute(update_query)
    
    print(update_query)

    connection.commit()
    cursor.close()
    connection.close()

    return redirect(url_for('tasks'))

@app.route('/accept_task/<int:task_id>')
@is_logged_in
def accept_task(task_id):
    connection = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')

    cursor = connection.cursor()

    #responsible = session['username']

    update_query = sql.SQL('UPDATE tasks SET accepted_time = now(), accepted = true WHERE "id" = {}').format(sql.Literal(task_id))
    cursor.execute(update_query)
    
    connection.commit()
    cursor.close()
    connection.close()

    return redirect(url_for('tasks'))






@app.route('/sales')
@is_logged_in
def sales():

    initialize_sales_data()

    # Connect to PostgreSQL
    conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')
    cursor = conn.cursor()

    # Fetch data from the database
    query = "SELECT * FROM sales_data;"
    cursor.execute(query)
    data = cursor.fetchall()

    # Close the cursor and connection
    cursor.close()
    conn.close()

    return render_template('sales.html', data=data)


@app.route('/plot')
@is_logged_in
def plot_graph():
    # Connect to PostgreSQL
    conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')
    cursor = conn.cursor()

    # Fetch data from the database
    query = "SELECT sales_agent, calls_contacts, new_customers, meetings_booked FROM sales_data;"
    cursor.execute(query)
    data = cursor.fetchall()

    # Close the cursor and connection
    cursor.close()
    conn.close()

    # Extract data for plotting
    agents = [row[0] for row in data]
    calls = [row[1] for row in data]
    customers = [row[2] for row in data]
    meetings = [row[3] for row in data]

    # Create a bar plot
    plt.figure(figsize=(10, 6))
    plt.bar(agents, calls, label='Calls/Contacts')
    plt.bar(agents, customers, bottom=calls, label='New Customers')
    plt.bar(agents, meetings, bottom=[i + j for i, j in zip(calls, customers)], label='Meetings Booked')
    plt.xlabel('Sales Agents')
    plt.ylabel('Metrics')
    plt.title('Sales Metrics by Agent')
    plt.legend()

    # Convert plot to image
    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()

    return render_template('plot.html', plot_url=plot_url)



def send_sms(msg,dst,sender_id):
  
  print(sender_id)
  account_sid = "AC952933e9303a9c0021be3c0ce432caec"
  auth_token = "5e14a5105201307f6d9a77af3fd81853"

  client = Client(account_sid, auth_token)
  message = client.messages.create(body=msg,from_=sender_id,to=dst)
  print(sender_id)
  
  print('SMS Sent:'+msg+'para o numero:'+dst+' sender_id:'+sender_id) 
 
  conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')

  cursor= conn.cursor()
  cursor.execute("""INSERT INTO sms("from",dst,body,account_sid,auth_token,data) VALUES ('%s','%s','%s','%s','%s','%s')""" %(sender_id, dst, msg, account_sid, auth_token, data1))
  
  conn.commit()
  return message.sid

@app.route('/saldo', methods=['GET', 'POST'])
@is_logged_in
def saldo():
    create_transactions_table()  # Create the 'transacoes' table if it doesn't exist
    saldo = calculate_balance()
    saldo_formatted = format_currency_mzn(saldo)

    # Get the last 10 transactions with balances and evidence links
    last_10_transactions = get_last_10_transactions()

    return render_template('saldo.html', saldo=saldo_formatted, last_10_transactions=last_10_transactions)

@app.route('/registrar_entrada', methods=['POST'])
@is_logged_in
def registrar_entrada():
    valor = float(request.form['valor'])

    # Insert the entry into the database with the updated cumulative balance
    conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')
    cur = conn.cursor()
    cur.execute("INSERT INTO transacoes (tipo, valor, saldo) VALUES (%s, %s, %s)", ("Entrada", valor, calculate_balance() + Decimal(valor)))
    conn.commit()
    cur.close()

    return redirect(url_for('saldo'))

@app.route('/registrar_saida', methods=['POST'])
@is_logged_in
def registrar_saida():
    valor = float(request.form['valor'])

    # Insert the withdrawal into the database with the updated cumulative balance
    conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')
    cur = conn.cursor()
    cur.execute("INSERT INTO transacoes (tipo, valor, saldo, evidencia) VALUES (%s, %s, %s, %s)", ("Saída", valor, calculate_balance() -  Decimal(valor),request.form['evidencia']))
    conn.commit()
    cur.close()

    return redirect(url_for('saldo'))


@app.route('/')
@is_logged_in
def home():

    return render_template('home.html')

@app.route('/db')
def db():

    return render_template('dashboard.html')


@app.route('/campanhas')
@is_logged_in
def campanhas():
    org_id = session['last_org']
    conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')

    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM campanhas where orgid='{org_id}'")

    dados=cursor.fetchall()

    # Close connection
    conn.close()

    return render_template('campanhas.html', campanhas = dados)


@app.route('/campanhas_ativas')
@is_logged_in
def campanhas_ativas():
    org_id = session['last_org']
    conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')

    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM campanhas where orgid='{org_id}' and status = 'ativo';")

    dados=cursor.fetchall()

    # Close connection
    conn.close()

    return render_template('campanhas.html', campanhas = dados, type = 'Campanhas ativas')


@app.route('/inquerito_ativo')
@is_logged_in
def inquerito_ativo():
    org_id = session['last_org']
    conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')

    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM campanhas where orgid='{org_id}' and status = 'ativo' and tipo ='inquerito';")

    dados=cursor.fetchall()

    # Close connection
    conn.close()

    return render_template('campanhas.html', campanhas = dados, type = 'Campanhas ativas')

@app.route('/formacao_ativa')
@is_logged_in
def formacao_ativa():
    org_id = session['last_org']
    conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')

    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM campanhas where orgid='{org_id}' and status = 'ativo' and tipo ='formacao';")

    dados=cursor.fetchall()

    # Close connection
    conn.close()

    return render_template('campanhas.html', campanhas = dados, type='Fomacao Remota')
   


@app.route('/pendentes')
@is_logged_in
def pendentes():

    conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM pendentes where estado ='pendente' ORDER BY id_pendentes")

    dados=cursor.fetchall()

    # Close connection
    conn.close()

    return render_template('pendentes.html', pendentes = dados)


@app.route('/sms')
@is_logged_in
def sms():

    conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')
 
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM sms ORDER BY id_sms')

    dados=cursor.fetchall()

    # Close connection
    conn.close()

    return render_template('sms.html', sms = dados)


@app.route('/requisicoes')
@is_logged_in
def requisicoes():

    conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM requisicao where estado ='pendente' ORDER BY id_requisicao")

    dados=cursor.fetchall()

    # Close connection
    conn.close()

    return render_template('requisicoes.html', requisicoes = dados)


@app.route('/cobrancas')
@is_logged_in
def cobrancas():
    conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')

    cursor = conn.cursor()

    cursor.execute('SELECT * FROM cobrancas ORDER BY id_cobrancas')

    dados=cursor.fetchall()

    return render_template('cobrancas.html', cobrancas = dados)



@app.route('/about')
def about():
    return render_template('about.html')

class SmsForm(Form):
    site = StringField('Sender_ID:', [validators.Length(min=3, max=10)])
    contacto = StringField('Contacto:',[validators.Length(min=9, max=9),validators.DataRequired()])
    sms = TextAreaField('SMS:',[validators.Length(min=3, max=800),validators.DataRequired()])



class RequisicaoForm(Form):
    cliente = SelectField('Cliente:', coerce=str, choices=dados_cliente)
    requisicao = TextAreaField('Requisicao:',[validators.Length(min=5),validators.DataRequired()])
    valor = DecimalField('Valor(MZN):')
    estado = SelectField('Estado:',coerce=str,choices=[("pendente","Pendente"),("pago","Pago")])
    destinatario= SelectField('Destinatario:', coerce=str, choices=dados1_usuarios)
    observacao= TextAreaField('Observacao:')
    file = FileField("File", validators=[InputRequired('Upload File')])
    submit = SubmitField("Save")
    estado1= SelectField('Estado:',coerce=str,choices=[("Pago","Pago"),("Parcelado","Parcelado")])



class AddInvoiceForm(Form):
    numero = DecimalField('Numero da factura:')
    cliente = SelectField('Cliente:', coerce=str, choices=dados_cliente)
    descricao = TextAreaField('Descricao:',[validators.Length(min=5),validators.DataRequired()])
    valor = DecimalField('Valor(MZN):')
    estado = SelectField('Estado:',coerce=str,choices=[("pendente","Pendente"),("pago","Pago")])
    mes = TextAreaField('Mes:',[validators.DataRequired()])
    date = DateField('Data:', format='%d/%m/%Y', validators=(validators.Optional(),))
    
    
class TicketForm(Form):
    site = SelectField('Cliente:', coerce=str, choices=dados_cliente)
    responsavel = SelectField('Responsavel:', coerce=str, choices=dados_usuarios)

    ticket = TextAreaField('Ticket:',[validators.Length(min=5),validators.DataRequired()])
    criador = StringField('Criado por:', [validators.Length(min=3, max=10)])

class CampForm(Form):
    
    #ticket = TextAreaField('Ticket:',[validators.Length(min=5),validators.DataRequired()])
    projecto = StringField('Projecto:', [validators.Length(min=3, max=200)])

class PerguntaForm(Form):
    #ticket = TextAreaField('Ticket:',[validators.Length(min=5),validators.DataRequired()])
    pergunta = StringField('Pergunta:', [validators.Length(min=3, max=200)])

class AprocidaForm(Form):
    nome = StringField('Nome:',[validators.Length(min=9, max=90),validators.DataRequired()])
    apelido = StringField('Apelido:',[validators.Length(min=9, max=90),validators.DataRequired()])
    sexo = SelectField('Sexo:',coerce=str,choices=[("masculino","Masculino"),("femenino","Femenino")])
    contacto = StringField('Contacto:',[validators.Length(min=9, max=9),validators.DataRequired()])
    contacto_alternativo = StringField('Contacto alternativo:',[validators.Length(min=9, max=9),validators.DataRequired()])
    estadocivil = SelectField('Estado civil:',coerce=str,choices=[("solteiro","Solteiro"),("casado","Casado")])
    endereco = TextAreaField('Endereco:',[validators.Length(min=9, max=190),validators.DataRequired()])
    nivelacademico = SelectField('Nivel Academico:',coerce=str,choices=[("medio","Medio"),("licenciatura","Licenciatura"),("mestre","Mestre"),("phd","Phd")])
    identidade = SelectField('Tipo de documento:',coerce=str,choices=[("bi","BI"),("passaporte","Passaporte"),("carta","Carta de conducao"),("outro","Outro")])

    
class CadastroForm(Form):
    name = StringField('Name:',[validators.Length(min=9, max=90),validators.DataRequired()])
    contact1 = IntegerField('Contacto 1:',[validators.Length(min=9, max=9),validators.DataRequired()])
    contact2 = IntegerField('Contacto 2:')
    email = EmailField('Email:')
    email2 = EmailField('Email Alternativo:')
    city = StringField('Cidade:',[validators.Length(min=4, max=90),validators.DataRequired()])
    residence = SelectField('Residence type:',coerce=str,choices=[("Owner","Owner"),("Intermediary","Intermediary")])
    phase= SelectField('Work Phase:',coerce=str,choices=[("Beginning","Beginning"),("Middle","Middle"),("End","End")])
    sale= SelectField('Sale Phase:',coerce=str,choices=[("Approach","Approach"),("Presentation","Presentation"),("Negotiation","Negotiation"), ("After-sales","After-sales")])
    areas= SelectField('What do you want to automate:',coerce=str,choices=[("Lighting","Lighting"),("Blinds","Blinds"),("AC","AC"), ("Sound","Sound")])
    interested= SelectField('ONG ou Automação?',coerce=str,choices=[("True","ONG"),("False","Automação")])
    know= SelectField('How do you know about us:',coerce=str,choices=[("Instagram","Instagram"),("Linkedin","Linkedin"),("Whatsapp","Whatsapp"),("Friends","Friends"), ("Dep Vendas","Dep Vendas"), ("Others","Others")])
 

class TaskForm(Form):
    text = TextAreaField('Description:',[validators.Length(min=9, max=190),validators.DataRequired()])
    time = TimeField('Time:', format='%H:%M', validators=[DataRequired()])
    actionNow= SelectField('Action:',coerce=str,choices=[("Select","Select action...."),("Call","Call"),("Meeting","Meeting"),("submission of proposal","submission of proposal")])
    action= SelectField('Next action:',coerce=str,choices=[("Call","Call"),("Meeting","Meeting"),("submission of proposal","submission of proposal")])
    calendar = DateField('Calendar:', format='%d/%m/%Y',validators=[DataRequired()])
    submit = SubmitField('submit') 
    
class OptionForm(Form):
    opcao = StringField('Opção:',[validators.Length(min=3, max=120),validators.DataRequired()])
    
    
    
class addcredencialForm(Form):
    cliente= SelectField('Cliente:', coerce=str, choices=dados_cliente)
    local= SelectField('Site:', coerce=str, choices=dados2_cliente)
    user= StringField('User:')
    password= StringField('Password:')
    ipadress= StringField('IP adress:')
    ippublico= StringField('Public IP:')
    senha_wifi= StringField('WIFi Pass:')
    user= StringField('User:')
    user_router= StringField('User Router:')
    senha_router= StringField('Router Pass:')
    ipadress_router= StringField('Router Ipaddress:')
  


class funcaoForm(Form):
    funcao= TextAreaField('Function:',[validators.Length(min=5),validators.DataRequired()])
    estado = SelectField('Estado:',coerce=str,choices=[("pendente","Pendente"),("resolvido","resolvido")])
    date = DateField('Data:', format='%d/%m/%Y', validators=(validators.Optional(),))
    usuario = StringField('Criado por:', [validators.Length(min=3, max=10)])
    
class CalForm(Form):
    num1=DecimalField('Valor(MZN):')
    num2=DecimalField('Valor(MZN):')    

class propostasForm(Form):
    cliente= SelectField('Cliente:', coerce=str, choices=dados3_cliente)
    pasta= StringField('Pasta:')
    contexto= TextAreaField('Contexto:',[validators.Length(min=40),validators.DataRequired()])
    

@app.route('/aprocida', methods=['GET', 'POST'])
def aprocida():
    
    form = AprocidaForm(request.form)
    
    if request.method == 'POST':

        #current_dateTime = datetime.now()
        #current_dateTime = str(datetime.date(current_dateTime))+" "+str(datetime.time(current_dateTime))

        #conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')

        #cursor = conn.cursor()

        # Execute query
        #cursor.execute("INSERT INTO pendentes(site, descricao_actividade, responsavel, data) VALUES (%s,%s,%s,%s)",(form.site.data,form.ticket.data,session['username'],current_dateTime))
        
        # Commit to DB
        #conn.commit()

        # Close connection
        #conn.close()

        flash('Inscricao feita com Successo', 'success')

        return redirect(url_for('aprocida'))

    return render_template('aprocida.html', form = form)   
    

@app.route('/addproposal', methods=['GET', 'POST'])
@is_logged_in
def addproposal():
    
    form = propostasForm(request.form)

    
    if request.method == 'POST': 

        current_dateTime = datetime.now()
        current_dateTime = str(datetime.date(current_dateTime))+" "+str(datetime.time(current_dateTime))

        conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')

        cursor = conn.cursor()

        # Execute query
        cursor.execute("INSERT INTO propostas(cliente, linker, contexto, requisitante) VALUES (%s,%s,%s,%s)",(form.cliente.data,form.pasta.data,form.contexto.data,session['username']))
        
        # Commit to DB
        conn.commit()

        # Close connection
        conn.close()

        flash('Pedido de proposta adicinado com Successo', 'success')

        return redirect(url_for('propostas'))

    return render_template('addproposal.html', form = form)


@app.route('/addticket', methods=['GET', 'POST'])
@is_logged_in
def addticket():
    
    form = TicketForm(request.form)
    
    if request.method == 'POST':

        current_dateTime = datetime.now()
        current_dateTime = str(datetime.date(current_dateTime))+" "+str(datetime.time(current_dateTime))

        conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')

        cursor = conn.cursor()

        # Execute query
        cursor.execute("INSERT INTO pendentes(site, descricao_actividade, criou, data, estado) VALUES (%s,%s,%s,%s,%s)",(form.site.data,form.ticket.data,session['username'],current_dateTime,'pendente'))
        
        # Commit to DB
        conn.commit()

        # Close connection
        conn.close()

        flash('Ticket adicinado com Successo', 'success')

        return redirect(url_for('pendentes'))

    return render_template('addticket.html', form = form)

       

@app.route('/add_update/<int:invoice_id>', methods=['GET','POST'])
def add_update(invoice_id):
    if request.method == 'POST':
        update_text = request.form['update_text']
        sales_team_member = session['username']  # Replace with actual user information

        conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')
        cursor = conn.cursor()

        # Insert update into the updates table
        cursor.execute('INSERT INTO updates (invoice_id, update_date, sales_team_member, update_text) VALUES (%s, CURRENT_DATE, %s, %s)',
                       (invoice_id, sales_team_member, update_text))

        conn.commit()
        conn.close()

        flash('Update added successfully', 'success')

    return redirect(url_for('invoices'))



@app.route('/invoices', methods=['GET'])
@is_logged_in
def invoices():

    conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')

    cursor = conn.cursor()

     # Execute query to get all updates
    cursor.execute('SELECT invoice_id, update_text, update_date, sales_team_member FROM updates')

    data = cursor.fetchall()

    

    # Organize the data into a dictionary with invoice_id as keys and a list of updates as values
    invoice_updates = {}
    for row in data:
        invoice_id = row[0]
        update_text = row[1]
        update_date = row[2]
        sales_team_member = row[3]

        if invoice_id not in invoice_updates:
            invoice_updates[invoice_id] = []

        invoice_updates[invoice_id].append({
            'update_text': update_text,
            'update_date': update_date,
            'sales_team_member': sales_team_member
        })
    
    # Execute query to get all invoices
    cursor.execute('SELECT faturas.id_faturas, faturas.cliente, faturas.descricao,  faturas.valor, faturas.estado FROM faturas ORDER BY faturas.cliente')

    data = cursor.fetchall()

    # Close connection
    conn.close()

    return render_template('invoices2.html', dados=data, invoice_updates=invoice_updates)


class crentesForm(Form):
    nome = StringField('Nome:', [validators.Length(min=3, max=20),validators.DataRequired()])
    apelido = StringField('Apelido:', [validators.Length(min=3, max=20),validators.DataRequired()])
    telemovel = StringField('Contacto:',[validators.Length(min=9, max=9),validators.DataRequired()])


@app.route('/addcrentes', methods=['GET', 'POST'])
def addcrentes():
    
    form = crentesForm(request.form)
    
    if request.method == 'POST':

        conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')

        cursor = conn.cursor() 

        # Check if telemovel already exists
        cursor.execute('SELECT telemovel FROM crentes_divina WHERE telemovel = %s', (int(form.telemovel.data),))
        existing_telemovel = cursor.fetchone()

        if existing_telemovel:
            # Telemovel already registered, show flash message
            conn.close()
            flash('Este número de telefone já está registrado.', 'danger')
            return redirect(url_for('addcrentes'))

        # If telemovel is not registered, proceed with insertion
        cursor.execute('INSERT INTO crentes_divina(telemovel, nome, apelido) VALUES(%s, %s, %s)', (int(form.telemovel.data), form.nome.data, form.apelido.data))

        # Commit to DB
        conn.commit()

        # Close connection
        conn.close()

        flash('Dados adicionados com sucesso', 'success')

        return redirect(url_for('addcrentes'))

    return render_template('divina.html', form=form)



@app.route('/addinvoices', methods=['GET', 'POST'])
@is_logged_in
def addinvoices():
    
    form = AddInvoiceForm(request.form)
    
    if request.method == 'POST':

        conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')

        cursor = conn.cursor() 

        # Execute query
        cursor.execute('INSERT INTO faturas(id_faturas,cliente,descricao,valor,data,estado, mes) VALUES(%s,%s,%s,%s,%s,%s,%s)',(form.numero.data,form.cliente.data,form.descricao.data,form.valor.data,form.date.data,form.estado.data, form.mes.data))
        
        # Commit to DB
        conn.commit()

        # Close connection
        conn.close()

        flash('Factura adicinada com Successo', 'success')

        return redirect(url_for('invoices'))

    return render_template('addinvoices.html', form = form)


@app.route('/addrequest', methods=['GET', 'POST'])
@is_logged_in
def addrequest():
    
    form = RequisicaoForm(request.form)
    
    if request.method == 'POST':

        current_dateTime = datetime.now()
        current_dateTime = str(datetime.date(current_dateTime))+" "+str(datetime.time(current_dateTime))

        conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')

        cursor = conn.cursor()

        # Execute query
        cursor.execute("INSERT INTO requisicao(requisicao,cliente, valor, data_pagamento, estado) VALUES (%s,%s,%s,%s,%s)",(form.requisicao.data,form.cliente.data,form.valor.data,current_dateTime,form.estado.data))
        
        # Commit to DB
        conn.commit()

        # Close connection
        conn.close()

        flash('Pedido adicinado com Successo', 'success')

        return redirect(url_for('requisicoes'))

    return render_template('addrequest.html', form = form)

# Edit Request
@app.route('/edit_request/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_request(id):

    conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')
    
    # Create cursor
    cursor = conn.cursor()

    # Get article by id
    result = cursor.execute("SELECT * FROM requisicao WHERE id_requisicao = %s", [id])

    requisicao = cursor.fetchone()
    
    #conn.close()
    
    # Get form

    form = RequisicaoForm(request.form)

    # Populate tikrts form fields
    form.cliente.data = requisicao[3]
    form.requisicao.data = requisicao[1]
    form.valor.data = Decimal(requisicao[5])


    if request.method == 'POST':
        requisicao = request.form['requisicao']
        cliente = request.form['cliente']
        valor = request.form['valor']


        #current_dateTime = datetime.now()

        # Create Cursor
        cursor = conn.cursor()
        #app.logger.info(title)
        
        # Execute
        cursor.execute("UPDATE requisicao SET cliente=%s, requisicao=%s, valor=%s WHERE id_requisicao=%s",(cliente,requisicao,valor,id))
        
        # Commit to DB
        conn.commit()

        #Close connection
        conn.close()

        flash('Request Updated', 'success')

        return redirect(url_for('requisicoes'))

    return render_template('edit_request.html', form=form)


@app.route('/testes', methods=['GET', 'POST'])
@is_logged_in
def testes():
    form = SmsForm(request.form)
    if request.method == 'POST':

        conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')

        
        # Create cursor
        cursor = conn.cursor()
        
        print("Mensagem:")
        print(form.sms.data)
        
        # Send SMS
        sid= send_sms(form.sms.data,str("+258"+form.contacto.data),form.site.data)
        account_sid = "AC952933e9303a9c0021be3c0ce432caec"
        auth_token = "5e14a5105201307f6d9a77af3fd81853"
        
        #message_sid = 'SMbc7fc62463f463c39ba12f9be200802a'
        client = Client(account_sid, auth_token)
        messagem = client.messages(sid).fetch()
        status = messagem.status
        print(f'este e o status do encio da mensagem:  {status}')
        # Execute query
        cmd=f"INSERT INTO envio_sms(mensagem, contato, nv_enviadas, sender_id, status_sms) VALUES ('{form.sms.data}','+258{form.contacto.data}','0','{form.site.data}','{status}') RETURNING id_alerta"

        cursor.execute(cmd)
        dnh = cursor.fetchone()[0]
        # Commit to DB
        conn.commit()

        # Close connection
        conn.close()
       
        flash(f'Sms enviado com sucesso', 'success')

        return redirect(url_for('testes'))

    return render_template('testes.html', form = form)


@app.route('/enviar_sms_grupo', methods=['GET','POST'])
@is_logged_in
def enviar_sms_grupo():
        org_id = session['last_org']
        form = SmsForm(request.form)
        data = request.get_json()
    
        grupo_id = data.get('grupo')
        mensagem = data.get('mensagem')
        Sender_id = data.get('Sender_id')
        
        print(mensagem)
        conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')

        cursor = conn.cursor()

        cursor.execute(f"SELECT * FROM contacts join contact_group on contacts.id = contact_group.id_cont where contact_group.grp_id = '{grupo_id}';")
        
        sms_grupo=cursor.fetchall()

        account_sid = "AC952933e9303a9c0021be3c0ce432caec"
        auth_token = "5e14a5105201307f6d9a77af3fd81853"
        
        #message_sid = 'SMbc7fc62463f463c39ba12f9be200802a'
    
        for sms in sms_grupo:
          message_sid = send_sms(mensagem,str("+258"+sms[3]),Sender_id)
          client = Client(account_sid, auth_token)
          messagem = client.messages(message_sid).fetch()
          status = messagem.status
          cmd='INSERT INTO envio_sms(mensagem, contato, nv_enviadas, sender_id, status_sms) VALUES ('+"'"+mensagem+"'"+",'"+str("+258"+sms[3])+"','0','"+org_id+"'"+status+"'"+') RETURNING id_alerta'
          cursor.execute(cmd)
          conn.commit()

        conn.close()  
        return redirect(url_for('sucesso_sms'))


@app.route('/sucesso_sms', methods=['GET'])
@is_logged_in
def sucesso_sms():
        form = SmsForm(request.form)
        flash('Teste criado com sucesso', 'success')
        return render_template('testes.html', form = form)


def status_sms(message_sid):
    message = Client.messages(message_sid).fetch()
    status_msg = message.status

    return  status_msg


@app.route('/manage_privileges', methods=['GET', 'POST'])
def manage_privileges():
    if request.method == 'POST':
        user_id = request.form['user_id']
        privileges = request.form.getlist('privileges')
        conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')
        cursor = conn.cursor()
        cursor.execute('UPDATE usuarios SET privileges = %s WHERE "user" = %s', (','.join(privileges), user_id))
        conn.commit()
        return redirect(url_for('manage_privileges'))
    conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')
    cursor = conn.cursor()
    cursor.execute('SELECT id_usuarios, "user" FROM usuarios')
    users = cursor.fetchall()
    cursor.execute('SELECT privileges FROM usuarios where "user" = %s',(session['username'],))
    user = cursor.fetchone()
    session['privileges'] = user[0].split(',')
    return render_template('manage_privileges.html', users=users)



def check_referer():
    return '/tarefas' in request.headers.get('Referer', '')
# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    
    # Check if 'login_attempts' is in the session, if not, set it to 0
    if 'login_attempts' not in session:
        session['login_attempts'] = 0

    if request.method == 'POST':
        # Get Form Fields
        username = request.form['username']
        password_candidate = request.form['password']
        username_check = 'nok'
        pass_check = 'nok'

        conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')

        # Create cursor
        cursor = conn.cursor()

        # Get user by username
        cmd = "SELECT * FROM usuarios WHERE" + ' "user"=' + "'" + username + "'"
        result = cursor.execute(cmd)

        result = cursor.fetchall()

        for z in result:
            if z[1] == username and z[5] != True:
                username_check = 'ok'
                valid_user = z[1]
                break
            
            else:
                username_check = 'nok'
        
       

        if username_check == 'nok':
            flash('Username invalido ou sua conta esta bloqueada ', 'danger')
            # Close connection
            conn.close()
            return redirect(url_for('login'))

        for z in result:
            if z[4] == password_candidate:
                pass_check = 'ok'
                break
            else:
                pass_check = 'nok'

        if pass_check == 'nok':
            session['login_attempts'] += 1

            if session['login_attempts'] >= 3:
                
                cmd = "UPDATE usuarios SET bloqueado=True WHERE"+ ' "user"='+"'"+ username + "'"
                cursor.execute(cmd)
                # Commit to DB
                conn.commit()

                flash('Muitas tentativas falhadas. Sua conta esta bloqueada.', 'danger')
                # Close connection
                conn.close()
                return redirect(url_for('login'))
            else:
                flash('Password invalida. Tem mais {} chances'.format(3 - session['login_attempts']), 'danger')
                # Close connection
                conn.close()
                return redirect(url_for('login'))
            
        elif pass_check == 'ok':
            # Reset login attempts on successful login
            session['login_attempts'] = 0
            
            # Get last org id from user
            cmd = "SELECT * FROM usuarios join usuario_org on usuarios.id_usuarios = usuario_org.usuario_id WHERE" + ' "user"=' + "'" + username + "' limit 1;"
            result = cursor.execute(cmd)
            result = cursor.fetchone()

            cmm = "SELECT * FROM usuarios  WHERE" + ' "user"=' + "'" + username + "' ;"
            resulte = cursor.execute(cmm)
            resulte = cursor.fetchone()
           
            if result:

             # Upadate session parameters
             session['logged_in'] = True
             session['username'] = username
             session['last_org'] = str(result[9])
             session['saldo'] = str(result[10])
             dados = str(result[6])

            else: 
             session['logged_in'] = True
             session['username'] = username
             session['last_org'] = str(resulte[6])
             if username == "Temoteo" or username == "Shelton" or username == "Marta":
                session['saldo'] = "Ilimitado"
             dados = str(resulte[6])

            

            flash('Login com Sucesso', 'success')
            # Close connection
            conn.close()
            if check_referer():
                return redirect(url_for('tarefas_diarias'))
            else:
                return redirect(url_for('tasks', dados = dados))

    return render_template('login.html')


# Edit ticket
@app.route('/edit_ticket/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_ticket(id):

    conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')
    
    # Create cursor
    cursor = conn.cursor()

    # Get article by id
    result = cursor.execute("SELECT * FROM pendentes WHERE id_pendentes = %s", [id])

    ticket = cursor.fetchone()
    
    #conn.close()
    
    # Get form

    form = TicketForm(request.form)

    # Populate tikrts form fields
    form.site.data = ticket[1]
    form.ticket.data = ticket[2]

    if request.method == 'POST':
        site = request.form['site']
        ticket = request.form['ticket']

        #current_dateTime = datetime.now()

        # Create Cursor
        cursor = conn.cursor()
        #app.logger.info(title)
        
        # Execute
        cursor.execute("UPDATE pendentes SET site=%s, descricao_actividade=%s WHERE id_pendentes=%s",(site,ticket,id))
        
        # Commit to DB
        conn.commit()

        #Close connection
        conn.close()

        flash('Ticket Updated', 'success')

        return redirect(url_for('pendentes'))

    return render_template('edit_ticket.html', form=form)

# Assign ticket
@app.route('/assign_ticket/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def assign_ticket(id):

    conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')
    
    # Create cursor
    cursor = conn.cursor()

    # Get article by id
    result = cursor.execute("SELECT * FROM pendentes WHERE id_pendentes = %s", [id])

    ticket = cursor.fetchone()
    
    #conn.close()
    
    # Get form

    form = TicketForm(request.form)

    # Populate tikrts form fields
    form.site.data = ticket[1]
    form.ticket.data = ticket[2]
    form.responsavel.data = ticket[14]

    if request.method == 'POST':
        site = request.form['site']
        ticket = request.form['ticket']
        responsavel = request.form['responsavel']


        #current_dateTime = datetime.now()

        # Create Cursor
        cursor = conn.cursor()
        #app.logger.info(title)
        
        # Execute
        cursor.execute("UPDATE pendentes SET site=%s, descricao_actividade=%s, responsavel=%s WHERE id_pendentes=%s",(site,ticket,responsavel,id))
        
        # Commit to DB
        conn.commit()

        #Close connection
        conn.close()

        flash('Ticket Assigned', 'success')

        return redirect(url_for('pendentes'))

    return render_template('assign_ticket.html', form=form)



# Delete Tiket
@app.route('/del_tiket/<string:id>', methods=['POST'])
@is_logged_in
def del_tiket(id):
    # Create cursor
    conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')

    cursor = conn.cursor()

    # Execute
    cursor.execute("UPDATE pendentes SET estado='resolvido' WHERE id_pendentes = %s", [id])

    # Commit to DB
    conn.commit()

    #Close connection
    conn.close()

    flash('Ticket Deleted', 'success')

    return redirect(url_for('pendentes'))


@app.route('/addoption/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def addoption(id):
    form = OptionForm(request.form)
    id = int(id)
    if request.method == 'POST':
        conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')
        cursor = conn.cursor()
        opcao = form.opcao.data
        # Query
        #query = sql.SQL("INSERT INTO {} (opcao) VALUES (%s)").format(sql.Identifier(id))

        # Execute query with parameterized value
        if type == 'inquerito':
           cursor.execute(f"Insert into campanha_option values({id},'{opcao}');")

           # Commit to DB
           conn.commit()

        else:   
           cursor.execute(f"Insert into questoes_opcoes values({id},'{opcao}');")

           # Commit to DB
           conn.commit()
        # Close connection
        conn.close()

        flash('Opcao adicionada com Successo', 'success')

        return redirect(url_for('perguntas', id=id))

    return render_template('addoption.html', form=form)



def buscar_Audio(id):
    conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')
    cursor = conn.cursor()
    
    data = []
    cursor.execute(f"""
                     SELECT
                         ca.audio,
                         cq.tipo,
                         ca.idioma
                     FROM
                         campanha_question cq
                     JOIN
                         campanha_audio ca ON cq.questao_id = ca.questao_id
                     WHERE
                         cq.campanha_id = {id};                   
                     """)
    audio_files = [row[0] for row in cursor.fetchall()]


    base_url = "https://insightsap.com/get_audio/"
    audio_urls = [f"{base_url}{audio_file}" for audio_file in audio_files]

    conn.close()

    
    
    return audio_urls



@app.route('/deletar_audio/<string:id>', methods=['GET'])
@is_logged_in
def deletar_audio(id):
    conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')
    cursor = conn.cursor()
  
    print(id)
    
    cursor.execute(f"DELETE FROM  display_ref_linguas  WHERE  id = {id} ;")
    conn.commit()
    conn.close()
    
    partes = id.split("_")
    resultado = "_".join(partes[:2])
   
    return redirect(url_for('campanha_n', id=resultado))




@app.route('/carragar_questoes/<string:id>', methods=['GET'])
@is_logged_in
def carragar_questoes(id):
   
    data = questoes(id)

    return jsonify(data)


def questoes(id):
    conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')
    cursor = conn.cursor()
  
    org_id = session['last_org']
    print(id)
   
           
    cursor.execute("SELECT * FROM display_ref WHERE id LIKE %s;", (id + "_%",))
    questoes = cursor.fetchall()
    conn.close()
    print(questoes)
    data = [{'id': questao[0], 'questao': questao[1]} for questao in questoes]

    print(data)
    return data



@app.route('/campanha_n/<int:id>/<type>',methods=['GET'])
@is_logged_in
def campanha_n(id, type):
        print(id)
        # Connect to the PostgreSQL database
        connection = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')
        cursor = connection.cursor()
        tema = 'Aula'
        if type != 'formacao':
           cursor.execute(f"SELECT projecto FROM campanhas where id_campanha ={id};")
           tema = cursor.fetchone()[0]

        else:
           cursor.execute(f"SELECT tema FROM aulas where id ={id};")
           tema = cursor.fetchone()[0]

        # Executar uma função que retorna os resultados de acordo com o tipo de campanha e id fornecidos
        cursor.execute(f"SELECT * FROM get_info_by_id_and_type({id}, '{type}');")
        result = cursor.fetchall()
            
        return render_template('campanha_n.html', columns_list = result, id=id, type=type, tema=tema)


@app.route('/add_question/<id>/<type>', methods=['GET', 'POST'])
def add_question(id, type):
      # Conecte-se ao banco de dados PostgreSQL
      conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')
      cursor = conn.cursor()
      
      # Converta o id de string para inteiro
      id = int(id)
      
      # Verifique o tipo de campanha e insira a pergunta apropriada
      if type == 'formacao':
         # Insere a pergunta na tabela aula_info para formação
         cursor.execute(f"INSERT INTO aula_info(aula, descricao, audios, tipo) VALUES (%s, %s, %s, %s);", (id, 'Inicialise a informacao da pergunta', 0, 'Pergunta'))
         conn.commit()
      else:
         # Insere a pergunta na tabela campanha_question para campanha
         cursor.execute(f"INSERT INTO campanha_question(campanha_id, descricao, audios, tipo) VALUES (%s, %s, %s, %s);", (id, 'Inicialise a informacao da pergunta', 0, 'Pergunta'))
         conn.commit()

      # Feche a conexão com o banco de dados
      conn.close()
      
      # Redirecione para a página de campanha correspondente
      return redirect(url_for('campanha_n', id=id, type=type))


@app.route('/audios/<int:id>/<string:type>', methods=['GET', 'POST'])
@is_logged_in
def audios(id, type):
    # Inicializar o formulário de áudio
    form = AudioForm()
    
    # Conectar ao banco de dados dentro de um bloco 'with' para garantir que a conexão seja fechada
    conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')
    cursor = conn.cursor()

    # Executar uma função que retorna os resultados de acordo com o tipo de campanha e id fornecidos
    cursor.execute(f"SELECT * FROM get_audio_data({id}, '{type}');")
    audios = cursor.fetchall()
    print(id)
          
    # Fechar o cursor e a conexão com o banco de dados
    cursor.close()
    conn.close()

    # Renderizar o template 'audios.html' com os dados obtidos, incluindo o tipo e id
    return render_template('audios.html', audios=audios, type=type, id=id)



@app.route('/add_audio/<int:id>/<type>', methods=['GET', 'POST'])
def add_audio(id,type):
    # Verifica se o método da requisição é POST
    if request.method == 'POST':
        try:
            # Conecta ao banco de dados PostgreSQL usando as credenciais fornecidas
            conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')
            cursor = conn.cursor()
            
            # Converte o id de string para inteiro
            id = int(id)
            cursor.execute("SELECT campanha_id FROM campanha_question WHERE questao_id = %s", (id,))
            campanha_id = cursor.fetchone()[0]
            
            # Obtém o arquivo de áudio enviado pelo usuário
            audio = request.files['audio']
            audio_lingua = request.form['idioma']
            
            # Salva o arquivo de áudio no servidor com um nome seguro
            audio_filename = secure_filename(audio.filename)
            audio.save(os.path.join(app.config['AUDIO_FOLDER'], audio_filename))
            
            # Verifica se já existem registros de áudio para a questão fornecida
            cursor.execute("SELECT * FROM campanha_audio WHERE questao_id = %s", (id,))
            dados = cursor.fetchall()
            
            # Determina o número da questão com base na quantidade de registros existentes
            if dados:
                questao_nr = len(dados) + 1
            else:
                questao_nr = 1
            
            # Insere um novo registro de áudio na tabela aula_audio
            cursor.execute(
                "INSERT INTO campanha_audio (questao_id, questao_nr, audio, idioma) VALUES (%s, %s, %s, %s)",
                (id, questao_nr, audio_filename, audio_lingua)
            )
            conn.commit()
        
        except (Exception, psycopg2.DatabaseError) as error:
            # Imprime o erro, se houver
            print(f"Erro ao executar a query: {error}")
        
        finally:
            # Fecha a conexão com o banco de dados
            if conn is not None:
                conn.close()
        
        # Redireciona para a página de campanha correspondente
        return redirect(url_for('campanha_n', id=campanha_id, type=type))
    
    # Obtém as opções de idioma para o formulário
    choices = request_languge()
    print(choices)
    
    # Renderiza o template add_audio.html com as opções de idioma
    return render_template('add_audio.html', id=id, options=choices, type=type)


def criar_aula(id, tema, intro, base, con, audio_intro, audio_base, audio_con, audio_lingua):
    try:
        # Estabelece uma conexão com o banco de dados PostgreSQL usando psycopg2
        conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')
        cursor = conn.cursor()
        
        # Insere um novo registro na tabela 'Aulas' e retorna o 'id' gerado
        cursor.execute(f"INSERT INTO Aulas (tema, modulo) VALUES ('{tema}', {id}) RETURNING id;")
        aula_id = cursor.fetchone()[0]
        conn.commit()

        # Insere um novo registro na tabela 'aula_info' para a introdução da aula e retorna o 'questao_id' gerado
        cursor.execute(f"INSERT INTO aula_info(aula, descricao, audios, tipo) VALUES ('{aula_id}', '{intro}', 0, 'Introducao') RETURNING questao_id;")
        intro_id = cursor.fetchone()[0]
        conn.commit()

        # Insere um novo registro na tabela 'aula_info' para o conteúdo da aula e retorna o 'questao_id' gerado
        cursor.execute(f"INSERT INTO aula_info(aula, descricao, audios, tipo) VALUES ('{aula_id}', '{base}', 0, 'Corpo') RETURNING questao_id;")
        tema_id = cursor.fetchone()[0]
        conn.commit()

        # Insere um novo registro na tabela 'aula_info' para a conclusão da aula e retorna o 'questao_id' gerado
        cursor.execute(f"INSERT INTO aula_info(aula, descricao, audios, tipo) VALUES ('{aula_id}', '{con}', 0, 'Conclusao') RETURNING questao_id;")
        con_id = cursor.fetchone()[0]
        conn.commit()

        # Se o áudio de introdução foi fornecido, insere-o na tabela 'aula_audio'
        if audio_intro:
            cursor.execute(f"INSERT INTO aula_audio(questao_id, audio, idioma) VALUES ('{intro_id}', '{audio_intro}', '{audio_lingua}');")
            conn.commit()

        # Se o áudio base foi fornecido, insere-o na tabela 'aula_audio'
        if audio_base:
            cursor.execute(f"INSERT INTO aula_audio(questao_id, audio, idioma) VALUES ('{tema_id}', '{audio_base}', '{audio_lingua}');")
            conn.commit()

        # Se o áudio de conclusão foi fornecido, insere-o na tabela 'aula_audio'
        if audio_con:
            cursor.execute(f"INSERT INTO aula_audio(questao_id, audio, idioma) VALUES ('{con_id}', '{audio_con}', '{audio_lingua}');")
            conn.commit()

        return aula_id
    
    except psycopg2.Error as e:
        # Se ocorrer um erro durante a operação, exibe uma mensagem de erro usando flash
        return flash(f'Erro ao enviar dados {e}', 'error')


        
def criar_campanha(id, tema ,intro, base, con, audio_intro, audio_base, audio_con,audio_lingua ):
        try:
            conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')
            cursor = conn.cursor()
            cursor.execute(f" UPDATE campanhas set projecto = '{tema}' where id_campanha = {id}")
            conn.commit()

            cursor.execute(f"INSERT INTO campanha_question(campanha_id, descricao, audios, tipo) VALUES ({id}, '{intro}', 0, 'Introducao') RETURNING questao_id ;")
            conn.commit()
            intro_id = cursor.fetchone()[0]

            cursor.execute(f"INSERT INTO campanha_question(campanha_id, descricao, audios, tipo) VALUES ({id}, '{base}', 0, 'Corpo') RETURNING questao_id ;")
            conn.commit()
            audio_id = cursor.fetchone()[0]

            cursor.execute(f"INSERT INTO campanha_question(campanha_id, descricao, audios, tipo) VALUES ({id}, '{con}', 0, 'Conclusao') RETURNING questao_id;")
            conn.commit()
            con_id = cursor.fetchone()[0]
            
            if audio_intro:
               cursor.execute(f"INSERT INTO campanha_audio(questao_id, audio, idioma) VALUES ('{intro_id}', '{audio_intro}', '{audio_lingua}');")
               conn.commit()
            
            if audio_base:
               cursor.execute(f"INSERT INTO campanha_audio(questao_id, audio, idioma) VALUES ('{audio_id}', '{audio_base}', '{audio_lingua}');")
               conn.commit()
            
            if audio_con:
               cursor.execute(f"INSERT INTO campanha_audio(questao_id, audio, idioma) VALUES ('{con_id}', '{audio_con}', '{audio_lingua}');")
               conn.commit()  

            return flash('Dados inseridos com sucesso', 'success')  
        except psycopg2.Error as e:
            return flash(f'Erro ao enviar dados: {e}', 'error')      


def inquerito(id, tema ,intro,  con, audio_intro,  audio_con,audio_lingua ):
          try:
            conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')
            cursor = conn.cursor()
            cursor.execute(f" UPDATE campanhas set projecto = '{tema}' where id_campanha = {id}")
            conn.commit()

            cursor.execute(f"INSERT INTO campanha_question(campanha_id, descricao, audios, tipo) VALUES ({id}, '{intro}', 0, 'Introducao') RETURNING questao_id ;")
            conn.commit()
            intro_id = cursor.fetchone()[0]

            cursor.execute(f"INSERT INTO campanha_question(campanha_id, descricao, audios, tipo) VALUES ({id}, '{con}', 0, 'Conclusao') RETURNING questao_id;")
            conn.commit()
            con_id = cursor.fetchone()[0]
            
            if audio_intro:
               cursor.execute(f"INSERT INTO campanha_audio(questao_id, audio, idioma) VALUES ('{intro_id}', '{audio_intro}', '{audio_lingua}');")
               conn.commit()
            
            if audio_con:
               cursor.execute(f"INSERT INTO campanha_audio(questao_id, audio, idioma) VALUES ('{con_id}', '{audio_con}', '{audio_lingua}');")
               conn.commit()  

            return flash('Dados inseridos com sucesso', 'success')  
          except psycopg2.Error as e:
            return flash(f'Erro ao enviar dados: {e}', 'error')      
       


@app.route('/criar_campanhas/<type>/<int:id>', methods=['GET','POST'])
@is_logged_in
def criar_campanhas(type, id):
    # Obter o ID da organização da sessão
    org_id = session['last_org']

    if request.method == 'POST':
        
        # Obter dados do formulário
        tema = request.form['name']
        audio_lingua = request.form['idioma']
        introducao = request.form['introducao']
        conclusao = request.form['conclusao']
        intro= request.files['intro']
        con = request.files['con']
        audio_intro = ""
        audio_con = ""
        audio_base = ""

        # Obter e salvar arquivos de áudio
        if intro:
           audio_intro = secure_filename(intro.filename)
           intro.save(os.path.join(app.config['AUDIO_FOLDER'], audio_intro))

        
        if con:
           audio_con = secure_filename(con.filename)
           con.save(os.path.join(app.config['AUDIO_FOLDER'], audio_con))

         # Conectar ao banco de dados e inserir nova campanha se id for 0
        if id == 0:
           conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')
           cursor = conn.cursor()
           cursor.execute("SELECT * FROM campanhas;")
           ref = 36 + len(cursor.fetchall())
           cursor.execute(f"INSERT INTO campanhas (orgid, campanha_ref, status, tipo) VALUES ('{org_id}', 'campanha_{ref}', 'inativo', '{type}') RETURNING id_campanha;")
           conn.commit()
           id = int(cursor.fetchone()[0])
           print('diz'+str(id))
           conn.close()
        

        # Inserir dados na tabela correspondente, dependendo do tipo de campanha
        if type == 'inquerito':
           print("escreva"+str(id)) 
           inquerito(id, tema ,introducao, conclusao, audio_intro, audio_con,audio_lingua )
        
        else:
           base = request.form['aula_base']
           audio = request.files['audio']
           if audio:
              audio_base = secure_filename(audio.filename)
              audio.save(os.path.join(app.config['AUDIO_FOLDER'], audio_base))
           if type == 'formacao':
              id = criar_aula(id, tema ,introducao, base , conclusao, audio_intro,audio_base, audio_con,audio_lingua )         
           else:
              criar_campanha(id, tema ,introducao, base , conclusao, audio_intro,audio_base, audio_con,audio_lingua )



        # Redirecionar para a página de visualização da campanha
        return redirect(url_for('campanha_n', id=id, type=type))

    # Obter opções de idioma
    choices = request_languge()

    # Renderizar o template com as opções
    return render_template('criar_campanhas.html', options=choices, id=id, campanha=type)




@app.route('/criar_modulo/<int:id>', methods=['GET', 'POST'])
@is_logged_in
def criar_modulo(id):
    # Se o método da solicitação for POST, processar o formulário
    if request.method == 'POST':
        # Conectar ao banco de dados
        conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')
        org_id = session['last_org']
        cursor = conn.cursor()
        
        # Obter o nome do módulo do formulário
        modulo = request.form['modulo']
        
        # Se o id for 0, criar uma nova campanha
        if id == 0:
            cursor.execute(f"INSERT INTO campanhas (orgid, tipo) VALUES ('{org_id}', 'formacao') RETURNING id_campanha;")
            id = int(cursor.fetchone()[0])
            conn.commit()
        
        # Inserir o novo módulo na campanha
        cursor.execute(f"INSERT INTO modulos (campanha, nome) VALUES ({id}, '{modulo}') RETURNING modulo;")
        conn.commit()
        modulo = int(cursor.fetchone()[0])
        
        # Fechar a conexão com o banco de dados
        conn.close()
        
        # Redirecionar para a página de criação de campanhas
        return redirect(url_for('criar_campanhas', id=modulo, type='formacao'))
    
    # Renderizar o template para criar módulos
    return render_template('Modulos.html', id=id)

@app.route('/ver_campanha/<type>', methods=['GET'])
@is_logged_in
def ver_campanha(type):
    # Conectar ao banco de dados
    conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')
    cursor = conn.cursor()
    
    # Selecionar campanhas do tipo especificado
    cursor.execute(f"SELECT * FROM campanhas WHERE tipo='{type}'")
    dados = cursor.fetchall()
    
    # Fechar a conexão com o banco de dados
    conn.close()
    
    # Renderizar o template de visualização de campanhas
    return render_template('campanhas.html', campanhas=dados, type=type)

@app.route('/ver_formacao/<int:id>', methods=['GET'])
@is_logged_in
def ver_formacao(id):
    # Conectar ao banco de dados
    conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')
    cursor = conn.cursor()
    
    # Selecionar módulos da formacao
    cursor.execute(f"SELECT * FROM modulos WHERE campanha={id}")
    modulo = cursor.fetchall()
    
    # Selecionar módulos e aulas associadas
    cursor.execute(f"SELECT * FROM modulos JOIN aulas ON modulos.modulo = aulas.modulo WHERE modulos.campanha={id}")
    dados = cursor.fetchall()
    
    # Fechar a conexão com o banco de dados
    conn.close()
    
    # Renderizar o template de visualização de formação
    return render_template('formacao.html', modulos=modulo, formacao=dados, id=id)

@app.route('/ativar_campanha/<int:id>', methods=['GET'])
@is_logged_in
def ativar_campanha(id):
    # Conectar ao banco de dados
    conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')
    cursor = conn.cursor()
    
    # Atualizar o status da campanha para 'ativo'
    cursor.execute(f"UPDATE campanhas SET status='ativo' WHERE id_campanha={id};")
    conn.commit()
    
    # Selecionar todas as campanhas
    cursor.execute(f"SELECT * FROM campanhas;")
    dados = cursor.fetchall()
    
    # Fechar a conexão com o banco de dados
    conn.close()
    
    # Exibir mensagem de sucesso
    flash('Campanha ativada com sucesso', 'success')
    
    # Renderizar o template de visualização de campanhas
    return render_template('campanhas.html', campanhas=dados, type=type)

@app.route('/campanha/<int:id>/<type>', methods=['GET'])
@is_logged_in
def campanha(id, type):
    print(id)
    
    # Conectar ao banco de dados
    connection = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')
    cursor = connection.cursor()
    
    # Se o tipo for 'formacao', selecionar as aulas associadas
    if type == 'formacao':
        cursor.execute(f"SELECT * FROM aulas WHERE id={id};")
        result = cursor.fetchall()
        return render_template('campanha.html', campanha=result, id=id, tipo=type)
    
    # Redirecionar para a visualização da campanha
    return redirect(url_for('campanha_n', id=id, type=type))



@app.route('/create_camp')
@is_logged_in
def create_camp():
    
    base_table_name_to_check = 'campanha'

    try:
        

        # Connect to the PostgreSQL database
        connection = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')
        cursor = connection.cursor()


        if table_exists(cursor, base_table_name_to_check):
            # If the base table exists, create a new table with an auto-incrementing suffix
            new_table_name = get_next_table_name(cursor, base_table_name_to_check)
            create_table(cursor, new_table_name)

            # Include into main campagn list
            cursor.execute('INSERT INTO public.campanhas (orgid, campanha_ref) VALUES (%s, %s)',(session['last_org'],new_table_name))

            connection.commit()

            flash('Campanha criada: '+new_table_name, 'success')
            print(f'Table "{new_table_name}" created.')
        else:
            print(f'Table "{base_table_name_to_check}" does not exist.')

    except Exception as e:
        print(f"Error: {e}")

    finally:

         # Execute query
        cursor.execute('SELECT * FROM campanhas')
        
        dados=cursor.fetchall()

        # Close the database connection
        cursor.close()
        connection.close()

    return render_template('campanhas.html', campanhas=dados)


@app.route('/create_col/<string:id>')
@is_logged_in
def create_col(id):
    # Assuming id is the name of the table to modify
    table_name_to_modify = id
    base_column_name = 'pergunta'
    print('pergunta start')

    try:
        
        # Connect to the PostgreSQL database
        connection = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')
        cursor = connection.cursor()

        
        # Get the next column name
        new_column_name = get_next_column_name(cursor, base_column_name, table_name_to_modify)
        print(new_column_name)

        # Add a new column with the generated name
        add_column(cursor, table_name_to_modify, new_column_name, 'VARCHAR(255)')
        
        # Query
        query = "INSERT INTO display_ref(id,ref) VALUES ('"+id+"_"+new_column_name+"','Inicialise a informacao da pergunta')"

        print(query)

        # Execute query with parameterized value
        cursor.execute(query)
        
        connection.commit()

        result_message = f'Column "{new_column_name}" added to table "{table_name_to_modify}".'
        print(result_message)

        # Create a new table for the new column
        create_table_for_column(cursor, table_name_to_modify, new_column_name)
        connection.commit()
        
        flash(result_message, 'success')

    except Exception as e:
        result_message = f"Error: {e}"
        connection.rollback()

    finally:
        # Execute query
        cursor.execute('SELECT * FROM '+id)
        
        dados=cursor.fetchall()

        # Close the database connection
        cursor.close()
        connection.close()

    return redirect(url_for('campanha_n',id=id))


@app.route('/perguntas/<int:id>/<type>')
@is_logged_in
def perguntas(id, type):
    # Imprimir o ID para depuração
    print(id)
    
    # Conectar ao banco de dados
    conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')
    cursor = conn.cursor()

    # Verificar o ID
    if id == 18512:
        # Se o ID for 18512, selecionar todas as entradas da tabela especificada pelo tipo
        cursor.execute(f"SELECT * FROM {type}")
        dados = cursor.fetchall()
    else:
        # Se o tipo for 'formacao', selecionar todas as entradas da tabela 'questoes_opcoes' onde a questão é igual ao ID
        if type == 'formacao':
            cursor.execute(f"SELECT * FROM questoes_opcoes WHERE questao = {id}")
            dados = cursor.fetchall()
        else:
            # Para outros tipos, selecionar todas as entradas da tabela 'campanha_option' onde a questão é igual ao ID
            cursor.execute(f"SELECT * FROM campanha_option WHERE questao = {id}")
            dados = cursor.fetchall()
    
    # Fechar a conexão com o banco de dados
    conn.close()

    # Renderizar o template de perguntas com os dados obtidos
    return render_template('perguntas.html', dados=dados, pergunta_ref=id, type=type)


@app.route('/survey_dashboard')
def survey_dashboard():
    return render_template('survey_dashboard.html', questions=survey_questions, responses=survey_responses)


@app.route('/dashboard2/<int:id>/<string:type>' , methods=['GET'])
@is_logged_in
def dashboard2(id, type):
    # Connect to the database
    conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')
    cursor = conn.cursor()

    
    if id == 18512:
        cursor.execute(f"SELECT opcao, count_ from {type}; ")
        rows=cursor.fetchall()
        cursor.execute(f"SELECT ref FROM display_ref where id='{type}';")
        table_name = cursor.fetchone()[0]
        

    else:    
       cursor.execute(f"SELECT opcao, count FROM campanha_option where questao ={id}")
       rows = cursor.fetchall()
       cursor.execute(f"SELECT questao FROM campanha_question where questao_nr={id}")
       rows = cursor.fetchone()
       table_name = rows[0]

    
    print(rows[0])

       

    # Prepare data for chart
    labels = [row[0] for row in rows]
    counts = [row[1] for row in rows]

    
    cursor.close()
    conn.close()

    return render_template('dashboard2.html', labels=labels, counts=counts, table_name=table_name)


# Route to render the survey form
@app.route('/survey/<string:survey_name>')
def survey(survey_name):
    # Connect to the database
    conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')
    cursor = conn.cursor()
    
    # Fetch survey title and column titles from the database
    survey_title, questions = get_survey_data(cursor, survey_name)

    return render_template('survey.html', survey_title=survey_title, questions=questions)


# Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))





@app.route('/cliente', methods=['GET'])
@is_logged_in
def clientecad():

    conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')

    cursor = conn.cursor()

    # Execute query
    cursor.execute('SELECT * FROM cliente_vendas WHERE ong IS NULL OR ong = false ORDER BY nome;')
        
    dados=cursor.fetchall()

    # Close connection
    conn.close()

    return render_template('cad-cliente.html', dados = dados)


@app.route('/cliente_srv', methods=['GET'])
@is_logged_in
def cliente_srv():

    conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')

    cursor = conn.cursor()

    # Execute query
    cursor.execute('SELECT * FROM cliente_vendas WHERE srv = true ORDER BY nome;')
        
    dados=cursor.fetchall()

    # Close connection
    conn.close()

    return render_template('cad-cliente_srv.html', dados = dados)


@app.route('/cliente_ong', methods=['GET'])
@is_logged_in
def cliente_ong():

    conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')

    cursor = conn.cursor()

    # Execute query
    cursor.execute("SELECT * FROM cliente_vendas WHERE ong = true ORDER BY nome;")
        
    dados=cursor.fetchall()

    # Close connection
    conn.close()

    return render_template('cad-cliente_ong.html', dados = dados)


#cadastro_cliente
@app.route('/cadastro', methods=['GET', 'POST'])
@is_logged_in
def cadastro ():
    
    form = CadastroForm(request.form)
    
    if request.method == 'POST':

        current_dateTime = datetime.now()
        current_dateTime = str(datetime.date(current_dateTime))+" "+str(datetime.time(current_dateTime))

        conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')

        cursor = conn.cursor()

        # Execute query
        cursor.execute("INSERT INTO cliente_vendas(nome, email, contato, contato_alternativo, city, residence_type, work_phase, sale_phase, ong, email2) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id_vendas",
                       (form.name.data,form.email.data,form.contact1.data,form.contact2.data, form.city.data, form.residence.data,form.phase.data, form.sale.data, form.interested.data, form.email2.data))
        id = cursor.fetchone()[0]
        # Inserir na tabela actividades
        task_title = "Cadastro de novo cliente: " + form.name.data + " no Sistema"       
        insert_query = sql.SQL("INSERT INTO tasks (title, due_date, responsible, accepted_time, completed_time, accepted, completed) VALUES ({}, CURRENT_DATE,{}, now(),now(), 'TRUE','TRUE')")
        cursor.execute(insert_query.format(sql.Literal(task_title), sql.Literal(session['username'])))

        cursor.execute("INSERT INTO Action_rel(usuario, descricao, action, data, cliente, cliente_id) VALUES (%s,%s,%s,%s,%s,%s)",
                       (session['username'], "Cadastro de Novo Cliente",  "Register", datetime.now(), form.name.data,id))
    

        # Commit to DB
        conn.commit()

        # Close connection
        conn.close()

        flash(f'Cliente "{form.name.data}" adicionado com sucesso', 'success')

        return redirect(url_for('clientecad'))

    return render_template('crm.html', form = form)


@app.route('/depedencias/<int:id>', methods=['GET', 'POST'])
@is_logged_in
def depedencias(id):
    conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')
    cursor = conn.cursor()
    cont = request.form['cont']
 
    for i in range(int(cont)):
        i = i+1
        contacto = request.form[f'cont{i}']
        nome = request.form[f'nome{i}']
        cargo = request.form[f'cargo{i}']
        whatsapp = request.form[f'whatsapp{i}']
        email = request.form[f'email{i}']
        
        current_dateTime = datetime.now()
        cursor.execute("INSERT INTO depedencias(ong, nome, cargo, whatsapp, email,contacto, data) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                           (id,nome, cargo,  whatsapp, email,contacto, current_dateTime))
    
    conn.commit()
    conn.close()  
    return redirect(url_for('add_call', id = id))



@app.route('/add_call/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def add_call(id):
    conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM cliente_vendas WHERE id_vendas = %s', (id,))
    client = cursor.fetchone()
    calendar_data = None

    form = TaskForm(request.form)
    current_dateTime = datetime.now()
    current_dateTime = str(datetime.date(current_dateTime)) + " " + str(datetime.time(current_dateTime))


    if request.method == 'POST':
        cursor.execute("INSERT INTO Action_rel(usuario, descricao, action, data, cliente, cliente_id) VALUES (%s,%s,%s,%s,%s,%s)",
                       (session['username'], form.text.data,  form.actionNow.data, datetime.now(), client[0], client[4]))
    
        conn.commit()

        cursor.execute("INSERT INTO calendar(usuario, descricao, data, next_action, time, cliente, id_cliente, hora_actual) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                       (session['username'], form.text.data, form.calendar.data, form.action.data, form.time.data, client[0], client[4], current_dateTime))
        conn.commit()

        # Inserir na tabela actividades
        task_title = "Follow-up feito ao cliente: " + client[0] + " no Sistema"       
        insert_query = sql.SQL("INSERT INTO tasks (title, due_date, responsible, accepted_time, completed_time, accepted, completed) VALUES ({}, CURRENT_DATE,{}, now(),now(), 'TRUE','TRUE')")
        cursor.execute(insert_query.format(sql.Literal(task_title), sql.Literal(session['username'])))
        conn.commit()
        
        conn.close()

        print(client)

        flash(f'Update: {client[0]}', 'success')

        if client[11]==True:
            return redirect(url_for('cliente_srv'))
        if client[9]==True:
            return redirect(url_for('cliente_ong'))
        
        return redirect(url_for('clientecad'))

    if request.method == 'GET':
        cursor.execute('SELECT * FROM cliente_vendas WHERE id_vendas = %s ;', (id,))
        calendar = cursor.fetchall()

        cursor.execute('SELECT * FROM calendar WHERE id_cliente = %s ORDER BY data DESC;', (id,))
        calendar_data = cursor.fetchall()

        cursor.execute('SELECT * FROM depedencias WHERE ong = %s ORDER BY data DESC;', (id,))
        depedencias = cursor.fetchall()
        print(calendar_data)
        conn.close()

    return render_template('/task.html', client=client,calendar=calendar, calendar_data=calendar_data, depedencias=depedencias, form=form)


@app.route('/tarefas_diarias_data/<string:data>', methods=['GET', 'POST'])
@is_logged_in
def tarefas_diarias_data(data):
     return redirect(url_for('tarefas_diarias', data=data))    


@app.route('/tarefas_diarias/<string:data>', methods=['GET', 'POST'])
@is_logged_in
def tarefas_diarias(data):

    datas=[]
    today = datetime.now().date()
    for i in range(0,5):
        dat = today-timedelta(days=i)
        datas.append(dat)

    print(data)     
   
    conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')
    cursor = conn.cursor()
    today = datetime.now().date()
    yesterday = today - timedelta(days=2)
    cursor.execute(F"SELECT * FROM Action_rel where data ='{data}'")
    calendar_data = cursor.fetchall()
    print(F"SELECT * FROM Action_rel where data ='{data}'")
    conn.close()

    Marta ={}
    call = 0
    meeting =0
    proposal=0
    register = 0

    calls = 0
    meetings =0
    proposals=0
    registers = 0
    categorias = ["Call","Meeting", "Submission proposal"] 
    for data in calendar_data:

        if data[1] == 'Marta':
            call = sum(1 for calendar in calendar_data if calendar[3] == 'Call' and calendar[1]=='Marta')
            meeting = sum(1 for calendar in calendar_data if calendar[3] == "Meeting" and calendar[1]=="Marta")
            proposal = sum(1 for calendar in calendar_data if calendar[3] == "submission of proposal" and calendar[1]=="Marta")
            register = sum(1 for calendar in calendar_data if calendar[3] == "Register" and calendar[1]=="Marta")


        if data[1] == 'Sara':
            calls = sum(1 for calendar in calendar_data if calendar[3] == "Call" and calendar[1]=="Sara")
            meetings = sum(1 for calendar in calendar_data if calendar[3] == "Meeting" and calendar[1]=="Sara")
            proposals = sum(1 for calendar in calendar_data if calendar[3] == "submission of proposal" and calendar[1]=="Sara")
            registers = sum(1 for calendar in calendar_data if calendar[3] == "Register" and calendar[1]=="Sara")


    Marta = [call, meeting, proposal,register]
    Sara = [calls, meetings, proposals,registers]
    print(Marta)
    print(Sara)
    return render_template('tarefas.html',datas=datas ,categorias=categorias, Marta=Marta ,Sara=Sara)

    
@app.route('/pagamento/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def pagamento(id):
        

        conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')

        cursor = conn.cursor()

        cursor.execute('SELECT * FROM requisicao WHERE id_requisicao = %s', (id,))

        requisicao = cursor.fetchone()

        form = RequisicaoForm(request.form)
        form.cliente.data = requisicao[3]
        form.requisicao.data = requisicao[1]
        form.valor.data = Decimal(requisicao[5])
        form.estado.data = requisicao[7]
        
   
        if request.method == 'POST':
                estado = request.form['estado']

                
                cursor.execute("INSERT INTO pagamento(destinatario,observacao, estado, valor) VALUES (%s,%s,%s,%s)",(form.destinatario.data,form.observacao.data, form.estado1.data,form.valor.data))  
                
                
                cursor.execute("UPDATE requisicao SET estado=%s WHERE id_requisicao=%s", [estado, id])


                conn.commit()
                
                conn.close()
                return redirect(url_for('requisicoes'))
   
        return render_template('pagamento.html', form = form)




@app.route('/credencial')
@is_logged_in
def credencial():

    conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM credenciais ORDER BY id_credencial")

    dados=cursor.fetchall()


    conn.close()

    return render_template('credencial.html', credencial = dados)

@app.route('/propostas')
@is_logged_in
def propostas():

    conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM propostas")

    dados=cursor.fetchall()


    conn.close()

    return render_template('propostas.html', dados = dados)


@app.route('/addcredencial', methods=['GET', 'POST'])
@is_logged_in
def addcredencial():
    
    form = addcredencialForm(request.form)
    
    if request.method == 'POST':

        current_dateTime = datetime.now()
        current_dateTime = str(datetime.date(current_dateTime))+" "+str(datetime.time(current_dateTime))
        print(current_dateTime)

        conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')

        cursor = conn.cursor()

   
        cursor.execute("INSERT INTO credenciais(cliente, password, local, usuario, ip_adress, ip_publico,senha_wifi,user_router,senha_router,ipadress_router) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(str(form.cliente.data),str(form.password.data),str(form.local.data),str(form.user.data),str(form.ipadress.data), str (form.ippublico.data),str(form.senha_wifi.data),str(form.user_router.data),str(form.senha_router.data),str(form.ipadress_router)))
        
        
        conn.commit()

        
        conn.close()

        flash('Pedido adicinado com Successo', 'success')

        return redirect(url_for('credencial'))

    return render_template('addcredencial.html', form = form)


@app.route('/ivr_test')
@is_logged_in
def ivr_test():
    return render_template('ivr_test.html')


# IVR route
@app.route('/ivr/<string:campaign>', methods=['POST'])
def ivr(campaign):
    response = VoiceResponse()

    if campaign == 'Simples':
       response.play(CAMPANHA_AUDIO_URL[0]) 

    elif campaign == 'formacao':     
       response.play(CAMPANHA_AUDIO_URL[0])
    else:
        response.play(QUESTION_AUDIO_URLS[0])

        current_question_index = request.args.get('current_question_index', default=1, type=int)
        with response.gather(num_digits=1, action=url_for('handle_question', current_question_index=current_question_index,campaign=campaign), method='POST', input='dtmf') as gather:
           gather.play(QUESTION_AUDIO_URLS[current_question_index])     
          

    return str(response), 200, {'Content-Type': 'application/xml'}

# Handle question route
@app.route('/handle_question', methods=['POST'])
def handle_question():
    selected_option = request.form.get('Digits')
    phone_number = request.form.get('To')
    current_question_index = int(request.args.get('current_question_index'))
    campaign=request.args.get('campaign')

    response = VoiceResponse()

    if current_question_index < len(QUESTION_AUDIO_URLS) - 1:  # Not the concluding message
        try:
            selected_option = int(selected_option)
            if selected_option < 1 or selected_option > 5:
                raise ValueError()
        except ValueError:
            # Handle invalid input by redirecting back to /ivr with current_question_index
            return redirect(url_for('ivr', current_question_index=current_question_index))

        # Save the survey response to the database
        save_survey_response(phone_number, current_question_index, selected_option, campaign)

        # Continue with the next question
        next_question_index = current_question_index + 1
        with response.gather(num_digits=1, action=url_for('handle_question', current_question_index=next_question_index,campaign=campaign), method='POST', input='dtmf') as gather:
            gather.play(QUESTION_AUDIO_URLS[next_question_index])

    else:  # Concluding message
        response.play(QUESTION_AUDIO_URLS[-1])

    return str(response), 200, {'Content-Type': 'application/xml'}


def get_call_duration(start_time_str, end_time_str):
    if start_time_str and end_time_str:
        start_time = datetime.strptime(start_time_str, '%a, %d %b %Y %H:%M:%S %z')
        end_time = datetime.strptime(end_time_str, '%a, %d %b %Y %H:%M:%S %z')
        return (end_time - start_time).total_seconds() / 60
    else:
        return 0  # Call was not answered


@app.route('/campaign_status', methods=['GET','POST'])
@is_logged_in
def campaign_status():
    return render_template('campaign_status.html')


@app.route('/get_call_status', methods=['GET'])
@is_logged_in
def get_call_status():
    # Initialize a list to store call statuses
    call_statuses = []
    dados = {}
    org_id = session['last_org']

    conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')
    cursor = conn.cursor()
    
    cursor.execute(f"SELECT * FROM contacts WHERE id in (select id_cont from contact_org where org_id = '{org_id}') Limit 1;")
    contacts = cursor.fetchone()
    conn.close()
    for key, dado in contacts[6].items():
            dados[key] = 'No data'

    # Fetch call status using Twilio REST API
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    for call in client.calls.list( start_time=datetime.now()):

        if call.end_time:
            end_time = call.end_time.strftime('%Y-%m-%d %H:%M:%S')
        else:
            end_time = 'N/A'
        # Calculate call duration in minutes
        duration_minutes = 0
        if call.start_time and call.end_time:
            start_time = call.start_time
            end_time = call.end_time
            duration_minutes = (end_time - start_time).total_seconds() / 60
            if call.status == 'busy' or call.status == 'no-answer':
                duration_minutes = 0
        
        conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')
        cursor = conn.cursor()
        numero = call.to[4:]
        
        cursor.execute(f"SELECT * FROM contacts WHERE phone = '{numero}';")
        contact = cursor.fetchone()
        conn.close()
        
        
        # Extração de dados de contact[6] (assumindo que é um dicionário)
        dados_contact = {}
        if contact is not None:
            # Certifique-se de que contact tem pelo menos 7 elementos (índice 6 existe)
            if len(contact) > 6 and isinstance(contact[6], dict):
                dados_contact = {}
                for key, dado in contact[6].items():
                    dados_contact[key] = dado
                   
        else:
          # Definir valores padrão caso contact seja None
           dados_contact = dados

        # Append call status to the list
        call_status = {
             **dados_contact,
            'sid': call.sid,
            'status': call.status,
            'phone_number': call.to,
            'start_time': call.start_time.strftime('%Y-%m-%d %H:%M:%S'),
            'end_time': call.end_time.strftime('%Y-%m-%d %H:%M:%S'),
            'duration_minutes': round(duration_minutes, 2)
        }
        call_statuses.append(call_status)
        print(call_statuses)
        
        try:
           conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')
           cursor = conn.cursor()
           numero = call.to[4:]
                 
           cursor.execute(f"SELECT * FROM contacts WHERE phone = '{numero}';")
           contact = cursor.fetchone()
    
           if contact is not None:
            cursor.execute("""
              INSERT INTO call_logs (contact_id, status, phone_number, start_time, end_time, duration_minutes)
              VALUES (%s, %s, %s, %s, %s, %s);
              """,( contact[0],
                    call_status['status'],
                    call_status['phone_number'],
                    call_status['start_time'],
                    call_status['end_time'],
                    call_status['duration_minutes']
                   ) )
           conn.commit()
           cursor.close()
           conn.close()
        except psycopg2.Error as e:
          pass 

    # Return call statuses as JSON response
    return render_template('campaign_status.html', call_statuses=call_statuses, dados=dados)


@app.route('/get_call_day/<day>', methods=['GET'])
@is_logged_in
def get_call_day(day):
   
    day = int(day)    
    
    return redirect(url_for('get_call_status2', day = day, csv = 0))

@app.route('/get_call', methods=['GET'])
@is_logged_in
def get_call():
      
    return redirect(url_for('get_call_status'))


def gerar_csv(call_statuses, filename='call_statuses.csv'):
    # Verifica se há dados para escrever
    if not call_statuses:
        print("Nenhum dado disponível para escrever no CSV.")
        return
    
    # Obtém as chaves do primeiro dicionário como cabeçalhos do CSV
    output = io.BytesIO()
    
    # Usa o modo de texto e encoding para escrever no BytesIO
    text_io = io.TextIOWrapper(output, encoding='utf-8', newline='')
  
    try: 
        # Define os cabeçalhos
        fieldnames = call_statuses[0].keys()
        
        # Cria o escritor do CSV
        writer = csv.DictWriter(text_io, fieldnames=fieldnames)
        
        # Escreve os cabeçalhos e os dados
        writer.writeheader()
        for status in call_statuses:
            writer.writerow(status)
    
        # Certifica-se de que todos os dados foram escritos
        text_io.flush()
    
        # Move o cursor para o início do BytesIO
        output.seek(0)
        
        # Envia o arquivo como uma resposta de download
        return send_file(output, mimetype='text/csv', as_attachment=True, download_name='call_statuses.csv')
    finally:
        # Fecha o TextIOWrapper sem fechar o BytesIO
        text_io.detach()



@app.route('/get_call_status2/<day>/<csv>', methods=['GET'])
@is_logged_in
def get_call_status2(day,csv):

    
    # Initialize a list to store call statuses
    call_statuses = []
    dados = {}
    org_id = session['last_org']

    conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')
    cursor = conn.cursor()
    
    cursor.execute(f"SELECT * FROM contacts WHERE id in (select id_cont from contact_org where org_id = '{org_id}') Limit 1;")
    contacts = cursor.fetchone()
    cursor.close()
    conn.close()

    for key, dado in contacts[6].items():
            dados[key] = 'No data'

    day = int(day)  
    print(day)
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    
    
    conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')
    cursor = conn.cursor()  
    if day > 0:
      start_date = datetime.now() - timedelta(days=day)

      # Filtrar as chamadas desde a data de início até a data atual  
      cursor.execute(f"SELECT * FROM call_logs cl join contacts ct on cl.contact_id = ct.id WHERE cl.start_time > '{start_date}';")
      calls = cursor.fetchall()

    else:    
      cursor.execute(f"SELECT * FROM call_logs cl join contacts ct on cl.contact_id = ct.id;")
      calls = cursor.fetchall()
      
      # Extração de dados de contact[6] (assumindo que é um dicionário)
    dados_contact = {}
    if calls is not None:
      for call in calls:
    
        # Certifique-se de que contact tem pelo menos 7 elementos (índice 6 existe)
        if len(call) > 6 and isinstance(call[13], dict):
            dados_contact = {}
            for key, dado in call[13].items():
                dados_contact[key] = dado
               
    
        # Criando o dicionário call_status
        call_status = {
             **dados_contact,  # Mescla os dados do dicionário dados_contact
            'status': call[2],
            'phone_number': call[3],
            'start_time': call[4],
            'end_time': call[5],
            'duration_minutes': call[6]
        }
        call_statuses.append(call_status) 
       

    
    if csv == '1':
       return  gerar_csv(call_statuses)
            
    else:
       
       return render_template('teste2.html',dados = dados, call_statuses=call_statuses, day=day)

# Start IVR campaign route
@app.route('/start_ivr_campaign', methods=['POST'])
def start_ivr_campaign():
    # Extract phone numbers from the HTML form
    phone_numbers = request.form.get('phone_numbers')
    campaign = request.form.get('campaign')

    print(phone_numbers)
    conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')
    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM contacts WHERE phone = '{phone_numbers}';")
    contact = cursor.fetchone()
    conn.close()
    tamanho = 4 

    #if contact is None:
    #    
    #    flash('Contacto inexistente', 'success')
    #    return redirect(url_for('ivr_test'))

    #else:   
    print(contact) 
    print(phone_numbers)
    print(campaign)
    
    url='https://insightsap.com/ivr/'+campaign

    for number in phone_numbers:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        call = client.calls.create(
            url=url,  # URL for handling IVR logic
            to=number,
            from_=TWILIO_PHONE_NUMBER
        )

    return redirect(url_for('get_call_status'))


@app.route('/start_ivr_group', methods=['POST'])
def start_ivr_group():
    # Extract phone numbers from the HTML form
    grupo = request.form['grupo']
    #campaign = request.form.get('campaign')

    campaign = 'teste'

    conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')
    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM contacts JOIN contact_org ON contacts.id = contact_org.id_cont WHERE contact_org.grupo_id = {grupo};")
    contact = cursor.fetchall()
    cursor.close()
    conn.close()
    print(contact)
    print(grupo)

    #if contact is None:
    #    
    #    flash('Contacto inexistente', 'success')
    #    return redirect(url_for('ivr_test'))

    #else:   
    print(campaign)
    
    url='https://insightsap.com/ivr/'+campaign

    for number in contact:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        call = client.calls.create(
            url=url,  # URL for handling IVR logic
            to=number[3],
            from_=TWILIO_PHONE_NUMBER
        )

    return redirect(url_for('get_call_status'))



@app.route('/audio/<path:filename>')
def serve_audio(filename):
    # Serve the audio file from the 'static' directory
    return send_from_directory('audio', filename)


# Assign Campaign

@app.route('/assign_camp/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def assign_camp(id):

    conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')
    
    # Create cursor
    cursor = conn.cursor()

    # Get article by id
    cursor.execute("SELECT * FROM campanhas WHERE id_campanha = %s", [id])

    campanha = cursor.fetchone()
    
    form = CampForm(request.form)

    # Populate tikrts form fields
    form.projecto.data = campanha[2]
    

    if request.method == 'POST':
        projecto = request.form['projecto']

        # Create Cursor
        cursor = conn.cursor()
        
        # Execute
        cursor.execute("UPDATE campanhas SET projecto=%s WHERE id_campanha=%s",(projecto,id))
        # Commit to DB
        conn.commit()

        #Close connection
        conn.close()

        flash('Campanha atualizada', 'success')

        return redirect(url_for('campanhas'))

    return render_template('assign_camp.html', form=form)

    

# Assign question
@app.route('/assign_question/<int:camp>/<int:id>/<string:type>', methods=['GET', 'POST'])
@is_logged_in
def assign_question(camp,id,type):

    conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')
    
    # Create cursor
    cursor = conn.cursor()   
   
    # Get article by id
    cursor.execute(f"SELECT * FROM campanha_question WHERE questao_id= {id};")

    pergunta = cursor.fetchone()
    
    if request.method == 'POST':
           #verifica se o fromulario e da inserssao de audio
           pergunta = request.form['pergunta']
           
           cursor.execute("UPDATE campanha_question SET descricao=%s WHERE questao_id = %s",(pergunta,id))
           
           # Commit to DB
           conn.commit()
   
           #Close connection
           conn.close()
   
           flash('Pergunta atualizada', 'success')
           type ='inquerito'
           return redirect(url_for('campanha_n', id=camp, type =type))
        
    
  
    form = PerguntaForm(request.form)
    form.pergunta.data = pergunta[2]

    
    # Obtém os idiomas já utilizados para a questão atual
    cursor.execute("SELECT * FROM campanha_audio WHERE questao_id = %s;", (id,))
    idiomas_usados = cursor.fetchall()
    print(idiomas_usados)
    
    # Obtém todas as opções de idiomas disponíveis
    choices = request_languge()
    
    # Cria um conjunto com os idiomas já usados
    idiomas_usados_set = {idioma[3] for idioma in idiomas_usados}
    
    # Filtra as opções removendo os idiomas já usados
    options = [choice for choice in choices if choice[1] not in idiomas_usados_set]
    
    print(options)      
    
   
    return render_template('assign_question.html', form=form, type = type,camp= camp, id=id, options = options)


@app.route('/addfunction', methods=['GET', 'POST'])
@is_logged_in
def addfunction():
    
    form = funcaoForm(request.form)
    
    if request.method == 'POST':

        current_dateTime = datetime.now()
        current_dateTime = str(datetime.date(current_dateTime))+" "+str(datetime.time(current_dateTime))
        print(current_dateTime)

        conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')

        cursor = conn.cursor()

   
        cursor.execute("INSERT INTO funcao_software(funcao, estado, usuario, data1) VALUES (%s,%s,%s,%s)",(str(form.funcao.data),str(form.estado.data), session['username'],current_dateTime))
        
        
        conn.commit()

        
        conn.close()

        return redirect(url_for('funcao'))

    return render_template('addfunction.html', form = form)


@app.route('/candidaturas')
def formulario():
    return render_template('formulario.html')

@app.route('/submit', methods=['POST'])
def submit():
    criar_tabela()
    conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO respostas (nome, pergunta1, pergunta2, pergunta3, pergunta4, pergunta5, pergunta6, pergunta7, pergunta8, pergunta9, pergunta10, pergunta11, pergunta12, pergunta13, pergunta14, pergunta15)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        request.form['nome'],
        request.form['pergunta1'],
        request.form['pergunta2'],
        request.form['pergunta3'],
        request.form['pergunta4'],
        request.form['pergunta5'],
        request.form['pergunta6'],
        request.form['pergunta7'],
        request.form['pergunta8'],
        request.form['pergunta9'],
        request.form['pergunta10'],
        request.form['pergunta11'],
        request.form['pergunta12'],
        request.form['pergunta13'],
        request.form['pergunta14'],
        request.form['pergunta15']
    ))
    conn.commit()
    conn.close()
    return 'Respostas enviadas com sucesso!'


@app.route('/contacts_by_collaborator', methods=['GET', 'POST'])
def contacts_by_collaborator():
    if request.method == 'POST':
        start_date = request.form['start_date']
        end_date = request.form['end_date']

        print(start_date)
        print(end_date)

        # Connect to the database
        conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')
        cur = conn.cursor()
        
        # Query the database
        cur.execute("""
            SELECT colaborador, COUNT(DISTINCT contacto) AS num_unique_contacts
            FROM public.clientes
            WHERE data_cadastro BETWEEN %s AND %s
            GROUP BY colaborador
        """, (start_date, end_date))
        rows = cur.fetchall()

        cur.execute("""    
            SELECT nome, contacto, email, colaborador, data_cadastro
	        FROM public.clientes WHERE data_cadastro BETWEEN %s AND %s
        """, (start_date, end_date))
        rows2 = cur.fetchall()
        cur.close()
        
        # Process the data
        data = [{'colaborador': row[0], 'num_unique_contacts': row[1]} for row in rows]
        
        print(data)

        # Render the template with the data
        return render_template('metas_srv.html', data=data, start_date = start_date, end_date=end_date, rows2=rows2)

    # If it's a GET request, simply render the form page
    return render_template('form.html')


@app.route('/respostas')
#@is_logged_in
def ver_respostas():
    respostas=obter_respostas()
    return render_template('ver_respostas.html', respostas=respostas)


# Rota para exibir o formulário
@app.route('/cadastro_clientes')
def cadastro_clientes():
    return render_template('cadastro_clientes.html')


# Rota para enviar os dados do formulário SRV
@app.route('/submit_srv', methods=['POST'])
def submit_srv():
    if request.method == 'POST':

        conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')
        cur = conn.cursor()

        # Verificar se a tabela clientes existe, se não, criar
        cur.execute('''CREATE TABLE IF NOT EXISTS clientes (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(255) NOT NULL,
                tipo VARCHAR(10) NOT NULL,
                quantidade_carros INTEGER NOT NULL,
                contacto VARCHAR(20) NOT NULL,
                email VARCHAR(255) NOT NULL,
                pais VARCHAR(100) NOT NULL,
                provincia VARCHAR(100) NOT NULL,
                bairro VARCHAR(100) NOT NULL,
                colaborador VARCHAR(50) NOT NULL,
                data_cadastro DATE NOT NULL DEFAULT CURRENT_DATE,
                hora_cadastro TIME NOT NULL DEFAULT CURRENT_TIME
            )''')
        conn.commit()

        nome = request.form['nome']
        tipo = request.form['tipo']
        quantidade_carros = request.form['quantidade_carros']
        contacto = request.form['contacto']
        email = request.form['email']
        pais = request.form['pais']
        provincia = request.form['provincia']
        bairro = request.form['bairro']
        Colaborador = request.form['Colaborador']

        # Capturar data e hora atual
        data_atual = datetime.now().date()
        hora_atual = datetime.now().time()

        

        # Inserir dados no banco de dados
        cur.execute("INSERT INTO clientes (nome, tipo, quantidade_carros, contacto, email, pais, provincia, bairro, Colaborador, data_cadastro, hora_cadastro) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (nome, tipo, quantidade_carros, contacto, email, pais, provincia, bairro, Colaborador,  data_atual, hora_atual))
        
        # Execute query
        cur.execute("INSERT INTO cliente_vendas(nome, email, contato, city, srv ) VALUES (%s,%s,%s,%s,%s)",(nome,email,contacto,bairro,'true'))
        
        
        conn.commit()

        return 'Dados enviados com sucesso!'


# Gerar dados fictícios
num_registros = 1000
genero = np.random.choice(['Masculino', 'Feminino'], num_registros)
provincia = np.random.choice(['Maputo', 'Gaza', 'Inhambane', 'Sofala', 'Manica', 'Tete', 'Zambezia', 'Nampula', 'Niassa', 'Cabo Delgado'], num_registros)
idade = np.random.randint(18, 80, num_registros)  # Gera idades entre 18 e 79 anos
completado = np.random.choice([True, False], num_registros)

# Calcular taxas de conclusão por género
completado_por_genero = {'Masculino': {'Completado': 0, 'Não Completado': 0}, 'Feminino': {'Completado': 0, 'Não Completado': 0}}
for g, c in zip(genero, completado):
    if c:
        completado_por_genero[g]['Completado'] += 1
    else:
        completado_por_genero[g]['Não Completado'] += 1

# Calcular taxas de conclusão por província
completado_por_provincia = {}
for p in set(provincia):
    completado_por_provincia[p] = {'Completado': sum((p == provincia) & completado), 'Não Completado': sum((p == provincia) & ~completado)}

# Calcular taxa de conclusão geral da campanha
taxa_conclusao_geral = sum(completado) / num_registros

# Calcular porcentagem de conclusão por província
porcentagens_por_provincia = {p: completado_por_provincia[p]['Completado'] / (completado_por_provincia[p]['Completado'] + completado_por_provincia[p]['Não Completado']) * 100 for p in completado_por_provincia}

# Agrupar idades em faixas etárias
bins = [18, 30, 40, 50, 60, 70, 80]
idades_por_faixa = np.histogram(idade, bins=bins)[0]

# Calcular taxas de conclusão por faixa etária
completado_por_faixa = {}
for i in range(len(bins)-1):
    faixa_etaria = f'{bins[i]}-{bins[i+1]}'
    completado_por_faixa[faixa_etaria] = {'Completado': sum((idade >= bins[i]) & (idade < bins[i+1]) & completado), 'Não Completado': sum((idade >= bins[i]) & (idade < bins[i+1]) & ~completado)}

# Gerar gráficos Plotly
figura_genero = go.Figure(data=[
    go.Bar(name='Completado', x=list(completado_por_genero.keys()), y=[v['Completado'] for v in completado_por_genero.values()]),
    go.Bar(name='Não Completado', x=list(completado_por_genero.keys()), y=[v['Não Completado'] for v in completado_por_genero.values()])
])
grafico_genero = figura_genero.to_html(full_html=False)

figura_provincia = go.Figure(data=[
    go.Bar(name='Completado', x=list(completado_por_provincia.keys()), y=[v['Completado'] for v in completado_por_provincia.values()]),
    go.Bar(name='Não Completado', x=list(completado_por_provincia.keys()), y=[v['Não Completado'] for v in completado_por_provincia.values()])
])
grafico_provincia = figura_provincia.to_html(full_html=False)

# Gerar gráfico para a taxa de conclusão geral
figura_geral = go.Figure(data=go.Indicator(
    mode="gauge+number",
    value=taxa_conclusao_geral,
    title={'text': "Taxa de Conclusão Geral"},
    gauge={'axis': {'range': [0, 1]}, 'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 0.5}}))
grafico_geral = figura_geral.to_html(full_html=False)

# Calcular taxas de conclusão por faixa etária
taxas_conclusao_faixa = {faixa: round(completado_por_faixa[faixa]['Completado'] / (completado_por_faixa[faixa]['Completado'] + completado_por_faixa[faixa]['Não Completado']) * 100, 2) for faixa in completado_por_faixa}

# Gerar gráfico de barras para a porcentagem de conclusão por faixa etária
figura_faixa_etaria = go.Figure(data=go.Bar(
    x=list(taxas_conclusao_faixa.keys()),
    y=list(taxas_conclusao_faixa.values()),
    text=list(taxas_conclusao_faixa.values()),
    textposition='auto',
    marker_color='green'
))
grafico_faixa_etaria = figura_faixa_etaria.to_html(full_html=False)

# Modificar a rota para usar '/dashboard_demo'
@app.route('/dashboard_demo')
def dashboard_demo():
    return render_template('dashboard_demo.html', grafico_genero=grafico_genero, grafico_provincia=grafico_provincia, grafico_geral=grafico_geral, grafico_faixa_etaria=grafico_faixa_etaria)

# Esta deve ser sempre a ultima funcao
@app.route("/<name>")
def hello(name):
    flash('Pagina '+name+ ' nao existe', 'danger')
    return render_template('home.html')


# FUNCAO DE RELATORIO DE OBRAS(AUTOMACAO)
def relatorio_obra_db_connection():
    """Função para obter uma conexão com o banco de dados"""
    return  psycopg2.connect('postgresql://admin:AXjwTaMmH88i7x0G1rNwzSwhmnhYlIdo@dpg-co2n3ggl6cac73br3680-a.frankfurt-postgres.render.com/relatorio_obra')



@app.route('/Relatorio_obra')
@is_logged_in
def Relatorio_obra():
    try:
        # Conectar ao banco de dados PostgreSQL
       with relatorio_obra_db_connection() as conn:
        cur = conn.cursor()
        
        # Recuperar todos os clientes
        cur.execute("SELECT * FROM cliente")
        clientes = cur.fetchall()
        
        conn.commit()
        cur.close()
        conn.close()
        
        # Renderiza o template com a lista de clientes
        return render_template('formulario_de_obra.html', clientes=clientes)
    except psycopg2.Error as e:
        # Exibe uma página de erro caso ocorra um problema
        return render_template('formulario_de_obra.html')


@app.route('/ver_relatorio/<int:id>')
@is_logged_in
def ver_relatorio(id):
    try:
        # Conectar ao banco de dados PostgreSQL
       with relatorio_obra_db_connection() as conn:
        cur = conn.cursor()
        
        # Recuperar detalhes do relatório, cliente e dificuldades associadas ao relatório
        cur.execute("""
            SELECT
                relatorios.id AS relatorio_id,
                relatorios.relatorio,
                relatorios.status AS status_relatorio,
                relatorios.hora_entrada,
                relatorios.hora_saida,
                relatorios.data,
                cliente.id AS cliente_id,
                cliente.nome AS cliente_nome,
                dificuldades.id AS dificuldade_id,
                dificuldades.dificuldade,
                dificuldades.status AS status_dificuldade
            FROM
                relatorios
            JOIN
                cliente ON relatorios.cliente_id = cliente.id
            JOIN
                dificuldades ON relatorios.id = dificuldades.rel_id
            WHERE
                relatorios.id = %s
        """, (id,))
        relatorios = cur.fetchall()
        
        cur.close()
        conn.close()
        
        # Renderiza o template com os detalhes do relatório
        return render_template('ver_relatorio.html', relatorios=relatorios)
    except psycopg2.Error as e:
        # Exibe uma página de erro caso ocorra um problema
        error_msg = f"Erro ao fazer a transação: {e}"
        return render_template('erro.html', error=error_msg)


@app.route('/pdf_obra')
@is_logged_in
def pdf_obra():
    user = True
    try:
        # Conectar ao banco de dados PostgreSQL
       with relatorio_obra_db_connection() as conn:
        cur = conn.cursor()
        
        # Recuperar todos os relatórios ordenados por data
        cur.execute("""
            SELECT 
                relatorios.id,
                relatorios.relatorio,
                relatorios.status,
                relatorios.hora_entrada,
                relatorios.hora_saida,
                relatorios.data,
                relatorios.cliente_id,
                cliente.nome AS nome_cliente
            FROM 
                relatorios
            JOIN 
                cliente ON relatorios.cliente_id = cliente.id 
            ORDER BY relatorios.data;
        """)
        relatoriopdf = cur.fetchall()
        
        conn.close()
        
        today = datetime.now().date()
        
        # Renderiza o template com os dados dos relatórios
        return render_template('relatorio_de_obra_pdf.html', user=user, relatorios=relatoriopdf, today=today)
    except psycopg2.Error as e:
        # Exibe uma página de erro caso ocorra um problema
        error_msg = f"Erro ao fazer a transação: {e}"
        return render_template('erro.html', error=error_msg)


@app.route('/deletar_relatorio/<int:id>', methods=['GET','POST'])
def deletar_relatorio(id):
    try:
        # Conectar ao banco de dados PostgreSQL
       with relatorio_obra_db_connection() as conn:
        cur = conn.cursor()
        
        # Deletar dificuldades associadas ao relatório
        cur.execute("DELETE FROM dificuldades WHERE rel_id = %s;", (id,))
        conn.commit()
        
        # Deletar o relatório
        cur.execute("DELETE FROM relatorios WHERE id = %s;", (id,))
        conn.commit()
        
        conn.close()
        
        flash = "Relatório removido com sucesso"
        return redirect(url_for('pdf_obra'))
    except psycopg2.Error as e:
        # Exibe uma página de erro caso ocorra um problema
        error_msg = f"Erro ao fazer a transação: {e}"
        return render_template('erro.html', error=error_msg)


# Função para submissão de relatório de obra
@app.route('/submit_rel', methods=['POST'])
def submit_rel():
    relatorio = request.form['relatorio']
    cliente = request.form['cliente']
    status = request.form['status']
    dificuldade = request.form['dificuldade']
    hora_chegada = request.form['tempo']
    hora_saida = request.form['hora']
    data_atual = datetime.now().date()

    try:
        # Conectar ao banco de dados PostgreSQL
       with relatorio_obra_db_connection() as conn:
        cur = conn.cursor()
        
        # Inserir novo relatório
        cur.execute("INSERT INTO relatorios(relatorio, status, hora_entrada, hora_saida, data, cliente_id) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id", (relatorio, status, hora_chegada, hora_saida, data_atual, cliente,))
        relatorio_id = cur.fetchone()[0]
        conn.commit()
        
        # Inserir dificuldade associada ao relatório
        cur.execute("INSERT INTO dificuldades(rel_id, dificuldade, status) VALUES (%s, %s, %s)", (relatorio_id, dificuldade, 'Pendentes',))
        conn.commit()
        
        cur.close()
        cur = conn.cursor()
        
        # Recuperar informações do cliente associado
        cur.execute("SELECT * FROM cliente WHERE id = %s", (cliente,))
        cliente = cur.fetchone()
        cur.close()
        conn.close()
        
        sucesso = "O seu relatório foi concluído com sucesso"
        return render_template('relatorio_de_obra_pdf.html', relatorio_id=relatorio_id, cliente=cliente)
    except psycopg2.Error as e:
        # Exibe uma página de erro caso ocorra um problema
        error_msg = f"Erro ao fazer a transação: {e}"
        return render_template('erro.html', error=error_msg)
 

@app.route('/Gerir_clientes')
@is_logged_in
def gerir_clientes():
    #Exibe a lista de clientes
    try:
        with relatorio_obra_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM cliente")
                clientes = cur.fetchall()
        return render_template('gestao_clientes.html', clientes=clientes)
    except psycopg2.Error as e:
        error_msg = f"Erro ao fazer a transação: {e}"
        return render_template('erro.html', error=error_msg)

@app.route('/novo_cliente', methods=['POST'])
def novo_cliente():
    #Adiciona um novo cliente
    cliente = request.form.get('cliente')
    if not cliente:
        flash("Nome do cliente é obrigatório", 'error')
        return redirect(url_for('gerir_clientes'))

    try:
        with relatorio_obra_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO cliente (nome) VALUES (%s) RETURNING id", (cliente,))
                conn.commit()
                cur.execute("SELECT * FROM cliente")
                clientes = cur.fetchall()
        flash("Cliente inserido com sucesso", 'success')
        return render_template('gestao_clientes.html', clientes=clientes)
    except psycopg2.Error as e:
        error_msg = f"Erro ao fazer a transação: {e}"
        return render_template('erro.html', error=error_msg)

@app.route('/edit_cliente/<int:id>', methods=['POST'])
def edit_cliente(id):
    #Atualiza um cliente existente
    cliente = request.form.get('cliente')
    if not cliente:
        flash("Nome do cliente é obrigatório", 'error')
        return redirect(url_for('gerir_clientes'))

    try:
        with relatorio_obra_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE cliente SET nome = %s WHERE id = %s", (cliente, id))
                conn.commit()
                cur.execute("SELECT * FROM cliente")
                clientes = cur.fetchall()
        flash("Cliente atualizado com sucesso", 'success')
        return render_template('gestao_clientes.html', clientes=clientes)
    except psycopg2.Error as e:
        error_msg = f"Erro ao fazer a transação: {e}"
        return render_template('erro.html', error=error_msg)

@app.route('/delete_cliente/<int:id>', methods=['POST'])
def delete_cliente(id):
    #Remove um cliente existente
    try:
        with relatorio_obra_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM cliente WHERE id = %s", (id,))
                conn.commit()
                cur.execute("SELECT * FROM cliente")
                clientes = cur.fetchall()
        flash("Cliente removido com sucesso", 'success')
        return render_template('gestao_clientes.html', clientes=clientes)
    except psycopg2.Error as e:
        error_msg = f"Erro ao fazer a transação: {e}"
        return render_template('erro.html', error=error_msg)



@app.route('/ralatori/pdf/<int:id>')
def gerar_pdf(id):
    # Obtendo relatórios do banco de dados para o usuário
    try: 
     with relatorio_obra_db_connection() as conn:
      with conn.cursor() as cur:
          cur.execute("SELECT * FROM relatorios where id = %s ",(id,))
          relatoriopdf = cur.fetchone() 
          cur.close()
          cur.close()
          cur = conn.cursor()
          cur.execute("SELECT * FROM cliente where id = %s ",(relatoriopdf[6],))
          cliente = cur.fetchone()
    except psycopg2.Error as e:
        error_msg = f"Erro ao fazer a transação: {e}"
        return render_template('erro.html') 

    
    # Criando o PDF
    filename = f'relatorios__{relatoriopdf[0]}.pdf'
    
    doc = SimpleDocTemplate(filename, pagesize=letter)
    
    style_right = ParagraphStyle(name='right', alignment=TA_RIGHT)
    style_left = ParagraphStyle(name='left', alignment=TA_LEFT)
    style_center = ParagraphStyle(name='center', alignment=TA_JUSTIFY , fontSize=12)
    style_center2 = ParagraphStyle(name='center2', alignment=TA_CENTER , fontSize=14, underline=True,)
    styles = getSampleStyleSheet()

    elementos = []

    dir_path = os.path.dirname(os.path.realpath(__file__))

     # Caminho para a imagem dentro da pasta 'static'
    img_path = os.path.join(dir_path, 'static', 'cardinal.png')
    icon = Image(img_path,  width=2*inch, height=1*inch) 
    icon.wrapOn(doc, 4, 2) # Ajuste a largura e a altura conforme necessário
    elementos.append(Spacer(1, 4))
    elementos.append(icon)
    elementos.append(Spacer(1, 12)) 
    texto_direita = Paragraph(f"Ficha Técnica nr: {relatoriopdf[0]}<br/>Cliente: <b>{cliente[1]}</b><br/>Data: {relatoriopdf[5]}<br/>", style_right)
    elementos.append(texto_direita)
    elementos.append(Spacer(1, 24))
    texto_central = Paragraph(f'Fase da Obra: <u>{relatoriopdf[2]}</u>', style_right)
    elementos.append(texto_central)
    elementos.append(Spacer(1, 24))
    texto = Paragraph(f"<b>RESUMO:</b> <br/>{relatoriopdf[1]}<br/>", style_center)
    elementos.append(texto)
    elementos.append(Spacer(1, 12))
    texto_esquerda = Paragraph(f"<br/>Hora de entrada: {relatoriopdf[3]}<br/>Hora de saida: {relatoriopdf[4]}", style_left)
    elementos.append(texto_esquerda)
    elementos.append(PageBreak()) 
    # Adicionando imagens ao PDF
   
    doc.build(elementos)

    return send_file(filename, as_attachment=True)



def get_db_connection():
    #Função para obter uma conexão com o banco de dados
    return psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')

@app.route('/saltar_org_id', methods=['GET'])
@is_logged_in
def saltar_org_id():
    #Retorna informações sobre as organizações para o usuário logado
    user = session['username']
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id FROM usuarios WHERE \"user\" = %s", (user,))
                user_id = cursor.fetchone()[0]
                
                if session['last_org'] == 'Demo_Org':
                    cursor.execute("SELECT * FROM usuarios WHERE id_usuarios = %s", (user_id,))
                    orgs = cursor.fetchall()
                    data = [{'Org_id': org[6], 'Nome': org[1], 'Saldo': '00.0'} for org in orgs]
                else:
                    cursor.execute("""
                        SELECT * FROM organizacao
                        JOIN usuario_org ON organizacao.org_id = usuario_org.org_id
                        WHERE usuario_org.usuario_id = %s
                    """, (user_id,))
                    orgs = cursor.fetchall()
                    data = [{'Org_id': org[1], 'Nome': org[0], 'Saldo': org[7]} for org in orgs]
                
                return jsonify(data)
    except psycopg2.Error as e:
        return jsonify({"error": f"Erro ao fazer a transação: {e}"})

@app.route('/selecionar_group', methods=['GET'])
@is_logged_in
def selecionar_group():
    #Retorna a lista de grupos disponíveis
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM grupo")
                grupos = cursor.fetchall()
                data = [{'id': grupo[0], 'nome': grupo[1]} for grupo in grupos]
                return jsonify(data)
    except psycopg2.Error as e:
        return jsonify({"error": f"Erro ao fazer a transação: {e}"})

@app.route('/adicionar_lingua', methods=['GET', 'POST'])
@is_logged_in
def adicionar_lingua():
    #Adiciona uma nova língua à organização
    if request.method == 'POST':
        org_id = session['last_org']
        lingua = request.form.get('lingua')
        abreviatura = request.form.get('abreviatura')

        if not lingua or not abreviatura:
            flash('Língua e abreviatura são obrigatórios', 'error')
            return redirect(url_for('adicionar_lingua'))

        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("INSERT INTO org_linguas (org_id, lingua, abreviatura) VALUES (%s, %s, %s)",
                                   (org_id, lingua, abreviatura))
                    conn.commit()
                    flash('Língua inserida com sucesso', 'success')
        except psycopg2.Error as e:
            flash(f"Erro ao inserir a língua: {e}", 'error')

    linguas = ["Português", "Emakhuwa", "Cisena", "Xachangana", "Cinyanja", "Ciswati", "Gitonga", "Elomwe", "Chuwabo", "Shimakonde", "Cinyungwe", "Koti", "Ronga", "Bitonga", "Kimwani", "Shona"]
    choices = request_languge()

    idioma = [lingua for lingua in linguas if any(lingua == choice[1] for choice in choices)]
    linguas = [lingua for lingua in linguas if lingua not in idioma]

    return render_template('org_information.html', idiomas=choices, linguas=linguas)

@app.route('/get_org/<org_id>', methods=['GET'])
def get_org(org_id):
    #Redireciona o usuário para a organização selecionada
    return redirect(url_for('org_id', org_id=org_id))

@app.route('/org_id/<org_id>', methods=['GET'])
@is_logged_in
def org_id(org_id):
    #Configura a organização selecionada na sessão do usuário
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM organizacao WHERE org_id = %s", (org_id,))
                org = cursor.fetchone()
                if org:
                    session['last_org'] = org_id
                    session['saldo'] = str(org[7])
                else:
                    flash("Organização não encontrada", 'error')
                    return redirect(url_for('gerir_clientes'))
                
                return render_template('tasks.html')
    except psycopg2.Error as e:
        return render_template('erro.html', error=f"Erro ao fazer a transação: {e}")

# FUNCAO DE RELATORIO DE CAMERAS
@app.route('/Relatorio_camera')
@is_logged_in
def Relatorio_camera():
    return render_template('Resumo_rel_camera.html')


@app.route('/resumo', methods=['POST'])
@is_logged_in
def resumo():
    cliente = request.form['clientes']
    resumo = request.form['resumo']
    id_user = request.form['user']

    conn = psycopg2.connect('postgresql://admin:AXjwTaMmH88i7x0G1rNwzSwhmnhYlIdo@dpg-co2n3ggl6cac73br3680-a.frankfurt-postgres.render.com/Relatorio_de_Manuntecao_de_Cameras')
    cur = conn.cursor()
    cur.execute("INSERT INTO resumo_rel ( resumo) VALUES (%s) RETURNING id", ( resumo,))
    conn.commit()
    idResumo =cur.fetchone()[0]
    cur.close()

    conn = psycopg2.connect('postgresql://admin:AXjwTaMmH88i7x0G1rNwzSwhmnhYlIdo@dpg-co2n3ggl6cac73br3680-a.frankfurt-postgres.render.com/Relatorio_de_Manuntecao_de_Cameras')
    cur = conn.cursor()
    cur.execute("INSERT INTO clientes (id_usuario,id_resumo, cliente) VALUES (%s, %s,%s) RETURNING id", (id_user, idResumo, cliente,))
    conn.commit()
    cli_id =cur.fetchone()[0]
    cur.close()

    print(resumo)
    return render_template('relatorio_camera.html', resumo=resumo, idResumo=idResumo, cli_id=cli_id)

@app.route('/submit_rel_cm', methods=['POST'])
@is_logged_in
def submit_rel_cm():
    descricao = request.form['descricao']
    estado = request.form['estado']
    assunto = request.form['assunto']
    idResumo = request.form['idResumo']
    resumo = request.form['resumo'] 
    cli_id = request.form['cliente']  # Supondo que você tenha um campo no formulário para o ID do usuário

    # Inserindo dados na tabela Relatorio
    id_user=1
    conn = psycopg2.connect('postgresql://admin:AXjwTaMmH88i7x0G1rNwzSwhmnhYlIdo@dpg-co2n3ggl6cac73br3680-a.frankfurt-postgres.render.com/Relatorio_de_Manuntecao_de_Cameras')
    cur = conn.cursor()
    cur.execute("INSERT INTO Relatorio (descricao, assunto, estado, id_resumo) VALUES (%s, %s, %s, %s)", (descricao, assunto, estado, idResumo))
    conn.commit()
    cur.close()

    # Obtendo o ID do relatório recém-inserido
    cur = conn.cursor()
    cur.execute("SELECT id FROM Relatorio ORDER BY id DESC LIMIT 1")
    id_relatorio = cur.fetchone()[0]
    cur.close()

    # Inserindo dados na tabela Imagens (se houver)
    for imagem in request.files.getlist('imagem'):
        if imagem.filename != '':
            cur = conn.cursor()
            imagem_bytes = BytesIO(imagem.read())  # Lê os bytes da imagem
            cur.execute("INSERT INTO Imagens (id_relatorio, imagem) VALUES (%s, %s)", (id_relatorio, psycopg2.Binary(imagem_bytes.getvalue())))
            conn.commit()
            cur.close()

    return render_template('relatorio_camera.html' , resumo=resumo, idResumo=idResumo,cli_id=cli_id)


@app.route('/ralatorios/pdf/<int:id_resumo>')
@is_logged_in
def gerar_pdf_cameras(id_resumo):
    # Obtendo relatórios do banco de dados para o usuário
    

    conn = psycopg2.connect('postgresql://admin:AXjwTaMmH88i7x0G1rNwzSwhmnhYlIdo@dpg-co2n3ggl6cac73br3680-a.frankfurt-postgres.render.com/Relatorio_de_Manuntecao_de_Cameras')
    cur = conn.cursor()
    cur.execute("SELECT cliente FROM clientes WHERE id_resumo = %s", (id_resumo,))
    cliente = cur.fetchone()[0]
    cur.close()

    conn = psycopg2.connect('postgresql://admin:AXjwTaMmH88i7x0G1rNwzSwhmnhYlIdo@dpg-co2n3ggl6cac73br3680-a.frankfurt-postgres.render.com/Relatorio_de_Manuntecao_de_Cameras')
    cur = conn.cursor()
    cur.execute("SELECT id, descricao, assunto, estado FROM Relatorio WHERE id_resumo = %s", (id_resumo,))
    relatorios = cur.fetchall()
    cur.close()

    conn = psycopg2.connect('postgresql://admin:AXjwTaMmH88i7x0G1rNwzSwhmnhYlIdo@dpg-co2n3ggl6cac73br3680-a.frankfurt-postgres.render.com/Relatorio_de_Manuntecao_de_Cameras')
    cur = conn.cursor()
    cur.execute("SELECT id , resumo , data FROM resumo_rel WHERE id = %s", (id_resumo,))
    resumo = cur.fetchone()
    cur.close()

    # Criando os dados da tabela para o PDF
    dados_tabela = [['Descrição', 'Assunto', 'Estado']]
    for relatorio in relatorios:
        dados_tabela.append(relatorio[1:])  # Ignorando o ID para a tabela

    # Criando o PDF
    filename = f'relatorios_camera_{cliente[0]}.pdf'
    
    doc = SimpleDocTemplate(filename, pagesize=letter)
    style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.white),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 16),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)])
    style_right = ParagraphStyle(name='right', alignment=TA_RIGHT)
    style_center = ParagraphStyle(name='center', alignment=TA_CENTER , fontSize=18)
    style_left = ParagraphStyle(name='left', alignment=TA_LEFT , fontSize=14, underline=True,)
    styles = getSampleStyleSheet()
    tabela = Table(dados_tabela, colWidths=[180, 200, 150])
    tabela.setStyle(style)

    elementos = []

    dir_path = os.path.dirname(os.path.realpath(__file__))

     # Caminho para a imagem dentro da pasta 'static'
    img_path = os.path.join(dir_path, 'static', 'cardinal.png')
    icon = Image(img_path,  width=2*inch, height=1*inch) 
    icon.wrapOn(doc, 4, 2) # Ajuste a largura e a altura conforme necessário
    elementos.append(icon)
    elementos.append(Spacer(1, 24)) 
    texto_direita = Paragraph(f"Ficha Técnica nr: {resumo[0]}<br/>Data: {resumo[2]}<br/>Cliente: <b>{cliente}</b>", style_right)
    texto_centro = Paragraph("Manutenção Preventiva", style_center)
    texto_esquerdo = Paragraph("<u><b>Sistema de Videovigilância</b></u>", style_left)
    elementos.append(texto_direita)
    elementos.append(Spacer(1, 24))
    elementos.append(texto_centro)
    elementos.append(Spacer(1, 24))
    elementos.append(texto_esquerdo)
    elementos.append(Spacer(1, 24))
    elementos.append(tabela)
    elementos.append(Spacer(1, 12))
    texto = Paragraph(f"<b>RESUMO:</b> {resumo[1]}<br/>", styles["Normal"])
    elementos.append(texto)
    elementos.append(Spacer(1, 12))
    elementos.append(PageBreak()) 
    # Adicionando imagens ao PDF
    for relatorio in relatorios:
        id_relatorio = relatorio[0]
        cur = conn.cursor()
        cur.execute("SELECT imagem, data_criacao FROM Imagens WHERE id_relatorio = %s", (id_relatorio,))
        imagens_info = cur.fetchall()
        cur.close()
        for imagem_info in imagens_info:
            image_data = BytesIO(imagem_info[0])
            img = Image(image_data)
            original_width, original_height = img.wrap(0, 0)
            scale = min(456 / original_width, 636 / original_height)
            img.drawHeight =  original_height*scale   # Altura da imagem no PDF
            img.drawWidth =  original_width*scale  # Largura da imagem no PDF
            legenda = Paragraph(f"<b>Descrição:</b> {relatorio[1]}<br/><b>Data da Imagem:</b> {imagem_info[1]}", styles["Normal"])
            elementos.append(legenda)
            elementos.append(Spacer(1, 12))  # Espaçamento entre a legenda e a próxima imagem
            elementos.append(img)
            elementos.append(PageBreak())  # Quebra de página entre as imagens

    doc.build(elementos)

    return send_file(filename, as_attachment=True)



UPLOAD_FOLDER = 'static/videos'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/uploads/<filename>')
@is_logged_in
def uploaded_file(filename):
    return send_from_directory(app.config['AUDIO_FOLDER'], filename)

#funcoes de gerenciamento de videos da igreja
@app.route('/videos/<type>', methods=['GET','POST'])
def videos(type):
    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form['descricao']
        file = request.files['video']
        categoria = request.form['categoria']
        data_video = datetime.strptime(request.form['data_video'], '%Y-%m-%d')

        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            try:
             conn = psycopg2.connect('postgresql://admin:AXjwTaMmH88i7x0G1rNwzSwhmnhYlIdo@dpg-co2n3ggl6cac73br3680-a.frankfurt-postgres.render.com/Videos')
             cur = conn.cursor()
             cur.execute('INSERT INTO testemunho( nome, descricao, video, data_video, assunto) VALUES (%s, %s, %s, %s, %s);',(nome, descricao, video_path, data_video,categoria,))
             conn.commit()
             cur.execute('SELECT * FROM testemunho;')
             testemunhos = cur.fetchall()
             conn.close()        
             return render_template('tabela_videos.html', testemunhos=testemunhos)
            except psycopg2.Error as e:
             error_msg = f"Erro ao fazer a transação: {e}"
             return render_template('erro.html', error=error_msg)
    

    if type !='null':
        conn = psycopg2.connect('postgresql://admin:AXjwTaMmH88i7x0G1rNwzSwhmnhYlIdo@dpg-co2n3ggl6cac73br3680-a.frankfurt-postgres.render.com/Videos')
        cur = conn.cursor()
        cur.execute("SELECT * FROM testemunho where assunto = '{type}';")
        testemunhos = cur.fetchall()
        conn.close()        
        return render_template('videos.html', testemunhos=testemunhos)

    conn = psycopg2.connect('postgresql://admin:AXjwTaMmH88i7x0G1rNwzSwhmnhYlIdo@dpg-co2n3ggl6cac73br3680-a.frankfurt-postgres.render.com/Videos')
    cur = conn.cursor()
    cur.execute('SELECT * FROM testemunho;')
    testemunhos = cur.fetchall()
    conn.close()        
    return render_template('home_video.html', testemunhos=testemunhos)
        



    
@app.route('/formulario_videos')
def formulario_videos():
    return render_template('formulario_videos.html')

@app.route('/atualizar/<int:id>', methods=['GET','POST'])
def atualizar(id):
    descricao = request.form['descricao']
    
    conn = psycopg2.connect('postgresql://admin:AXjwTaMmH88i7x0G1rNwzSwhmnhYlIdo@dpg-co2n3ggl6cac73br3680-a.frankfurt-postgres.render.com/Videos')
    cur = conn.cursor()
    cur.execute('UPDATE testemunho set descricao where id = %s;',(id,))
    conn.commit()
    conn.close()    

    return redirect('/videos')




@app.route('/Link_video/<int:testemunho_id>',methods=['GET'])
def Link_video(testemunho_id):
    conn = psycopg2.connect('postgresql://admin:AXjwTaMmH88i7x0G1rNwzSwhmnhYlIdo@dpg-co2n3ggl6cac73br3680-a.frankfurt-postgres.render.com/Videos')
    cur = conn.cursor()
    cur.execute('SELECT * FROM testemunho where id = %s;',(testemunho_id,))
    testemunho = cur.fetchone()
    conn.close() 
    return redirect(url_for('detalhes', nome=testemunho[1]))




@app.route('/detalhes/<nome>',methods=['POST','GET'])
def detalhes(nome):
    conn = psycopg2.connect('postgresql://admin:AXjwTaMmH88i7x0G1rNwzSwhmnhYlIdo@dpg-co2n3ggl6cac73br3680-a.frankfurt-postgres.render.com/Videos')
    cur = conn.cursor()
    cur.execute('SELECT * FROM testemunho where nome = %s;',(nome,))
    testemunho = cur.fetchone()
    conn.close() 
    if testemunho:
       return render_template('detalhes_testemunho.html', testemunho=testemunho) 
    else:
        conn = psycopg2.connect('postgresql://admin:AXjwTaMmH88i7x0G1rNwzSwhmnhYlIdo@dpg-co2n3ggl6cac73br3680-a.frankfurt-postgres.render.com/Videos')
        cur = conn.cursor()
        cur.execute('SELECT * FROM testemunho;')
        testemunhos = cur.fetchall()
        conn.close()    
        erro = "algo deu errado!"
        return render_template('Testemunhos.html', testemunhos=testemunhos, erro=erro)
      



@app.route('/buscar_testemunho', methods=['POST'])
def buscar_testemunho(): 
    nome = request.form['nome']
    try:
     conn = psycopg2.connect('postgresql://admin:AXjwTaMmH88i7x0G1rNwzSwhmnhYlIdo@dpg-co2n3ggl6cac73br3680-a.frankfurt-postgres.render.com/Videos')
     cur = conn.cursor()
     cur.execute('SELECT * FROM testemunho where nome = %s;',(nome,))
     testemunho = cur.fetchone()
     conn.close()
     print(testemunho)
     return render_template('detalhes_testemunho.html', testemunho=testemunho)
    except psycopg2.Error as e:
     error_msg = f"Erro ao fazer a transação: {e}"
     return render_template('erro.html', error=error_msg) 



@app.route('/testes_OV')
def testes_OV():
    # Redireciona para a função 'teste_ov' com o parâmetro 'tipo' definido como 'iniciar'
    return redirect(url_for('teste_ov', tipo='iniciar')) 


@app.route('/teste_ov/<tipo>', methods=['POST', 'GET'])
def teste_ov(tipo): 
    if request.method == 'POST':
        resposta = {}
        try:
            # Conectar ao banco de dados
            conn = psycopg2.connect('postgresql://admin:AXjwTaMmH88i7x0G1rNwzSwhmnhYlIdo@dpg-co2n3ggl6cac73br3680-a.frankfurt-postgres.render.com/Quizdb')
            cur = conn.cursor()
            # Selecionar as questões com base no tipo
            cur.execute("SELECT * FROM quiz WHERE tipo = %s;", (tipo,))
            questoes = cur.fetchall()
            
            for questao in questoes:
                resposta = request.form.get(f'quiz{questao[0]}')
                # Verificar se já existe uma resposta para essa questão
                cur.execute("SELECT * FROM respostas WHERE usuario_id = 1 AND questao_id = %s;", (questao[0],))
                resposta_existente = cur.fetchall()
                if resposta_existente:
                    for resp in resposta_existente:
                        cur.execute("SELECT * FROM quiz WHERE id = %s;", (resp[1],))
                        resposta_quiz = cur.fetchone()
                        cur.execute("DELETE FROM respostas WHERE usuario_id = 1 AND questao_id = %s;", (resp[1],))
                        conn.commit()
                        if resposta_quiz[3] == resposta:
                            situacao = 'correcto'
                        else:
                            situacao = 'incorrecto'
                        cur.execute(
                            "INSERT INTO respostas (usuario_id, questao_id, resposta, situacao) VALUES (%s, %s, %s, %s);",
                            (1, resp[1], resposta, situacao)
                        )
                        conn.commit()
                else:
                    if questao[3] == resposta:
                        situacao = 'correcto'
                    else:
                        situacao = 'incorrecto'
                    cur.execute(
                        "INSERT INTO respostas (usuario_id, questao_id, resposta, situacao) VALUES (%s, %s, %s, %s);",
                        (1, questao[0], resposta, situacao)
                    )
                    conn.commit()
            conn.close()   
        except psycopg2.Error as e:
            error_msg = f"Erro ao fazer a transação: {e}"
            print(error_msg)

    try:
        # Conectar ao banco de dados novamente para obter as questões
        conn = psycopg2.connect('postgresql://admin:AXjwTaMmH88i7x0G1rNwzSwhmnhYlIdo@dpg-co2n3ggl6cac73br3680-a.frankfurt-postgres.render.com/Quizdb')
        cur = conn.cursor()
        # Selecionar questões com base no tipo
        if tipo == "iniciar": 
            cur.execute("SELECT * FROM quiz WHERE tipo = 'logico' ORDER BY id;")
            questoes = cur.fetchall()
            logico = True
            return render_template('testes_OV.html', questoes=questoes, logico=logico)
        elif tipo == "verbal": 
            cur.execute("SELECT * FROM quiz WHERE tipo = 'numerico' ORDER BY id;")
            questoes = cur.fetchall()
            numerico = True
            return render_template('testes_OV.html', questoes=questoes, numerico=numerico)
        elif tipo == "logico": 
            cur.execute("SELECT * FROM quiz WHERE tipo = 'verbal' ORDER BY id;")
            questoes = cur.fetchall()
            verbal = True
            return render_template('testes_OV.html', questoes=questoes, verbal=verbal)
        elif tipo == "numerico": 
            cur.execute("SELECT * FROM quiz WHERE tipo = 'preferencias' ORDER BY id;")
            questoes = cur.fetchall()
            preferencias = True
            return render_template('testes_OV.html', questoes=questoes, preferencias=preferencias)
        else:
            return redirect(url_for('resultado', usuario_id=1))
        conn.close()
    except psycopg2.Error as e:
        error_msg = f"Erro ao fazer a transação: {e}"
        return render_template('erro.html', error=error_msg) 
    



# Rota para a página de avaliação
@app.route('/resultado/<int:usuario_id>')
@is_logged_in
def resultado(usuario_id):
  query = f"""
        SELECT u.id AS usuario_id, u.nome AS usuario_nome,
               r.questao_id, r.resposta,
               q.questao, q.opcoes,  q.opcao_correcta, q.tipo,
               r.situacao
        FROM usuario u
        JOIN respostas r ON u.id = r.usuario_id
        JOIN quiz q ON r.questao_id = q.id
        WHERE u.id ={usuario_id}
         """
  try:
     conn = psycopg2.connect('postgresql://admin:AXjwTaMmH88i7x0G1rNwzSwhmnhYlIdo@dpg-co2n3ggl6cac73br3680-a.frankfurt-postgres.render.com/Quizdb')
     cur = conn.cursor()
     cur.execute(query)
     resultados = cur.fetchall()
     cur.execute(f'select * from usuario where id = {usuario_id}')
     usuario = cur.fetchone()
     conn.close()
  except psycopg2.Error as e:
     error_msg = f"Erro ao fazer a transação: {e}"
     return render_template('erro.html', error=error_msg)    
  percentual_correto_verbal = 0    
  percentual_correto_numerico = 0
  percentual_correto_logico = 0
  for respostas in resultados:
   if respostas[7] =='verbal': 
    total_respostas = len(resultados)
    respostas_corretas = sum(1 for respostas in resultados if respostas[8] == "correcto" and respostas[7] =='verbal')
    percentual_correto_verbal = respostas_corretas
    
   if respostas[7] =='logico': 
    total_respostas = len(resultados)
    respostas_corretas = sum(1 for respostas in resultados if respostas[8] == "correcto" and respostas[7]=="logico")
    percentual_correto_logico = respostas_corretas

   if respostas[7] =='numerico': 
    total_respostas = len(resultados)
    respostas_corretas = sum(1 for respostas in resultados if respostas[8] == "correcto" and respostas[7]=="numerico")
    percentual_correto_numerico = respostas_corretas  
   
  tipo = ["logico","numerico", "verbal"] 
  total_respostas = [ percentual_correto_logico, percentual_correto_numerico,  percentual_correto_verbal] 
  return render_template('resultado.htm', resultados=resultados,  tipo=tipo, total_respostas=total_respostas, usuario=usuario)



# apaga todos os dados do usuario e reenicia os testes 
@app.route('/reniciar/<int:usuario_id>')
@is_logged_in
def reniciar(usuario_id):
    try:
     conn = psycopg2.connect('postgresql://admin:AXjwTaMmH88i7x0G1rNwzSwhmnhYlIdo@dpg-co2n3ggl6cac73br3680-a.frankfurt-postgres.render.com/Quizdb')
     cur = conn.cursor()
     cur.execute(f"SELECT * FROM respostas WHERE usuario_id={usuario_id} ;")
     resposta_existente = cur.fetchall()
    
     for resposta in resposta_existente:
      cur.execute(f"DELETE FROM respostas WHERE usuario_id={usuario_id};")
      conn.commit()
     conn.close() 
    except psycopg2.Error as e:
     error_msg = f"Erro ao fazer a transação: {e}"
     return render_template('erro.html', error=error_msg)   

    conn = psycopg2.connect('postgresql://admin:AXjwTaMmH88i7x0G1rNwzSwhmnhYlIdo@dpg-co2n3ggl6cac73br3680-a.frankfurt-postgres.render.com/Quizdb')
    cur = conn.cursor()
    cur.execute("SELECT * FROM quiz WHERE tipo='logico';")
    questoes = cur.fetchall()
    conn.close()
    logico = True
    return render_template('testes_OV.html', questoes=questoes, logico = logico)



# FUNCAO DE TICKETS
db_params = {
    'user': 'admin',
    'password': 'AXjwTaMmH88i7x0G1rNwzSwhmnhYlIdo',
    'host': 'dpg-co2n3ggl6cac73br3680-a.frankfurt-postgres.render.com',
    'database': 'tickets',
}
# ConexÃ£o com o banco de dados
def connect_to_db():
    try:
        conn = psycopg2.connect(**db_params)
        print("conectado ao banco de dados")
        return conn
    except psycopg2.Error as e:
        print("Erro ao conectar ao banco de dados:", e)
        return None
    
@app.route('/suport')
def suport():
    return render_template('novo_ticket.html')




@app.route('/tickets')
@is_logged_in
def tickets():
    conn = connect_to_db()
    try:
     cur = conn.cursor()
     cur.execute("SELECT * FROM ticket;")
     tickets = cur.fetchall()
    except psycopg2.Error as e:
     error_msg = f"Erro ao fazer a transação: {e}"
     return render_template('erro.html', error=error_msg)  
    conn.close() 
    return render_template('lista_ticket.html', tickets=tickets)

@app.route('/ticket/<int:id>')
@is_logged_in
def ticket(id):
    conn = connect_to_db()
    try:
     cur = conn.cursor()
     cur.execute("SELECT * FROM ticket join funcionario on ticket.funcionario_id = funcionario.id WHERE ticket.id = %s ;",(id,))
     ticket = cur.fetchone()
    except psycopg2.Error as e:
     error_msg = f"Erro ao fazer a transação: {e}"
     return render_template('erro.html', error=error_msg)  
    conn.close() 
    return render_template('ticket.html', ticket=ticket)




@app.route('/novo_ticket', methods=['GET', 'POST'])
@is_logged_in
def novo_ticket():
    if request.method == 'POST':
        titulo = request.form['titulo']
        descricao = request.form['descricao']
        dificuldade = request.form['dificuldade']
        categoria = request.form['categoria']

        conn = connect_to_db()
        try:
          cur = conn.cursor()
          cur.execute('INSERT INTO ticket( pedido, descricao, categoria, prioridade) VALUES (%s, %s, %s, %s) RETURNED id;',(titulo, descricao, categoria, dificuldade,))
          ticket_id = cur.fetchone()[0]
          conn.commit()
        except psycopg2.Error as e:
          error_msg = f"Erro ao fazer a transação: {e}"
          return render_template('erro.html', error=error_msg)  
        conn.close() 
        
        ticket_id = novo_ticket.id
        
        return  redirect(url_for('confirmacao', ticket_id=ticket_id))
    return render_template('novo_ticket.html')



# metodo para atualizar tickets
@app.route('/atualizar_ticket/<int:id>', methods=['GET', 'POST'])
@is_logged_in
def atualizar_ticket(id):
    if request.method == 'POST':
        titulo = request.form['titulo']
        descricao = request.form['descricao']
        prioridade = request.form['dificuldade']
        status = request.form['status']

        conn = connect_to_db()
        try:
          cur = conn.cursor()
          cur.execute('UPDATE ticket SET pedido = %s, descricao= %s, prioridade = %s, status = %s WHERE id = %s) VALUES (%s, %s, %s, %s, %s) ;',(titulo, descricao, prioridade, status,id,))
          conn.commit()
        except psycopg2.Error as e:
          error_msg = f"Erro ao fazer a transação: {e}"
          return render_template('erro.html', error=error_msg)  
        conn.close() 
        return redirect(url_for('tickets'))


        
    
@app.route('/confirmacao/<ticket_id>')
@is_logged_in
def confirmacao(ticket_id):
    return render_template('confirmacao.html', ticket_id=ticket_id)

@app.route('/funcionarios/<int:ticket_id>', methods=['GET', 'POST'])
@is_logged_in
def funcionarios(ticket_id):
    funcionarios =[]
    conn = connect_to_db()
    try:
     cur = conn.cursor()
     cur.execute("SELECT * FROM ticket WHERE id=%s ;",(ticket_id,))
     ticket = cur.fetchone()
    except psycopg2.Error as e:
     error_msg = f"Erro ao fazer a transação: {e}"
     return render_template('erro.html', error=error_msg)  
    conn.close() 
    conn = connect_to_db()
    try:
     cur = conn.cursor()
     cur.execute("SELECT * FROM funcionario;")
     func = cur.fetchall()
    except psycopg2.Error as e:
     error_msg = f"Erro ao fazer a transação: {e}"
     return render_template('erro.html', error=error_msg)  
    conn.close() 
    for func in func:
        if func[6] != 'Ocupado':
            funcionarios.append(func)
    return render_template('atribuir_ticket.html', ticket=ticket, funcionarios=funcionarios)




@app.route('/atribuir_ticket/<int:ticket_id>', methods=['GET', 'POST'])
@is_logged_in
def atribuir_ticket(ticket_id):
    funcionarios =[]
    if request.method == 'POST':
        funcionario_id = request.form['funcionario']
        prazo_conclusao = request.form['prazo_conclusao']

        conn = connect_to_db()
        try:
          cur = conn.cursor()
          cur.execute("UPDATE ticket SET prazo_conclusao = %s, funcionario_id = %s WHERE id =%s ;",(prazo_conclusao, funcionario_id, ticket_id,))
          conn.commit()
        except psycopg2.Error as e:
          error_msg = f"Erro ao fazer a transação: {e}"
          return render_template('erro.html', error=error_msg)  
        conn.close() 
        conn = connect_to_db()
        try:
         cur = conn.cursor()
         cur.execute("UPDATE funcionario SET status = 'Ocupado' WHERE id = %s;",(funcionario_id,))
         conn.commit()
         cur.execute("SELECT * FROM funcionario;")
         funcionario = cur.fetchall() 
        except psycopg2.Error as e:
         error_msg = f"Erro ao fazer a transação: {e}"
         return render_template('erro.html', error=error_msg)  
        conn.close()

        for f in funcionario:
          if f[6] != 'Ocupado':
             funcionarios.append(f)
    return render_template('atribuir_ticket.html', ticket=ticket, funcionarios=funcionarios)




@app.route('/deletar_ticket/<int:ticket_id>', methods=['GET', 'POST'])
@is_logged_in
def deletar_ticket(ticket_id):
    conn = connect_to_db()
    try:
     cur = conn.cursor()
     cur.execute("SELECT * FROM ticket WHERE id=%s ;",(ticket_id,))
     ticket = cur.fetchone()
     cur.execute("UPDATE funcionario SET status = 'Disponivel' WHERE id = %s;",(ticket[6],))
     conn.commit()
     cur.execute("delete FROM ticket WHERE id=%s ;",(ticket_id,))
     conn.commit()
     conn.close() 
     return redirect(url_for('tickets'))
    except psycopg2.Error as e:
     error_msg = f"Erro ao fazer a transação: {e}"
     return render_template('erro.html', error=error_msg)  

 
@app.route('/concluir_ticket/<int:ticket_id>', methods=['GET', 'POST'])
@is_logged_in
def concluir_ticket(ticket_id):
    conn = connect_to_db()
    try:
     cur = conn.cursor()
     cur.execute("SELECT * FROM ticket WHERE id=%s ;",(ticket_id,))
     ticket = cur.fetchone()
     cur.execute("UPDATE ticket SET status = 'Concluido' WHERE id = %s;",(ticket_id,))
     conn.commit()
     cur.execute("UPDATE funcionario SET status = 'Disponivel' WHERE id = %s;",(ticket[6],))
     conn.commit()
     conn.close() 
     return redirect(url_for('tickets'))
    except psycopg2.Error as e:
     error_msg = f"Erro ao fazer a transação: {e}"
     return render_template('erro.html', error=error_msg)      
        



@app.route('/idioma_inscricao/<idioma>', methods=['GET'])
def idioma_inscricao(idioma):
    print('idioma')
    return redirect(url_for('submit_inscricao', idioma= idioma))


@app.route('/submit_inscricao/<idioma>', methods=['POST','GET'])
def submit_inscricao(idioma):

    if request.method == 'POST': 
        nome = request.form['nome']
        titulo = request.form['titulo']
        igreja = request.form['igreja']
        cargo = request.form['cargo']
      #  endereco = request.form['endereco']
       # cidade = request.form['cidade']
        #estado = request.form['estado']
        #codigoPostal = request.form['codigoPostal']
      #  pais = request.form['pais']
        telefone = request.form['telefone']
        email = request.form['email']
       # acomodacao = request.form['acomodacao']
       # restricoesAlimentares = request.form.get('restricoesAlimentares', '')
       # contatoEmergencia = request.form['contatoEmergencia']
       # telefoneContatoEmergencia = request.form['telefoneContatoEmergencia']
       # sessao = ', '.join(request.form.getlist('sessao'))
       # outroSessao = request.form.get('outroSessao', '')
       # jantarNetworking = request.form['jantarNetworking']
       # oficina = ', '.join(request.form.getlist('oficina'))
       # outraOficina = request.form.get('outraOficina', '')
       # solicitacoesEspeciais = request.form.get('solicitacoesEspeciais', '')
       # taxaInscricao = request.form['taxaInscricao']
       # metodoPagamento = request.form['metodoPagamento']
       # numeroCartao = request.form.get('numeroCartao', '')
       # validadeCartao = request.form.get('validadeCartao', '')
       # cvvCartao = request.form.get('cvvCartao', '')
       # nomeCartao = request.form.get('nomeCartao', '')
       # comentariosAdicionais = request.form.get('comentariosAdicionais', '')
    
        # Conectando ao banco de dados e inserindo os dados
        conn = psycopg2.connect('postgresql://admin:AXjwTaMmH88i7x0G1rNwzSwhmnhYlIdo@dpg-co2n3ggl6cac73br3680-a.frankfurt-postgres.render.com/Videos')
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO inscricoes2 (nome, titulo, igreja, cargo,  telefone, email)
            VALUES (%s, %s, %s, %s, %s,%s)
        ''', (nome, titulo, igreja, cargo, telefone, email))
        conn.commit()
        cur.close()
        conn.close()
        
        flash('Dados inseridos com sucesso', 'success')

        return redirect(url_for('submit_inscricao', idioma = idioma))

    
    if idioma == 'en':
      return render_template('inscricao_pastoral_EN.html', idioma=idioma)
    else:
      return render_template('inscricao_pastoral_PT.html', idioma = idioma)
   


@app.route('/get_audio/<path:filename>')
def get_audio(filename):
    
    return send_from_directory('audios', filename)
    
        

def save_survey_response2(phone_number, campaign):
    # Connect to the database
    conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')

    # Create a cursor object
    cur = conn.cursor()

    # Create survey_responses table if not exists
    cur.execute("""
        CREATE TABLE IF NOT EXISTS simple_responses (
            id SERIAL PRIMARY KEY,
            phone_number VARCHAR(20),
            campaign int references campanhas(id_campanha),
            data timestamp without time zone )
    """)
    current_dateTime = datetime.now()
    current_dateTime = str(datetime.date(current_dateTime)) + " " + str(datetime.time(current_dateTime))

    # Insert survey response into the table
    cur.execute("""
        INSERT INTO simple_responses (phone_number,campaign, data)
        VALUES (%s, %s, %s)
    """, ('258849109478', campaign, current_dateTime ))

    conn.commit()
    conn.close()

    
if __name__ == '__main__':
    app.secret_key='secret123'
    #app.run(debug=True)
    http_server = WSGIServer(('', 5000), app)
    http_server.serve_forever()
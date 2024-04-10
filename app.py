import os
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse

from flask import Flask, render_template, request, session, flash, session, logging, url_for, redirect, Response,  send_from_directory
import psycopg2
from markupsafe import escape
from wtforms import Form, StringField, TextAreaField, PasswordField, validators, SelectField, DecimalField, DateField, IntegerField, EmailField, TimeField, FileField,  SubmitField, FieldList, FormField, DateTimeField
from gevent.pywsgi import WSGIServer
from functools import wraps
from datetime import datetime, time, timedelta, date
from decimal import Decimal
from wtforms.validators import InputRequired
from psycopg2 import sql
from flask_wtf import FlaskForm

from io import BytesIO
import base64

from apscheduler.schedulers.background import BackgroundScheduler


from flask_babel import Babel

from babel.numbers import format_currency

from flask import make_response
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

import json
import re
import PyPDF2
import io

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build


app = Flask(__name__)


SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

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


# Mock function to save survey responses to the database
def save_survey_response(phone_number, question_index, selected_option):
    # Connect to the database
    conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')

    # Create a cursor object
    cur = conn.cursor()

    # Create survey_responses table if not exists
    cur.execute("""
        CREATE TABLE IF NOT EXISTS survey_responses (
            id SERIAL PRIMARY KEY,
            phone_number VARCHAR(20),
            question_index INT,
            selected_option INT
        )
    """)
    print("Dentro")
    print(phone_number)
    print(question_index)
    print(selected_option)

    # Insert survey response into the table
    cur.execute("""
        INSERT INTO survey_responses (phone_number, question_index, selected_option)
        VALUES (%s, %s, %s)
    """, (phone_number, question_index, selected_option))

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
            t_name VARCHAR(50) DEFAULT %s
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
        extracted_text = extract_text(io.BytesIO(attachment_data))

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

def get_db_connection():
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

class ProformaInvoiceForm(FlaskForm):
    invoice_number = StringField('Invoice Number')
    date = DateField('Date')
    customer_name = StringField('Customer Name')

    items = FieldList(FormField(ItemForm), min_entries=1)
    add_item = SubmitField('Add Item')
    generate_invoice = SubmitField('Generate Invoice')


# Add contact
@app.route('/add_contact', methods=['GET', 'POST'])
def add_contact():
    
    name = request.form.get('name')
    location = request.form.get('location')
    phone = request.form.get('phone')
    gender = request.form.get('gender')
    org_id = session['org_id']

    #Connect to database
    conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')

    # Create cursor
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM contacts where org_id = "+"'"+ str(org_id)+"'")
    contacts = cursor.fetchall()

    
    
    if request.method == 'POST':
        # Insert a new contact into the database
        insert_query = '''
            INSERT INTO contacts (name, location, phone, gender, org_id)
            VALUES (%s, %s, %s, %s, %s)
            '''
        cursor.execute(insert_query, (name, location, phone, gender, org_id))
        conn.commit()

        return render_template('add_contat.html', contacts=contacts)

    # Close connection
    conn.close()

    return render_template('add_contat.html', contacts=contacts)



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
    
    query = "SELECT "+'"'+ "id"+'"'+" ,title, due_date, accepted_time, completed_time, responsible, completed, accepted FROM tasks where due_date = Current_date OR completed = false OR completed_time = Current_date;"
    
    print(query)
    cursor.execute(query)
    tasks = cursor.fetchall() 

    print(tasks)

    
    return render_template('tasks.html', tasks=tasks)

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

    conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM campanhas")

    dados=cursor.fetchall()

    # Close connection
    conn.close()

    return render_template('campanhas.html', campanhas = dados)


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
    time = TimeField('Time:', format='%H:%M')
    action= SelectField('Next action:',coerce=str,choices=[("Call","Call"),("Meeting","Meeting"),("submission of proposal","submission of proposal")])
    calendar = StringField('Calendar')
    
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
        send_sms(form.sms.data,str("+258"+form.contacto.data),form.site.data)
        
        # Execute query
        cmd='INSERT INTO envio_sms("Mensagem", "Contato", "NV_enviadas", "sender_id") VALUES ('+"'"+form.sms.data+"'"+",'"+str("+258"+form.contacto.data)+"','0','"+form.site.data+"')"

        cursor.execute(cmd)
        print(cmd)
        # Commit to DB
        conn.commit()

        # Close connection
        conn.close()

        flash('Teste criado com sucesso', 'success')

        return redirect(url_for('testes'))

    return render_template('testes.html', form = form)


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
            cmd = "SELECT * FROM usuarios WHERE" + ' "user"=' + "'" + username + "'"
            result = cursor.execute(cmd)
            result = cursor.fetchone()

            

            # Upadate session parameters
            session['logged_in'] = True
            session['username'] = username

            session['last_org'] = str(result[6])
            session['org_id'] = str(result[6])

            

            flash('Login com Sucesso', 'success')
            # Close connection
            conn.close()
            return redirect(url_for('tasks', dados = str(result[6])))

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
    
    if request.method == 'POST':
        conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')
        cursor = conn.cursor()

        # Query
        query = sql.SQL("INSERT INTO {} (opcao) VALUES (%s)").format(sql.Identifier(id))

        # Execute query with parameterized value
        cursor.execute(query, (form.opcao.data,))

       

        # Commit to DB
        conn.commit()

        # Close connection
        conn.close()

        flash('Opcao adicionada com Successo', 'success')

        return redirect(url_for('perguntas', id=id))

    return render_template('addoption.html', form=form)


@app.route('/campanha_n/<string:id>')
@is_logged_in
def campanha_n(id):
    table_name_to_list = id
    column_prefix_to_list = 'pergunta'

    try:
        
        # Connect to the PostgreSQL database
        connection = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')
        cursor = connection.cursor()

        # Get a list of columns for the specified table and column name prefix
        columns_list = list_columns(cursor, table_name_to_list, column_prefix_to_list)
        
        couples = []

        print(columns_list)
        # Campanha
        # table_name_to_list = display_ref(cursor,table_name_to_list)
        for i in range(len(columns_list)):
            item = columns_list[i]
            var = display_ref(cursor,id + "_" + item)
            if var is not None:
                print(id + "_" + item)
                print(var)
                couples.append((item,var))
                print(couples)
            else:
                print("Error: display_ref() returned None for", id + "_" + item)

        campanha_ref = display_ref(cursor,table_name_to_list)
    except Exception as e:
        print(f"Error: {e}")

    finally:
        # Close the database connection
        cursor.close()
        connection.close()
    
    
    

    return render_template('campanha_n.html', columns_list = couples, campanha=table_name_to_list, campanha_ref=campanha_ref)


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
            cursor.execute('INSERT INTO public.campanhas (orgid, campanha_ref) VALUES (%s, %s)',(session['org_id'],new_table_name))

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


@app.route('/perguntas/<string:id>')
@is_logged_in
def perguntas(id):

    conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')

    cursor = conn.cursor()

    pergunta = display_ref(cursor,id)

    cursor.execute("SELECT * from "+id)

    dados=cursor.fetchall()

    conn.close()

    return render_template('perguntas.html', dados = dados, pergunta = pergunta, pergunta_ref = id)


@app.route('/survey_dashboard')
def survey_dashboard():
    return render_template('survey_dashboard.html', questions=survey_questions, responses=survey_responses)


@app.route('/dashboard2/<string:table_name>')
@is_logged_in
def dashboard2(table_name):
    # Connect to the database
    conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')
    cursor = conn.cursor()

    # Execute the SQL query to fetch data from the specified table
    cursor.execute(f"SELECT opcao, count_ FROM public.{table_name}")
    rows = cursor.fetchall()

    # Prepare data for chart
    labels = [row[0] for row in rows]
    counts = [row[1] for row in rows]
    
    # Display ref
    cursor.execute(f"SELECT ref FROM display_ref where id='{table_name}'")
    rows = cursor.fetchone()

    table_name = rows[0]

    print(rows[0])

    # Close the cursor and connection
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


@app.route('/cliente_ong', methods=['GET'])
@is_logged_in
def cliente_ong():

    conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')

    cursor = conn.cursor()

    # Execute query
    cursor.execute('SELECT * FROM cliente_vendas WHERE ong = true ORDER BY nome;')
        
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
        cursor.execute("INSERT INTO cliente_vendas(nome, email, contato, contato_alternativo, city, residence_type, work_phase, sale_phase, ong, email2) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(form.name.data,form.email.data,form.contact1.data,form.contact2.data, form.city.data, form.residence.data,form.phase.data, form.sale.data, form.interested.data, form.email2.data))
        
        # Inserir na tabela actividades
        task_title = "Cadastro de novo cliente: " + form.name.data + " no Sistema"       
        insert_query = sql.SQL("INSERT INTO tasks (title, due_date, responsible, accepted_time, completed_time, accepted, completed) VALUES ({}, CURRENT_DATE,{}, now(),now(), 'TRUE','TRUE')")
        cursor.execute(insert_query.format(sql.Literal(task_title), sql.Literal(session['username'])))


        # Commit to DB
        conn.commit()

        # Close connection
        conn.close()

        flash(f'Cliente "{form.name.data}" adicionado com sucesso', 'success')

        return redirect(url_for('clientecad'))

    return render_template('crm.html', form = form)



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
        cursor.execute("INSERT INTO calendar(usuario, descricao, data, next_action, time, cliente, id_cliente, hora_actual) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                       (session['username'], form.text.data, form.calendar.data, form.action.data, form.time.data, client[0], client[4], current_dateTime))
        
        # Inserir na tabela actividades
        task_title = "Follow-up feito ao cliente: " + client[0] + " no Sistema"       
        insert_query = sql.SQL("INSERT INTO tasks (title, due_date, responsible, accepted_time, completed_time, accepted, completed) VALUES ({}, CURRENT_DATE,{}, now(),now(), 'TRUE','TRUE')")
        cursor.execute(insert_query.format(sql.Literal(task_title), sql.Literal(session['username'])))

        conn.commit()
        conn.close()

        flash(f'{client[0]}', 'success')
        return redirect(url_for('clientecad'))

    if request.method == 'GET':
        cursor.execute('SELECT * FROM calendar WHERE id_cliente = %s ORDER BY data DESC', (id,))
        calendar_data = cursor.fetchall()
        print(calendar_data)
        conn.close()

    return render_template('/task.html', client=client, calendar_data=calendar_data, form=form)

    
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
def ivr_test():
    return render_template('ivr_test.html')


# IVR route
@app.route('/ivr', methods=['POST'])
def ivr():
    response = VoiceResponse()
    response.play(QUESTION_AUDIO_URLS[0])

    current_question_index = request.args.get('current_question_index', default=1, type=int)
    with response.gather(num_digits=1, action=url_for('handle_question', current_question_index=current_question_index), method='POST', input='dtmf') as gather:
        gather.play(QUESTION_AUDIO_URLS[current_question_index])

    return str(response), 200, {'Content-Type': 'application/xml'}

# Handle question route
@app.route('/handle_question', methods=['POST'])
def handle_question():
    selected_option = request.form.get('Digits')
    phone_number = request.form.get('To')
    current_question_index = int(request.args.get('current_question_index'))

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
        save_survey_response(phone_number, current_question_index, selected_option)

        # Continue with the next question
        next_question_index = current_question_index + 1
        with response.gather(num_digits=1, action=url_for('handle_question', current_question_index=next_question_index), method='POST', input='dtmf') as gather:
            gather.play(QUESTION_AUDIO_URLS[next_question_index])

    else:  # Concluding message
        response.play(QUESTION_AUDIO_URLS[-1])

    return str(response), 200, {'Content-Type': 'application/xml'}

# Start IVR campaign route
@app.route('/start_ivr_campaign', methods=['POST'])
def start_ivr_campaign():
    #if not authenticate_twilio_request():
    #    return Response("Unauthorized", 401)

    #phone_numbers = get_phone_numbers_from_database()
    phone_numbers = ['+258856017354']

    for number in phone_numbers:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        call = client.calls.create(
            url='https://insightsap.com/ivr',  # URL for handling IVR logic
            to=number,
            from_=TWILIO_PHONE_NUMBER
        )

    return 'IVR campaign started successfully'


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
    result = cursor.execute("SELECT * FROM campanhas WHERE id_campanha = %s", [id])

    campanha = cursor.fetchone()
    
    #conn.close()
    
    # Get form

    form = CampForm(request.form)

    # Populate tikrts form fields
    form.projecto.data = campanha[2]
    

    if request.method == 'POST':
        projecto = request.form['projecto']
        
        #current_dateTime = datetime.now()

        # Create Cursor
        cursor = conn.cursor()
        #app.logger.info(title)
        
        # Execute
        cursor.execute("UPDATE campanhas SET projecto=%s WHERE id_campanha=%s",(projecto,id))
        cursor.execute("INSERT INTO display_ref(id, ref) VALUES (%s,%s)",(campanha[3],projecto))
        # Commit to DB
        conn.commit()

        #Close connection
        conn.close()

        flash('Campanha atualizada', 'success')

        return redirect(url_for('campanhas'))

    return render_template('assign_camp.html', form=form)

# Assign question
@app.route('/assign_question/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def assign_question(id):

    conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')
    
    # Create cursor
    cursor = conn.cursor()

    # Get article by id
    result = cursor.execute("SELECT * FROM display_ref WHERE id = %s", [id])

    pergunta = cursor.fetchone()
    
    #conn.close()
    
    # Get form

    form = PerguntaForm(request.form)

    # Populate tikrts form fields
    form.pergunta.data = pergunta[1]
    

    if request.method == 'POST':
        pergunta = request.form['pergunta']
        
        #current_dateTime = datetime.now()

        # Create Cursor
        cursor = conn.cursor()
        #app.logger.info(title)
        
        # Execute
        cursor.execute("UPDATE display_ref SET ref=%s WHERE id=%s",(pergunta,id))
        
        # Commit to DB
        conn.commit()

        #Close connection
        conn.close()

        flash('Pergunta atualizada', 'success')

        return redirect(url_for('perguntas', id=id))

    return render_template('assign_question.html', form=form)

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

@app.route('/respostas')
#@is_logged_in
def ver_respostas():
    respostas = obter_respostas()
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
        conn.commit()

        return 'Dados enviados com sucesso!'


# Esta deve ser sempre a ultima funcao
@app.route("/<name>")
def hello(name):
    flash('Pagina '+name+ ' nao existe', 'danger')
    return render_template('home.html')



if __name__ == '__main__':
    app.secret_key='secret123'
    #app.run(debug=True)
    http_server = WSGIServer(('', 5000), app)
    http_server.serve_forever()
    

# Functions
from actual import Actual
from actual.queries import get_account, get_accounts, get_transactions, reconcile_transaction, get_ruleset
from datetime import datetime, timedelta
import decimal
import requests
import json

def backup_actual(URL_ACTUAL, PASSWORD_ACTUAL, FILE_ACTUAL):
    with Actual(base_url=URL_ACTUAL, password=PASSWORD_ACTUAL, file=FILE_ACTUAL) as actual:
        current_date = datetime.now().strftime("%Y%m%d")
        actual.export_data(f"./data/Backup/{FILE_ACTUAL}-{current_date}.zip")
        print("Data backed up.\n")

def getPluggy_secrets(string):
    clientID = None
    clientSecret = None
    lines = string.split('\n')
    for line in lines:
        if line.startswith("#clientID"):
            clientID = line.split('"')[1]
        elif line.startswith("#clientSecret"):
            clientSecret = line.split('"')[1]
    if clientID != None and clientSecret != None: 
        print("Credenciais para o Pluggy detectada.")
    else: 
        print("Não há credenciais válidas para o Pluggy.")
        raise ValueError("Não há credenciais válidas para o Pluggy.")

    # Get Pluggy API Key
    url = "https://api.pluggy.ai/auth"
    payload = {
        "clientId": clientID,
        "clientSecret": clientSecret
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json"
    }
    response = requests.post(url, json=payload, headers=headers)
    json_apiKey = json.loads(response.text)
    apiKey = json_apiKey["apiKey"]

    return apiKey

def getPluggy_transactions(apiKey, itemType, itemID, cardNumber, start_date, end_date):
    """ Connect to Pluggy API with Account's correspondent itemID and get transactions.
    :account_name: Actual's Account name to integrate transactions with. Use for exporting .csv (not implemented) 
    :param itemType: itemType from Pluggy Account (BANK, CREDIT)
    :param itemID: itemID from Pluggy connection (Demo Pluggy Connect)
    :param cardNumber: last 4 digits from credit card
    :param start_date: first date to search for transactions
    :param end_date: last date to search for transactions
    """
    # Pluggy API
    accountID = ""
    try: 
        headers = {
            "accept": "application/json",
            "X-API-KEY": apiKey
        }
        # List Accounts
        url = "https://api.pluggy.ai/accounts?itemId=" + itemID + "&type=" + itemType 
        response = requests.get(url, headers=headers)
        jAccounts = json.loads(response.text)
        
        if itemType == "BANK":
            accountID = jAccounts["results"][0]["id"]
        elif itemType == "CREDIT":
            # Se a conta possuir diversos cartões, procura até achar o correspondente
            for i in range(jAccounts["total"]):
                if jAccounts["results"][i]["number"] == cardNumber:
                    accountID = jAccounts["results"][i]["id"]

        # List Transactions
        url = "https://api.pluggy.ai/transactions?accountId=" + accountID + "&from=" + start_date + "&to=" + end_date
        response = requests.get(url, headers=headers)
        jTransactions = json.loads(response.text)
        # print("SUCCESS: Pluggy connected!")
    except:
        # print("FAILED Pluggy Connection!")
        return [], False

    nTransactions = jTransactions["total"]
    # print(f"Total Transactions: {nTransactions} | Pages: {jTransactions['totalPages']}")

    # | Date | Payee | Notes | Category | Amount | Cleared | Imported_ID
    # [["Date","Payee","Notes","Category","Payment/Deposit","Cleared", "imported_ID"]]

    def BANKtransactions (jTransactions):
        csv_data = []
        nTransactions = jTransactions["total"]
        for i in range(nTransactions):
            date = jTransactions['results'][i]['date'].split('T')[0]
            
            # Payment Method
            try:
                pay_method = jTransactions['results'][i]["paymentData"]["paymentMethod"]
                if pay_method == None: pay_method = "Unknown"
                else: pay_method = str(pay_method)
            except:
                pay_method = "No_method"

            # Payee or Notes
            tType = jTransactions["results"][i]["type"] # Transaction Type: CREDIT or DEBIT
            description = jTransactions['results'][i]["description"]
            payer, receiver = "", ""
            if tType == "CREDIT": # Dinheiro recebido
                try:
                    pay_docnumval = jTransactions['results'][i]["paymentData"]["payer"]["documentNumber"]["value"].replace("-", "").replace(".", "")
                    pay_doctype = jTransactions['results'][i]["paymentData"]["payer"]["documentNumber"]["type"]
                    pay_bank = jTransactions["results"][i]["paymentData"]["payer"]["routingNumber"] # Return bank code
                    payer = " from " + pay_doctype + " " + pay_docnumval + " - BANK: " + pay_bank
                except:
                    payer = ""
            elif tType == "DEBIT": # Dinheiro enviado
                try:
                    merchant = jTransactions['results'][i]['merchant']['businessName'] # PJ
                    receiver = " to " + merchant
                except:
                    try:
                        rec_docnumval = jTransactions['results'][i]["paymentData"]["receiver"]["documentNumber"]["value"].replace("-", "").replace(".", "") # PF
                        rec_doctype = jTransactions['results'][i]["paymentData"]["receiver"]["documentNumber"]["type"]
                        rec_bank = jTransactions["results"][i]["paymentData"]["receiver"]["routingNumber"]  # Return bank code
                        receiver = " to " + rec_doctype + " " + rec_docnumval + " - BANK: " + rec_bank
                    except:
                        receiver = ""
            payee = pay_method + payer + receiver #" "
            notes = description #+ " | " + pay_method + payer + receiver
            category = "" # jtransactions['results'][i]["category"]
            amount = str(jTransactions['results'][i]["amount"])
            cleared = ""
            imported_ID = str(jTransactions['results'][i]["id"])
            new_data = [date, payee, notes, category, amount, cleared, imported_ID]
            csv_data.append(new_data)
        return csv_data
    
    def CREDITtransactions (jTransactions):
        csv_data = []
        nTransactions = jTransactions["total"]
        for i in range(nTransactions):
            date = jTransactions['results'][i]['date'].split('T')[0]
            category_raw = jTransactions['results'][i]["category"]
            # Description strip
            description = jTransactions['results'][i]["description"]
            try:
                description_payee = description.split(" PARC ")[0].strip()
            except:
                description_payee = description.strip()

            # Verify installments (Parcelamento)
            try:
                totalPARC = jTransactions['results'][i]['creditCardMetadata']['totalInstallments']
                PARCnumber = jTransactions['results'][i]['creditCardMetadata']['installmentNumber']
            except:
                totalPARC = 1
                PARCnumber = 1
            
            # Define amount como valor da parcela * total de parcelas
            # O amount do json se refere ao valor da parcela
            amount_raw = abs(jTransactions['results'][i]["amount"])
            if PARCnumber == 1:
                amount = round(totalPARC * amount_raw, 2)
            else:
                amount = 0
            description_PARC = f" | PARC: {PARCnumber}/{totalPARC} | R$ {amount_raw}"

            # Notes and Amount
            tType = jTransactions["results"][i]["type"] # Transaction Type: CREDIT or DEBIT
            if tType == "CREDIT": # Dinheiro recebido
                amount = amount
  
            elif tType == "DEBIT": # Dinheiro enviado
                amount = -amount
                # merchant = jTransactions['results'][i]['merchant']['businessName'] # PJ
 
            payee = description_payee
            notes = description + " | " + category_raw + description_PARC #+ " | " + 
            category = ""
            amount = str(amount)
            cleared = ""
            imported_ID = str(jTransactions['results'][i]["id"])
            new_data = [date, payee, notes, category, amount, cleared, imported_ID]
            csv_data.append(new_data)
        return csv_data
    
    if itemType == "BANK":
        csv_data = BANKtransactions(jTransactions)
    elif itemType == "CREDIT":
        csv_data = CREDITtransactions(jTransactions)

    return csv_data, True

def data_to_actual(csv_data, actual_session, account):
    ruleset = get_ruleset(actual_session)
    added_transactions = []
    for row in csv_data:
        # here, we define the basic information from the file
        date, payee, notes, category, amount, cleared, imported_ID = (
            datetime.strptime(row[0], "%Y-%m-%d").date(),  # transform to date
            row[1],
            row[2],
            row[3],
            decimal.Decimal(row[4]),  # transform to decimal
            row[5] == "Cleared",  # transform to boolean
            row[6],
        )
        t = reconcile_transaction(
            actual_session,
            date,
            account,
            payee,
            notes,
            category,
            amount,
            imported_ID,
            cleared=cleared,
            imported_payee=payee,
            already_matched=added_transactions,
        )
        actual_session.flush()  # flush to load the ids and relationships
        # print(t)
        ruleset.run(t)  # run the rule here
        added_transactions.append(t)
        
        # if t.changed():
        #     print(f"Added or modified {t}")

def getPluggy_acc_config(account_notes):
    """
    Search for Pluggy links configurated within Actual
    Template: #pluggy accountType, itemID
    accountType = BANK or CREDIT
    """
    pluggyLink = 0
    accNotes, itemID, itemType, cardNumber = "", "", "", ""
    try:
        accNotes = account_notes.split("\n")
        for line in accNotes:
            if line.startswith("#pluggy"):
                pluggyLink += 1
                # print(f"Pluggy link configured!")
                accNotes = line.split('"')[1]
                # accNotes = line.strip("#pluggy").strip().split(",")
                itemType = accNotes.split(",")[0].strip()
                itemID = accNotes.split(",")[1].strip()
                if itemType == "CREDIT":
                    cardNumber = accNotes.split(",")[2].strip()
    except:
        pluggyLink += 0
    return pluggyLink, itemType, itemID, cardNumber

def pluggy_range_dates(session, account, range_days):
    """ 
    Define o range de datas para consulta na API Pluggy.
        Busca a última transação no Actual para definir como start_date.
        Força start_date = today - range_days, caso a última transação seja mais recente.
    """
    days_delta = timedelta(days=range_days)
    today = datetime.today()
    start_tdate = today - timedelta(days=30)
    transactions = get_transactions(session, start_tdate, account=account)
    bigger_date = int((today - timedelta(days=10)).strftime('%Y%m%d'))
    for t in transactions:
        date = t.date
        bigger_date = date if bigger_date < date else bigger_date
    last_tdate = datetime.strptime(str(bigger_date), "%Y%m%d")
    if today - last_tdate < days_delta: 
        start_date = today - days_delta
        end_date = today
    else: 
        start_date = last_tdate
        end_date = last_tdate + timedelta(days=10)

    start_date = start_date.strftime('%Y-%m-%d')
    end_date = end_date.strftime('%Y-%m-%d')
    # print(f"Fetching transactions from {start_date} to {end_date}.")
    return start_date, end_date

def pluggy_sync(URL_ACTUAL, PASSWORD_ACTUAL, FILE_ACTUAL, start_date, end_date, apiKey):
    """
    Connects to Pluggy API and extract bank transactions to sync with Actual
    Requires free (personal) version of Pluggy (demo.pluggy.ai) and actualpy API
    """
    with Actual(base_url=URL_ACTUAL, password=PASSWORD_ACTUAL, file=FILE_ACTUAL) as actual:
        # Busca token para conexão de cada conta
        errFlag = 0
        accounts = get_accounts(actual.session)
        for account in accounts:
            accName = account.name
            if accName != "Pluggy":
                # print(f"\n{accName}: Verifying link with Pluggy.")
                pluggyLink, itemType, itemID, cardNumber = getPluggy_acc_config(account.notes)

                if pluggyLink > 1: 
                    print(f"More than one #pluggy data found for {accName} - Only 1 is expected.")
                    errFlag += 1
                elif pluggyLink == 0: 
                    # print(f"Account not linked.")
                    errFlag += 1

                elif pluggyLink == 1:
                    # start_date, end_date = pluggy_range_dates(actual.session, account, range_days=5)
                    csv_data, pluggy_status = getPluggy_transactions(apiKey, itemType, itemID, cardNumber, start_date, end_date)

                    if pluggy_status: # if pluggy connection failed, do nothing
                        print(f"Starting Actual reconciliation for {accName}")
                        data_to_actual(csv_data, actual.session, account)
        actual.commit() # push the changes to the server

def get_pluggy_api(URL_ACTUAL, PASSWORD_ACTUAL, FILE_ACTUAL):
    # Conectar ao Actual e obtém credenciais Pluggy configuradas
    # Utiliza credenciais para conectar com API Pluggy
    # Em caso de falha, soma +1 no errFlag
    with Actual(base_url=URL_ACTUAL, password=PASSWORD_ACTUAL, file=FILE_ACTUAL) as actual:
        pluggy = get_account(actual.session, "Pluggy")
        apiKey = getPluggy_secrets(pluggy.notes)
    return apiKey
from database.database import init_database
from services.account_service import insert_accounts, list_accounts, count_accounts
from services.transaction_service import insert_transactions, list_transactions, count_transactions
from simulation.account_generator import generate_accounts
from simulation.transaction_generator import generate_transactions

init_database()
print('DB initialized')
existing_accounts = count_accounts()
print('existing accounts', existing_accounts)
accounts = generate_accounts(5, start_index=existing_accounts + 1)
insert_accounts(accounts)
print('stored accounts', len(list_accounts()))
existing_tx = count_transactions()
print('existing transactions', existing_tx)
transactions = generate_transactions(list_accounts(), 10, start_index=existing_tx + 1)
insert_transactions(transactions)
print('stored tx', len(list_transactions()))
print('sample account', list_accounts()[0])
print('sample tx', list_transactions()[0])

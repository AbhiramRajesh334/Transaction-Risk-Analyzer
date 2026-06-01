from database.database import init_database
from services.account_service import insert_accounts, list_accounts
from services.transaction_service import insert_transactions
from simulation.account_generator import generate_accounts
from simulation.transaction_generator import generate_transactions
from app.simulation.fraud_injector import inject_scenarios, list_ground_truth

init_database()
accounts = list_accounts()
if len(accounts) < 10:
    new_accounts = generate_accounts(10, start_index=len(accounts) + 1)
    insert_accounts(new_accounts)
    accounts = list_accounts()

transactions = generate_transactions(accounts, 50, start_index=1)
insert_transactions(transactions)
print('normal accounts', len(accounts))
print('normal tx', len(transactions))
result = inject_scenarios()
print('injection result', result)
ground_truth = list_ground_truth()
print('ground truth count', len(ground_truth))
print('sample ground truth', ground_truth[:3])

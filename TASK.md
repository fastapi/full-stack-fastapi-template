# Backend task for implementation

Create a backend endpoints which implements following functionality:

- Introduce a new entity Wallet and Transaction.
- Wallet should have fields: id, user_id (foreign key to User), balance (float), currency (string).
- Available currencies: USD, EUR, RUB.
- Transaction should have fields: id, wallet_id (foreign key to Wallet), amount (float), type (enum: 'credit', 'debit'), timestamp (datetime), currency (string).
- Implement endpoint to create a wallet for a user.
- Implement endpoint to get wallet details including current balance.
- Implement endpoint to create a transaction (credit or debit) for a wallet.

# Rules for wallet

- A user can have three wallets.
- Wallet balance should start at 0.0.
- Arithmetic operations on balance should be precise up to two decimal places.

# Rules for transaction

- For 'credit' transactions, the amount should be added to the wallet balance.
- For 'debit' transactions, the amount should be subtracted from the wallet balance.
- Ensure that the wallet balance cannot go negative. If a debit transaction would cause the balance to go negative, the transaction should be rejected with an appropriate error message.
- Transaction between wallets with different currencies must be converted using a fixed exchange rate (you can hardcode some exchange rates for simplicity) and fees should be applied.

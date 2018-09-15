# Lisk Reward Distributor
A tool to calculate and distribute forging rewards among voters.

Only compatible with Lisk Core 1.0 and up.

If you like this software, please consider a donation =] `6725360537423611335L`

## Prerequisites
@karek314's [LISK-PHP](https://github.com/karek314/lisk-php) is used for pushing TXs to the network. 

Please install and configure this tool before proceeding.

## Installation & Configuration
```
git clone https://github.com/Lemii/lisk-reward-distributor
cd lisk-reward-distributor
pip install -r requirements.txt
```

#### config.json
Most of the values are already pre-configured. If you're only using this on testnet and have installed everything as user 'Lisk' in the default directories, simply add your `delegate_address` and `passphrase` and go to **Usage**.

If you want to customize more values, please see the list below:

```
node                            Node address used for API calls.
delegate_address                Your delegate's address
passphrase                      Your 12 word mnemonic passphrase
second_passphrase               Your (optional) second 12 word mnemonic passphrase (default = false)
limit                           Maximum weight of a voter (default of 70500000000000 equals 750,000 LSK)
percentage                      Total sharing percentage
fee                             Transaction fee that will be deducted from payment
threshold                       Payout threshold
lisk-php_path                   Path to lisk-php
exclusions                      Addresses that will be excluded from reward calcution and distribution
dev                             Enable or disable "dev mode"
```
While `dev` is `true`, all payment TXs will be printed to screen rather than pushed out to the network.


Node ports:
- 8000 = mainnet
- 7000 = testnet
- 5000 = betanet


## Usage
Even though it's possible to run this script manually, it is highly recommended to set up a Cron Job to do it for you.

The example below runs the script every day at 12:00. 
```
crontab -e 
```

Add line:
```
0 12 * * * /usr/bin/python [path to lisk-reward-distributor.py]
```

## How it works
When the script is ran, the following things happen:
1. Voter database gets imported from csv. If no database exists, a new one is created
2. New voters are added to database
3. All voters' weight (balances) are updated
4. Total forged Lisk since last timestamp is calculated
5. Each voter's reward is calculated (can be limited to X relational amount in config)
6. Rewards are added to voters' pending balances
7. If new pending balance exceeds configured payout threshold, construct TX command line and send to lisk-php 
8. If TX is sent, reset voter's balance to 0
9. New voter dabase is dumped to csv
10. New timestamp is dumped to file

All steps are logged in `lisk-reward-distributor.log`.

## License
Licensed under the [MIT license](https://github.com/Lemii/lisk-reward-distributor/blob/master/LICENSE)

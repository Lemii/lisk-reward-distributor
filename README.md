# Lisk Reward Distributor
##### Current version: 1.0 (rc1)
##### Platform: Ubuntu

A tool to calculate and distribute forging rewards.

Only compatible with Lisk Core 1.0 and up.

## Requirements
karek314's [LISK-PHP](https://github.com/karek314/lisk-php) is required for pushing TXs to the network.

## Installation & Configuration
```git clone https://github.com/Lemii/lisk-reward-distributor```

#### config.json
```
node				Your node address 
delegate_address	        Your delegate address
passphrase			Your 12 word mnemonic passphrase
limit 				Maximum weight of a voter (default of 30000000000000 equals 300,000 LSK)
percentage			Total sharing percentage
fee				Transaction fee that will be deducted from payment
threshold			Payout threshol
```
The "dev" value can be set to "true" to (temporarily) enable an alternative set of "dev" variables. While in "dev" mode, the payment TXs will be printed to screen rather than pushed out to the network.

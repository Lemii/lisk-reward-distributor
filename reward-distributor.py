import requests
import json
import sys
import time
import datetime
import csv
import subprocess


# Open config file and set variables
with open("config.json", "r") as json_f:
	json_config = json.load(json_f)

	# Set alternative "dev" variables for testing purposes
	if json_config["dev"]:
		node = json_config["dev-node"]
		script_path = json_config["dev-script_path"]
		timestamp = json_config["dev-timestamp"]

	# Set regular variables
	else:
		node = json_config["node"]
		script_path = json_config["script_path"]

		try:
			with open(script_path + "timestamp", "r") as f:
				timestamp = f.read()

		except:
			timestamp = int(time.time() * 1000)

	lisk_php = json_config["lisk-php_path"]
	delegate_address = json_config["delegate_address"]
	passphrase = '"%s"' % json_config["passphrase"]
	limit = json_config["limit"]
	percentage = float(json_config["percentage"] * 0.01)
	fee = json_config["fee"]
	threshold = json_config["threshold"]
	exclusions = json_config["exclusions"]


# Log message to file
def logger(msg):
	with open(script_path + "reward-distributor.log", "a") as f:
		f.write("%s - %s\n" % (str(datetime.datetime.now()), msg))


# Convert request to Python object
def get_json_data(url):
	response = requests.get(url)
	return response.json()
	#return json.loads(response.json())	


# Calculate total forged amount from previous timestamp	
def get_forging_reward(start_timestamp):
	logger('Calculating forging reward..')

	json_data = get_json_data(node + "api/delegates/%s/forging_statistics?fromTimestamp=%s" % (delegate_address, start_timestamp))
	reward = (int(json_data['data']['forged']) / 100000000) * percentage
	
	logger("LSK to be distributed: %s" % reward)	
	return reward


# Update voter database with new entries
def update_voters():
	logger("Updating voters..")

	def voter_update_iteration(json_data):
		for voter in json_data['data']['voters']:
			if voter['address'] not in voters_check and voter['address'] not in exclusions:
				voter_as_list = [voter['address'], voter['balance'], 0.0]
				voters.append(voter_as_list)
				logger("%s added to database" % voter['address'])

	json_data = get_json_data(node + "api/voters?address=%s" % (delegate_address))
	
	# Set offset interation amount - Mandatory because API output is limited to 100 entries
	offset, leftovers = divmod(json_data['data']['votes'], 100)

	i = 0
	while i < (offset + 1):
		voter_update_iteration(get_json_data(node + "api/voters?limit=100&address=%s&offset=%s" % (delegate_address, i * 100)))
		i += 1

	logger("Total voters: %s" % len(voters))


def update_voters_weight():
	logger("Updating existing voter's weight..")

	if len(voters) > 0:
		for voter in voters:
			logger("Updating %s's weight.." % voter[0])
			json_data = get_json_data(node + "api/accounts?address=%s" % voter[0])
			voter[1] = json_data['data'][0]['balance']

		logger("All weight updated")

	else:
		logger("No voters found")


def get_total_weight():
	weight = 0
	for voter in voters:
		if int(voter[1]) > limit:
			weight += limit
		else:
			weight += int(voter[1])
	return weight


def reward_distributor(reward):
	for x in voters:
		logger("Calculating %s's reward.." % x[0])

		# Limit voter's weight to distribute rewards more fairly
		if int(x[1]) > limit:
			weight = limit

		else:
			weight = x[1]

		relational_weight = float(weight) / float(get_total_weight())
		balance_old = float(x[2])
		x[2] = balance_old + (reward * relational_weight)	

		# Execute payout if above threshold
		if x[2] > threshold:
			logger("%.8f to be paid out" % (x[2]))
			cmd = "php %slisk-cli.php SendTransaction " % lisk_php + x[0]+ " " + "%.8f" % (x[2] - fee) + " %s" % passphrase
			
			# If "dev" is true, print out command line instead of push tx
			if json_config["dev"]:
				print cmd

			else:
				subprocess.Popen(cmd, shell=True)

			# Reset voter's balance to 0.0 after payout	
			x[2] = 0.0

		else:
			logger("%.8f > %.8f" % (balance_old, x[2]))


def main():		
	logger("Running script..")

		
	try:
		with open(script_path + "voters.csv", "r") as csv_file:
			csv_reader = csv.reader(csv_file, delimiter='\t')

			for line in csv_reader:
				voters.append(line)
				voters_check.append(line[0])

		logger("Voter database succesfully opened")
		
	except:
		logger("Creating new voter database")


	update_voters_weight()
	update_voters()
	reward_distributor(get_forging_reward(timestamp))


	# Backing up voter database before dumping new one
	logger("Backing up voters.csv")
	subprocess.Popen("cp voters.csv voters_backup.csv", shell=True)
			

	# Dump new database with current voters / balances	
	with open(script_path + "voters.csv", "w") as new_csv_file:
		logger("Writing updated database to voters.csv")

		csv_writer = csv.writer(new_csv_file, delimiter='\t')
		
		for line in voters:
			csv_writer.writerow(line)		


	# Dump new timestamp to file			
	with open(script_path + "timestamp", "w") as f:
		logger("Writing new timestamp to config (%s > %s)" % (timestamp, timestamp_new))
		f.write(str(timestamp_new))


	logger("Exiting script..\n-----------------------------------------")


voters = []
voters_check = []	
timestamp_new = int(time.time() * 1000)


if __name__ == "__main__":
	main()
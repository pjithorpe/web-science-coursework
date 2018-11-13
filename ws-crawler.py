from twython import Twython as twy
import json
import pandas as pd
import sys

def update_creds():
	# Store credentials
	credentials = {}
	credentials['CONSUMER_KEY'] = input("Consumer key: \n")
	credentials['CONSUMER_SECRET'] = input("Consumer secret: \n")
	credentials['ACCESS_TOKEN'] = input("Access token: \n")
	credentials['ACCESS_SECRET'] = input("Access secret: \n")

	with open("twitter_credentials.json", "w") as file:
		json.dump(credentials, file)


# Check if user wants to update credentials
if len(sys.argv) > 1 and sys.argv[1] == "-c":
	update_creds()		

# Load credentials from JSON file
with open("twitter_credentials.json", "r") as file:
	creds = json.load(file)

# TESTING TWYTHON

# Instantiate tweet object
python_tweets = twy(creds['CONSUMER_KEY'], creds['CONSUMER_SECRET'])

query = {
	'q': 'rugby',
	'result_type': 'popular',
	'lang': 'en',
}

# Search tweets
results_dict = {'user': [], 'date': [], 'text': [], 'favorite_count': []}
for status in python_tweets.search(**query)['statuses']:
	results_dict['user'].append(status['user']['screen_name'])
	results_dict['date'].append(status['created_at'])
	results_dict['text'].append(status['text'])
	results_dict['favorite_count'].append(status['favorite_count'])


# Put data into pandas DataFrame
df = pd.DataFrame(results_dict)
df.sort_values(by='favorite_count', inplace=True, ascending=False)
print(df.head(5))



# TASK 1

# a.

from twython import TwythonStreamer
import csv

def process_tweet(tweet):
	d = {}
	d['hashtags'] = [hashtag['text'] for hashtag in tweet['entities']['hashtags']]
	d['text'] = tweet['text']
	d['user'] = tweet['user']['screen_name']
	d['user_loc'] = tweet['user']['location']
	return d

class Streamer(TwythonStreamer):

	def on_success(self, data):

		# Only get English tweets
		if data['lang'] == 'en':
			tweet_data = process_tweet(data)
			self.save_to_csv(tweet_data)

	def on_error(self, status_code, data):
		print(status_code, data)
		self.disconnect()

	def save_to_csv(self, tweet):
		with open(r'saved_tweets.csv', 'a') as file:
			writer = csv.writer(file)
			writer.writerow(list(tweet.values()))

stream = Streamer(creds['CONSUMER_KEY'], creds['CONSUMER_SECRET'], creds['ACCESS_TOKEN'], creds['ACCESS_SECRET'])

stream.statuses.filter(track='rugby')
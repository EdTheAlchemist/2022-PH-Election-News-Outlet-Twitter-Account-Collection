from Configurations import BEARER_TOKEN
from twarc import Twarc2, expansions
from zoneinfo import ZoneInfo

import json
import pytz
import datetime

"""
2020 National Elections Campaign Period
Collection Duration: 09 Jan 2022 to 08 Jun 2022

List of Media Outlets   
	1. Abante
	2. Politiko
	3. ABS-CBN
	4. PTV
	5. BusinessMirror
	6. Radyo Pilipinas
	7. BusinessWorld
	8. Rappler
	9. CNN Philippines
	10. SMNI
	11. DZRH
	12. Summit Express
	13. Eagle News
	14. SunStar Philippines
	15. GMA Network
	16. Super Balita DZBB
	17. Manila Bulletin
	18. TeleRadyo
	19. Manila Standard
	20. The Philippine Star
	21. Manila Times
	22. TV5 Information
	23. Philippine Daily Inquirer

List of 2022 Presidential Candidate:
    1. Ernesto Corpus Abella - @ernieabella @ernieabella_ph
    2. Leodegario de Guzman  - @LeodyManggagawa
    3. Norberto Gonzales - @NBGonzalesph
    4. Ping Lacson - @iampinglacson
    5. Faisal Mangondato - @FaisalMangonda2
    6. Ferdinand Marcos Jr. - @bongbongmarcos
    7. Jose Montemayor - @DoctorneyJoey
    8. Isko Moreno - @IskoMoreno
    9. Manny Pacquiao - @MannyPacquiao
    10. Leni Robredo - @lenirobredo

List of 2022 Vice Presidential Candidate:
    1. Jose Livioko Atienza Jr. - @lito_atienza
    2. Walden Bello - @WaldenBello
    3. Rizalito David - @david_rizalito
    4. Sara Duterte - @indaysara
    5. Emmanuel Lopez - @MannySDLopez
    6. Willie Ong - @DocWillieOng
    7. Francis Pangilinan - @kikopangilinan
    8. Carlos Serapio
    9. Tito Sotto - @sotto_tito

Data to extract: Text, Date, Userhandle (who it came from), 
specify which candidate is being talked about
Repeated content still needed, sentiment, language 
"""

KEYWORDS = {
	# President Candidates
	'Abella': 			['Ernesto Corpus Abella', 'Ernesto Abella', 'Ernie Abella', 'Ernesto "Ernie" Abella', 'spokesperson Abella', '@ernieabella', '@ernieabella_ph'],
	'de Guzman': 		['Leodegario Quitain de Guzman', 'Leodegario de Guzman', 'Leody de Guzman', 'Ka Leody', '@LeodyManggagawa'],
	'Gonzales': 		['Norberto Borja Gonzales', 'Norberto Gonzales', '@NBGonzalesph'],
	'Lacson': 			['Panfilo Morena Lacson Sr.', 'Panfilo Lacson', 'Ping Lacson', '@iampinglacson'],
	'Mangondato': 		['Faisal Montay Mangondato', 'Faisal Mangondato', '@FaisalMangonda2'],
	'Marcos': 			['Ferdinand Romualdez Marcos Jr.', 'Ferdinand Marcos', 'Bongbong Marcos', 'Marcos Jr.', '@bongbongmarcos'],
	'Montemayor': 		['Jose Cabrera Montemayor Jr.', 'Jose Montemayor', '@DoctorneyJoey'],
	'Moreno': 			['Francisco Moreno Domagoso', 'Francisco Domagoso', 'Isko Moreno', '@IskoMoreno'],
	'Pacquiao': 		['Emmanuel Dapidran Pacquiao Sr.', 'Emmanuel Pacquiao', 'Manny Pacquiao', '@MannyPacquiao'],
	'Robredo': 			['Maria Leonor Gerona Robredo', 'Maria Leonor Robredo', 'Leni Robredo', '@lenirobredo'],
	
	# Vice President Candidates
	'Atienza': 			['Jose Livioko Atienza Jr.','Jose Atienza', 'Lito Atienza', '@lito_atienza'],
	'Bello': 			['Walden Flores Bello', 'Walden Bello', '@WaldenBello'],
	'David': 			['Rizalito Yap David','Rizalito David', '@david_rizalito'],
	'Duterte': 			['Sara Zimmerman Duterte-Carpio', 'Sara Duterte-Carpio', 'Sara Duterte', 'Duterte-Carpio', 'Inday Sara', '@indaysara'],
	'Lopez': 			['Emmanuel Santo Domingo Lopez', 'Emmanuel SD Lopez', 'Emmanuel Lopez', 'Manny SD Lopez', 'Manny Lopez', '@MannySDLopez'],
	'Ong': 				['Willie Tan Ong', 'Willie Ong', '@DocWillieOng'],
	'Pangilinan': 		['Francis Pancratius Nepomuceno Pangilinan', 'Francis Pancratius Pangilinan', 'Francis Pangilinan', 'Kiko Pangilinan', '@kikopangilinan'],
	'Serapio': 			['Carlos Gelacio Serapio', 'Carlos Serapio', 'Kuya Charlie Serapio'],
	'Sotto': 			['Vicente Castelo Sotto III','Vicente Sotto', 'Tito Sotto', '@sotto_tito'],

	# General Hashtags
	'general_hastags' : ['#nle2022', '#2022nle', '#bumotoka', '#halalan2022', '#piniliay2022', '#hijalalan2022', '#phvote', '#phvoteresults', '#wedecide', '#votesafepilipinas', '#askpilipinasdebates', '#eleksyon2022', '#pilipinasdebates2022']
}

def prepare_keywords(list_of_words):
	query = "("
	for keyword in list_of_words[:-1]:
		query = query + '"' +  keyword + '"' +  " OR "
	query = query + list_of_words[-1] + ")"

	return query

# Current account to search
ACCOUNTS = [
	'AbanteNews',
	'Politiko_Ph',
	'ABSCBNNews',
	'PTVph',
	'BusinessMirror',
	'radyopilipinas1',
	'bworldph',
	'rapplerdotcom',
	'cnnphilippines',
	'smninews',
	'dzrhnews',
	'mysummitexpress',
	'EagleNews',
	'sunstaronline',
	'gmanews',
	'dzbb',
	'manilabulletin',
	'DZMMTeleRadyo',
	'MlaStandard',
	'PhilippineStar',
	'TheManilaTimes',
	'News5PH',
	'phildailyinq'
]

# Client information
client = Twarc2(bearer_token=BEARER_TOKEN)

def main():
	# Prints when the program starts
	print("Time script started:", datetime.datetime.now())

	# Start: first microsecond of 09 Jan 2022 UTC+8
	start_time = datetime.datetime(2022, 1, 9, 0, 0, 0, 0, pytz.timezone("Asia/Manila"))
	# End: last microsecond of 08 Jun 2022 UTC+8
	end_time = datetime.datetime(2022, 6, 8, 23, 59, 59, 59, pytz.timezone("Asia/Manila"))

	for account in ACCOUNTS:
		# Prints which new outlet is currently being collected from
		print("\tcollecting from", account, "...")
		for key in KEYWORDS:
			# Prints which keywords are currently being searched
			print("\t\tsearching for keywords of", key, "...")

			# Search for non-retweet tweets from the selected Twitter account using the keyword query
			full_query = prepare_keywords(KEYWORDS[key]) + " from:" + account + " -is:retweet"

			# Ready the client using the specified attributes
			search_results = client.search_all(
				query=full_query, 
				start_time=start_time, 
				end_time=end_time, 
				max_results=100)

			# Ready the file name
			OUTPUT_FILE_NAME = "Raw Tweets/%s_raw_tweet_dump.jsonl" % (account.lower())

			# Writes the results to a JSONL file for later processing
			for page in search_results:
				result = expansions.flatten(page)
				with open(OUTPUT_FILE_NAME, "a+") as f:
					for tweet in result:
						temp = {
							'id': tweet['id'],
							'created_at': str(datetime.datetime.strptime(tweet['created_at'] ,"%Y-%m-%dT%H:%M:%S.%fZ").astimezone(ZoneInfo('Asia/Manila'))),
							'author': tweet['author']['username'],
							'lang': tweet['lang'],
							'text': tweet['text']
						}

						f.write(json.dumps(temp) + "\n")

	# Prints when the program ends
	print("Time script ended:", datetime.datetime.now())

if __name__ == "__main__":
    main()
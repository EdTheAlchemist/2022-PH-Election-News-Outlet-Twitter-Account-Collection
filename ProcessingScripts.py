from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas as pd
import datetime
import json
import os
import regex as re

ANALYZER = SentimentIntensityAnalyzer()

KEYWORDS = {
	# President Candidates
	'Abella': 			[r'Ernesto Corpus Abella', r'Ernesto Abella', r'Ernie Abella', 'Ernesto "Ernie" Abella', r'spokesperson Abella', r'@ernieabella', r'@ernieabella_ph'],
	'de Guzman': 		[r'Leodegario Quitain de Guzman', r'Leodegario de Guzman', r'Leody de Guzman', r'Ka Leody', r'@LeodyManggagawa'],
	'Gonzales': 		[r'Norberto Borja Gonzales', r'Norberto Gonzales', r'@NBGonzalesph'],
	'Lacson': 			[r'Panfilo Morena Lacson Sr\.?', r'Panfilo( \'Ping\')? Lacson', r'Ping Lacson', r'Sen\.? Lacson' r'@iampinglacson'],
	'Mangondato': 		[r'Faisal Montay Mangondato', r'Faisal Mangondato', r'@FaisalMangonda2'],
	'Marcos': 			[r'Ferdinand R(omualdez|\.)? Marcos Jr\.?', r'Ferdinand Marcos', r'Ferdinand "Bongbong" Marcos', r'Bong[Bb]ong Marcos', r'Marcos,? Jr', r'@bongbongmarcos'],
	'Montemayor': 		[r'Jose Cabrera Montemayor Jr\.?', r'Jose Montemayor', r'@DoctorneyJoey'],
	'Moreno': 			[r'Francisco Moreno Domagoso', r'Francisco Domagoso', r'Isko Moreno', r'@IskoMoreno'],
	'Pacquiao': 		[r'Emmanuel Dapidran Pacquiao Sr\.?', r'Emmanuel Pacquiao', r'Manny Pacquiao', r'@MannyPacquiao'],
	'Robredo': 			[r'Maria Leonor Gerona Robredo', r'Maria Leonor Robredo', r'Leni Robredo', r'@lenirobredo'],
	
	# Vice President Candidates
	'Atienza': 			[r'Jose Livioko Atienza Jr\.?',r'Jose Atienza', r'Lito Atienza', r'@lito_atienza'],
	'Bello': 			[r'Walden Flores Bello', r'Walden Bello', r'@WaldenBello'],
	'David': 			[r'Rizalito Yap David',r'Rizalito David', r'@david_rizalito'],
	'Duterte': 			[r'Sara Zimmerman Duterte-Carpio', r'Sara Duterte-Carpio', r'Sara Duterte', r'Duterte-Carpio', r'Inday Sara', r'Mayor Sara', r'@indaysara'],
	'Lopez': 			[r'Emmanuel Santo Domingo Lopez', r'Emmanuel SD Lopez', r'Emmanuel Lopez', r'Manny SD Lopez', r'Manny Lopez', r'@MannySDLopez'],
	'Ong': 				[r'Willie Tan Ong', r'Willie Ong', r'@DocWillieOng'],
	'Pangilinan': 		[r'Francis Pancratius Nepomuceno Pangilinan', r'Francis Pancratius Pangilinan', r'Francis Pangilinan', r'Kiko Pangilinan', r'@kikopangilinan'],
	'Serapio': 			[r'Carlos Gelacio Serapio', r'Carlos Serapio', r'Kuya Charlie Serapio'],
	'Sotto': 			[r'Vicente Castelo Sotto III',r'Vicente Sotto', r'Tito Sotto', r'@sotto_tito'],

	# General Hashtags
	'General Hastags' : [r'#nle2022', r'#2022nle', r'#bumotoka', r'#halalan2022', r'#piniliay2022', r'#hijalalan2022', r'#phvote', r'#phvoteresults', r'#wedecide', r'#votesafepilipinas', r'#askpilipinasdebates', r'#eleksyon2022', r'#pilipinasdebates2022']
}

KEYWORDS_AS_EXPRESSION = ""
for keywords in KEYWORDS:
	if keywords != 'general_hastags':
		KEYWORDS_AS_EXPRESSION += "|".join(KEYWORDS[keywords])
	KEYWORDS_AS_EXPRESSION += "|"
KEYWORDS_AS_EXPRESSION = KEYWORDS_AS_EXPRESSION[:-1]
KEYWORDS_REGEX = re.compile(KEYWORDS_AS_EXPRESSION, flags=re.IGNORECASE)

def extract_usernme(entry):
	return dict(entry)['username']

def read_output_file(file_name):
	tweet_df = pd.read_json(path_or_buf=file_name, lines=True)
	tweet_df.drop_duplicates()
	
	tweet_df = tweet_df[['id', 'created_at', 'author', 'lang', 'text']]
	tweet_df['id'] = tweet_df['id'].astype(str)
	tweet_df['author'] = tweet_df['author']
	tweet_df['created_at'] = tweet_df['created_at'].dt.tz_convert('Asia/Manila')
	tweet_df['created_at'] = tweet_df['created_at'].apply(lambda a: datetime.datetime.strftime(a, "%Y-%m-%d %H:%M:%S"))
	tweet_df.rename(columns={'id': 'Tweet ID', 'created_at': 'Created at UTC+8', 'author': 'News Outlet', 'lang': 'Language Tag', 'text': 'Text'}, inplace=True)

	return tweet_df

def extract_sentiment(tweet_df):
	tweet_df['vader_compound'] = [ANALYZER.polarity_scores(x)['compound'] for x in tweet_df['Text']]
	tweet_df['vader_neg'] = [ANALYZER.polarity_scores(x)['neg'] for x in tweet_df['Text']]
	tweet_df['vader_neu'] = [ANALYZER.polarity_scores(x)['neu'] for x in tweet_df['Text']]
	tweet_df['vader_pos'] = [ANALYZER.polarity_scores(x)['pos'] for x in tweet_df['Text']]
	
	return tweet_df

def check_if_present(entry, keywords):
	for category, keywords in KEYWORDS.items():
		tweet_df[category] = tweet_df['Text'].str.contains("|".join(keywords))
	return false

def extract_keyword_information(tweet_df):
	for category, items in KEYWORDS.items():
		tweet_df[category] = tweet_df['Text'].str.contains(pat="|".join(items), regex=True, flags=re.IGNORECASE)
	tweet_df['category_count'] = tweet_df[[key for key in KEYWORDS]].astype(int).sum(axis=1)

	return tweet_df

def anonymization(text):
	return KEYWORDS_REGEX.sub('__KEYWORD__', text)

def annonymize_keywords(tweet_df):
	tweet_df['Annonymized Text'] = tweet_df['Text'].apply(anonymization)
	return tweet_df

def write_df_to_excel(tweet_df, file_name='output.xlsx'):
	if file_name[-4:] == 'xlsx':
		writer = pd.ExcelWriter(file_name)
		tweet_df.to_excel(writer, 'Sentiments', index=False)
		writer.save()
	else:
		raise ValueError('Error with file name (%s). Please ensure file name ends with xlsx' % file_name)

def main():
	directory = "Raw Tweets/"
	list_of_dfs = []
	for file in os.listdir(directory):
		print(f"Working on {file}...")
		if file.endswith(".jsonl"): 
			temp_df = read_output_file(directory + file)
			temp_df = extract_keyword_information(temp_df)
			temp_df = annonymize_keywords(temp_df)
			temp_df = extract_sentiment(temp_df)
			list_of_dfs.append(temp_df)

	tweet_df = pd.concat(list_of_dfs)
	write_df_to_excel(tweet_df=tweet_df, file_name='Output/tweets_and_sentiment.xlsx')

if __name__ == "__main__":
	main()
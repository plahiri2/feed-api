import subprocess
import sys
import os
#sys.path.insert(0,os.getcwd())
import json
import unittest
import requests
#import threading
import time
from multiprocessing import Process
from pymongo import MongoClient
import api.feedsapp as app

def db_setup():
	client = MongoClient('localhost', 27017)
	client.drop_database('testdb')
	db=client['testdb']
	users=[{"user_id":"user1",
			"feeds":["feed1","feed2","feed3"]},
			{"user_id":"user2",
			 "feeds":["feed1","feed2"]},
			{"user_id":"user3",
			 "feeds":["feed2"]}]

	db.user.insert_many(users)

	feeds=[{"feed_id":"feed1",
			"articles":["article1","article2","article3"]},
		   {"feed_id":"feed2",
			"articles":["article1","article2"]},
		   {"feed_id":"feed3",
			"articles":["article2"]}]

	db.feed.insert_many(feeds)

	articles=[{"article_id":"article1",
		"title":"title1","description":"description1"},
			   {"article_id":"article2",
				  "title":"title2","description":"description2"},
			  {"article_id":"article3",
			   "title":"title3","description":"description3"}]

	db.article.insert_many(articles)
	#client.close()
	#return db

class APITestCase(unittest.TestCase):
	def setUp(self):
		db_setup()
		app.app.config["MONGO_DBNAME"] = "testdb"
		self.app_process=Process(target=app.app.run,kwargs={'threaded': True})
		self.app_process.start()
		time.sleep(1)

	def tearDown(self):
		self.app_process.terminate()

class UserAPITestCase(APITestCase):
	
	def test_getuser(self):
		response = requests.get('http://localhost:5000/feedsapp/api/v1.0/users/user3')
		response_json = response.json()
		self.assertEqual(response_json['user'][0]['user_id'],'user3')
		self.assertEqual(response_json['user'][0]['feeds'],['feed2'])	


class FeedAPITestCase(APITestCase):
	def test_get_user_feeds(self):
		response = requests.get('http://localhost:5000/feedsapp/api/v1.0/feeds/user1')
		response_json = response.json()
		self.assertEqual(len(response_json['feeds']),3)
	
	def test_get_all_feeds(self):
		response = requests.get('http://localhost:5000/feedsapp/api/v1.0/feeds/')
		response_json = response.json()
		self.assertEqual(len(response_json['feeds']),3)
				
	def test_subscribe_feed(self):
		response = requests.post('http://localhost:5000/feedsapp/api/v1.0/feeds/user2',
									json={'subscribe':'feed3'})
		response_json = response.json()
		self.assertEqual(len(response_json['user'][0]['feeds']),3)

	def test_unsubscribe_feed(self):
		response = requests.post('http://localhost:5000/feedsapp/api/v1.0/feeds/user2',
									json={'unsubscribe':'feed2'})
		response_json = response.json()
		self.assertEqual(len(response_json['user'][0]['feeds']),1)

	def test_add_article_feed(self):
		response = requests.post('http://localhost:5000/feedsapp/api/v1.0/feeds/feed2',
				                    json={'article':'article3'})

		response_json = response.json()
		feed2_len=0
		for i in range(len(response_json['feeds'])):
			if response_json['feeds'][i]["feed_id"]=="feed2":
				feed2_len=len(response_json['feeds'][i]['articles'])
		self.assertEqual(feed2_len,3)

class ArticleAPITestCase(APITestCase):
	def test_get_all_articles(self):
		response = requests.get('http://localhost:5000/feedsapp/api/v1.0/articles/user1')
		response_json = response.json()
		self.assertEqual(len(response_json['articles']),3)

if __name__=="__main__":
	unittest.main()




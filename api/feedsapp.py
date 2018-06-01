#!flask/bin/python


from flask import Flask, jsonify, redirect, url_for
from flask_restful import Api, Resource, reqparse, fields, marshal
from flask_pymongo import PyMongo
from pymongo import MongoClient

app = Flask(__name__, static_url_path="")
app.config["MONGO_DBNAME"] = "testdb"
mongo = PyMongo(app, config_prefix='MONGO')
api = Api(app)

def db_setup():
	"""
	Helper function to setup a mongoDB called testdb
	with some dummy data
	"""
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
	client.close()

class UserAPI(Resource):
	"""
	Class implementing User API
	Fields:
	==========================================================================
	user_id: String
	feeds: list of strings (which are feed_id's)

	Calls Handled:
	===========================================================================
	GET /feedsapp/api/v1.0/users/[user_id]

	"""
	def __init__(self):
		self.user_fields = {'user_id': fields.String, 
							'feeds': fields.List(fields.String)}
		super(UserAPI, self).__init__()

	def get(self,user_id):
		user = mongo.db.user.find_one({'user_id':user_id})
		if user:
			return jsonify({'user': [marshal(user,self.user_fields)]})
		else:
			return {"response": "User does not exist"}

class FeedAPI(Resource):
	"""
	Class implementing Feed API
	Fields:
	========================================================================
	feed_id: String
	articles: list of strings (which are article_id's)

	Calls Handled:
	========================================================================
	GET /feedsapp/api/v1.0/feeds/
	GET /feedsapp/api/v1.0/feeds/[user_id]
	POST /feedsapp/api/v1.0/feeds/[id]
	"""

	def __init__(self):
		self.feed_fields = {'feed_id': fields.String, 
							'articles': fields.List(fields.String)}
		self.reqparse = reqparse.RequestParser()
		
		# Argument parsing for post request
		self.reqparse.add_argument('subscribe', type = str, location = 'json')	
		self.reqparse.add_argument('unsubscribe', type = str, location = 'json')
		self.reqparse.add_argument('article', type = str, location = 'json')
		super(FeedAPI,self).__init__()

	def get(self, user_id=None):
		
		# If user_id provided, fetch feeds only for that user
		if user_id:
			user = mongo.db.user.find_one({'user_id':user_id})
			if user:
				feed_ids = user['feeds']
				feeds = mongo.db.feed.find({'feed_id':{'$in': feed_ids}})
			else:
				feeds=mongo.db.feed.find({})
		
		# Fetching all feeds	
		else:
			feeds=mongo.db.feed.find({})
		return jsonify({'feeds': [marshal(feed, self.feed_fields) for feed in feeds]})

	def post(self, user_id):
		args = self.reqparse.parse_args()
		
		# Reading post json data
		a=args['article']
		s=args['subscribe'] 
		u=args['unsubscribe']

		# Only one operation allowed per request
		if all([a,s]) or all([a,u]) or all([a,s]):
			return {"response": "Only one of subscribe, unsubscribe or\
								article allowed at at time"}
		
		# Subscribe operation
		if s:
			
			# Checking if feed to be subscribed to exists
			if mongo.db.feed.find_one({'feed_id':s}):
				mongo.db.user.update(
					{ 'user_id': user_id },
					{ '$push': { 'feeds': s} })
				
				# Redirect to show updated data for user
				return redirect(url_for("user",user_id=user_id))
			else:
				return {"response": "Feed does not exist"}

		# Unsubscribe operation
		elif u:
			mongo.db.user.update(
				{ 'user_id': user_id },
				{ '$pull': {'feeds': u }})
			
			# redirect to show updated data for user
			return redirect(url_for("user",user_id=user_id))
		
		# Add Article to feed. Article must already exist
		elif a:
			if mongo.db.article.find_one({'article_id': a}):
				# here the variable user_id is actually a feed_id
				mongo.db.feed.update(
					{ 'feed_id': user_id },
					{ '$push': {'articles': a }})

				# redirect to show all feeds
				return redirect(url_for("feeds"))
			else:
				return {'response': "Article does not exist"}
			
		return redirect(url_for("user",user_id=user_id))


class ArticleAPI(Resource):
	"""
	Class implemeting Article API
	Fields:
	=========================================
	article_id: String
	title: String
	description: String

	Calls Handled:
	========================================
	GET /feedsapp/api/v1.0/articles/<string:id>
	"""
	
	def __init__(self):
		self.article_fields={'article_id': fields.String,
							 'title': fields.String,
							 'description': fields.String }
		super(ArticleAPI, self).__init__()

	def get(self, id):

		# Getting user
		user=mongo.db.user.find_one({'user_id': id})
		if not user:
			return {'response': "User does not exist"}
		
		# Getting users feeds
		feed_ids = user['feeds']
		feeds = mongo.db.feed.find({'feed_id':{'$in': feed_ids}})
		article_ids=[]
		
		# An article can be in multiple feeds, so, get set of article ids
		for feed in feeds:
			article_ids.extend(feed['articles'])
		article_ids = list(set(article_ids))
		
		# Search database for articles
		articles = mongo.db.article.find({'article_id': {'$in': article_ids}})
		return jsonify({'articles': [ marshal(article, self.article_fields) 
										for article in articles ]})



api.add_resource(UserAPI, '/feedsapp/api/v1.0/users/<string:user_id>', endpoint='user')
api.add_resource(FeedAPI, '/feedsapp/api/v1.0/feeds/', endpoint='feeds')
api.add_resource(FeedAPI, '/feedsapp/api/v1.0/feeds/<string:user_id>', endpoint='feed')
api.add_resource(ArticleAPI, '/feedsapp/api/v1.0/articles/<string:id>', endpoint='articles')


if __name__ == '__main__':
	db_setup()
	app.run(debug=True)

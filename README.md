# feed-api
Feed reader system with 3 entities- Users, Feeds, Articles.
==================================================================================================================
API ENDPOINTS
===================================================================================================================
HTTPMETHOD |               URI                       | ACTION
--------------------------------------------------------------------------------------------------------------------
GET        |  /feedsapp/api/v1.0/users/[user_id]     | get all user data for a users
--------------------------------------------------------------------------------------------------------------------
GET        |  /feedsapp/api/v1.0/articles/[user_id]  | get all aricles from all feeds that a user has subscribed to
--------------------------------------------------------------------------------------------------------------------
GET        |  /feedsapp/api/v1.0/feeds/[user_id]     | get all feeds with article ids a user has subscribed to
--------------------------------------------------------------------------------------------------------------------
GET        |  /feedsap/api/v1.0/feeds/               | get all feeds
--------------------------------------------------------------------------------------------------------------------
POST       |  /feedsapp/api/v1.0/feeds/[id]          | subscribe, unsubscribe or add article to a feed decided by the
		   |									     | id's passed through the 'subscribe','unsubscribe', 'article' fields
		   |										 | in the json data with the POST request. Only one operation
		   |										 | permitted per request- i.e subscribe to 1 feed, unsubcribe
		   |										 | from 1 feed or add 1 article to a feed. Response is redirected
		   |										 | to GET /feedsapp/api/v1.0/users/[user_id] for subscribe and
		   |										 | unsubscribe and GET /feedsap/api/v1.0/feeds/ for article operation.
---------------------------------------------------------------------------------------------------------------------							

The User, Feed, Article system has been implemented using Flask and MongoDB.
They were chosen because Flask can handle multiple conccurent requests and 
MongoDB implements transactions.

------------------------------------------------------------------
DATA MODEL
-----------------------------------------------------------------
Each user has a user_id and a list of id's referencing feeds they
have subscribed to.
Each feed has a feed_id and a list of id's referencing articles
in the feed
Each article has an article_id, title and description
The API assumes that all users, feeds and articles are already present in
the database. The add article endpoint simply adds an existing article to
a field
Example Data:
{"user_id":"user1", "feeds":["feed1","feed2","feed3"]}
{"feed_id":"feed1", "articles":["article1","article2","article3"]}
{"article_id":"article1", "title":"title1","description":"description1"}

------------------------------------------------------------------
RUNNING AND TESTING THE PROGRAM
------------------------------------------------------------------ 
1) run setup.sh to install python dependencies in a python virtualenviroment
2) install mongodb
3) start mongodb server
4) activate virtualenvironment
5) run python api/feedsapp.py

The feedapp module has some code to setup dummy data for a demo.
Unittests have been implemented in tests/test_feedsapp.py

----------------------------------------------------------
DOCUMENTATION
----------------------------------------------------------
Created using pydoc and stored as html file feedsapp.html
in docs folder

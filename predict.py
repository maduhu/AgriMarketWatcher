from pymongo import MongoClient
import pymongo
import operator
import datetime
import copy
from sklearn import linear_model

MAX_DIFF = 0.5
NUM_TRAIN = 0
DAY_RANGE = 30

def connect2DB():
	try:
		client = MongoClient("mongodb://agriapp:simplePassword@ds043057.mongolab.com:43057/heroku_app24455461")
		db = client.get_default_database()
		return db
	except Exception as e:
		print e.strerror
		return None

def predict():
	clf = linear_model.LinearRegression()
	Y_arr = [4.7, 6.5, 5.5, 7.5]
	X_arr = [[2011, 1], [2012, 2], [2013, 3], [2014, 4]]
	clf.fit(X_arr, Y_arr)
	#print coef
	#print coef[1]*2 + coef[0]
	ans = clf.predict([2015, 5])
	print ans

def train(X, Y):
	NUM_TRAIN = len(X)
	clf = linear_model.LinearRegression()
	clf.fit(X, Y)
	return clf

def makePrediction(clf, date):
	return clf.predict([date, ++NUM_TRAIN])

def evalPrediction(expected, actual):
    if abs(expected - actual) == MAX_DIFF:
        return False
    return True

def storePredictions(db, dData):
	length = 0
	if (dData and len(dData) > 0):
		db.drop_collection("predictions")
		predictions = db.predictions
		predictions.insert(dData)
		length = predictions.count()
	return length

def run(crop):
	today = datetime.date.today() + datetime.timedelta(days=1)
	prices = []
	dates = []
	i = 0
	db = connect2DB()
	if db:
		for year in range(2007, today.year):
			#get price from db
			hi_date = datetime.datetime(year, today.month, today.day, 0, 0, 0) + datetime.timedelta(days=DAY_RANGE)
			lo_date = datetime.datetime(year, today.month, today.day, 0, 0, 0) - datetime.timedelta(days=DAY_RANGE)
			recs = list(db.daily.find({"commodity": crop, "date": {'$gte': lo_date, '$lte': hi_date}}))
			if len(recs) > 0:
				prices.append(recs[0]["price"])
				i += 1
				dates.append([year, i])
	if len(prices) != 0 and len(dates) != 0:
		clf = train(dates, prices)
		pred = makePrediction(clf, today.year)
		print pred
		return round(pred,2)
	return -1
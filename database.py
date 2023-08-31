import sqlite3

def createConection():
    dbase = sqlite3.connect("RMHGO.db")
    return dbase

def closeConection(dbase):
    dbase.close()

def createTableCustomers(dbase):
	dbase.execute('''CREATE TABLE IF NOT EXISTS customer (name TEXT, phone TEXT,  date_ TEXT,
					time_ TEXT, issues TEXT, state TEXT)''')

def getMessagesIsues(dbase):
	data = dbase.execute("SELECT * FROM customer WHERE issues='True' ")
	result = data.fetchall()    
	return result

def insertNewIssue(dbase, dictdata):
	name = dictdata['name']
	phone = dictdata['phone']	
	date_ = dictdata['date']
	time_ = dictdata['time']
	state = dictdata['state']
	issues = 'True'
	

	dbase.execute(''' INSERT INTO customer (name, phone, date_, time_, issues, state) VALUES (?, ?, ?, ?, ?, ?)''',
	 (name, phone, date_, time_, issues, state))
	dbase.commit()

dbase = createConection()
createTableCustomers(dbase)
# results = getMessagesIsues(dbase)
# for result in results:
# 	print(result)
# print(result)
closeConection(dbase)
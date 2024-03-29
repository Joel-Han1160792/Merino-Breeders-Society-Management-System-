from app.config.database import getDbConnection
from app.config.database import getCursor

# get_all functions 

def get_tutors_for_dropdown():
    # Fetch tutors from the database
    connection = getDbConnection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT UserID, CONCAT(Title, FirstName, FamilyName) AS FullName FROM TutorProfiles")
        tutors = cursor.fetchall()
        return tutors
    finally: 
        cursor.close()
        connection.close()        

def get_all_locations():   
    cursor = getCursor()
    cursor.execute('SELECT * from location')
    locationList = cursor.fetchall()
    return locationList

def get_all_workshops():   
    cursor = getCursor()
    cursor.execute('SELECT w.workshopid, w.details, w.location, w.date, w.time, w.cost, w.capacity, t.userId, t.firstname,t.familyname FROM Workshops w inner join TutorProfiles t on w.tutorId = t.userId;')
    workshopList = cursor.fetchall()
    return workshopList

def get_all_tutors():
    cursor = getCursor()
    cursor.execute('SELECT * FROM TutorProfiles;')
    tutorlist = cursor.fetchall()
    return tutorlist

def get_all_members():
    cursor = getCursor()
    cursor.execute('SELECT  * FROM MemberProfiles;')
    memberlist = cursor.fetchall()
    return memberlist
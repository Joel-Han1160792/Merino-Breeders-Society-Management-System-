from flask import Flask, flash
from app import app
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import session
import os
import re
from app.config.database import getCursor, getDbConnection
from app.config.helpers import require_role
from app.config.models import get_all_locations

dir_path = os.path.dirname(os.path.realpath(__file__))

@app.route('/tutor')
def tutor_dashboard():
    if 'loggedin' in session and session['role'] == 2:
        return render_template('dashboard/tutor_dashboard.html', username=session['username'])
    return redirect(url_for('login'))
  
@app.route('/booking/lesson/details/<int:booking_id>',methods=['GET', 'POST'])
@require_role(2)
def lesson_booking_details(booking_id):
    conn = getDbConnection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        status = request.form.get('status')
        # Default to an empty string if note is not provided
        note = request.form.get('note', '')  
        
        try:
            cursor.execute("""
                UPDATE Bookings
                SET Status = %s, Note = %s
                WHERE BookingID = %s
            """, (status, note, booking_id))
            conn.commit()
            flash('Booking updated successfully.', 'success')
        except Exception as e:
            conn.rollback()
            flash('An error occurred while updating the booking.', 'danger')
            print(e)
        finally:
            cursor.close()
            conn.close()
        # Redirect to the same page to show the updated details
        return redirect(url_for('lesson_booking_details', booking_id=booking_id))
    
    cursor.execute("""
        SELECT 
            b.BookingID, 
            b.Status, 
            b.Note,
            l.Date, 
            l.StartTime, 
            l.EndTime, 
            l.Location, 
            l.Cost,
            l.IsBooked,
            lt.Name AS LessonType, 
            lt.Description,
            m.Title,
            m.FirstName, 
            m.FamilyName,
            m.PhoneNumber,
            m.Email,
            m.ProfileImage
        FROM Bookings b
        JOIN OneOnOneLessons l ON b.LessonID = l.LessonID
        JOIN LessonTypes lt ON l.LessonTypeID = lt.LessonTypeID
        JOIN MemberProfiles m ON b.MemberID = m.UserID
        WHERE b.BookingID = %s
    """, (booking_id,))
    
    booking_details = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if not booking_details:
        flash('Booking not found.', 'danger')
        return redirect(url_for('tutor_dashboard'))  # Redirect to a default page if booking is not found
    
    return render_template('tutor/lesson_booking_details.html', booking=booking_details)

  
@app.route("/tutor_workshop")
def tutor_workshop():
    connection = getCursor()

    # Get the search query from the URL parameters
    search_query = request.args.get('search', '')
    
    # Modify the SQL query to include the search condition
    sql_query = f"""
        SELECT CONCAT(tp.FirstName, ' ', tp.FamilyName) AS TutorName,
               w.Title AS WorkshopTitle,
               w.Date AS WorkshopDate,
               w.Time AS WorkshopTime,
               w.Location AS WorkshopLocation,
               w.Cost AS WorkshopCost,
               w.Capacity AS WorkshopCapacity
        FROM TutorProfiles tp
        JOIN Workshops w ON tp.UserID = w.TutorID
        WHERE CONCAT(tp.FirstName, ' ', tp.FamilyName) LIKE %s
    """
    
    # Execute the query with the search condition
    connection.execute(sql_query, (f"%{search_query}%",))
    tutor_workshops = connection.fetchall()
    
    return render_template("tutor/tutor_workshop.html", tutor_workshops=tutor_workshops, search_query=search_query)


@app.route('/editTutor/<int:profileID>', methods=['POST','GET'])
@require_role(2)
def editTutor(profileID):
    msg=""
    if request.method == 'POST':
        if 'photo' not in request.files:
            msg = 'No file part in the request'
            return render_template('tutor/tutorProfileEdit.html', msg=msg) 
        file = request.files['photo']
        if file.filename == '':
            msg = 'No selected file'
            return render_template('tutor/tutorProfileEdit.html', msg=msg) 
        if file:
            # Save the uploaded file
            file.save(dir_path+'/static/images/tutors/' + file.filename)
            msg = 'File uploaded successfully'
            # Database action here
            cursor = getCursor()
            cursor.execute("update TutorProfiles set ProfileImage = %s where UserId = %s",(file.filename,profileID,))

            cursor.execute("select * from TutorProfiles where UserId = %s",(profileID,))
            tutor = cursor.fetchone()

            return render_template('tutor/tutorProfileEdit.html', msg=msg, profileID=profileID,tutor=tutor,) 
    else:
        cursor = getCursor()      
        cursor.execute("select * from TutorProfiles where UserId = %s",(profileID,))
        tutor = cursor.fetchone()
        msg = request.args.get('msg', "")
        return render_template('tutor/tutorProfileEdit.html', msg=msg, profileID=profileID, tutor=tutor,) 


@app.route('/tutor_manage_lesson', methods=['GET', 'POST'])
def tutor_manage_lesson():
    if 'loggedin' in session and (session['role'] == 2 or session['role'] == 3):
        tutor_id = session['id']
        connection = getCursor()
        connection.execute(f"""
                           SELECT ool.LessonID,
                                lt.Name AS LessonName,
                                ool.Date,
                                ool.StartTime,
                                ool.EndTime,
                                ool.Location,
                                ool.Cost,
                                ool.IsBooked
                           FROM OneOnOneLessons ool
                           JOIN LessonTypes lt ON ool.LessonTypeID = lt.LessonTypeID
                           WHERE ool.TutorID = %s;
                           """, (tutor_id,))
        tutor_lessons = connection.fetchall()
        return render_template('tutor/tutor_manage_lesson.html', tutor_lessons=tutor_lessons)
    else:
        return redirect(url_for('login'))


@app.route('/edit/lesson/<int:lesson_id>', methods=['GET', 'POST'])
@require_role(2)
def tutor_edit_lesson(lesson_id):
    connection = getDbConnection()
    try:
        if request.method == 'POST':
            date = request.form['date']
            start_time = request.form['start_time']
            end_time = request.form['end_time']
            location = request.form['location'].strip()
            cost = request.form['cost']
            is_booked = request.form['is_booked']

            cursor = connection.cursor()
            sql = "UPDATE OneOnOneLessons SET Date = %s, StartTime = %s, EndTime = %s, Location = %s, Cost = %s, IsBooked = %s WHERE LessonID = %s"
            cursor.execute(sql, (date, start_time, end_time, location, cost, is_booked, lesson_id))
            connection.commit()
            flash('Lesson updated successfully!', 'success')
            return redirect(url_for('tutor_manage_lesson'))
        else:
            cursor = connection.cursor(dictionary=True) 
            sql = """ SELECT ooo.*, l.description, l.available,  t.FirstName AS TutorFirstName, t.FamilyName AS TutorFamilyName 
            FROM OneOnOneLessons ooo
            inner join location l on ooo.location = l.locationName
            inner join tutorprofiles t ON t.UserID = ooo.tutorID
            WHERE LessonID = %s """
            cursor.execute(sql, (lesson_id,))
            lesson = cursor.fetchone()
            locations = get_all_locations()
            if lesson:
                return render_template('tutor/tutor_edit_lesson.html', lesson=lesson, locations = locations)
            else:
                flash('Lesson not found.', 'danger')
                return redirect(url_for('tutor_manage_lesson'))
    except Exception as e:
        flash(f"Database error occurred: {e}", 'danger')
    finally:
        if connection:
            connection.close()
         # return render_template(' lesson_details.html')
@app.route('/delete_lesson/<int:lesson_id>', methods=['POST'])
@require_role(2)
def delete_lesson(lesson_id):
    connection = getDbConnection()
    cursor = connection.cursor()

    try:
        cursor.execute("DELETE FROM OneOnOneLessons WHERE LessonID = %s", (lesson_id,))
        connection.commit()
        flash('Lesson deleted successfully.', 'success')
    except Exception as e:
        # Log the error if needed
        flash('An error occurred while deleting the lesson.', 'danger')
    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('tutor_manage_lesson'))


@app.route('/tutor_add_lesson', methods=['GET', 'POST'])
@require_role(2)
def tutor_add_lesson():
    if request.method == 'POST':
        name = request.form['name'].strip()
        date = request.form['date']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        location = request.form['location'].strip()
        cost = request.form['cost']
        is_booked = request.form['is_booked']

        try:
            connection = getDbConnection()
            with connection.cursor() as cursor:
                # Get the LessonTypeID for the given name
                cursor.execute("SELECT LessonTypeID FROM LessonTypes WHERE Name = %s", (name,))
                lesson_type_id = cursor.fetchone()
                if not lesson_type_id:
                    flash('Lesson type not found.', 'danger')
                    return redirect(url_for('tutor_add_lesson'))

                # Insert the lesson with the LessonTypeID
                sql = "INSERT INTO OneOnOneLessons (LessonTypeID, TutorID, Date, StartTime, EndTime, Location, Cost, IsBooked) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                cursor.execute(sql, (lesson_type_id[0], session['id'], date, start_time, end_time, location, cost, is_booked))
                connection.commit()
                flash('Lesson added successfully!', 'success')
        except Exception as e:
            connection.rollback()
            flash(f"Database error occurred: {e}", 'danger')
        finally:
            if connection:
                connection.close()

        return redirect(url_for('tutor_manage_lesson'))

    return render_template('tutor/tutor_add_lesson.html')





#profile
@app.route("/profile/tutor")
def tutor_profile():
    role = session.get('role')
    print(role)
    #get userID
    msg = ""
    username = session.get('username')
    cur = getCursor()
    cur.execute("SELECT * FROM Users where Username = %s;",(username,))
    user = cur.fetchone()
    # get proflie
    cur.execute("select * FROM TutorProfiles where UserID = %s;",(user[0],))
    profile = cur.fetchone()
    return render_template('tutor/tutor_profile.html', profile = profile, msg = msg, role=role)


#update info for tutor

@app.route('/update/info/tutor' , methods=['GET', 'POST'])
def update_info_tutor():
    msg = ""
    if request.method =='POST':
        title = request.form.get('title')
        first_name = request.form.get('firstname')
        family_name = request.form.get('familyname')
        position = request.form.get('position')
        phone = request.form.get('phonenumber')
        email = request.form.get('email')
        profile = request.form.get('profile')
        # using session to get username for define where in sql
        username = session.get('username')
        #validation for name
        pattern = re.compile("^[A-Za-z]+$")
        if pattern.match(first_name) and pattern.match(family_name):
        #update into Users table   
            cur = getCursor()
            cur.execute("select * FROM Users where Username = %s;",(username,))
            userid = cur.fetchone()
            cur.execute("UPDATE TutorProfiles SET Title = %s, FirstName = %s,FamilyName = %s, Position = %s, PhoneNumber = %s, Email = %s, Tutor Profile WHERE UserID = %s", (title, first_name, family_name, position, phone, email, profile, userid[0]))
            msg="Information Updated"
            return render_template('updateinfo.html', msg=msg, form_action = '/update/info/tutor')
        else:
            msg="Please make sure your inputs for names are only letters"
            return render_template('updateinfo.html', msg=msg, form_action = '/update/info/tutor')
        
    else:
        return render_template('updateinfo.html', msg=msg, form_action = '/update/info/tutor')
#  upload imgage
@app.route("/tutor/image/<int:userID>", methods=['POST','GET'])
def tutor_image(userID):
    msg=""
    if request.method == 'POST':
        if 'photo' not in request.files:
            msg = 'No file part in the request'
            return render_template('tutor/upload_image.html', msg=msg) 
        file = request.files['photo']
        if file.filename == '':
            msg = 'No selected file'
            return render_template('tutor/upload_image.html', msg=msg) 
        if file:
            # Save the uploaded file
            global dir_path
            img_folder = dir_path + "/static/images/tutors/"
            file.save(os.path.join(img_folder, file.filename))
            msg = 'File uploaded successfully'
            # Database action here
            cursor = getCursor()
            cursor.execute("UPDATE TutorProfiles SET ProfileImage = %s where UserId = %s",(file.filename, userID))

            cursor.execute("select * from TutorProfiles where UserId = %s",(userID,))
            profile = cursor.fetchone()
           
            return render_template('tutor/tutor_profile.html',profile = profile,role = 2) 
    else:
     
        return render_template('tutor/upload_image.html', userID = userID) 
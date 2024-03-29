from app import app
from flask import flash, redirect, render_template, url_for
from flask import request
from flask import session
import functools
import math
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta
from app.config.database import getCursor, getDbConnection
from app.config.helpers import require_role, format_date
import os
from app.config.database import getCursor, getDbConnection
from app.config.helpers import require_role
from app.config.models import get_all_workshops
from app.config.helpers import format_date

dir_path = os.path.dirname(os.path.realpath(__file__))

@app.route('/member')
def member_dashboard():
    if 'loggedin' in session and session['role'] == 1:
        return render_template('dashboard/member_dashboard.html', username=session['username'])
    return redirect(url_for('login'))
                    
# update member's info
@app.route('/update/info/member' , methods=['GET', 'POST'])
def update_info_member():
    msg = ""
   
    if request.method =='POST':
        title = request.form.get('title')
        first_name = request.form.get('firstname')
        family_name = request.form.get('familyname')
        position = request.form.get('position')
        phone = request.form.get('phonenumber')
        email = request.form.get('email')
        address =request.form.get('address')
        date_of_birth = request.form.get('DoB')

    # optional breeding info  
        if 'breeding'not in request.form:
            breeding = None
        else:
            breeding = request.form.get('breeding')

        # using session to get username for where in sql
        username = session.get('username')
        cur = getCursor()
        cur.execute("SELECT * FROM Users where Username = %s;",(username,))
        user = cur.fetchone()
        #validation for name
        pattern = re.compile("^[A-Za-z]+$")
        if pattern.match(first_name) and pattern.match(family_name):
        #update into Users table   
            cur = getCursor()
            sql = """
            UPDATE MemberProfiles 
            SET Title = %s,
                FirstName = %s,
                FamilyName = %s,
                Position = %s,
                PhoneNumber = %s,
                Email = %s,
                Address = %s,
                DateOfBirth = %s,
                
            
                MerinoBreedingDetails =COALESCE(%s, MerinoBreedingDetails)
            WHERE UserID = %s;
            
            """
            cur.execute(sql, (
                title,
                first_name,
                family_name,
                position,
                phone, 
                email,
                address, 
                date_of_birth, 
                breeding, 
                user[0]))
           


            msg="Information Updated"
            return render_template('updateinfo.html', msg=msg, form_action = '/update/info/member')
        else:
            msg="Please make sure your inputs for names are only letters"
            return render_template('updateinfo.html', msg=msg, form_action = '/update/info/member')
    else:
        return render_template('updateinfo.html', msg=msg, form_action = '/update/info/member')
        







@app.route('/lesson/details/<int:lesson_id>')
@require_role(1)
def lesson_details(lesson_id):
    connection = getDbConnection()
    cursor = connection.cursor(dictionary=True)
    # Only show lesson that hasn't been booked
    cursor.execute("""
    SELECT l.*, lt.Name AS LessonType, lt.Description,
            t.FirstName AS TutorFirstName, t.FamilyName AS TutorFamilyName,
            t.ProfileImage AS TutorProfileImage
    FROM OneOnOneLessons l
    JOIN LessonTypes lt ON l.LessonTypeID = lt.LessonTypeID
    JOIN TutorProfiles t ON l.TutorID = t.UserID
    WHERE l.LessonID = %s AND l.IsBooked = FALSE
    """, (lesson_id,))
    
    lesson_details = cursor.fetchone()
    cursor.close()
    connection.close()
    
    if not lesson_details:
        flash('Lesson not found.', 'danger')
        return redirect(url_for('member_dashboard'))  # Redirect to a dashboard or relevant page if lesson is not found
    
    return render_template('member/lesson_details.html', lesson=lesson_details)

@app.route('/book_lesson', methods=['POST'])
@require_role(1)
def book_lesson():
    lesson_id = request.form.get('lesson_id')
    member_id = session.get('id')

    try:
        connection = getDbConnection()
        cursor = connection.cursor(dictionary=True)

        # Retrieve lesson cost for payment record.
        cursor.execute("""
            SELECT Cost FROM OneOnOneLessons WHERE LessonID = %s
        """, (lesson_id,))
        lesson = cursor.fetchone()
        lesson_cost = lesson['Cost'] if lesson else 0

        # Update the lesson as booked
        cursor.execute("""
            UPDATE OneOnOneLessons
            SET IsBooked = TRUE
            WHERE LessonID = %s
        """, (lesson_id,))

        # Create a booking record
        cursor.execute("""
            INSERT INTO Bookings (MemberID, LessonID, BookingDate, CreatedAt, Status)
            VALUES (%s, %s, NOW(), NOW(),'Confirmed')
        """, (member_id, lesson_id))

        booking_id = cursor.lastrowid
        # Create a payment record for booking the lesson
        cursor.execute("""
            INSERT INTO Payments (MemberID, BookingID, Amount, Date, CreatedAt, Type)
            VALUES (%s, %s, %s, NOW(), NOW(), 'Lesson')
        """, (member_id, booking_id, lesson_cost))

        connection.commit()
        flash('Lesson booked and payment processed successfully!', 'success')
    except Exception as e:
        connection.rollback()
        flash('An error occurred during booking or payment processing.', 'danger')
        print(e)
    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('my_bookings', lesson_id=lesson_id))

@app.route('/my_bookings')
@require_role(1)
def my_bookings():
    
    member_id = session.get('id')
    connection = getDbConnection()
    cursor = connection.cursor(dictionary=True)
    print(member_id)
    cursor.execute("""
        SELECT b.BookingID, b.Status, b.BookingDate, 
               CASE 
                   WHEN b.WorkshopID IS NOT NULL THEN (SELECT Title FROM Workshops w WHERE w.WorkshopID = b.WorkshopID)
                   WHEN b.LessonID IS NOT NULL THEN (SELECT lt.Name FROM OneOnOneLessons l JOIN LessonTypes lt ON l.LessonTypeID = lt.LessonTypeID WHERE l.LessonID = b.LessonID)
               END AS BookingType,
               CASE 
                   WHEN b.WorkshopID IS NOT NULL THEN 'Workshop'
                   WHEN b.LessonID IS NOT NULL THEN 'One-on-One Lesson'
               END AS BookingCategory
        FROM Bookings b
        WHERE b.MemberID = %s
        ORDER BY b.BookingDate DESC
    """, (member_id,))
    
    bookings = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template('member/my_bookings.html', bookings=bookings)

@app.route('/booking_details/<int:booking_id>')
@require_role(1)
def booking_details(booking_id):
    member_id = session.get('id')
    connection = getDbConnection()
    cursor = connection.cursor(dictionary=True)

    # Fetch general booking information
    cursor.execute("""
        SELECT b.BookingID, b.Status, b.BookingDate, 
               CASE 
                   WHEN b.WorkshopID IS NOT NULL THEN 'Workshop'
                   WHEN b.LessonID IS NOT NULL THEN 'One-on-One Lesson'
               END AS BookingCategory,
               b.WorkshopID, b.LessonID
        FROM Bookings b
        WHERE b.BookingID = %s AND b.MemberID = %s
    """, (booking_id, member_id))

    booking = cursor.fetchone()

    # Fetch specific details based on booking type
    details = None
    if booking and booking['WorkshopID']:
        cursor.execute("""
            SELECT w.Title, w.Details, w.Location, w.Date, w.Time, w.Cost
            FROM Workshops w
            WHERE w.WorkshopID = %s
        """, (booking['WorkshopID'],))
        details = cursor.fetchone()
        details['Type'] = 'Workshop'
    elif booking and booking['LessonID']:
        cursor.execute("""
            SELECT l.Date, l.StartTime, l.EndTime, l.Location, l.Cost, lt.Name AS LessonType, lt.Description
            FROM OneOnOneLessons l
            JOIN LessonTypes lt ON l.LessonTypeID = lt.LessonTypeID
            WHERE l.LessonID = %s
        """, (booking['LessonID'],))
        details = cursor.fetchone()
        details['Type'] = 'One-on-One Lesson'

    cursor.close()
    connection.close()

    if not booking:
        flash('Booking not found.', 'danger')
        return redirect(url_for('member_dashboard'))

    return render_template('member/booking_details.html', booking=booking, details=details)

@app.route('/cancel_booking/<int:booking_id>', methods=['POST'])
@require_role(1)
def cancel_booking(booking_id):
    member_id = session.get('id')

    try:
        connection = getDbConnection()
        cursor = connection.cursor(dictionary=True)

        # Retrieve the booking to determine if it's a workshop or lesson booking
        cursor.execute("""
            SELECT WorkshopID, LessonID FROM Bookings 
            WHERE BookingID = %s AND MemberID = %s
        """, (booking_id, member_id))
        booking = cursor.fetchone()

        if booking:
            # Update booking status to 'Cancelled'
            cursor.execute("""
                UPDATE Bookings SET Status = 'Cancelled' WHERE BookingID = %s
            """, (booking_id,))

            if booking['LessonID']:
                # If it's a lesson, make the lesson available again
                cursor.execute("""
                    UPDATE OneOnOneLessons SET IsBooked = FALSE WHERE LessonID = %s
                """, (booking['LessonID'],))

            connection.commit()
            flash('Booking cancelled successfully.', 'success')
        else:
            flash('Booking not found.', 'danger')

    except Exception as e:
        connection.rollback()
        flash('An error occurred during the cancellation process.', 'danger')
        print(e)

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('my_bookings'))


@app.route("/view_tutorprofile")
def view_tutorprofile():
    connection = getCursor()
    connection.execute(f"""
                       SELECT
                        UserID AS TutorID,
                        CONCAT(Title, ' ', FirstName, ' ', FamilyName) AS Name,
                        Position,
                        PhoneNumber AS Phone,
                        Email,
                        TutorProfile AS Profile,
                        ProfileImage AS Image
                        FROM
                        TutorProfiles;
                        """)
    view_tutorprofile = connection.fetchall()
    print(view_tutorprofile)
    return render_template("member/view_tutorprofile.html", view_tutorprofile=view_tutorprofile)


@app.route("/tutor_lessons/<int:tutorid>")
def tutor_lessons(tutorid):
    connection = getCursor()
    connection.execute("""
                       SELECT
                           lt.Name AS LessonName,
                           ool.Date AS BookingDate,
                           ool.StartTime,
                           ool.EndTime,
                           ool.Location,
                           ool.Cost
                       FROM
                           OneOnOneLessons ool
                           JOIN LessonTypes lt ON ool.LessonTypeID = lt.LessonTypeID
                       WHERE
                           ool.TutorID = %s
                           AND ool.IsBooked = FALSE;
                       """, (tutorid,))
    tutor_lessons = connection.fetchall()
    print(tutor_lessons)
    return render_template("member/tutor_lessons.html", tutorid=tutorid, tutor_lessons=tutor_lessons)







@app.route("/subscription")
def subscription():
    cursor = getCursor()
    cursor.execute('SELECT * FROM Subscriptions WHERE MemberID = %s', (session['id'],))
    subdetails = cursor.fetchone()

    cursor.execute('SELECT * FROM Payments WHERE Type = "Subscription" and MemberID = %s', (session['id'],))
    paymentsdetails = cursor.fetchall()

    today = datetime.now().date()

    return render_template("member/subscriptionDetail.html", subdetails = subdetails, paymentsdetails = paymentsdetails, today = today, format_date = format_date )


@app.route("/cancelsubscription")
def cancelsubscription():
    cursor = getCursor()
    cursor.execute('UPDATE Subscriptions SET EndDate = %s WHERE MemberID = %s ;', (datetime.now().date(), session['id'],))
    return redirect("/subscription")


@app.route("/renewsubscription", methods=["get", "post"])
def renewsubscription():
    if request.method == 'POST':
        memberID = session['id']
        subscription = request.form['subscription']
        startdate = request.form['startdate']
        startdate = datetime.strptime(startdate, "%Y-%m-%d").date()
        amount = request.form['fee']
        months = int(request.form['months'],0)
        
        if subscription == 'Annual':
            fee = 50.00
            if request.form.get('discount') == "on":
                discount =15.00
            else:
                discount = 0.00
            enddate = startdate + relativedelta(months=12)
        else:
            fee = 5.00
            if request.form.get('discount') == "on":
                discount =1.50
            else:
                discount = 0.00
            enddate = startdate + relativedelta(months=months)            

        cursorID=getCursor()
        cursorID.execute('UPDATE Subscriptions SET Type = %s, Fee = %s, Discount = %s, StartDate = %s, EndDate = %s WHERE MemberID = %s ;', \
                         (subscription,fee,discount,startdate, enddate, memberID,))
        
        cursorSubID = getCursor()
        cursorSubID.execute('SELECT SubscriptionID FROM Subscriptions WHERE MemberID = %s;', (memberID,))
        SubID = cursorSubID.fetchone()[0]

        cursorSubID.execute('INSERT INTO Payments(MemberID, SubscriptionID, BookingID, Amount, Date, CreatedAt, Type) VALUES( \
                       %s, %s, NULL, %s, %s, %s, "Subscription");', (memberID, SubID, amount, startdate, startdate, ))
        return redirect("/subscription")

            
    else:
        today = datetime.now().date()
        cursor = getCursor()
        cursor.execute('SELECT EndDate FROM Subscriptions WHERE MemberID = %s;', (session['id'],))
        enddate = cursor.fetchone()[0]
        if today <= enddate:
            return render_template("member/renewsubscription.html", defaultdate = enddate)
        else:
            return render_template("member/renewsubscription.html", defaultdate = today)
# Book a workshop
@app.route("/workshops/booking") 
def book_workshop():
    connection = getDbConnection()
    cursor = connection.cursor(dictionary=True)

    search_query = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Set the number of items per page

    query_base = """
        FROM Workshops
        WHERE Title LIKE %s
    """
    # Pagination calculation
    count_query = f"SELECT COUNT(*) as total {query_base}"
    cursor.execute(count_query, (f"%{search_query}%",))
    total = cursor.fetchone()['total']
    total_pages = math.ceil(total / per_page)

    # Fetching paginated workshops
    workshops_query = f"""
       SELECT w.WorkshopID, w.Title, w.Details, w.Location, w.Date, w.Time, w.Cost, w.Capacity, t.UserId, t.Firstname,t.Familyname FROM Workshops w INNER JOIN TutorProfiles t ON w.TutorId = t.UserID;
        {query_base}
        ORDER BY WorkshopID DESC
        LIMIT %s OFFSET %s
    """
    offset = (page - 1) * per_page
    cursor.execute(workshops_query, (f"%{search_query}%", per_page, offset))
    workshops = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template('member/workshopList.html', workshops=workshops, page=page, total_pages=total_pages)


@app.route("/workshops/booking/<int:workshopID>")
@require_role(1) 
def workshop(workshopID):
    #get workshop for render template
    cursor = getCursor()
    cursor.execute('SELECT w.WorkshopID, w.Details, w.Location, w.Date, w.Time, w.Cost, w.Capacity, t.UserId, t.Firstname,t.Familyname FROM Workshops w inner join TutorProfiles t on w.TutorId = t.UserId WHERE WorkshopID = %s;',(workshopID,))
    workshop = cursor.fetchone()

    #get memberID 
    username = session.get('username')
    cursor = getCursor()
    cursor.execute("SELECT UserID FROM Users where Username = %s;",(username,))
    memberID = cursor.fetchone()
    print(memberID[0])
    #get CreatedAt
    cursor = getCursor()
    cursor.execute("SELECT CreatedAt FROM Workshops WHERE WorkshopID = %s",(workshopID,))
    createdAT = cursor.fetchone()
    print(createdAT[0])
    #Transer the format of date
    date_created = format_date(createdAT[0], format='%Y-%m-%d')
    # Check if already existed to avoid repetitive booking 
    connection = getDbConnection()
    cursor = connection.cursor()
    sql_check = """
                SELECT * FROM Bookings 
                WHERE MemberID = %s AND WorkshopID = %s AND CreatedAt = %s;
 
        """
    cursor.execute(sql_check,(memberID[0], workshopID, date_created))
    booking_existed = cursor.fetchone()
    if not booking_existed:
    # INSERT INTO Bookings  
        sql_insert = """
            INSERT INTO Bookings (MemberID, WorkshopID, BookingDate, CreatedAt)
            VALUES (%s, %s, CURDATE(), %s);
            
        """
        cursor.execute(sql_insert,(memberID[0], workshopID, date_created))
        connection.commit()
        cursor.close()
        connection.close()
        flash('You have successfully booked this workshop!')
    else:
        flash('You booked this workshop before!')
    return render_template('/member/workshop_booking.html',workshop = workshop )






# profile that was missing
@app.route("/profile/member")
def member_profile():
    #get userID
    msg = ""
    username = session.get('username')
    cur = getCursor()
    cur.execute("SELECT * FROM Users where Username = %s;",(username,))
    user = cur.fetchone()
    # get proflie
    cur.execute("select * FROM MemberProfiles where UserID = %s;",(user[0],))
    profile = cur.fetchone()
    return render_template('member/member_profile.html', profile = profile, msg = msg)


# upload image
@app.route("/upload/image/<int:userID>", methods=['POST','GET'])
def upload_image(userID):
    msg=""
    if request.method == 'POST':
        if 'photo' not in request.files:
            msg = 'No file part in the request'
            return render_template('member/upload_image.html', msg=msg) 
        file = request.files['photo']
        if file.filename == '':
            msg = 'No selected file'
            return render_template('member/upload_image.html', msg=msg) 
        if file:
            # Save the uploaded file
            global dir_path
            img_folder = dir_path + "/static/images/members/"
            file.save(os.path.join(img_folder, file.filename))
            msg = 'File uploaded successfully'
            # Database action here
            cursor = getCursor()
            cursor.execute("UPDATE MemberProfiles SET ProfileImage = %s where UserId = %s",(file.filename, userID))

            cursor.execute("select * from MemberProfiles where UserId = %s",(userID,))
            profile = cursor.fetchone()
           
            return render_template('member/member_profile.html',profile = profile) 
    else:
     
        return render_template('member/upload_image.html', userID = userID) 
    

#jump to tutor profile through workshop list
@app.route("/profile/tutor/<int:userID>")
def check_tutor(userID):
    role = session.get('role')
    cur = getCursor()
    cur.execute("select * FROM TutorProfiles where UserID = %s;",(userID,))
    profile = cur.fetchone()
    return render_template('tutor/tutor_profile.html', profile = profile, role = role)

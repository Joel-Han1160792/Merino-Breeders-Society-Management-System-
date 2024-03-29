import functools
import math
from app import app
from flask import redirect, render_template, url_for, flash
from flask import request
from flask import session
import re
from app.config.database import getCursor, getDbConnection
from app.config.helpers import require_role
from app.config.models import get_tutors_for_dropdown, get_all_locations




@app.route('/manager')
def manager_dashboard():
    if 'loggedin' in session and session['role'] == 3:
        return render_template('dashboard/manager_dashboard.html', username=session['username'])
    return redirect(url_for('login'))

#update info for manager
@app.route('/update/info/manager' , methods=['GET', 'POST'])
def update_info_manager():
    msg = ""
    if request.method =='POST':
        title = request.form.get('title')
        first_name = request.form.get('firstname')
        family_name = request.form.get('familyname')
        position = request.form.get('position')
        phone = request.form.get('phonenumber')
        email = request.form.get('email')
        # using session to get username for define where in sql

        username = session.get('username')
        #validation for name
        pattern = re.compile("^[A-Za-z]+$")
        if pattern.match(first_name) and pattern.match(family_name):
        #update into Users table   
            cur = getCursor()
            cur.execute("select * FROM Users where Username = %s;",(username,))
            userid = cur.fetchone()
            cur.execute("UPDATE ManagerProfiles SET Title = %s, FirstName = %s,FamilyName = %s, Position = %s, PhoneNumber = %s, Email = %s WHERE UserID = %s", (title, first_name, family_name, position, phone, email, userid[0]))
            msg="Information Updated"
            return render_template('updateinfo.html', msg=msg, form_action = '/update/info/manager')
        else:
            msg="Please make sure your inputs for names are only letters"
            return render_template('updateinfo.html', msg=msg, form_action = '/update/info/manager')
        
    else:
        return render_template('updateinfo.html', msg=msg, form_action = '/update/info/manager')


@app.route('/workshop/new', methods=['GET', 'POST'])
@require_role(3)
def add_workshop():
    if request.method == 'POST':
        title = request.form['title']
        details = request.form['details']
        location = request.form['location']
        date = request.form['date']
        time = request.form['time']
        cost = request.form['cost']
        capacity = request.form['capacity']
        tutor_id = request.form['tutor_id']

        if not title or not details or not location:
            flash('Please fill out all required fields.', 'danger')
        elif not re.match(r'^\d+(\.\d{1,2})?$', cost):
            flash('Invalid cost format. Please enter a numeric value.', 'danger')
        elif not capacity.isdigit() or int(capacity) <= 0:
            flash('Capacity must be a positive integer.', 'danger')
        else:
            connection = getDbConnection()
            cursor = connection.cursor()
            insert_query = """
            INSERT INTO Workshops (Title, Details, Location, Date, Time, Cost, Capacity, TutorID)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (title, details, location, date, time, cost, capacity, tutor_id))
            connection.commit()
            cursor.close()
            connection.close()            
            flash('Workshop added successfully.', 'success')
            return redirect(url_for('view_workshops')) 

    tutors = get_tutors_for_dropdown() 
    locations = get_all_locations() 
    return render_template('manager/create_workshop.html', tutors=tutors)

@app.route('/workshops/edit/<int:workshop_id>', methods=['GET', 'POST'])
@require_role(3)
def edit_workshop(workshop_id):
    connection = getDbConnection()
    cursor = connection.cursor(dictionary=True)

    # Fetch workshop details for GET request
    if request.method == 'GET':
        cursor.execute("SELECT * FROM Workshops WHERE WorkshopID = %s", (workshop_id,))
        workshop = cursor.fetchone()
        print(workshop)
        if workshop:
            tutors = get_tutors_for_dropdown() 
            locations = get_all_locations() 
            return render_template('manager/edit_workshop.html', workshop=workshop, tutors=tutors, locations= locations)
        else:
            flash('Workshop not found.', 'danger')
            return redirect(url_for('view_workshops')) 
        
    # Handle POST request for updating workshop details
    if request.method == 'POST':
        title = request.form['title']
        details = request.form['details']
        location = request.form['location']
        date = request.form['date']
        time = request.form['time']
        cost = request.form['cost']
        capacity = request.form['capacity']
        tutor_id = request.form['tutor_id']


        if not title or not details or not location:
            flash('Please fill out all required fields.', 'danger')
        elif not re.match(r'^\d+(\.\d{1,2})?$', cost):
            flash('Invalid cost format. Please enter a numeric value.', 'danger')
        elif not capacity.isdigit() or int(capacity) <= 0:
            flash('Capacity must be a positive integer.', 'danger')
        else:
            update_query = """
            UPDATE Workshops
            SET Title = %s, Details = %s, Location = %s, Date = %s, Time = %s, Cost = %s, Capacity = %s, TutorID = %s
            WHERE WorkshopID = %s
            """
            cursor.execute(update_query, (title, details, location, date, time, cost, capacity, tutor_id, workshop_id))
            connection.commit()
            cursor.close()
            connection.close()
            flash('Workshop updated successfully.', 'success')
            return redirect(url_for('view_workshops')) 
    
    return render_template('manager/edit_workshop.html')

@app.route('/workshops', methods=['GET'])
def view_workshops():
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
        SELECT WorkshopID, Title, Details, Location, Date, Time, Cost, Capacity, TutorID
        {query_base}
        ORDER BY WorkshopID DESC
        LIMIT %s OFFSET %s
    """
    offset = (page - 1) * per_page
    cursor.execute(workshops_query, (f"%{search_query}%", per_page, offset))
    workshops = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template('manager/view_workshop.html', workshops=workshops, page=page, total_pages=total_pages)


@app.route('/lesson-schedules', methods=['GET'])
def view_lessons():
    connection = getDbConnection()
    cursor = connection.cursor(dictionary=True)

    search_query = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Set the number of items per page

    query_base = """
        FROM OneOnOneLessons l
        JOIN LessonTypes lt ON l.LessonTypeID = lt.LessonTypeID
        JOIN TutorProfiles t ON l.TutorID = t.UserID
        WHERE lt.Name LIKE %s
    """
    # Pagination calculation
    count_query = f"SELECT COUNT(*) as total {query_base}"
    cursor.execute(count_query, (f"%{search_query}%",))
    total = cursor.fetchone()['total']
    total_pages = math.ceil(total / per_page)

    # Fetching paginated workshops
    lessons_query = f"""
       SELECT l.*, lt.Name AS LessonType, lt.Description,
            t.FirstName AS TutorFirstName, t.FamilyName AS TutorFamilyName,
            t.ProfileImage AS TutorProfileImage
        {query_base}
        ORDER BY lt.Name DESC
        LIMIT %s OFFSET %s
    """
    offset = (page - 1) * per_page
    cursor.execute(lessons_query, (f"%{search_query}%", per_page, offset))
    lessons = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template('manager/view_lessions.html', lessons=lessons, page=page, total_pages=total_pages, )


@app.route('/delete_workshop/<int:workshop_id>', methods=['POST'])
@require_role(3)
def delete_workshop(workshop_id):
    connection = getDbConnection()
    cursor = connection.cursor()

    try:
        cursor.execute("DELETE FROM Workshops WHERE WorkshopID = %s", (workshop_id,))
        connection.commit()
        flash('Workshop deleted successfully.', 'success')
    except Exception as e:
        # Log the error if needed
        flash('An error occurred while deleting the workshop.', 'danger')
    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('view_workshops'))

@app.route('/create/lessonType', methods=['GET', 'POST'])
@require_role(3)
def add_lesson_type():
    if request.method == 'POST':
        name = request.form['name'].strip()
        description = request.form['description'].strip()

        if not name or not description:
            flash('All fields are required.', 'danger')
            return redirect(url_for('add_lesson_type'))
        try:
            connection = getDbConnection()
            with connection.cursor() as cursor:
                # Prepare SQL query
                sql = "INSERT INTO LessonTypes (Name, Description) VALUES (%s, %s)"
                # Execute the query
                cursor.execute(sql, (name, description))
                # Commit the transaction
                connection.commit()
                flash('Lesson type added successfully!', 'success')
        except Exception as e:
            # Rollback in case of error
            connection.rollback()
            flash(f"Database error occurred: {e}", 'danger')
        finally:
            if connection:
                connection.close()

        return redirect(url_for('add_lesson_type'))
    
    return render_template('manager/create_lesson_type.html')

@app.route('/edit/lessonType/<int:lesson_type_id>', methods=['GET', 'POST'])
@require_role(3)
def edit_lesson_type(lesson_type_id):
    connection = getDbConnection()
    try:
        if request.method == 'POST':
            name = request.form['name'].strip()
            description = request.form['description'].strip()

            if not name or not description:
                flash('All fields are required.', 'danger')
                return redirect(url_for('edit_lesson_type', lesson_type_id=lesson_type_id))

            with connection.cursor() as cursor:
                sql = "UPDATE LessonTypes SET Name = %s, Description = %s WHERE LessonTypeID = %s"
                cursor.execute(sql, (name, description, lesson_type_id))
                connection.commit()
                flash('Lesson type updated successfully!', 'success')
                return redirect(url_for('edit_lesson_type', lesson_type_id=lesson_type_id))
        else:
            with connection.cursor(dictionary=True) as cursor:
                sql = "SELECT LessonTypeID, Name, Description FROM LessonTypes WHERE LessonTypeID = %s"
                cursor.execute(sql, (lesson_type_id,))
                lesson_type = cursor.fetchone()
                if lesson_type:
                    return render_template('manager/edit_lesson_type.html', lesson_type=lesson_type)
                else:
                    flash('Lesson type not found.', 'danger')
                    return redirect(url_for('list_lesson_types'))          
    except Exception as e:
        flash(f"Database error occurred: {e}", 'danger')
    finally:
        if connection:
            connection.close()

@app.route('/lesson_types', methods=['GET'])
@require_role(3)
def list_lesson_types():
    search_query = request.args.get('search', '')
    connection = getDbConnection()
    try:
        with connection.cursor(dictionary=True) as cursor:
            if search_query:
                sql = "SELECT * FROM LessonTypes WHERE Name LIKE %s ORDER BY Name DESC"
                cursor.execute(sql, ('%' + search_query + '%',))
            else:
                sql = "SELECT * FROM LessonTypes ORDER BY Name DESC"
                cursor.execute(sql)
            lesson_types = cursor.fetchall()
    except Exception as e:
        flash(f"Database error occurred: {e}", 'danger')
    finally:
        if connection:
            connection.close()

    return render_template('manager/view_lesson_type.html', lesson_types=lesson_types, search_query=search_query)

@app.route('/delete/lesson_type/<int:lesson_type_id>', methods=['POST'])
@require_role(3)
def delete_lesson_type(lesson_type_id):
    connection = getDbConnection()
    try:
        with connection.cursor() as cursor:
            sql = "DELETE FROM LessonTypes WHERE LessonTypeID = %s"
            cursor.execute(sql, (lesson_type_id,))
            connection.commit()
            flash('Lesson type deleted successfully.', 'success')
    except Exception as e:
        flash(f"Database error occurred: {e}", 'danger')
        connection.rollback()
    finally:
        if connection:
            connection.close()

    return redirect(url_for('list_lesson_types'))

# profile that was missing
@app.route("/profile/manager")
def manager_profile():
    #get userID
    username = session.get('username')
    cur = getCursor()
    cur.execute("SELECT * FROM Users where Username = %s;",(username,))
    user = cur.fetchone()
    # get proflie
    cur.execute("select * FROM ManagerProfiles where UserID = %s;",(user[0],))
    profile = cur.fetchone()
    return render_template('manager/manager_profile.html', profile = profile)

@app.route("/member_subscription")
def member_subscription():
    connection = getCursor()

    # Get the search query from the URL parameters
    search_query = request.args.get('search', '')

    # Modify the SQL query to include the search condition
    sql_query = f"""
        SELECT
            m.UserID AS 'User ID/Member ID',
            CONCAT(m.FirstName, ' ', m.FamilyName) AS 'Member Name',
            s.Type AS 'Type from Subscription',
            s.StartDate AS 'Start Date',
            s.EndDate AS 'End Date',
            s.subscriptionStatus AS 'Subscription Status'
        FROM
            MemberProfiles m
        JOIN
            Subscriptions s ON m.UserID = s.MemberID
        WHERE
            CONCAT(m.FirstName, ' ', m.FamilyName) LIKE %s
    """

    # Execute the query with the search condition
    connection.execute(sql_query, (f"%{search_query}%",))
    member_subscriptions = connection.fetchall()

    return render_template("manager/member_subscription.html", member_subscriptions=member_subscriptions, search_query=search_query)

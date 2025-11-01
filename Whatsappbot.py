from flask import Flask, request, jsonify, render_template
from twilio.twiml.messaging_response import MessagingResponse
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)
client = MongoClient('mongodb+srv://J0hnMilt0n:python@dl.thj0wqz.mongodb.net/')
db = client['whatsapp_bot']
appointments = db['appointments']
placements = db['placements']
trainings = db['trainings']
admissions = db['admissions']  # Collection for admissions information
workshops = db['workshops']  # Collection for professional development workshops
welfare = db['welfare']  # Collection for student welfare information

# Dictionary to store user state
user_state = {}

# Course details
course_details = {
    "a": [
        {
            "Batch": "2022 - 2024",
            "HOD": "Ms. Ranjana Kumari",
            "Professor": "Basavaraju",
            "No. of Students": 58,
            "No. of Students Placed": 45
        }
    ],
    "b": [
        {
            "Batch": "2022 - 2024",
            "HOD": "Ms. kavitha N",
            "Professor": "Harshitha",
            "No. of Students": 61,
            "No. of Students Placed": 35
        }
    ],
    "c": [
        
        {
            "Batch": "2022 - 2025",
            "HOD": "Ms. Ranjana Kumari",
            "Professor": "Basavaraju",
            "No. of Students": 65,
            "No. of Students Placed": 35
        }
    ],
    "d": [
        {
            "Batch": "2022 - 2024",
            "HOD": "M.G. Gurubasavanna",
            "Professor": "John Milton M",
            "No. of Students": 48,
            "No. of Students Placed": 28
        }
    ],
    "e": [
        {
            "Batch": "2022 - 2024",
            "HOD": " Rudrappa K M",
            "Professor": "Pramod S",
            "No. of Students": 58,
            "No. of Students Placed": 25
        }
    ]
}

# About Pentagon Space
Pentagon_Space = "Pentagon Space is the #1 training institute in Bangolore"

# Contact Information
contact_info = {
    "Address": "Pentagon Space, Bangalore",
    "Phone": "+91 7373367802",
    "©": "Pentagon Space pvt ltd"
}

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET'])
def index1():
    return render_template('signup.html')

@app.route('/webhook', methods=['POST'])
def webhook():
    incoming_msg = request.values.get('Body', '').lower()
    sender_phone_number = request.values.get('From', '')

    resp = MessagingResponse()

    # Check if it's the user's first message and display welcome messages
    if sender_phone_number not in user_state:
        user_state[sender_phone_number] = {}

        # Send welcome messages separately
        welcome_messages = [
            "*Welcome to our Pentagon Space!!! 💐*",
            "*Hello! 😃*\n *I am from GLAD Association, your guide from Pentagon Space. I can help you with courses, placements, trainings, admissions information, professional development workshops, student welfare, and much more!*",
            "Choose one of the options below for me to assist you:\n1. Courses\n2. Placements\n3. Trainings\n4. Admissions Information\n5. Professional Development Workshops\n6. Student Welfare\n7. Book Appointment \n8. Upcoming Appointment \n9. About\n10. Contact Us\n11. Upcoming Events\nPlease reply with the number corresponding to the option you want."
        ]
        for message in welcome_messages:
            resp.message(message)
        return str(resp)

    # Process the message
    response_msg, display_thank_you = handle_message(incoming_msg, sender_phone_number)
    resp.message(response_msg)
    if display_thank_you:
        resp.message("Thank you for choosing us 😃, Have a great day")
        resp.message("Choose one of the options below for me to assist you:\n1. Courses\n2. Placements\n3. Trainings\n4. Admissions Information\n5. Professional Development Workshops\n6. Student Welfare\n7. Book Appointment \n8. Upcoming Appointment \n9. About\n10. Contact Us\n11. Upcoming Events\nPlease reply with the number corresponding to the option you want.")

    return str(resp)

def handle_message(message, phone_number):
    global user_state

    if 'booking' in user_state.get(phone_number, {}):
        return handle_booking(message, phone_number)

    if message.strip().lower() == "1":
        return "*List of Courses:*\na. Master of Computer Applications (MCA)\nb. Bachelor of Computer Applications (BCA)\nc. Master of Business Administration (MBA)\nd. Bachelor of Business Administration (BBA)\ne. Bachelor of Commerce (B.Com)\n\nPlease reply with the letter corresponding to the course if you want more details about it:", False

    if message.strip().lower() in ["a", "b", "c", "d", "e"]:
        course_code = message.strip().lower()
        course_data = course_details.get(course_code)
        if course_data:
            formatted_data = format_course_details(course_data)
            return f"Course Details for {get_courses()[course_code]}:\n\n{formatted_data}", True
        else:
            return "Course details not available for the selected course.", True

    if message.strip().lower() == "2":
        placement_data = get_placements_data()
        return placement_data, True

    if message.strip().lower() == "3":
        training_data = get_training_data()
        return training_data, True

    if message.strip().lower() == "4":
        return get_admissions_info_message(), True

    if message.strip().lower() == "5":
        return get_workshops_info_message(), True

    if message.strip().lower() == "6":
        return get_student_welfare_info(), True
    
    if message.strip().lower() == "7":
        user_state[phone_number]['booking'] = {}
        return "Sure, let's book an appointment. What's your name?", False

    if message.strip().lower() == "8":
        return get_upcoming_appointments(phone_number), False

    if message.strip().lower() == "9":
        return Pentagon_Space, True

    if message.strip().lower() == "10":
        return get_contact_info(), True

    if message.strip().lower() == "11":
        return "There is an upcoming Pentagon Space Campus drive. Register through this link to get connected: https://docs.google.com/forms/d/1XN9qJlIim66HQKS8-jz8uP9gwuTYA2XZRundgGQ6tco/edit", True

    return "I'm sorry, I didn't understand that. Please reply with a valid option.", False

def handle_booking(message, phone_number):
    booking_state = user_state[phone_number].get('booking', {})

    if 'name' not in booking_state:
        booking_state['name'] = message.strip()
        return "Thanks! What service would you like to book an appointment for?", False

    if 'service' not in booking_state:
        booking_state['service'] = message.strip()
        return "Please provide the date for the appointment (DD/MM/YYYY):", False

    if 'date' not in booking_state:
        date_str = message.strip()
        try:
            date = datetime.strptime(date_str, '%d/%m/%Y')
            booking_state['date'] = date
            appointments.insert_one({
                'name': booking_state['name'],
                'service': booking_state['service'],
                'date': date,
                'phone_number': phone_number
            })
            del user_state[phone_number]['booking']
            return f"Your appointment has been booked for {date.strftime('%d/%m/%Y')} for {booking_state['service']}.", True
        except ValueError:
            return "Invalid date format. Please provide the date in DD/MM/YYYY format:", False

    return "I'm sorry, something went wrong. Please try again.", True

def format_course_details(course_data):
    formatted_data = ""
    for data in course_data:
        formatted_data += f"Batch: {data['Batch']}\n"
        formatted_data += f"HOD: {data['HOD']}\n"
        formatted_data += f"Professor: {data['Professor']}\n"
        formatted_data += f"No. of Students: {data['No. of Students']}\n"
        formatted_data += f"No. of Students Placed: {data['No. of Students Placed']}\n\n"
    return formatted_data

def get_courses():
    return {
        "a": "Master of Computer Applications (MCA)",
        "b": "Bachelor of Computer Applications (BCA)",
        "c": "Master of Business Administration (MBA)",
        "d": "Bachelor of Business Administration (BBA)",
        "e": "Bachelor of Commerce (B.Com)"
    }
def get_placements_data():
    # Sample data to be inserted into the placements collection
    sample_data = [
        {
            "Student": "Ruthu AS",
            "Degree": "MCA, 85%",
            "Company": "Google",
            "Role": "Software Engineer",
            "Salary": "9,000,000 INR"
        },
        {
            "Student": "John Milton M",
            "Degree": "BCA, 88%",
            "Company": "Microsoft",
            "Role": "Data Scientist",
            "Salary": "8,500,000 INR"
        },
        {
            "Student": "Harish A",
            "Degree": "MBA, 90%",
            "Company": "Amazon",
            "Role": "Cloud Engineer",
            "Salary": "8,800,000 INR"
        }
    ]

    # Insert sample data into the placements collection if it's empty
    if placements.count_documents({}) == 0:
        placements.insert_many(sample_data)

    # Retrieve placement data from the MongoDB collection
    placement_data = placements.find({})
    formatted_data = "*Placement Information:*\n"
    for data in placement_data:
        formatted_data += f"Student Name: {data['Student']}\n"
        formatted_data += f"Degree with Percentage: {data['Degree']}\n"
        formatted_data += f"Company: {data['Company']}\n"
        formatted_data += f"Role: {data['Role']}\n"
        formatted_data += f"Salary: {data['Salary']}\n\n"
    return formatted_data

def get_training_data():
    # Sample data to be inserted into the trainings collection
    sample_data = [
        {
            "Program": "Python Programming",
            "Description": "An introductory course on Python programming covering basics to advanced topics."
        },
        {
            "Program": "Data Science Bootcamp",
            "Description": "A comprehensive bootcamp on data science, covering data analysis, visualization, and machine learning."
        },
        {
            "Program": "Web Development",
            "Description": "A course on full-stack web development using HTML, CSS, JavaScript, and popular frameworks."
        },
        {
            "Program": "Digital Marketing",
            "Description": "A course on digital marketing strategies, SEO, and social media marketing."
        },
        {
            "Program": "Financial Accounting",
            "Description": "An introductory course on financial accounting principles and practices."}
    ]

    # Insert sample data into the trainings collection if it's empty
    if trainings.count_documents({}) == 0:
        trainings.insert_many(sample_data)

    # Retrieve training data from the MongoDB collection
    training_data = trainings.find({})
    formatted_data = "*Training Information:*\n"
    for data in training_data:
        formatted_data += f"Program: {data['Program']}\n"
        formatted_data += f"Description: {data['Description']}\n\n"
    return formatted_data

def get_admissions_info_message():
    # Sample data to be inserted into the admissions collection
    sample_data = [
        {
            "Batch": "2023-2024",
            "CutOff Rankings": {
                "General": "1500",
                "OBC": "2000",
                "SC/ST": "3000"
            },
            "Tuition Fees": "50,000 INR per year"
        },
        {
            "Batch": "2022-2023",
            "CutOff Rankings": {
                "General": "1400",
                "OBC": "1900",
                "SC/ST": "2900"
            },
            "Tuition Fees": "48,000 INR per year"
        }
    ]

    # Insert sample data into the admissions collection if it's empty
    if admissions.count_documents({}) == 0:
        admissions.insert_many(sample_data)

    # Retrieve admissions data from the MongoDB collection
    admissions_data = admissions.find({})
    formatted_data = "*Admissions Information:*\n"
    for data in admissions_data:
        formatted_data += f"\nBatch: {data['Batch']}\n"
        formatted_data += "CutOff Rankings:\n"
        for category, rank in data['CutOff Rankings'].items():
            formatted_data += f"  {category}: {rank}\n"
        formatted_data += f"Tuition Fees: {data['Tuition Fees']}\n"
    return formatted_data

def get_workshops_info_message():
    # Sample data to be inserted into the workshops collection
    sample_data = [
        {
            "Company": "Google",
            "Certification": "Cloud Computing",
            "Description": "A workshop on cloud computing fundamentals and Google Cloud Platform."
        },
        {
            "Company": "Microsoft",
            "Certification": "AI and Machine Learning",
            "Description": "An advanced workshop on AI and machine learning using Microsoft Azure."
        }
    ]

    # Insert sample data into the workshops collection if it's empty
    if workshops.count_documents({}) == 0:
        workshops.insert_many(sample_data)

    # Retrieve workshop data from the MongoDB collection
    workshop_data = workshops.find({})
    formatted_data = "*Professional Development Workshops:*\n"
    for data in workshop_data:
        formatted_data += f"\nCompany: {data['Company']}\n"
        formatted_data += f"Certification: {data['Certification']}\n"
        formatted_data += f"Description: {data['Description']}\n"
    return formatted_data

def get_student_welfare_info():
    # Sample data to be inserted into the welfare collection
    sample_data = [
        {
            "Title": "Mental Health Support",
            "Description": "We provide mental health support and counseling services for students."
        },
        {
            "Title": "Financial Aid",
            "Description": "Financial aid and scholarships are available for eligible students."
        }
    ]

    # Insert sample data into the welfare collection if it's empty
    if welfare.count_documents({}) == 0:
        welfare.insert_many(sample_data)

    # Retrieve student welfare data from the MongoDB collection
    welfare_data = welfare.find({})
    formatted_data = "*Student Welfare Information:*\n"
    for data in welfare_data:
        formatted_data += f"\nTitle: {data['Title']}\n"
        formatted_data += f"Description: {data['Description']}\n"
    return formatted_data

def get_upcoming_appointments(phone_number):
    upcoming_appointments = appointments.find({'phone_number': phone_number})
    if appointments.count_documents({}) == 0:
        return "You have no upcoming appointments."

    formatted_data = "*Your Upcoming Appointments:*\n"
    for appointment in upcoming_appointments:
        formatted_data += f"\nName: {appointment['name']}\n"
        formatted_data += f"\nService: {appointment['service']}\n"
        formatted_data += f"Date: {appointment['date'].strftime('%d/%m/%Y')}\n"
    return formatted_data

def get_contact_info():
    formatted_data = "*Contact Information:*\n"
    for key, value in contact_info.items():
        formatted_data += f"{key}: {value}\n"
    return formatted_data

if __name__ == '__main__':
    app.run(debug=True)
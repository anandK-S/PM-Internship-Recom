import os
import sqlite3

def init_db():
    """Initialize the database with schema."""
    # Create data directory if it doesn't exist
    if not os.path.exists('data'):
        os.makedirs('data')
    
    # Connect to database
    conn = sqlite3.connect('data/internship_recommender.db')
    db = conn.cursor()
    
    # Create tables
    db.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            education TEXT,
            skills TEXT,
            interests TEXT,
            location TEXT,
            resume_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    db.execute('''
        CREATE TABLE IF NOT EXISTS internships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            company TEXT NOT NULL,
            location TEXT NOT NULL,
            description TEXT NOT NULL,
            requirements TEXT,
            stipend TEXT,
            duration TEXT,
            deadline TEXT,
            sector TEXT,
            skills_required TEXT,
            education_required TEXT,
            is_external INTEGER DEFAULT 0,
            external_id TEXT,
            external_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    db.execute('''
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            internship_id INTEGER NOT NULL,
            cover_letter TEXT,
            resume_path TEXT,
            status TEXT NOT NULL,
            applied_date TIMESTAMP,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (internship_id) REFERENCES internships (id)
        )
    ''')
    
    # Insert sample data if the database is empty
    if db.execute('SELECT COUNT(*) FROM internships').fetchone()[0] == 0:
        insert_sample_data(db)
    
    conn.commit()
    conn.close()
    
    print("Database initialized successfully!")

def insert_sample_data(db):
    """Insert sample internships into the database."""
    internships = [
        (
            'Software Development Intern', 
            'TechCorp India', 
            'Bangalore, Karnataka', 
            'Join our team to develop cutting-edge web applications using modern technologies.',
            'Python, JavaScript, React, Node.js',
            '₹15,000 - ₹20,000 per month',
            '3 months',
            '2025-10-15',
            'Information Technology',
            'Python, JavaScript, React, Node.js, Git',
            'B.Tech/B.E. in Computer Science or related field'
        ),
        (
            'Data Science Intern', 
            'Analytics Hub', 
            'Hyderabad, Telangana', 
            'Work on real-world data science projects and gain hands-on experience with machine learning models.',
            'Python, Statistics, Machine Learning',
            '₹18,000 - ₹25,000 per month',
            '6 months',
            '2025-09-30',
            'Data Science',
            'Python, Pandas, NumPy, Scikit-learn, SQL',
            'B.Tech/B.E./M.Tech in Computer Science, Statistics, or Mathematics'
        ),
        (
            'Marketing Intern', 
            'BrandMasters', 
            'Mumbai, Maharashtra', 
            'Assist in developing and implementing marketing strategies for various clients.',
            'Social Media Marketing, Content Creation',
            '₹12,000 - ₹15,000 per month',
            '3 months',
            '2025-10-05',
            'Marketing',
            'Social Media, Content Writing, Adobe Creative Suite',
            'BBA/MBA in Marketing or related field'
        ),
        (
            'Finance Intern', 
            'FinSecure Solutions', 
            'Delhi, NCR', 
            'Learn financial analysis, reporting, and investment strategies in a fast-paced environment.',
            'Financial Analysis, Excel, Accounting',
            '₹15,000 - ₹18,000 per month',
            '4 months',
            '2025-09-25',
            'Finance',
            'Excel, Financial Modeling, Accounting Principles',
            'B.Com/BBA/MBA in Finance or related field'
        ),
        (
            'UI/UX Design Intern', 
            'DesignWave', 
            'Pune, Maharashtra', 
            'Create user-centered designs for web and mobile applications.',
            'UI Design, UX Research, Prototyping',
            '₹15,000 - ₹20,000 per month',
            '3 months',
            '2025-10-10',
            'Design',
            'Figma, Adobe XD, Sketch, User Research',
            'Bachelor\'s degree in Design, HCI, or related field'
        ),
        (
            'Content Writing Intern', 
            'ContentCraft', 
            'Chennai, Tamil Nadu', 
            'Develop engaging content for various platforms including blogs, social media, and websites.',
            'Content Writing, SEO Knowledge',
            '₹10,000 - ₹15,000 per month',
            '3 months',
            '2025-09-20',
            'Content',
            'Content Writing, SEO, Social Media',
            'Bachelor\'s degree in English, Journalism, or related field'
        ),
        (
            'HR Intern', 
            'PeopleFirst', 
            'Kolkata, West Bengal', 
            'Assist in recruitment, employee engagement, and HR operations.',
            'HR Processes, Communication Skills',
            '₹12,000 - ₹15,000 per month',
            '4 months',
            '2025-10-01',
            'Human Resources',
            'MS Office, Communication, HR Processes',
            'BBA/MBA in HR or related field'
        ),
        (
            'Operations Intern', 
            'SupplyChain Pro', 
            'Ahmedabad, Gujarat', 
            'Learn about supply chain management and operations optimization.',
            'Analytical Skills, Process Optimization',
            '₹14,000 - ₹18,000 per month',
            '6 months',
            '2025-09-15',
            'Operations',
            'Excel, Data Analysis, Process Mapping',
            'B.Tech/BBA/MBA in Operations or related field'
        ),
        (
            'Research Intern', 
            'InnovateResearch', 
            'Bhubaneswar, Odisha', 
            'Conduct research on emerging technologies and market trends.',
            'Research Methodology, Data Analysis',
            '₹15,000 - ₹20,000 per month',
            '6 months',
            '2025-10-20',
            'Research',
            'Research Methods, Data Analysis, Academic Writing',
            'Master\'s degree in relevant field'
        ),
        (
            'Digital Marketing Intern', 
            'DigitalEdge', 
            'Jaipur, Rajasthan', 
            'Gain hands-on experience in SEO, SEM, social media marketing, and analytics.',
            'Digital Marketing Tools, Analytics',
            '₹12,000 - ₹16,000 per month',
            '3 months',
            '2025-09-30',
            'Digital Marketing',
            'Google Analytics, SEO, SEM, Social Media Marketing',
            'Bachelor\'s degree in Marketing or related field'
        ),
        (
            'Mechanical Engineering Intern', 
            'EngineTech Solutions', 
            'Coimbatore, Tamil Nadu', 
            'Work on mechanical design and product development projects.',
            'CAD Software, Mechanical Design',
            '₹15,000 - ₹20,000 per month',
            '6 months',
            '2025-10-15',
            'Engineering',
            'AutoCAD, SolidWorks, Mechanical Design',
            'B.Tech/B.E. in Mechanical Engineering'
        ),
        (
            'Electrical Engineering Intern', 
            'PowerGrid Solutions', 
            'Vadodara, Gujarat', 
            'Assist in electrical system design and implementation.',
            'Electrical Circuit Design, Power Systems',
            '₹15,000 - ₹20,000 per month',
            '4 months',
            '2025-09-25',
            'Engineering',
            'Electrical Design, Circuit Analysis, AutoCAD Electrical',
            'B.Tech/B.E. in Electrical Engineering'
        ),
        (
            'Civil Engineering Intern', 
            'BuildRight Constructions', 
            'Lucknow, Uttar Pradesh', 
            'Gain experience in construction project management and structural design.',
            'Structural Analysis, Construction Management',
            '₹14,000 - ₹18,000 per month',
            '6 months',
            '2025-10-10',
            'Engineering',
            'AutoCAD, Structural Analysis, Construction Management',
            'B.Tech/B.E. in Civil Engineering'
        ),
        (
            'Biotechnology Intern', 
            'BioInnovate Research', 
            'Mysore, Karnataka', 
            'Work on biotechnology research projects and laboratory techniques.',
            'Laboratory Skills, Research Methodology',
            '₹15,000 - ₹20,000 per month',
            '6 months',
            '2025-09-30',
            'Biotechnology',
            'Laboratory Techniques, Research Methods, Data Analysis',
            'B.Tech/B.Sc/M.Sc in Biotechnology or related field'
        ),
        (
            'Graphic Design Intern', 
            'CreativeVision', 
            'Indore, Madhya Pradesh', 
            'Create visual content for various media including print and digital platforms.',
            'Graphic Design Tools, Visual Communication',
            '₹12,000 - ₹16,000 per month',
            '3 months',
            '2025-10-05',
            'Design',
            'Adobe Creative Suite, Visual Design, Typography',
            'Bachelor\'s degree in Graphic Design or related field'
        )
    ]
    
    for internship in internships:
        db.execute(
            '''INSERT INTO internships 
               (title, company, location, description, requirements, stipend, duration, deadline, sector, skills_required, education_required) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            internship
        )
    
    print(f"Added {len(internships)} sample internships to the database")

if __name__ == "__main__":
    init_db()
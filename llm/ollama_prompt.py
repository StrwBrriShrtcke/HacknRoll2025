import asyncio
import json
from typing import Optional, Literal
from pprint import pp  # just for pretty printing when testing

import ollama
from ollama import Client
from pydantic import BaseModel, ValidationError


##################################################
# Configuration
##################################################

base_model = "gemma2:9b"  # choose a model that you have
create_custom_model = True  # set to False if model already created

# Refer to https://github.com/ollama/ollama/blob/main/docs/modelfile.md for more information on modelfile

##################################################
# Model for generating questions per web page
##################################################

system_questions = """
You will be given text extracted from a university's website.

Generate a list of up to 3 questions based on the main article presented in the text.

Ignore the irrelevant text that does not pertain to the main article or content. The irrelevant text could be the navigation bar, contact information, links to other pages, etc.

The text might not informative in some cases. For example, when the text is an error page. If the text is not informative, generate no question.

If questions are generated, the following conditions must be met for each question:

- The CORRECT answer should be a DIRECT quote from the text.
- Each question has exactly 1 correct quote and 3 wrong quotes.
- Hallucinate the WRONG quotes ONLY and ensure that the wrong quotes CANNOT be found in the text.

Return the result in JSON format.
"""

modelfile_questions = f'''
FROM {base_model}
PARAMETER temperature 0.1
PARAMETER num_ctx 4096
SYSTEM """{system_questions}"""
'''

custom_model_questions = "web_questions_generator"


class WrongQuotes(BaseModel):
    wrong_quote_1: str
    wrong_quote_2: str
    wrong_quote_3: str


class QuestionAndQuotes(BaseModel):
    question: str
    correct_quote: str
    wrong_quotes: WrongQuotes


class WebPageQuestions(BaseModel):
    question_set1: Optional[QuestionAndQuotes]
    question_set2: Optional[QuestionAndQuotes]
    question_set3: Optional[QuestionAndQuotes]


##################################################
# Model for classifying each web page into categories
##################################################

system_classification = """
You will be given text extracted from a university website.

Based on the given text, decide which of the following categories is the MOST ACCURATE description of the given text such that a reader would refer to the given text for that specific purpose.

The following is a reference of the different identified categories.

### Error page
    - Error page: Page not found, 404 error.

### University or Institution Information
    - About the University: History, vision, mission, leadership, strategic goals, etc.
    - Administration: Governance, board of trustees, leadership profiles, organizational structure.
    - Accreditation and Rankings: Details about the university's accreditations, national and international rankings.
    - University News and Announcements: Updates, events, press releases, major milestones.
    - Publications or Annual Reports: University-wide publications, reports, or performance reviews.

### Academic Information
    - Curriculum Information: Undergraduate, graduate programs, courses, and subjects.
    - Academic Calendar: Important dates (semesters, holidays, application deadlines).
    - Departments and Faculties: Pages for different departments, schools, or faculties (e.g., Faculty of Engineering, School of Business).
    - Programs and Degrees Offered: Bachelor's, Master's, PhD programs, certifications, diplomas.
    - Admission Requirements: Entry requirements, application processes for different programs.
    - Tuition Fees and Scholarships: Tuition rates, financial aid, scholarship opportunities.
    - Student Services: Resources available to students (advising, counseling, career services).
    - Study Abroad Programs: Information on exchange programs, international collaborations.

### Research and Innovation
    - Research Centers and Institutes: Institutes, centers of excellence, and labs dedicated to research.
    - Research Projects: Ongoing research initiatives, collaborations with industries or international partners.
    - Publications and Research Output: Academic papers, research articles, journals.
    - Innovation and Startups: Technology transfer, entrepreneurship, startup incubators.
    - Research Funding: Grants, research funding opportunities, fellowships.

### Student Life
    - Campus Life: Information about campus culture, clubs, societies, sports, etc.
    - Student Accommodation: On-campus housing, dormitory details, cost, application process.
    - Student Events: Upcoming student events, orientations, activities.
    - Health and Well-being: Mental health resources, medical services, wellness programs.
    - Student Organizations and Clubs: Academic and extracurricular clubs, student government.
    - Internships and Career Services: Internships, job placements, career fairs, employment opportunities.

### Administrative Services
    - Student Portal or Portal Login: Login page for students, faculty, or staff to access personal information and academic services.
    - Online Forms: Forms for students or staff (e.g., enrollment forms, transcript requests).
    - IT Help or Support: IT support for students and faculty, troubleshooting, contact details.
    - Policies and Regulations: University rules, codes of conduct, academic integrity, etc.
    - Graduation and Alumni Services: Graduation requirements, alumni association, alumni events.
    - Library and Resources: Access to academic resources, digital libraries, journal subscriptions.

### Faculty and Staff Information
    - Faculty Directory: Contact information, profiles of faculty members, research interests.
    - Staff Directory: Non-academic staff roles, contact information, office locations.
    - Faculty Research and Publications: Details of faculty-led research, their publications.
    - Teaching and Administrative Roles: Information on the roles and responsibilities of faculty and staff.
    - Career Opportunities for Faculty or Staff: Job openings for faculty and staff positions.

### International and Global Engagement
    - Global Partnerships: Details on international partnerships, joint degree programs, research collaborations.
    - Study Abroad and Exchange Programs: Information on exchange programs and opportunities for global learning.
    - International Students: Admissions information, visas, scholarships, support services.

### External Relations and Partnerships
    - Corporate Partnerships: Partnerships with businesses and industries.
    - Alumni Relations: Engagement with alumni, newsletters, events, donations.
    - Community Engagement: Outreach programs, social responsibility initiatives, collaborations with local communities.
    - Donations and Fundraising: Information on how individuals or organizations can contribute to the university.

### Events and Conferences
    - University Events: Seminars, talks, webinars, and other events hosted by the university.
    - Conferences and Workshops: Academic conferences, symposia, workshops organized or hosted by the university.
    - Public Lectures: Events open to the public, keynote speeches, guest lectures.

### Technology and Innovation
    - IT Services and Support: Technical resources for students, faculty, and staff.
    - Digital Learning Platforms: Online education resources, learning management systems (e.g., Moodle, Canvas).
    - Smart Campus Technologies: Technologies used for campus management, smart classroom systems.
    - Campus Facilities: Information about campus facilities (e.g., sports, libraries, research labs).

### Sustainability and Environment
    - Sustainability Initiatives: University efforts toward environmental sustainability, green campus initiatives.
    - Environmental Research: Research focused on sustainability, climate change, and environmental science.

### Legal and Compliance
    - Legal Notices: Terms of service, privacy policies, copyright information, disclaimers.
    - Compliance and Ethics: University compliance with laws, ethical guidelines for students and staff.

### Accessibility
    - Accessibility Resources: Information on disability services, accommodations for students with disabilities.
    - Website Accessibility: Information on how to navigate the university website with assistive technologies.

### Unidentified
    - Unidentified: Does not belong to any category above.

Return the result in JSON format.
"""

custom_model_classification = "web_classifier"

modelfile_classification = f'''
FROM {base_model}
PARAMETER temperature 0
PARAMETER num_ctx 4096
SYSTEM """{system_questions}"""
'''


class Category(BaseModel):
    category: Literal[
        "Error page",
        "About the university",
        "Administration",
        "Accreditation and rankings",
        "University news and announcements",
        "Publications or annual reports",
        "Curriculum information",
        "Academic calendar",
        "Departments and faculties",
        "Programs and degrees offered",
        "Admission requirements",
        "Tuition fees and scholarships",
        "Student services",
        "Study abroad programs",
        "Research centers and institutes",
        "Research projects",
        "Publications and research output",
        "Innovation and startups",
        "Research funding",
        "Campus life",
        "Student accommodation",
        "Student events",
        "Health and well being",
        "Student organizations and clubs",
        "Internships and career services",
        "Student portal or portal login",
        "Online forms",
        "IT help or support",
        "Policies and regulations",
        "Graduation and alumni services",
        "Library and resources",
        "Faculty directory",
        "Staff directory",
        "Faculty research and publications",
        "Teaching and administrative roles",
        "Career opportunities for faculty or staff",
        "Global partnerships",
        "Study abroad and exchange programs",
        "International students",
        "Corporate partnerships",
        "Alumni relations",
        "Community engagement",
        "Donations and fundraising",
        "University events",
        "Conferences and workshops",
        "Public lectures",
        "IT services and support",
        "Digital learning platforms",
        "Smart campus technologies",
        "Campus facilities",
        "Sustainability initiatives",
        "Environmental research",
        "Legal notices",
        "Compliance and ethics",
        "Accessibility resources",
        "Website accessibility",
        "Unidentified",
    ]


if create_custom_model:
    print(f"Creating custom model {custom_model_questions}...")
    progress = ollama.create(
        model=custom_model_questions,
        modelfile=modelfile_questions,
        stream=True,
    )
    for p in progress:
        print(p)
    print(f"Custom model {custom_model_questions} created")
    print(f"Creating custom model {custom_model_classification}...")
    progress = ollama.create(
        model=custom_model_classification,
        modelfile=modelfile_classification,
        stream=True,
    )
    for p in progress:
        print(p)
    print(f"Custom model {custom_model_classification} created")


def generate_questions(content: str) -> Optional[dict]:
    response_questions = Client().chat(
        model=custom_model_questions,
        messages=[{"role": "user", "content": content}],
        format=WebPageQuestions.model_json_schema(),
    )
    json_response_questions = response_questions.message.content
    response_classification = Client().chat(
        model=custom_model_classification,
        messages=[{"role": "user", "content": content}],
        format=Category.model_json_schema(),
    )
    json_response_classification = response_classification.message.content
    try:
        WebPageQuestions.model_validate_json(json_response_questions)
        Category.model_validate_json(json_response_classification)

        return json.loads(json_response_questions) | json.loads(
            json_response_classification
        )
    except ValidationError:
        return None


def start_doing_from_db():
    import sqlite3
    from pathlib import Path
    from os import path

    results_dir = "results"

    Path(results_dir).mkdir(parents=True, exist_ok=True)
    db_filepath = path.join(results_dir, "site_info.db")

    # set up database connection
    con = sqlite3.connect(db_filepath)
    cur = con.cursor()

    # make table schema
    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS questions(
        id INTEGER PRIMARY KEY NOT NULL,
        created_at TEXT NOT NULL DEFAULT current_timestamp,
        site_id INTEGER NOT NULL REFERENCES sites(id),
        question TEXT NOT NULL,
        correct TEXT NOT NULL,
        wrong1 TEXT NOT NULL,
        wrong2 TEXT NOT NULL,
        wrong3 TEXT NOT NULL,
        FOREIGN KEY(site_id) REFERENCES sites(id)
    )
    """
    )

    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS site_category(
        id INTEGER PRIMARY KEY NOT NULL REFERENCES sites(id),
        created_at TEXT NOT NULL DEFAULT current_timestamp,
        category TEXT NOT NULL,
        FOREIGN KEY(id) REFERENCES sites(id)
    )
    """
    )

    undone_sites = cur.execute(
        "SELECT id, text_content FROM sites WHERE text_content IS NOT NULL"
    ).fetchall()

    for i, (site_id, text_content) in enumerate(undone_sites):
        print(f"{i} site id {site_id} generating questions")
        result = None
        tries = 0
        while not result:
            tries += 1
            print(f"try {tries}")
            result = generate_questions(text_content)
        print(f"{i} site id {site_id} generated!")

        question_data = []
        for i in range(1, 4):
            if question_set := result[f"question_set{i}"]:
                question_data.append(
                    {
                        "site_id": site_id,
                        "question": question_set["question"],
                        "correct": question_set["correct_quote"],
                        **{
                            k.replace("_quote_", ""): v
                            for k, v in question_set["wrong_quotes"].items()
                        },
                    }
                )

        if question_data:
            cur.executemany(
                """
        INSERT OR IGNORE INTO questions(
            site_id,
            question,
            correct,
            wrong1,
            wrong2,
            wrong3
        ) VALUES (
            :site_id,
            :question,
            :correct,
            :wrong1,
            :wrong2,
            :wrong3
        )
        """,
                question_data,
            )
            con.commit()
            print(f"{i} site id {site_id} questions inserted into database")

        if category := result["category"]:
            cur.execute(
                """
        INSERT OR IGNORE INTO site_category(
            id,
            category
        ) VALUES (?, ?)
        """,
                (site_id, category),
            )
            con.commit()
            print(f"{i} site id {site_id} category inserted into database")

        cur.execute(
            "UPDATE sites SET text_content = NULL WHERE id = ?",
            (site_id,),
        )
        con.commit()
        print(f"{i} site id {site_id} deleted old text content")

        print(f"Done site id {site_id}")

    print("ALL DONE!")


start_doing_from_db()

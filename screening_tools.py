# screening_tools.py

gad7_test = {
    "name": "GAD-7",
    "title": "Generalized Anxiety Disorder 7-item (GAD-7) Assessment",
    "instructions": "Over the last 2 weeks, how often have you been bothered by the following problems? Please answer with a number from 0 to 3.",
    "questions": [
        "1. Feeling nervous, anxious, or on edge",
        "2. Not being able to stop or control worrying",
        "3. Worrying too much about different things",
        "4. Trouble relaxing",
        "5. Being so restless that it is hard to sit still",
        "6. Becoming easily annoyed or irritable",
        "7. Feeling afraid as if something awful might happen"
    ],
    "options": [
        "(0) Not at all",
        "(1) Several days",
        "(2) More than half the days",
        "(3) Nearly every day"
    ],
    "scoring_rules": [
        {"range": (0, 4), "interpretation": "Minimal anxiety. Your anxiety levels appear to be low. Keep practicing healthy coping habits."},
        {"range": (5, 9), "interpretation": "Mild anxiety. You may be experiencing some symptoms of anxiety. Consider exploring stress management techniques from the knowledge base."},
        {"range": (10, 14), "interpretation": "Moderate anxiety. It seems you're dealing with a notable level of anxiety. It might be helpful to talk to a student counselor or a trusted professional."},
        {"range": (15, 21), "interpretation": "Severe anxiety. The score suggests you are experiencing significant anxiety. Please consider seeking professional support soon. You can find emergency resources in the 'Help' section."}
    ]
}

# You can add other tests here in the future, like phq9_test
tests = {
    "gad7": gad7_test
}

def get_test(name: str):
    return tests.get(name)
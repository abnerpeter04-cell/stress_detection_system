from questions import QUESTIONS


class StressAssessmentAgent:

    def __init__(self):
        self.reset()

    def reset(self):
        self.state = "start"
        self.category = None
        self.question_index = 0
        self.score = 0

    def reply(self, message):

        message = message.strip().lower()

        # ==========================
        # START
        # ==========================
        if self.state == "start":

            self.state = "choose"

            return {
                "reply":
                "👋 Welcome to the Undergraduate Stress Assessment Agent.<br><br>"
                "Please choose the area you want to assess:<br><br>"
                "1️⃣ Academic Stress<br>"
                "2️⃣ Financial Stress<br>"
                "3️⃣ Family Stress<br>"
                "4️⃣ Health & Lifestyle<br>"
                "5️⃣ Social & Emotional<br><br>"
                "Reply with a number (1-5)."
            }

        # ==========================
        # CHOOSE CATEGORY
        # ==========================
        if self.state == "choose":

            categories = {
                "1": "academic",
                "2": "financial",
                "3": "family",
                "4": "health",
                "5": "social"
            }

            if message not in categories:
                return {
                    "reply": "Please choose a number between 1 and 5."
                }

            self.category = categories[message]
            self.state = "assessment"

            question = QUESTIONS[self.category][0]

            return {
                "reply":
                f"✅ <b>{self.category.title()} Assessment Selected</b><br><br>"
                f"<b>Question 1 of {len(QUESTIONS[self.category])}</b><br><br>"
                f"{question}<br><br>"
                "<b>Select one option:</b><br>"
                "1️⃣ Never<br>"
                "2️⃣ Rarely<br>"
                "3️⃣ Sometimes<br>"
                "4️⃣ Often<br>"
                "5️⃣ Always"
            }

        # ==========================
        # ASSESSMENT
        # ==========================
        if self.state == "assessment":

            if message not in ["1", "2", "3", "4", "5"]:
                return {
                    "reply":
                    "Please answer using:<br><br>"
                    "1️⃣ Never<br>"
                    "2️⃣ Rarely<br>"
                    "3️⃣ Sometimes<br>"
                    "4️⃣ Often<br>"
                    "5️⃣ Always"
                }

            self.score += int(message)
            self.question_index += 1

            total = len(QUESTIONS[self.category])

            # Assessment Finished
            if self.question_index >= total:

                percentage = round((self.score / (total * 5)) * 100)

                if percentage < 30:
                    level = "LOW"

                elif percentage < 60:
                    level = "MODERATE"

                else:
                    level = "HIGH"

                recommendation = (
                    "• Take regular study breaks.<br>"
                    "• Maintain healthy sleep habits.<br>"
                    "• Exercise regularly.<br>"
                    "• Speak with trusted friends, lecturers or a counsellor.<br>"
                    "• Practice relaxation techniques."
                )

                self.reset()

                return {
                    "reply":
                    f"✅ <b>Assessment Complete!</b><br><br>"
                    f"Stress Level: <b>{level}</b><br>"
                    f"Stress Score: <b>{percentage}%</b><br><br>"
                    f"<b>Recommendations</b><br>"
                    f"{recommendation}<br><br>"
                    "Type <b>start</b> to begin another assessment."
                }

            # Next Question
            question = QUESTIONS[self.category][self.question_index]

            return {
                "reply":
                f"<b>Question {self.question_index + 1} of {total}</b><br><br>"
                f"{question}<br><br>"
                "<b>Select one option:</b><br>"
                "1️⃣ Never<br>"
                "2️⃣ Rarely<br>"
                "3️⃣ Sometimes<br>"
                "4️⃣ Often<br>"
                "5️⃣ Always"
            }

        # ==========================
        # UNKNOWN STATE
        # ==========================
        self.reset()

        return {
            "reply": "Something went wrong. Type <b>start</b> to begin again."
        }
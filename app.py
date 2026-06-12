from flask import Flask, render_template, request, send_file
from groq import Groq
from dotenv import load_dotenv
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import os

load_dotenv()

app = Flask(__name__)

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

latest_result = ""

@app.route("/", methods=["GET", "POST"])
def index():

    global latest_result

    result = ""

    if request.method == "POST":

        email_content = request.form["email"]

        prompt = f"""
You are a cybersecurity expert.

Analyze the email and return ONLY in this format:

🚨 Threat Level: LOW / MEDIUM / HIGH

🎯 Phishing Probability: XX%

🔍 Suspicious Indicators:
- point 1
- point 2
- point 3

⚠️ Potential Risks:
- risk 1
- risk 2

🛡️ Security Recommendations:
- recommendation 1
- recommendation 2
- recommendation 3

📧 Email:
{email_content}
"""

        try:

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            result = response.choices[0].message.content
            latest_result = result

        except Exception as e:
            result = f"❌ Error: {str(e)}"

    return render_template("index.html", result=result)


@app.route("/download")
def download_pdf():

    if latest_result == "":
        return "No report available. Analyze an email first."

    pdf_file = "CyberGuard_Report.pdf"

    doc = SimpleDocTemplate(pdf_file)
    styles = getSampleStyleSheet()

    content = [
        Paragraph("CyberGuard AI Threat Analysis Report", styles["Title"]),
        Paragraph(latest_result.replace("\n", "<br/>"), styles["BodyText"])
    ]

    doc.build(content)

    return send_file(pdf_file, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
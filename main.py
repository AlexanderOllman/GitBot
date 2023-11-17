from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
from openai import OpenAI


key = "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"
client = OpenAI(api_key = key)

app = Flask(__name__)

def scrape_open_issues(owner, repo):
    url = f"https://github.com/{owner}/{repo}/issues"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    issues = []

    for item in soup.find_all("div", class_="js-issue-row"):
        title = item.find("a", class_="Link--primary").text.strip()
        link = "https://github.com" + item.find("a", class_="Link--primary")['href']
        comments_text = item.find("a", class_="Link--muted").text.strip()
        comments = int(comments_text.split()[0]) if comments_text else 0
        issues.append({'title': title, 'link': link, 'comments': comments})

    return issues

def scrape_open_pull_requests(owner, repo):
    url = f"https://github.com/{owner}/{repo}/pulls"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    pull_requests = []

    for item in soup.find_all("div", class_="js-issue-row"):
        title = item.find("a", class_="Link--primary").text.strip()
        link = "https://github.com" + item.find("a", class_="Link--primary")['href']
        comments_text = item.find("a", class_="Link--muted").text.strip()
        comments = int(comments_text.split()[0]) if comments_text else 0
        pull_requests.append({'title': title, 'link': link, 'comments': comments})

    return pull_requests

def chat_with_gpt3(prompt):
    system = "You are a "
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": prompt},
        ]
    )
    return response.choices[0].message.content

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.json
    message = data['message']
    owner_repo = data['owner_repo']
    owner, repo = owner_repo.split('/')
    issues = scrape_open_issues(owner.strip(), repo.strip())

    issue_titles = '\n'.join([f"- {issue['title']}" for issue in issues])
    prompt = (
        "As a GitHub issue assistant, I'm here to help you find issues you can contribute to.\n"
        f"Here are some recent issues in the {owner}/{repo} repository:\n{issue_titles}\n\n"
        "Could you tell me about your coding experience and what areas you're interested in?"
        f"\n\nUser: {message}\n\n"
    )

    reply = chat_with_gpt3(prompt)
    return jsonify({'reply': reply})

if __name__ == '__main__':
    app.run(debug=True)
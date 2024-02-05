import os
import platform
import json
import requests
import logging
from subprocess import run
from rich.prompt import Prompt
from rich import print
from rich.console import Console
from rich.panel import Panel
from rich.console import Group
from rich.align import Align
from rich import box
from rich.markdown import Markdown
from typing import Any
from flask import Flask, request, jsonify
from flask_cors import CORS

# Initialize Flask application
app = Flask(__name__)
CORS(app)
@app.route('/get_ai_response', methods=['POST'])
def get_ai_response():
    data = request.json
    user_prompt = data.get("prompt", "")
    # Use your existing openai_api function to get the response
    ai_response = openai_api(user_prompt)
    return jsonify({"response": ai_response})
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
# Load environment variables
chat_history = []
OPENAI_API_KEY = "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"
console = Console()
AI_OPTION = ("OPENAI")
# OpenAI API URL
OPENAI_API_URL = "https://api.openai.com/v1/engines/text-davinci-003/completions"

def openai_api(prompt):
    try:
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {OPENAI_API_KEY}',
        }
        data = {
            "prompt": prompt,
            "max_tokens": 1024
        }
        response = requests.post(OPENAI_API_URL, headers=headers, json=data)
        response_json = response.json()
        logging.debug(f"API Response: {response_json}")
        return response_json.get("choices", [{}])[0].get("text", "")
    except Exception as e:
        logging.error(f"Error in openai_api function: {e}")
        return ""

# ... [Include your other functions here, like clearscr, save_chat, vuln_analysis, static_analysis] ...
def clearscr() -> None:
    try:
        osp = platform.system()
        match osp:
            case 'Darwin':
                os.system("clear")
            case 'Linux':
                os.system("clear")
            case 'Windows':
                os.system("cls")
    except Exception:
        pass
def save_chat(chat_history: list[Any, Any]) -> None:
    f = open('chat_history.json', 'w+')
    f.write(json.dumps(chat_history))
    f.close


def vuln_analysis(scan_type, file_path, ai_option) -> Panel:
    global chat_history
    f = open(file_path, "r")
    file_data = f.read()
    f.close
    instructions = """
    You are a Universal Vulnerability Analyzer powered by the Llama2 model. Your main objective is to analyze any provided scan data or log data to identify potential vulnerabilities in the target system or network. You can use the scan type or the scanner type to prepare better report.
        1. Data Analysis: Thoroughly analyze the given scan data or log data to uncover vulnerabilities and security issues in the target environment.
        2. Format Flexibility: Be adaptable to handle various data formats, such as NMAP scans, vulnerability assessment reports, security logs, or any other relevant data.
        3. Vulnerability Identification: Identify different types of vulnerabilities, including but not limited to software vulnerabilities, misconfigurations, exposed sensitive information, potential security risks, and more.
        4. Accuracy and Precision: Ensure the analysis results are accurate and precise to provide reliable information for further actions.
        5. Comprehensive Report: Generate a detailed vulnerability report that includes the following sections:
            - Vulnerability Summary: A brief overview of the detected vulnerabilities.
            - Software Vulnerabilities: List of identified software vulnerabilities with their respective severity levels.
            - Misconfigurations: Highlight any misconfigurations found during the analysis.
            - Exposed Sensitive Information: Identify any exposed sensitive data, such as passwords, API keys, or usernames.
            - Security Risks: Flag potential security risks and their implications.
            - Recommendations: Provide actionable recommendations to mitigate the detected vulnerabilities.
        6. Threat Severity: Prioritize vulnerabilities based on their severity level to help users focus on critical issues first.
        7. Context Awareness: Consider the context of the target system or network when analyzing vulnerabilities. Take into account factors like system architecture, user permissions, and network topology.
        8. Handling Unsupported Data: If the provided data format is unsupported or unclear, politely ask for clarifications or indicate the limitations.
        9. Language and Style: Use clear and concise language to present the analysis results. Avoid jargon and unnecessary technicalities.
        10. Provide output in Markdown. 
    """

    data = f"""
        Provide the scan type: {scan_type} 
        Provide the scan data or log data that needs to be analyzed: {file_data}
    """
    prompt = f"[INST] <<SYS>> {instructions}<</SYS>> Data to be analyzed: {data} [/INST]"
    if ai_option == "RUNPOD":
        out = llama_api(prompt)
    else:
        out = llm(prompt)
    ai_out = Markdown(out)
    message_panel = Panel(
        Align.center(
            Group("\n", Align.center(ai_out)),
            vertical="middle",
        ),
        box=box.ROUNDED,
        padding=(1, 2),
        title="[b red]The HackBot AI output",
        border_style="blue",
    )
    save_data = {
        "Query": str(prompt),
        "AI Answer": str(out)
    }
    chat_history.append(save_data)
    return message_panel


def static_analysis(language_used, file_path, ai_option) -> Panel:
    global chat_history
    f = open(file_path, "r")
    file_data = f.read()
    f.close
    instructions = """
        Analyze the given programming file details to identify and clearly report bugs, vulnerabilities, and syntax errors.
        Additionally, search for potential exposure of sensitive information such as API keys, passwords, and usernames. Please provide result in Markdown.
    """
    data = f"""
        - Programming Language: {language_used}
        - File Name: {file_path}
        - File Data: {file_data}
    """
    prompt = f"[INST] <<SYS>> {instructions}<</SYS>> Data to be analyzed: {data} [/INST]"
    if ai_option == "RUNPOD":
        out = openai_api(prompt)
    else:
        out = openai_api(prompt)
    ai_out = Markdown(out)
    message_panel = Panel(
        Align.center(
            Group("\n", Align.center(ai_out)),
            vertical="middle",
        ),
        box=box.ROUNDED,
        padding=(1, 2),
        title="[b red]The HackBot AI output",
        border_style="blue",
    )
    save_data = {
        "Query": str(prompt),
        "AI Answer": str(out)
    }
    chat_history.append(save_data)
    return message_panel

def Print_AI_out(prompt, ai_option) -> Panel:
    global chat_history
    out = openai_api(prompt)
    ai_out = Markdown(out)
    message_panel = Panel(
        Align.center(
            Group("\n", Align.center(ai_out)),
            vertical="middle",
        ),
        box=box.ROUNDED,
        padding=(1, 2),
        title="[b red]The HackBot AI output",
        border_style="blue",
    )
    save_data = {
        "Query": str(prompt),
        "AI Answer": str(out)
    }
    chat_history.append(save_data)
    return message_panel

def main() -> None:
    clearscr()
    banner = """
     _   _            _    ____        _   
    | | | | __ _  ___| | _| __ )  ___ | |_ 
    | |_| |/ _` |/ __| |/ /  _ \ / _ \| __| By: Morpheuslord
    |  _  | (_| | (__|   <| |_) | (_) | |_  AI used: Meta-LLama2
    |_| |_|\__,_|\___|_|\_\____/ \___/ \__|
    """
    contact_dev = """
    Email = morpheuslord@protonmail.com
    Twitter = https://twitter.com/morpheuslord2
    LinkedIn https://www.linkedin.com/in/chiranjeevi-g-naidu/
    Github = https://github.com/morpheuslord
    """

    help_menu = """
    - clear_screen: Clears the console screen for better readability.
    - quit_bot: This is used to quit the chat application
    - bot_banner: Prints the default bots banner.
    - contact_dev: Provides my contact information.
    - save_chat: Saves the current sessions interactions.
    - help_menu: Lists chatbot commands.
    - vuln_analysis: Does a Vuln analysis using the scan data or log file.
    - static_code_analysis: Does a Static code analysis using the scan data or log file.
    """
    console.print(Panel(Markdown(banner)), style="bold green")
    while True:
        try:
            prompt_in = Prompt.ask('> ')
            if prompt_in == 'quit_bot':
                quit()
            elif prompt_in == 'clear_screen':
                clearscr()
                pass
            elif prompt_in == 'bot_banner':
                console.print(Panel(Markdown(banner)), style="bold green")
                pass
            elif prompt_in == 'save_chat':
                save_chat(chat_history)
                pass
            elif prompt_in == 'static_code_analysis':
                print(Markdown('----------'))
                language_used = Prompt.ask('Language Used> ')
                file_path = Prompt.ask('File Path> ')
                print(Markdown('----------'))
                print(static_analysis(language_used, file_path, AI_OPTION))
                pass
            elif prompt_in == 'vuln_analysis':
                print(Markdown('----------'))
                language_used = Prompt.ask('Scan Type > ')
                file_path = Prompt.ask('File Path > ')
                print(Markdown('----------'))
                print(static_analysis(language_used, file_path, AI_OPTION))
                pass
            elif prompt_in == 'contact_dev':
                console.print(Panel(
                    Align.center(
                        Group(Align.center(Markdown(contact_dev))),
                        vertical="middle",
                    ),
                    title="Dev Contact",
                    border_style="red"
                ),
                    style="bold green"
                )
                pass
            elif prompt_in == 'help_menu':
                console.print(Panel(
                    Align.center(
                        Group(Align.center(Markdown(help_menu))),
                        vertical="middle",
                    ),
                    title="Help Menu",
                    border_style="red"
                ),
                    style="bold green"
                )
                pass
            else:
                instructions = """
                You are an helpful cybersecurity assistant and I want you to answer my query and provide output in Markdown: 
                """
                prompt = f"[INST] <<SYS>> {instructions}<</SYS>> Cybersecurity Query: {prompt_in} [/INST]"
                print(Print_AI_out(prompt, AI_OPTION))
                pass
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=6000)  # Run the Flask app on port 5000

from flask import Flask, request, jsonify, send_file
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
app = Flask(__name__)

chat_histories = {}  # Dictionary for session-specific chat histories

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.form.to_dict()
        user_email = request.headers.get('User-Email')
        session_id = request.form.get('session_id')
        prompt_in = data.get('prompt', '')
        # Retrieve or initialize the chat history for the session
        session_chat_history = chat_histories.get(session_id, [])
        session_chat_history.append(f'User: {prompt_in}')

        # Concatenate chat history for context
        chat_context = "\n".join(session_chat_history)
        file_content = None
        file_path = None

        if 'file' in request.files:
            uploaded_file = request.files['file']
            file_path = 'uploads/' + uploaded_file.filename
            uploaded_file.save(file_path)
            with open(file_path, 'r') as file:
                file_content = file.read()

        if prompt_in == 'static_code_analysis' and file_path:
            language_used = data.get('language_used', '')
            result = static_analysis(language_used, file_path, "OPENAI")
            return jsonify({"response": str(result), "FileUploaded": file_path})

        elif prompt_in == 'vuln_analysis' and file_path:
            scan_type = data.get('scan_type', '')
            result = vuln_analysis(scan_type, file_path, "OPENAI")
            return jsonify({"response": str(result), "FileUploaded": file_path})

        if prompt_in == 'quit_bot':
            quit()
        elif prompt_in == 'clear_screen':
            clearscr()
        elif prompt_in == 'bot_banner':
            banner = """
             """
            console.print(Panel(Markdown(banner)), style="bold green")
        elif prompt_in == 'save_chat':
            save_chat(chat_history)
        elif prompt_in == 'contact_dev':
            contact_info = """
            """
            return jsonify({"response": contact_info})
        elif prompt_in == 'help_menu':
            help_info = """
            - clear_screen: Clears the console screen for better readability.
            - quit_bot: This is used to quit the chat application
            - bot_banner: Prints the default bots banner.
            - contact_dev: Provides my contact information.
            - save_chat: Saves the current sessions interactions.
            - help_menu: Lists chatbot commands.
            - vuln_analysis: Does a Vuln analysis using the scan data or log file.
            - static_code_analysis: Does a Static code analysis using the scan data or log file.
            """
            return jsonify({"response": help_info})
        else:
            instructions = "You are a helpful cybersecurity assistant and I want you to answer my query and provide output in Markdown: "
            prompt = f"[INST] <<SYS>> {instructions}<</SYS>> Cybersecurity Query: {prompt_in} [/INST]"
            ai_out = openai_api(chat_context, prompt, file_content, file_path)
            save_data = {
                "UserEmail": user_email,
                "SessionId": session_id,
                "Query": str(prompt),
                "AI Answer": str(ai_out)
            }
            session_chat_history.append(f'AI: {ai_out}')
            chat_histories[session_id] = session_chat_history
            return jsonify({"response": ai_out})

    except Exception as e:
        logging.error(f"Error in /chat endpoint: {e}")
        return jsonify({"error": str(e)}), 500

# Configure logging to print to console
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
logging.getLogger().addHandler(console_handler)
# Load environment variables
chat_history = []

OPENAI_API_KEY = "sk-proj-gQzWO1s8RcfOAU5MjknsT3BlbkFJqjdnxsA4MEFKIZHfleBf"
console = Console()
AI_OPTION = ("OPENAI")
# OpenAI API URL
OPENAI_API_URL = "https://api.openai.com/v1/engines/gpt-4.0/completions"


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
    ... (rest of the instructions)
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
def ai_interpret_file(file_path):
    try:
        # Define the appropriate prompt and parameters for interpreting the file
        prompt = f"Interpret the contents of the file at {file_path}"
        response = openai_api(prompt, file_path)
        return response
    except Exception as e:
        logging.error(f"Error in ai_interpret_file function: {e}")
        return ""

def static_analysis(language_used, file_path, ai_option) -> str:
    global chat_history
    f = open(file_path, "r")
    file_data = f.read()
    f.close()
    instructions = """
    Analyze the given programming file details to identify and clearly report bugs, vulnerabilities, and syntax errors.
    Additionally, search for potential exposure of sensitive information such as API keys, passwords, and usernames. Please provide the result in Markdown.
    """
    data = f"""
        - Programming Language: {language_used}
        - File Name: {file_path}
        - File Data: {file_data}
    """
    prompt = f"[INST] <<SYS>> {instructions}<</SYS>> Data to be analyzed: {data} [/INST]"
    
    if ai_option == "RUNPOD":
        out = llama_api(prompt)  # You may need to replace this with the correct function if needed
    else:
        out = openai_api(prompt)  # Use the openai_api function here
    
    save_data = {
        "Query": str(prompt),
        "AI Answer": str(out)
    }
    chat_history.append(save_data)
    
    # Return the AI's response as plain text
    return str(out)

def openai_api(chat_context, prompt, file_content=None, file_name=None):
    try:
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {OPENAI_API_KEY}'
        }

        # Append chat context to the prompt
        if chat_context:
            prompt = f"{chat_context}\n\n{prompt}"

        # Append file name and content to the prompt if a file is provided
        if file_content and file_name:
            prompt += f"\n\nFile Name: {file_name}\nFile Content:\n{file_content}"

        data = json.dumps({
            "prompt": prompt,
            "max_tokens": 1024
        })

        response = requests.post(OPENAI_API_URL, headers=headers, data=data)
        response.raise_for_status()
        response_json = response.json()
        return response_json.get("choices", [{}])[0].get("text", "")
    except Exception as e:
        logging.error(f"Error in openai_api function: {e}")
        return ""
# Modify the Print_AI_out function to accept a file_path
def Print_AI_out(prompt, ai_option, file_path=None) -> Panel:
    global chat_history
    out = openai_api(prompt, file_path)
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
    
    """
    contact_dev = """
    
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
                scan_type = Prompt.ask('Scan Type > ')
                file_path = Prompt.ask('File Path > ')
                print(Markdown('----------'))
                print(static_analysis(scan_type, file_path, AI_OPTION))
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
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(debug=False,host='0.0.0.0', port=6001, use_reloader=False)

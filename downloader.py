import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import json
from selenium import webdriver

selected_file_path = ""

def load_profile():
    global selected_file_path
    file_path = filedialog.askopenfilename(filetypes=[("SIDE Files", "*.side")])
    if file_path:
        selected_file_path = file_path
        label.config(text=f"Ausgewählte SIDE-Datei: {file_path}")
        with open(file_path, 'r') as file:
            data = json.load(file)
            tests = data['tests']
            if len(tests) > 0:
                commands = tests[0]['commands']
                preview.delete("1.0", tk.END)
                for command in commands:
                    if 'target' in command and 'value' in command:
                        preview.insert(tk.END, f"{command['command']} | {command['target']} | {command['value']}\n")
            else:
                preview.delete("1.0", tk.END)
    else:
        label.config(text="Keine SIDE-Datei ausgewählt")
        preview.delete("1.0", tk.END)

def convert():
    if selected_file_path:
        output_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
        if output_path:
            with open(selected_file_path, 'r') as file:
                data = json.load(file)
                tests = data['tests']
                if len(tests) > 0:
                    commands = tests[0]['commands']
                    translated_commands = []
                    for command in commands:
                        if 'target' in command and 'value' in command:
                            translated_command = translate_command(command)
                            if translated_command:
                                translated_commands.append(translated_command)

                    translated_data = {
                        "commands": translated_commands
                    }

                    with open(output_path, 'w') as output_file:
                        json.dump(translated_data, output_file, indent=4)

                    messagebox.showinfo("Konvertierung abgeschlossen", "Die SIDE-Datei wurde erfolgreich konvertiert.")
                else:
                    messagebox.showwarning("Keine Befehle gefunden", "Die SIDE-Datei enthält keine Befehle.")
        else:
            messagebox.showwarning("Ungültiger Dateipfad", "Es wurde kein gültiger Dateipfad zum Speichern angegeben.")
    else:
        messagebox.showwarning("Keine SIDE-Datei ausgewählt", "Es wurde keine SIDE-Datei ausgewählt.")

def translate_command(command):
    if 'target' in command and 'value' in command:
        translated_command = {
            "command": command['command'],
            "target": translate_xpath(command['target']),
            "value": command['value']
        }
        return translated_command
    return None

def translate_xpath(xpath):
    if xpath.startswith("css="):
        return {"cssSelector": xpath[4:]}
    elif xpath.startswith("xpath="):
        return {"xpath": xpath[6:]}
    else:
        return xpath

def execute_selenium():
    json_file_path = filedialog.askopenfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
    if json_file_path:
        with open(json_file_path, 'r') as json_file:
            data = json.load(json_file)
            commands = data['commands']
            if len(commands) > 0:
                driver = webdriver.Chrome(r'C:\Users\Public\Downloads\chromedriver.exe')
                for command in commands:
                    execute_command(driver, command)
                driver.quit()
                messagebox.showinfo("Selenium-Ausführung abgeschlossen", "Die Selenium-Befehle wurden erfolgreich ausgeführt.")
            else:
                messagebox.showwarning("Keine Befehle gefunden", "Die JSON-Datei enthält keine Befehle.")
    else:
        messagebox.showwarning("Keine JSON-Datei ausgewählt", "Es wurde keine JSON-Datei ausgewählt.")

def execute_command(driver, command):
    if 'command' in command and 'target' in command and 'value' in command:
        if command['command'] == "open":
            driver.get(command['target'])
        elif command['command'] == "click":
            target = command['target']
            if isinstance(target, dict) and 'cssSelector' in target:
                element = driver.find_element_by_css_selector(target['cssSelector'])
                element.click()
            elif isinstance(target, dict) and 'xpath' in target:
                element = driver.find_element_by_xpath(target['xpath'])
                element.click()
        elif command['command'] == "type":
            target = command['target']
            value = command['value']
            if isinstance(target, dict) and 'cssSelector' in target:
                element = driver.find_element_by_css_selector(target['cssSelector'])
                element.send_keys(value)
            elif isinstance(target, dict) and 'xpath' in target:
                element = driver.find_element_by_xpath(target['xpath'])
                element.send_keys(value)

root = tk.Tk()
root.title("SIDE-Konverter")

window_width_cm = 30
window_height_cm = 20
pixels_per_cm = 15

window_width_pixels = int(window_width_cm * pixels_per_cm)
window_height_pixels = int(window_height_cm * pixels_per_cm)

root.geometry(f"{window_width_pixels}x{window_height_pixels}")

button_load_profile = tk.Button(root, text="Profil laden", command=load_profile)
button_load_profile.pack()

label = tk.Label(root, text="Keine SIDE-Datei ausgewählt")
label.pack()

preview = scrolledtext.ScrolledText(root, width=int(window_width_pixels/pixels_per_cm), height=10)
preview.pack()

button_convert = tk.Button(root, text="Konvertierung", command=convert)
button_convert.pack()

button_execute_selenium = tk.Button(root, text="Selenium-Befehle ausführen", command=execute_selenium)
button_execute_selenium.pack()

root.mainloop()

import tkinter as tk
from tkinter import messagebox
import requests
import os
import difflib
import pyttsx3

API_URL = "https://api.dictionaryapi.dev/api/v2/entries/en/"
HISTORY_FILE = "history.txt"


def speak_word():
    word = word_entry.get().strip()

    if word == "":
        messagebox.showwarning(
            "Speech",
            "Please enter a word first."
        )
        return

    try:
        speech = pyttsx3.init()
        speech.setProperty("rate", 145)
        speech.setProperty("volume", 1.0)

        speech.say(word)
        speech.runAndWait()
        speech.stop()

    except Exception as e:
        messagebox.showerror(
            "Speech Error",
            "Unable to pronounce the word.\n\n" + str(e)
        )


def save_history(word):
    try:
        with open(
            HISTORY_FILE,
            "a",
            encoding="utf-8"
        ) as file:
            file.write(word + "\n")

    except Exception as e:
        print("History Error:", e)


def clear_result():
    word_label.config(text="")
    pronunciation_value.config(text="")
    meaning_value.config(text="")
    synonyms_value.config(text="")
    antonyms_value.config(text="")
    example_value.config(text="")

    suggestion_title.pack_forget()
    suggestion_value.pack_forget()


def show_history():
    history_window = tk.Toplevel(root)
    history_window.title("Search History")
    history_window.geometry("450x450")
    history_window.config(bg="#F4F6F8")

    title = tk.Label(
        history_window,
        text="Search History",
        font=("Arial", 20, "bold"),
        bg="#F4F6F8",
        fg="#1F2937"
    )
    title.pack(pady=15)

    history_box = tk.Text(
        history_window,
        width=45,
        height=20,
        font=("Arial", 12),
        bg="white",
        fg="#333333"
    )
    history_box.pack(
        padx=15,
        pady=10
    )

    if not os.path.exists(HISTORY_FILE):
        history_box.insert(
            tk.END,
            "No search history available."
        )
        history_box.config(state="disabled")
        return

    try:
        with open(
            HISTORY_FILE,
            "r",
            encoding="utf-8"
        ) as file:
            history = file.readlines()

        if len(history) == 0:
            history_box.insert(
                tk.END,
                "No search history available."
            )
        else:
            for word in history:
                history_box.insert(
                    tk.END,
                    "• " + word
                )

        history_box.config(
            state="disabled"
        )

    except Exception:
        history_box.insert(
            tk.END,
            "Unable to read history."
        )
        history_box.config(
            state="disabled"
        )


def clear_history():
    if not os.path.exists(HISTORY_FILE):
        messagebox.showinfo(
            "History",
            "No search history found."
        )
        return

    result = messagebox.askyesno(
        "Clear History",
        "Are you sure you want to delete search history?"
    )

    if result:
        try:
            os.remove(HISTORY_FILE)

            messagebox.showinfo(
                "History",
                "Search history cleared successfully."
            )

        except Exception:
            messagebox.showerror(
                "Error",
                "Unable to clear history."
            )


def get_local_suggestion(word):
    common_words = [
        "apple",
        "application",
        "beautiful",
        "computer",
        "dictionary",
        "development",
        "education",
        "example",
        "friend",
        "future",
        "good",
        "happy",
        "hello",
        "house",
        "important",
        "knowledge",
        "language",
        "learning",
        "morning",
        "programming",
        "python",
        "school",
        "student",
        "technology",
        "university",
        "welcome",
        "world",
        "write",
        "writing"
    ]

    matches = difflib.get_close_matches(
        word,
        common_words,
        n=1,
        cutoff=0.6
    )

    if matches:
        return matches[0]

    return None


def search_word():
    word = word_entry.get().strip().lower()

    if word == "":
        messagebox.showwarning(
            "Input Error",
            "Please enter an English word."
        )
        return

    clear_result()

    try:
        response = requests.get(
            API_URL + word,
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()

            actual_word = data[0].get(
                "word",
                word
            )

            word_label.config(
                text=actual_word.upper()
            )

            pronunciation = "Not available"

            for phonetic in data[0].get(
                "phonetics",
                []
            ):
                if phonetic.get("text"):
                    pronunciation = phonetic["text"]
                    break

            pronunciation_value.config(
                text=pronunciation
            )

            meanings = data[0].get(
                "meanings",
                []
            )

            meaning_text = ""
            synonyms_list = []
            antonyms_list = []
            examples_list = []

            for meaning in meanings:
                definitions = meaning.get(
                    "definitions",
                    []
                )

                for definition in definitions:
                    definition_text = definition.get("definition")

                    if definition_text:
                        meaning_text += "• " + definition_text + "\n\n"

                    example = definition.get("example")
                    if example and example not in examples_list:
                        examples_list.append(example)

                    for synonym in definition.get("synonyms", []):
                        if synonym not in synonyms_list:
                            synonyms_list.append(synonym)

                    for antonym in definition.get("antonyms", []):
                        if antonym not in antonyms_list:
                            antonyms_list.append(antonym)

                for synonym in meaning.get("synonyms", []):
                    if synonym not in synonyms_list:
                        synonyms_list.append(synonym)

                for antonym in meaning.get("antonyms", []):
                    if antonym not in antonyms_list:
                        antonyms_list.append(antonym)

            if meaning_text:
                meaning_value.config(
                    text=meaning_text.strip()
                )
            else:
                meaning_value.config(
                    text="Not available"
                )

            if synonyms_list:
                synonyms_value.config(
                    text=", ".join(synonyms_list)
                )
            else:
                synonyms_value.config(
                    text="Not available"
                )

            if antonyms_list:
                antonyms_value.config(
                    text=", ".join(antonyms_list)
                )
            else:
                antonyms_value.config(
                    text="Not available"
                )

            if examples_list:
                example_text = ""
                for example in examples_list:
                    example_text += "• " + example + "\n\n"
                example_value.config(
                    text=example_text.strip()
                )
            else:
                example_value.config(
                    text="Not available"
                )

            save_history(word)
            suggestion_title.pack_forget()
            suggestion_value.pack_forget()

        else:
            suggestion = get_local_suggestion(word)

            if suggestion:
                suggestion_title.pack(pady=(10, 5))
                suggestion_value.config(text="Did you mean: " + suggestion + "?")
                suggestion_value.pack(pady=(0, 10))
            else:
                messagebox.showerror(
                    "Word Not Found",
                    "Sorry, this word was not found."
                )

    except requests.exceptions.Timeout:
        messagebox.showerror(
            "Connection Error",
            "The request timed out.\nPlease check your internet connection."
        )

    except requests.exceptions.ConnectionError:
        messagebox.showerror(
            "Connection Error",
            "Unable to connect to the Dictionary API.\nPlease check your internet connection."
        )

    except Exception as e:
        messagebox.showerror(
            "Error",
            "Something went wrong.\n\n" + str(e)
        )


def enter_search(event):
    search_word()


root = tk.Tk()
root.title("Smart Dictionary")
root.geometry("800x750")
root.config(bg="#EEF2FF")
root.resizable(False, False)

header = tk.Frame(
    root,
    bg="#4F46E5",
    height=100
)
header.pack(fill="x")
header.pack_propagate(False)

title = tk.Label(
    header,
    text="Smart Dictionary",
    font=("Arial", 28, "bold"),
    bg="#4F46E5",
    fg="white"
)
title.pack(pady=25)

subtitle = tk.Label(
    root,
    text="Search any English word and explore its meaning",
    font=("Arial", 13),
    bg="#EEF2FF",
    fg="#4B5563"
)
subtitle.pack(pady=(20, 10))

search_frame = tk.Frame(
    root,
    bg="#EEF2FF"
)
search_frame.pack(pady=10)

word_entry = tk.Entry(
    search_frame,
    width=35,
    font=("Arial", 15),
    bd=2,
    relief="solid"
)
word_entry.grid(row=0, column=0, padx=5)

search_button = tk.Button(
    search_frame,
    text="Search",
    font=("Arial", 12, "bold"),
    bg="#4F46E5",
    fg="white",
    activebackground="#3730A3",
    activeforeground="white",
    padx=15,
    pady=8,
    bd=0,
    cursor="hand2",
    command=search_word
)
search_button.grid(row=0, column=1, padx=5)

clear_button = tk.Button(
    search_frame,
    text="Clear",
    font=("Arial", 12, "bold"),
    bg="#EF4444",
    fg="white",
    activebackground="#DC2626",
    activeforeground="white",
    padx=15,
    pady=8,
    bd=0,
    cursor="hand2",
    command=clear_result
)
clear_button.grid(row=0, column=2, padx=5)

history_frame = tk.Frame(
    root,
    bg="#EEF2FF"
)
history_frame.pack(pady=5)

history_button = tk.Button(
    history_frame,
    text="Search History",
    font=("Arial", 11, "bold"),
    bg="#10B981",
    fg="white",
    padx=15,
    pady=6,
    bd=0,
    cursor="hand2",
    command=show_history
)
history_button.grid(row=0, column=0, padx=5)

clear_history_button = tk.Button(
    history_frame,
    text="Clear History",
    font=("Arial", 11, "bold"),
    bg="#F59E0B",
    fg="white",
    padx=15,
    pady=6,
    bd=0,
    cursor="hand2",
    command=clear_history
)
clear_history_button.grid(row=0, column=1, padx=5)

result_frame = tk.Frame(
    root,
    bg="white",
    bd=2,
    relief="groove"
)
result_frame.pack(fill="both", expand=True, padx=35, pady=15)

word_label = tk.Label(
    result_frame,
    text="",
    font=("Arial", 25, "bold"),
    bg="white",
    fg="#4F46E5"
)
word_label.pack(pady=(15, 5))

pronunciation_title = tk.Label(
    result_frame,
    text="Pronunciation",
    font=("Arial", 13, "bold"),
    bg="white",
    fg="#374151"
)
pronunciation_title.pack()

pronunciation_frame = tk.Frame(
    result_frame,
    bg="white"
)
pronunciation_frame.pack(pady=(0, 10))

pronunciation_value = tk.Label(
    pronunciation_frame,
    text="",
    font=("Arial", 14, "bold"),
    bg="white",
    fg="#4F46E5"
)
pronunciation_value.pack(side="left", padx=5)

speak_button = tk.Button(
    pronunciation_frame,
    text="🔊",
    font=("Arial", 14, "bold"),
    bg="#8B5CF6",
    fg="white",
    activebackground="#7C3AED",
    activeforeground="white",
    width=4,
    height=1,
    bd=0,
    cursor="hand2",
    command=speak_word
)
speak_button.pack(side="left", padx=5)

meaning_title = tk.Label(
    result_frame,
    text="Meaning",
    font=("Arial", 13, "bold"),
    bg="white",
    fg="#111827"
)
meaning_title.pack(anchor="w", padx=20)

meaning_value = tk.Label(
    result_frame,
    text="",
    font=("Arial", 11),
    bg="white",
    fg="#374151",
    justify="left",
    anchor="w",
    wraplength=700
)
meaning_value.pack(anchor="w", padx=20, pady=(5, 10))

synonyms_title = tk.Label(
    result_frame,
    text="Synonyms",
    font=("Arial", 13, "bold"),
    bg="white",
    fg="#111827"
)
synonyms_title.pack(anchor="w", padx=20)

synonyms_value = tk.Label(
    result_frame,
    text="",
    font=("Arial", 11),
    bg="white",
    fg="#374151",
    justify="left",
    anchor="w",
    wraplength=700
)
synonyms_value.pack(anchor="w", padx=20, pady=(5, 10))

antonyms_title = tk.Label(
    result_frame,
    text="Antonyms",
    font=("Arial", 13, "bold"),
    bg="white",
    fg="#111827"
)
antonyms_title.pack(anchor="w", padx=20)

antonyms_value = tk.Label(
    result_frame,
    text="",
    font=("Arial", 11),
    bg="white",
    fg="#374151",
    justify="left",
    anchor="w",
    wraplength=700
)
antonyms_value.pack(anchor="w", padx=20, pady=(5, 10))

example_title = tk.Label(
    result_frame,
    text="Examples",
    font=("Arial", 13, "bold"),
    bg="white",
    fg="#111827"
)
example_title.pack(anchor="w", padx=20)

example_value = tk.Label(
    result_frame,
    text="",
    font=("Arial", 11),
    bg="white",
    fg="#374151",
    justify="left",
    anchor="w",
    wraplength=700
)
example_value.pack(anchor="w", padx=20, pady=(5, 10))

suggestion_title = tk.Label(
    result_frame,
    text="Spelling Suggestion",
    font=("Arial", 13, "bold"),
    bg="white",
    fg="#F59E0B"
)

suggestion_value = tk.Label(
    result_frame,
    text="",
    font=("Arial", 12),
    bg="white",
    fg="#D97706"
)

word_entry.bind("<Return>", enter_search)

root.mainloop()
import tkinter as tk
from tkinter import messagebox
import requests
import threading
import os
from datetime import datetime
import pyttsx3




API_URL = "https://api.dictionaryapi.dev/api/v2/entries/en/"
HISTORY_FILE = "history.txt"


OFFLINE_DATA = {
    "beautiful": {
        "meaning": "Pleasing to the senses or mind; attractive and lovely.",
        "synonyms": ["attractive", "pretty", "lovely", "gorgeous", "charming"],
        "antonyms": ["ugly", "unattractive"],
        "example": "She has a beautiful smile.",
        "pronunciation": "/ˈbjuːtɪfəl/"
    },
    "happy": {
        "meaning": "Feeling or showing pleasure and contentment.",
        "synonyms": ["joyful", "cheerful", "glad", "delighted"],
        "antonyms": ["sad", "unhappy"],
        "example": "She was happy to see her friends.",
        "pronunciation": "/ˈhæpi/"
    },
    "sad": {
        "meaning": "Feeling unhappy or sorrowful.",
        "synonyms": ["unhappy", "sorrowful", "upset", "depressed"],
        "antonyms": ["happy", "cheerful"],
        "example": "He felt sad after hearing the news.",
        "pronunciation": "/sæd/"
    },
    "good": {
        "meaning": "Having desirable or positive qualities.",
        "synonyms": ["nice", "excellent", "great", "fine"],
        "antonyms": ["bad", "poor"],
        "example": "She is a good student.",
        "pronunciation": "/ɡʊd/"
    },
    "bad": {
        "meaning": "Not good; unpleasant or harmful.",
        "synonyms": ["poor", "awful", "terrible", "wrong"],
        "antonyms": ["good", "excellent"],
        "example": "The weather was bad yesterday.",
        "pronunciation": "/bæd/"
    },
    "beautiful": {
        "meaning": "Pleasing to the senses or mind; attractive and lovely.",
        "synonyms": ["attractive", "pretty", "lovely", "gorgeous", "charming"],
        "antonyms": ["ugly", "unattractive"],
        "example": "She has a beautiful smile.",
        "pronunciation": "/ˈbjuːtɪfəl/"
    },
    "beautifully": {
        "meaning": "In a very attractive or pleasing way.",
        "synonyms": ["attractively", "wonderfully", "elegantly"],
        "antonyms": [],
        "example": "She sings beautifully.",
        "pronunciation": "/ˈbjuːtɪfəli/"
    },
    "important": {
        "meaning": "Having great value or significance.",
        "synonyms": ["valuable", "significant", "essential"],
        "antonyms": ["unimportant", "insignificant"],
        "example": "This is an important decision.",
        "pronunciation": "/ɪmˈpɔːrtənt/"
    }
}

root = tk.Tk()

root.title("English Dictionary Application")

root.geometry("950x750")

root.minsize(750, 600)

root.configure(bg="#EEF2FF")




def speak_word():

    word = word_entry.get().strip()

    if not word:

        messagebox.showwarning(
            "No Word",
            "Please enter a word first."
        )

        return

    # Run speech in background
    threading.Thread(
        target=speak_text,
        args=(word,),
        daemon=True
    ).start()


def speak_text(word):

    try:

        engine = pyttsx3.init()

        engine.setProperty(
            "rate",
            140
        )

        engine.setProperty(
            "volume",
            1.0
        )

        # Try to select English voice
        voices = engine.getProperty("voices")

        for voice in voices:

            voice_name = voice.name.lower()

            if (
                "english" in voice_name
                or "zira" in voice_name
                or "david" in voice_name
            ):

                engine.setProperty(
                    "voice",
                    voice.id
                )

                break

        engine.say(word)

        engine.runAndWait()

        engine.stop()

    except Exception as e:

        root.after(
            0,
            lambda: messagebox.showerror(
                "Speech Error",
                "Unable to play pronunciation.\n\n"
                "Please check your Windows text-to-speech settings."
            )
        )




def search_word():

    word = word_entry.get().strip().lower()

    if not word:

        messagebox.showwarning(
            "Input Required",
            "Please enter a word."
        )

        return

    # Validate word
    if not word.replace("-", "").isalpha():

        messagebox.showwarning(
            "Invalid Input",
            "Please enter a valid English word."
        )

        return

    search_btn.config(
        state="disabled"
    )

    status_label.config(
        text="Searching... Please wait."
    )

    result_box.config(
        state="normal"
    )

    result_box.delete(
        "1.0",
        tk.END
    )

    result_box.insert(
        tk.END,
        "Searching for '" + word + "'...\n\n",
        "loading"
    )

    result_box.config(
        state="disabled"
    )

    threading.Thread(
        target=fetch_word,
        args=(word,),
        daemon=True
    ).start()



def fetch_word(word):

    try:

        response = requests.get(
            API_URL + word,
            timeout=(10, 25)
        )

        if response.status_code == 200:

            data = response.json()

            root.after(
                0,
                lambda: display_api_result(
                    data,
                    word
                )
            )

        else:

            if word in OFFLINE_DATA:

                root.after(
                    0,
                    lambda: display_offline_result(
                        word,
                        "Online API unavailable. Showing offline result."
                    )
                )

            else:

                root.after(
                    0,
                    lambda: show_not_found(word)
                )

    except requests.exceptions.Timeout:

        if word in OFFLINE_DATA:

            root.after(
                0,
                lambda: display_offline_result(
                    word,
                    "Online API timed out. Showing offline result."
                )
            )

        else:

            root.after(
                0,
                lambda: show_api_error(
                    "The dictionary API took too long to respond.\n\n"
                    "Please check your internet connection and try again."
                )
            )

    except requests.exceptions.ConnectionError:

        if word in OFFLINE_DATA:

            root.after(
                0,
                lambda: display_offline_result(
                    word,
                    "Internet connection unavailable. Showing offline result."
                )
            )

        else:

            root.after(
                0,
                lambda: show_api_error(
                    "Unable to connect to the dictionary API.\n\n"
                    "Please check your internet connection."
                )
            )

    except Exception:

        root.after(
            0,
            lambda: show_api_error(
                "Something went wrong while searching."
            )
        )


# =========================================================
# DISPLAY API RESULT
# =========================================================

def display_api_result(data, word):

    result_box.config(
        state="normal"
    )

    result_box.delete(
        "1.0",
        tk.END
    )

    # WORD
    result_box.insert(
        tk.END,
        word.upper() + "\n",
        "title"
    )

    # PRONUNCIATION
    pronunciation = get_pronunciation(data)

    result_box.insert(
        tk.END,
        "🔊 Pronunciation: "
        + pronunciation
        + "\n\n",
        "pronunciation"
    )

    # MEANINGS
    for entry in data:

        meanings = entry.get(
            "meanings",
            []
        )

        for meaning in meanings:

            part_of_speech = meaning.get(
                "partOfSpeech",
                ""
            )

            if part_of_speech:

                result_box.insert(
                    tk.END,
                    part_of_speech.capitalize()
                    + "\n",
                    "heading"
                )

            definitions = meaning.get(
                "definitions",
                []
            )

            # Show maximum 5 definitions
            for i, definition in enumerate(
                definitions[:5],
                1
            ):

                text = definition.get(
                    "definition",
                    "No definition available."
                )

                result_box.insert(
                    tk.END,
                    f"{i}. {text}\n",
                    "normal"
                )

                example = definition.get(
                    "example"
                )

                if example:

                    result_box.insert(
                        tk.END,
                        "   Example: "
                        + example
                        + "\n",
                        "example"
                    )

            # SYNONYMS
            synonyms = meaning.get(
                "synonyms",
                []
            )

            if synonyms:

                result_box.insert(
                    tk.END,
                    "\nSynonyms: "
                    + ", ".join(
                        synonyms[:10]
                    )
                    + "\n",
                    "synonym"
                )

            # ANTONYMS
            antonyms = meaning.get(
                "antonyms",
                []
            )

            if antonyms:

                result_box.insert(
                    tk.END,
                    "Antonyms: "
                    + ", ".join(
                        antonyms[:10]
                    )
                    + "\n",
                    "antonym"
                )

            result_box.insert(
                tk.END,
                "\n"
            )

    result_box.config(
        state="disabled"
    )

    save_history(word)

    status_label.config(
        text="✓ Word found successfully!"
    )

    search_btn.config(
        state="normal"
    )


# =========================================================
# GET PRONUNCIATION
# =========================================================

def get_pronunciation(data):

    for entry in data:

        if entry.get("phonetic"):

            return entry["phonetic"]

        for phonetic in entry.get(
            "phonetics",
            []
        ):

            if phonetic.get("text"):

                return phonetic["text"]

    return "Not available"


# =========================================================
# OFFLINE RESULT
# =========================================================

def display_offline_result(
    word,
    message="Offline dictionary result"
):

    data = OFFLINE_DATA[word]

    result_box.config(
        state="normal"
    )

    result_box.delete(
        "1.0",
        tk.END
    )

    # WORD
    result_box.insert(
        tk.END,
        word.upper() + "\n",
        "title"
    )

    result_box.insert(
        tk.END,
        "📌 " + message + "\n\n",
        "offline"
    )

    # PRONUNCIATION
    result_box.insert(
        tk.END,
        "🔊 Pronunciation\n",
        "heading"
    )

    result_box.insert(
        tk.END,
        data["pronunciation"]
        + "\n\n",
        "pronunciation"
    )

    # MEANING
    result_box.insert(
        tk.END,
        "📖 Meaning\n",
        "heading"
    )

    result_box.insert(
        tk.END,
        data["meaning"]
        + "\n\n",
        "normal"
    )

    # EXAMPLE
    result_box.insert(
        tk.END,
        "💡 Example\n",
        "heading"
    )

    result_box.insert(
        tk.END,
        data["example"]
        + "\n\n",
        "example"
    )

    # SYNONYMS
    result_box.insert(
        tk.END,
        "✓ Synonyms\n",
        "heading"
    )

    result_box.insert(
        tk.END,
        ", ".join(
            data["synonyms"]
        )
        + "\n\n",
        "synonym"
    )

    # ANTONYMS
    result_box.insert(
        tk.END,
        "✗ Antonyms\n",
        "heading"
    )

    if data["antonyms"]:

        result_box.insert(
            tk.END,
            ", ".join(
                data["antonyms"]
            ),
            "antonym"
        )

    else:

        result_box.insert(
            tk.END,
            "No antonyms available.",
            "normal"
        )

    result_box.config(
        state="disabled"
    )

    save_history(word)

    status_label.config(
        text="✓ Offline result displayed"
    )

    search_btn.config(
        state="normal"
    )


# =========================================================
# WORD NOT FOUND
# =========================================================

def show_not_found(word):

    result_box.config(
        state="normal"
    )

    result_box.delete(
        "1.0",
        tk.END
    )

    result_box.insert(
        tk.END,
        "Word Not Found\n\n",
        "error"
    )

    result_box.insert(
        tk.END,
        "No exact result was found for: ",
        "normal"
    )

    result_box.insert(
        tk.END,
        word,
        "suggestion"
    )

    result_box.insert(
        tk.END,
        "\n\nPlease check the spelling and try again.",
        "normal"
    )

    result_box.config(
        state="disabled"
    )

    status_label.config(
        text="Word not found."
    )

    search_btn.config(
        state="normal"
    )


# =========================================================
# API ERROR
# =========================================================

def show_api_error(message):

    result_box.config(
        state="normal"
    )

    result_box.delete(
        "1.0",
        tk.END
    )

    result_box.insert(
        tk.END,
        "⚠ Connection Problem\n\n",
        "error"
    )

    result_box.insert(
        tk.END,
        message,
        "normal"
    )

    result_box.insert(
        tk.END,
        "\n\nTry searching again after a few seconds.",
        "example"
    )

    result_box.config(
        state="disabled"
    )

    status_label.config(
        text="Connection problem."
    )

    search_btn.config(
        state="normal"
    )


# =========================================================
# SAVE HISTORY
# =========================================================

def save_history(word):

    try:

        with open(
            HISTORY_FILE,
            "a",
            encoding="utf-8"
        ) as file:

            date_time = datetime.now().strftime(
                "%d-%m-%Y %I:%M %p"
            )

            file.write(
                f"{date_time} | {word}\n"
            )

    except Exception:
        pass


# =========================================================
# SHOW HISTORY
# =========================================================

def show_history():

    history_window = tk.Toplevel(
        root
    )

    history_window.title(
        "Search History"
    )

    history_window.geometry(
        "550x500"
    )

    history_window.configure(
        bg="#EEF2FF"
    )

    tk.Label(
        history_window,
        text="🕒 Search History",
        font=("Arial", 22, "bold"),
        bg="#EEF2FF",
        fg="#4338CA"
    ).pack(
        pady=20
    )

    frame = tk.Frame(
        history_window,
        bg="white"
    )

    frame.pack(
        padx=25,
        pady=5,
        fill="both",
        expand=True
    )

    scrollbar = tk.Scrollbar(
        frame
    )

    scrollbar.pack(
        side="right",
        fill="y"
    )

    history_box = tk.Listbox(
        frame,
        font=("Arial", 12),
        yscrollcommand=scrollbar.set
    )

    history_box.pack(
        fill="both",
        expand=True
    )

    scrollbar.config(
        command=history_box.yview
    )

    if os.path.exists(
        HISTORY_FILE
    ):

        with open(
            HISTORY_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            history = file.readlines()

        for item in reversed(history):

            history_box.insert(
                tk.END,
                item.strip()
            )

    else:

        history_box.insert(
            tk.END,
            "No search history available."
        )


# =========================================================
# CLEAR
# =========================================================

def clear_results():

    word_entry.delete(
        0,
        tk.END
    )

    result_box.config(
        state="normal"
    )

    result_box.delete(
        "1.0",
        tk.END
    )

    result_box.insert(
        tk.END,
        "📖 English Dictionary\n\n",
        "title"
    )

    result_box.insert(
        tk.END,
        "Enter an English word above to search for its:\n\n",
        "normal"
    )

    result_box.insert(
        tk.END,
        "• Meaning\n"
        "• Pronunciation\n"
        "• Synonyms\n"
        "• Antonyms\n"
        "• Example sentences\n\n",
        "normal"
    )

    result_box.insert(
        tk.END,
        "Press Enter or click Search to begin.",
        "example"
    )

    result_box.config(
        state="disabled"
    )

    status_label.config(
        text="Ready - Enter a word to search"
    )


# =========================================================
# HEADER
# =========================================================

header = tk.Frame(
    root,
    bg="#4F46E5"
)

header.pack(
    fill="x"
)

tk.Label(
    header,
    text="📖 English Dictionary",
    font=("Arial", 28, "bold"),
    bg="#4F46E5",
    fg="white"
).pack(
    pady=(18, 2)
)

tk.Label(
    header,
    text="Search meanings, pronunciation, synonyms & examples",
    font=("Arial", 11),
    bg="#4F46E5",
    fg="#E0E7FF"
).pack(
    pady=(0, 12)
)


# =========================================================
# SEARCH AREA
# =========================================================

search_frame = tk.Frame(
    root,
    bg="#EEF2FF"
)

search_frame.pack(
    pady=25
)


# WORD ENTRY

word_entry = tk.Entry(
    search_frame,
    font=("Arial", 16),
    width=30,
    relief="solid",
    bd=1
)

word_entry.grid(
    row=0,
    column=0,
    padx=5
)


# ENTER KEY

word_entry.bind(
    "<Return>",
    lambda event: search_word()
)


# SEARCH BUTTON

search_btn = tk.Button(
    search_frame,
    text="🔍 Search",
    font=("Arial", 12, "bold"),
    bg="#4F46E5",
    fg="white",
    activebackground="#3730A3",
    activeforeground="white",
    padx=18,
    pady=8,
    relief="flat",
    command=search_word
)

search_btn.grid(
    row=0,
    column=1,
    padx=5
)


# SPEAK BUTTON

speak_btn = tk.Button(
    search_frame,
    text="🔊 Speak",
    font=("Arial", 12, "bold"),
    bg="#059669",
    fg="white",
    activebackground="#047857",
    activeforeground="white",
    padx=18,
    pady=8,
    relief="flat",
    command=speak_word
)

speak_btn.grid(
    row=0,
    column=2,
    padx=5
)


# HISTORY BUTTON

history_btn = tk.Button(
    search_frame,
    text="🕒 History",
    font=("Arial", 12, "bold"),
    bg="#7C3AED",
    fg="white",
    padx=15,
    pady=8,
    relief="flat",
    command=show_history
)

history_btn.grid(
    row=0,
    column=3,
    padx=5
)


# CLEAR BUTTON

clear_btn = tk.Button(
    search_frame,
    text="Clear",
    font=("Arial", 12),
    bg="#E5E7EB",
    fg="#111827",
    padx=18,
    pady=8,
    relief="flat",
    command=clear_results
)

clear_btn.grid(
    row=0,
    column=4,
    padx=5
)


# =========================================================
# RESULT AREA
# =========================================================

result_frame = tk.Frame(
    root,
    bg="white",
    bd=1,
    relief="solid"
)

result_frame.pack(
    padx=35,
    pady=5,
    fill="both",
    expand=True
)


# SCROLLBAR

scrollbar = tk.Scrollbar(
    result_frame
)

scrollbar.pack(
    side="right",
    fill="y"
)


# RESULT TEXT BOX

result_box = tk.Text(
    result_frame,
    font=("Arial", 12),
    wrap="word",
    padx=22,
    pady=18,
    bg="white",
    fg="#1F2937",
    yscrollcommand=scrollbar.set
)

result_box.pack(
    fill="both",
    expand=True
)


scrollbar.config(
    command=result_box.yview
)


# =========================================================
# TEXT STYLES
# =========================================================

result_box.tag_config(
    "title",
    font=("Arial", 24, "bold"),
    foreground="#4338CA"
)

result_box.tag_config(
    "heading",
    font=("Arial", 15, "bold"),
    foreground="#7C3AED"
)

result_box.tag_config(
    "pronunciation",
    font=("Arial", 13, "bold"),
    foreground="#059669"
)

result_box.tag_config(
    "example",
    font=("Arial", 11, "italic"),
    foreground="#6B7280"
)

result_box.tag_config(
    "synonym",
    font=("Arial", 11, "bold"),
    foreground="#2563EB"
)

result_box.tag_config(
    "antonym",
    font=("Arial", 11, "bold"),
    foreground="#DC2626"
)

result_box.tag_config(
    "suggestion",
    font=("Arial", 13, "bold"),
    foreground="#4F46E5"
)

result_box.tag_config(
    "error",
    font=("Arial", 20, "bold"),
    foreground="#DC2626"
)

result_box.tag_config(
    "offline",
    font=("Arial", 11, "italic"),
    foreground="#D97706"
)

result_box.tag_config(
    "loading",
    font=("Arial", 16, "bold"),
    foreground="#4F46E5"
)

result_box.tag_config(
    "normal",
    font=("Arial", 12),
    foreground="#1F2937"
)


# =========================================================
# STATUS
# =========================================================

status_label = tk.Label(
    root,
    text="Ready - Enter a word to search",
    font=("Arial", 10),
    bg="#EEF2FF",
    fg="#6B7280"
)

status_label.pack(
    pady=10
)


# =========================================================
# START SCREEN
# =========================================================

clear_results()


# =========================================================
# RUN APPLICATION
# =========================================================

root.mainloop()
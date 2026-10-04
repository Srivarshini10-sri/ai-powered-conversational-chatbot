
import tkinter as tk
from tkinter import scrolledtext
import requests
import threading
import json

# =============== SETTINGS ===============

MODEL = "llama3.2"
API_URL = "http://127.0.0.1:11434/api/chat"

BG = "#0F172A"
SIDEBAR = "#111827"
PANEL = "#1E293B"
BLUE = "#2563EB"
WHITE = "#F8FAFC"
MUTED = "#94A3B8"
ACCENT = "#60A5FA"

SYSTEM_PROMPT = (
    "You are a helpful AI assistant. "
    "Answer clearly using simple English. "
    "Use headings and bullet points when useful. "
    "Keep answers concise unless the user asks for details."
)

history = []
busy = False
message_widgets = []

# =============== MAIN WINDOW ===============

root = tk.Tk()
root.title("AI Chatbot")
root.geometry("1000x700")
root.minsize(650, 480)
root.configure(bg=BG)


# =============== CHAT DISPLAY ===============

def scroll_to_bottom():
    root.update_idletasks()
    chat_canvas.configure(
        scrollregion=chat_canvas.bbox("all")
    )
    chat_canvas.yview_moveto(1.0)


def copy_answer(text):
    root.clipboard_clear()
    root.clipboard_append(text)
    status_label.config(text="Answer copied!")


def add_message(sender, message, streaming=False):
    is_user = sender == "You"
    bubble_color = BLUE if is_user else PANEL

    row = tk.Frame(chat_inner, bg=BG)
    row.pack(fill="x", padx=18, pady=8)

    bubble = tk.Frame(row, bg=bubble_color)
    bubble.pack(
        side="right" if is_user else "left",
        padx=(50, 0) if is_user else (0, 50)
    )

    name_label = tk.Label(
        bubble,
        text=sender,
        font=("Segoe UI", 9, "bold"),
        bg=bubble_color,
        fg=WHITE if is_user else ACCENT,
        anchor="w"
    )
    name_label.pack(fill="x", padx=14, pady=(10, 2))

    answer_label = tk.Label(
        bubble,
        text=message,
        font=("Segoe UI", 11),
        bg=bubble_color,
        fg=WHITE,
        justify="left",
        anchor="w",
        wraplength=520
    )
    answer_label.pack(fill="x", padx=14, pady=(2, 12))

    message_widgets.append((answer_label, is_user))

    if not is_user and not streaming:
        add_copy_button(bubble, message)

    scroll_to_bottom()
    return answer_label


def add_copy_button(bubble, message):
    button = tk.Button(
        bubble,
        text="Copy answer",
        command=lambda text=message: copy_answer(text),
        font=("Segoe UI", 9),
        bg=PANEL,
        fg=MUTED,
        activebackground=PANEL,
        activeforeground=WHITE,
        relief="flat",
        bd=0,
        cursor="hand2"
    )
    button.pack(anchor="w", padx=10, pady=(0, 7))


def create_streaming_message():
    return add_message("Llama", "", streaming=True)


def update_streaming_text(label, text):
    label.config(text=text)

    # Adjust wrapping when the window is resized.
    width = max(220, chat_canvas.winfo_width() - 190)
    label.config(wraplength=width)

    scroll_to_bottom()


# =============== SEND MESSAGE ===============

def send_message(event=None):
    global busy

    # Prevent duplicate sends while the AI is working.
    if busy:
        return "break"

    # Text widgets require "1.0" and "end-1c".
    message = input_box.get("1.0", "end-1c").strip()

    if not message:
        return "break"

    # Clear the box immediately after reading the message.
    input_box.delete("1.0", tk.END)

    add_message("You", message)
    history.append({
        "role": "user",
        "content": message
    })

    # Create the AI response bubble before starting the request.
    answer_label = create_streaming_message()

    busy = True
    send_button.config(state="disabled", text="Sending...")
    new_button.config(state="disabled")
    status_label.config(text="Llama is thinking...")

    # Network work runs in a background thread.
    threading.Thread(
        target=ask_ollama,
        args=(history.copy(), answer_label),
        daemon=True
    ).start()

    input_box.focus_set()
    return "break"


def ask_ollama(messages, answer_label):
    answer = ""

    try:
        with requests.post(
            API_URL,
            json={
                "model": MODEL,
                "messages": messages,
                "stream": True
            },
            stream=True,
            timeout=(10, 300)
        ) as response:

            response.raise_for_status()

            for line in response.iter_lines():
                if not line:
                    continue

                data = json.loads(line.decode("utf-8"))

                piece = data.get("message", {}).get("content", "")

                if piece:
                    answer += piece

                    # Schedule UI updates on the Tkinter main thread.
                    root.after(
                        0,
                        update_streaming_text,
                        answer_label,
                        answer
                    )

                if data.get("done", False):
                    break

        if not answer:
            raise RuntimeError(
                "Ollama returned an empty response."
            )

        root.after(
            0,
            finish_response,
            answer_label,
            answer,
            None
        )

    except Exception as error:
        root.after(
            0,
            finish_response,
            answer_label,
            answer,
            str(error)
        )


def finish_response(answer_label, answer, error):
    global busy

    if error:
        answer_label.config(
            text=(
                "Unable to get a response from Ollama.\n\n"
                "Check that Ollama is running and the model "
                "is available.\n\nError: " + error
            )
        )

        if history and history[-1]["role"] == "user":
            history.pop()

        status_label.config(text="Request failed. Try again.")

    else:
        history.append({
            "role": "assistant",
            "content": answer
        })

        add_copy_button(answer_label.master, answer)
        status_label.config(text="Ready to chat")

    busy = False
    send_button.config(state="normal", text="Send")
    new_button.config(state="normal")
    input_box.focus_set()
    scroll_to_bottom()


# =============== NEW CHAT ===============

def new_chat():
    if busy:
        return

    history.clear()
    history.append({
        "role": "system",
        "content": SYSTEM_PROMPT
    })

    for widget in chat_inner.winfo_children():
        widget.destroy()

    message_widgets.clear()

    add_message(
        "Llama",
        "Hello! Welcome to your AI chatbot.\n"
        "Ask me anything to get started."
    )

    status_label.config(text="Ready to chat")
    input_box.focus_set()


# =============== SIDEBAR ===============

sidebar = tk.Frame(root, bg=SIDEBAR, width=205)
sidebar.pack(side="left", fill="y")
sidebar.pack_propagate(False)

tk.Label(
    sidebar,
    text="✦  AI CHATBOT",
    font=("Segoe UI", 17, "bold"),
    bg=SIDEBAR,
    fg=WHITE
).pack(anchor="w", padx=18, pady=(25, 30))

new_button = tk.Button(
    sidebar,
    text="+  New Chat",
    command=new_chat,
    font=("Segoe UI", 11, "bold"),
    bg=BLUE,
    fg=WHITE,
    activebackground="#1D4ED8",
    activeforeground=WHITE,
    relief="flat",
    bd=0,
    cursor="hand2",
    pady=12
)
new_button.pack(fill="x", padx=14, pady=(0, 25))

tk.Label(
    sidebar,
    text="YOUR ASSISTANT",
    font=("Segoe UI", 9, "bold"),
    bg=SIDEBAR,
    fg=MUTED
).pack(anchor="w", padx=18, pady=6)

tk.Label(
    sidebar,
    text="●  Llama 3.2",
    font=("Segoe UI", 11),
    bg=SIDEBAR,
    fg="#86EFAC"
).pack(anchor="w", padx=18, pady=5)

tk.Label(
    sidebar,
    text="Runs locally on your PC",
    font=("Segoe UI", 9),
    bg=SIDEBAR,
    fg=MUTED
).pack(anchor="w", padx=18, pady=3)

tk.Label(
    sidebar,
    text="Powered by Ollama",
    font=("Segoe UI", 9),
    bg=SIDEBAR,
    fg=MUTED
).pack(side="bottom", anchor="w", padx=18, pady=20)


# =============== MAIN CHAT AREA ===============

main = tk.Frame(root, bg=BG)
main.pack(side="left", fill="both", expand=True)

header = tk.Frame(main, bg=BG)
header.pack(fill="x", padx=24, pady=(20, 15))

tk.Label(
    header,
    text="AI Assistant",
    font=("Segoe UI", 21, "bold"),
    bg=BG,
    fg=WHITE
).pack(side="left")

tk.Label(
    header,
    text="  Ask anything",
    font=("Segoe UI", 10),
    bg=BG,
    fg=MUTED
).pack(side="left", pady=(8, 0))

tk.Frame(main, bg="#334155", height=1).pack(
    fill="x", padx=20
)

chat_canvas = tk.Canvas(
    main,
    bg=BG,
    highlightthickness=0
)

chat_scrollbar = tk.Scrollbar(
    main,
    orient="vertical",
    command=chat_canvas.yview
)

chat_canvas.configure(
    yscrollcommand=chat_scrollbar.set
)

chat_scrollbar.pack(side="right", fill="y")
chat_canvas.pack(fill="both", expand=True)

chat_inner = tk.Frame(chat_canvas, bg=BG)

canvas_window = chat_canvas.create_window(
    (0, 0),
    window=chat_inner,
    anchor="nw"
)


def resize_chat(event):
    chat_canvas.itemconfigure(
        canvas_window,
        width=event.width
    )

    width = max(220, event.width - 190)

    for label, is_user in message_widgets:
        label.config(wraplength=width)

    scroll_to_bottom()


chat_canvas.bind("<Configure>", resize_chat)

chat_inner.bind(
    "<Configure>",
    lambda event: chat_canvas.configure(
        scrollregion=chat_canvas.bbox("all")
    )
)


# =============== MESSAGE INPUT ===============

bottom = tk.Frame(main, bg=BG)
bottom.pack(fill="x", padx=22, pady=(10, 8))

input_frame = tk.Frame(
    bottom,
    bg=PANEL,
    highlightbackground="#334155",
    highlightthickness=1
)
input_frame.pack(fill="x")

input_box = tk.Text(
    input_frame,
    height=2,
    font=("Segoe UI", 11),
    bg=PANEL,
    fg=WHITE,
    insertbackground=WHITE,
    relief="flat",
    wrap="word",
    padx=12,
    pady=12
)
input_box.pack(
    side="left",
    fill="both",
    expand=True,
    padx=(2, 0),
    pady=2
)

send_button = tk.Button(
    input_frame,
    text="Send",
    command=send_message,
    font=("Segoe UI", 10, "bold"),
    bg=BLUE,
    fg=WHITE,
    activebackground="#1D4ED8",
    activeforeground=WHITE,
    relief="flat",
    bd=0,
    cursor="hand2",
    padx=20,
    pady=10
)
send_button.pack(side="right", padx=10, pady=8)

status_label = tk.Label(
    bottom,
    text="Ready to chat",
    font=("Segoe UI", 9),
    bg=BG,
    fg=MUTED,
    anchor="w"
)
status_label.pack(fill="x", pady=(8, 0))

tk.Label(
    main,
    text="AI can make mistakes. Check important information.",
    font=("Segoe UI", 9),
    bg=BG,
    fg="#64748B"
).pack(pady=(0, 12))


# Enter sends; Shift+Enter inserts a new line.
input_box.bind("<Return>", send_message)
input_box.bind(
    "<Shift-Return>",
    lambda event: None
)

# Start the app.
new_chat()
input_box.focus_set()
root.mainloop()
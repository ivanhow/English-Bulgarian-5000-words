import ftplib
import io
from tkinter import *
import pandas
from random import *
import socket
from PIL import Image, ImageTk
import requests
import pyperclip

BACKGROUND_COLOR = "#B1DDC6"
word_number = ''
eng_word = ''
bg_word = ''
data = []


# -----------------------------Internet--------------------------------------
def internet(input_data):
    url = "http://www.google.com"
    timeout = 5
    try:
        request = requests.get(url, timeout=timeout)
        input_data
    except (requests.ConnectionError, requests.Timeout) as exception:
        print("No internet connection.")


# -----------------------------Data--------------------------------------
def download(target):
    ftp = ftplib.FTP('ftp.photoretoucher.eu')
    ftp.login('bg_eng@photoretoucher.eu', 'Mikolino2009')
    download_file = io.BytesIO()
    ftp.retrbinary('RETR ' + str(target), download_file.write)
    download_file.seek(0)
    contents = download_file.read()
    download_file.seek(0)
    file_to_process = pandas.read_csv(download_file, engine='python')
    return file_to_process


def upload(df):
    csv_file = df.to_csv(index=False)

    ftp = ftplib.FTP('ftp.photoretoucher.eu')
    ftp.login('bg_eng@photoretoucher.eu', 'Mikolino2009')

    bio = io.BytesIO(csv_file.encode())
    ftp.storbinary('STOR words_to_learn.csv', bio)


def no_internet():
    canvas.itemconfig(words_to_learn, text='Yana, you Rock! Or you have no internet connection.')
    r_button.config(image=r_button_image, highlightthickness=0, command=lambda: None)
    x_button.config(image=x_button_image, highlightthickness=0, command=lambda: None)


def read_data():
    global data
    try:
        df = download('words_to_learn.csv')
    except ftplib.error_perm:
        df = download('eng_translated.csv')
        data = df.to_dict(orient='records')
        return data
    except pandas.errors.EmptyDataError:
        # data = []
        return []
    except socket.gaierror:
        data = []
        return data
    else:
        data = df.to_dict(orient='records')
        return data


# -----------------------------Generate a card and word--------------------
def generate_word():
    global word_number, eng_word, bg_word, data
    if len(data) != 0:
        word_number = randint(0, len(data) - 1)
        eng_word = data[word_number]['english']
        bg_word = data[word_number]['bulgarian']
        canvas.itemconfig(bulgarian_text, text='')
        canvas.itemconfig(bulgarian_word, text='')
        canvas.itemconfig(english_text, text='English')
        canvas.itemconfig(english_word, text=eng_word)
        canvas.itemconfig(canvas_img, image=card_front)
        # window.after(3000, flip_card)
    else:
        canvas.itemconfig(words_to_learn, text='Yana, you Rock!')
        r_button.config(image=r_button_image, highlightthickness=0, command=lambda: None)
        x_button.config(image=x_button_image, highlightthickness=0, command=lambda: None)


# -----------------------------Flip the card and word----------------------
def flip_card():
    canvas.itemconfig(english_word, text='')
    canvas.itemconfig(bulgarian_word, text=bg_word)
    canvas.itemconfig(canvas_img, image=card_back)
    canvas.itemconfig(bulgarian_text, text='Bulgarian')
    canvas.itemconfig(english_text, text='')


# -----------------------------Right button-----------------------------
def right_answer():
    if len(data) != 0:
        data.remove(data[word_number])
        new_df = pandas.DataFrame.from_dict(data)
        upload(new_df)

        canvas.itemconfig(words_to_learn, text=f'Yana, you need to learn {len(data)} words!')
        flip_card()
        window.after(5000, generate_word)
        # generate_word()
    else:
        new_df = pandas.DataFrame.from_dict(data)
        upload(new_df)
        canvas.itemconfig(words_to_learn, text='Yana, you Rock!')
        r_button.config(image=r_button_image, highlightthickness=0, command=lambda: None)


# -----------------------------Wrong button-----------------------------
def wrong_button():
    if len(data) == 0:
        x_button.config(image=x_button_image, highlightthickness=0, command=lambda: None)
    else:
        pyperclip.copy(eng_word)
        canvas.itemconfig(text_copied, text='Unknown English words are copied to clipboard.')
        flip_card()
        window.after(5000, generate_word)
        # generate_word()


# -----------------------------Hint button-----------------------------
def hint(event):
    canvas.itemconfig(hint_text, text=bg_word)


def hide_hint(event):
    canvas.itemconfig(hint_text, text='')


# -----------------------------UI---------------------------------------
def download_image(filename):
    ftp = ftplib.FTP('ftp.photoretoucher.eu')
    ftp.login('bg_eng@photoretoucher.eu', 'Mikolino2009')
    download_file = io.BytesIO()
    ftp.retrbinary('RETR ' + filename, download_file.write)
    download_file.seek(0)
    return Image.open(download_file)


internet(read_data())

window = Tk()
window.title("Yana's EN-BG learning tool")
window.config(padx=50, pady=50, bg=BACKGROUND_COLOR)

canvas = Canvas(height=526, width=800, bg=BACKGROUND_COLOR, highlightthickness=0)
card_front = ImageTk.PhotoImage(download_image('card_front.png'))
card_back = ImageTk.PhotoImage(download_image('card_back.png'))
canvas_img = canvas.create_image(402, 267, image=card_front)
english_text = canvas.create_text(400, 150, text='', fill='black', font=('Ariel', 40, 'italic'))
english_word = canvas.create_text(400, 263, text='', fill='black', font=('Ariel', 60, 'bold'))
bulgarian_text = canvas.create_text(400, 150, text='', fill='white', font=('Ariel', 40, 'italic'))
bulgarian_word = canvas.create_text(400, 263, text='', fill='white', font=('Ariel', 60, 'bold'))
words_to_learn = canvas.create_text(400, 50, text=f'Yana, you need to learn {len(read_data())} words!', fill='pink',
                                    font=('Ariel', 20, 'bold'))
hint_text = canvas.create_text(400, 380, text='', fill='red', font=('Ariel', 25, 'italic'))
text_copied = canvas.create_text(400, 450, text='', fill='pink', font=('Ariel', 15, 'italic'))
canvas.grid(row=0, column=0, columnspan=3)

# Buttons
x_button_image = ImageTk.PhotoImage(download_image('wrong.png'))
x_button = Button(image=x_button_image, highlightthickness=0, command=wrong_button)
x_button.grid(row=1, column=0)
r_button_image = ImageTk.PhotoImage(download_image('right.png'))
r_button = Button(image=r_button_image, highlightthickness=0, command=right_answer)
r_button.grid(row=1, column=2)
h_button_image = ImageTk.PhotoImage(download_image('hint.png'))
h_button = Button(image=h_button_image, highlightthickness=0)
h_button.bind('<ButtonPress-1>', hint)
h_button.bind('<ButtonRelease-1>', hide_hint)
h_button.grid(row=1, column=1)

generate_word()

window.mainloop()

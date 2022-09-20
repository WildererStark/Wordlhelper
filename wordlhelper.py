import tkinter as tk
import tkinter.font as font
from tkinter import DISABLED, NORMAL, ttk
from tkinter.messagebox import showinfo


# To do :

# 3) undo try


# Little Wordl Helper
#
# we use an english / german wordfile with 5 letter words
#
# User input :
# 1) a legal 5 letter word
# 2) the wordl - game - reaction/output (the color pattern )
#    we transpose this in a string
# the pattern is a string with wildcard letters
# 'g' (green)  for : letter is on this place
# 'y' (yellow) for : letter exists , but not on this place
# 'b' (black) for
#          a) letter xy does not exist in the word  or
#          b) if there is a letter xy  on the left side marked with 'y' or 'g'
#              letter exists, but not on this place or
#          c) if on left a letter xy is marked with 'g' no more xy exists
#

WORD_LENGTH_NEEDED = 5  # length of the word we are searching.
MAXIMUM_TRIES = 6      # how many tries do we have ?

GER_WORD_FILE = "ger5letterWordTrans.txt"
ENG_WORD_FILE = "englwords.txt"

negativ_list = []      # letters not in the word
positiv_list = []      # letters in the word
letter_places = []     # letters on the right place
letter_no_place = []   # list of letters not on this place
two_letter = []        # two or more of the same letter
one_letter = []

player_try = 0

filtered_words = []


def check_if_consistent(pattern, word):

    # check if current inputs (pattern, word) contradicts early inputs

    positiv_letters = []  # letters marked with yellow (y) or green (g)
    black_letters = []    # letters marked with black/grey (b)

    word = word.upper()
    pattern = pattern.lower()

    for index, wildcard in enumerate(pattern):

        if wildcard == 'g':
            # wrong green letter on this place
            if letter_places[index] != '' and letter_places[index] != word[index]:
                return False

        if wildcard == 'y':
            if letter_places[index] == word[index]:
                return False

        if wildcard == 'g' or wildcard == 'y':
            # print('wildcard  g und y')
            positiv_letters.append(word[index])

        if wildcard == 'b' and letter_places[index] == word[index]:
            # this black letter should be green
            return False

        if wildcard == 'b':
            black_letters.append(word[index])

    if set(negativ_list) & set(positiv_letters) != set():
        # some of these positiv ( yellow, green) letters shoud not be positiv
        return False

    if (set(black_letters) - set(positiv_letters)) & set(positiv_list) != set():
        # some of these black letters shoud not be black
        return False

    return True


def update_letter_lists(pattern, word):

    # update :
    #
    # positiv_letter
    # negativ_letter
    # letter_places
    # letter_no_place
    # two_letter

    positiv_letter = []  # letters marked with yellow or green

    for index, letter in enumerate(word):

        if pattern[index] == "g":
            positiv_letter.append(letter)
            if letter_places[index] == '':
                letter_places[index] = letter
                positiv_list.append(letter)

            continue

        if pattern[index] == "y":
            # (yellow) Letter exists, but not on this place
            positiv_letter.append(letter)
            letter_no_place[index] += letter

            if letter not in positiv_list:

                positiv_list.append(letter)

    # detect 2 or more identical letters ( positiv marked)
    letter_set = set(positiv_letter)
    letter_list = list(letter_set)
    for letter in letter_list:
        if positiv_letter.count(letter) >= 2:
            two_letter.append(letter)

    for index, letter in enumerate(word):

        if pattern[index] == "b":
            # letter could be positiv

            if letter not in positiv_list:
                negativ_list.append(letter)
            else:
                if positiv_letter.count(letter) == 1 :
                    one_letter.append(letter)
                letter_no_place[index] += letter

    #
    # print(" letter_places : ", letter_places)

    # print(" Negativ Liste : ", negativ_list)
    # print(" Positiv Liste : ", positiv_list)

    # print(" Letter not on this place ", letter_no_place)
    # print(" one letter ", one_letter)
    # print(" two letter ", two_letter)

    #  return len(letter_places)


def filter_list(prior_list):

    our_list = []

    for word in prior_list:

        legal_word = True

        for index, letter in enumerate(letter_places):
            if letter != '':
                if word[index] != letter:

                    legal_word = False
                    break

        if legal_word:
            for letter in positiv_list:
                if letter not in word:

                    legal_word = False
                    break

            if legal_word:
                for index, letter in enumerate(word):

                    if letter in negativ_list:

                        legal_word = False
                        break

                    if letter in letter_no_place[index]:

                        legal_word = False
                        break

                    if word.count(letter)<2:
                        if letter in two_letter:
                            legal_word = False
                            break
                    else:
                        if letter in one_letter:
                            legal_word = False
                            break

                # if legal_word:

                    
                #    for letter in two_letter:
                        # print(letter, word, word.count(letter))
                        #if word.count(letter) < 2:
                        #    legal_word = False
                        #    break

        if legal_word:
            our_list.append(word)

    # print("Our filtered list ", our_list)
    # print("Count of the legal words", len(our_list))

    return our_list


##########################################################################
#
# load the words


def load_selected_language():

    global filtered_words

    init_lists()

    if language_selected.get() == "English":
        wordfile = ENG_WORD_FILE
    else:
        wordfile = GER_WORD_FILE

    f = open(wordfile, 'r')

    for line in f:
        my_word = line[0:len(line) - 1]
        filtered_words.append(my_word.upper())

    f.close()

    filtered_words = sorted(filtered_words)
    list_items.set(filtered_words)
    word_pattern_button['state'] = NORMAL

    showinfo(
        title='The Language',
        message=language_selected.get()
    )


#############################################################################
#
# GUI root window

root = tk.Tk()
root.geometry("400x735")
root.resizable(False, False)
root.title("Little Wordl-Helper")

root.columnconfigure(1, weight=1)
root.rowconfigure(2, weight=1)
root['background'] = 'grey'
for widget in root.winfo_children():
    widget.grid(padx=3, pady=5)


def show_user_words(words, patterns):

    for grid_row, elem in enumerate(words):

        for grid_column in range(len(elem)):

            wildcard = patterns[grid_row][grid_column]
            wildcard = wildcard.lower()
            if wildcard == 'g':
                my_color = 'green'
            elif wildcard == 'y':
                my_color = 'gold'
            else:
                my_color = 'black'
            my_letter = elem[grid_column].upper()

            label = tk.Label(words_colored_frame, height=1, width=2, font=(
                "Arial", 24), fg='white')
            label['background'] = my_color
            label['text'] = my_letter
            label.grid(column=grid_column, row=grid_row, stick=tk.W)
            label['relief'] = 'sunken'

    for widget in words_colored_frame.winfo_children():
        widget.grid(padx=1, pady=1)

##############################################################################
#
#  GUI   select language frame


language_selected = tk.StringVar()

language_frame = tk.Frame(root)

language_label = ttk.Label(language_frame, text='What is your Language? ')
language_label.grid(column=0, row=0)

rb_english = ttk.Radiobutton(
    language_frame,
    text='English',
    value='English',
    variable=language_selected)
rb_english.grid(column=0, row=1, sticky="W")

rb_german = ttk.Radiobutton(
    language_frame,
    text='Deutsch',
    value='Deutsch',
    variable=language_selected)
rb_german.grid(column=0, row=2, sticky="W")

language_start_button = ttk.Button(
    language_frame,
    text='Start',
    command=load_selected_language
)

language_start_button.grid(column=0, row=3)

for widget in language_frame.winfo_children():
    widget.grid(padx=3, pady=5)

language_frame['relief'] = 'sunken'
language_frame['background'] = 'red'
language_frame.grid(column=0, row=0, padx=5, pady=5, sticky="W")


################################################################
#
# GUI user input and filter Frame (user_word and pattern)


my_words = []      # words, the user typed
my_patterns = []   # gamereaction , transscripted from user in a pattern like 'bbygb'


user_word = tk.StringVar()
pattern = tk.StringVar()


def check_user_input():

    # prove user input

    abc_set = {'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l',
               'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z'}
    wildcard_set = {'g', 'y', 'b', 'G', 'Y', 'B'}
    pattern_set = set(pattern.get())
    word_set = set(user_word.get().lower())

    if len(user_word.get()) != WORD_LENGTH_NEEDED or len(pattern.get()) != WORD_LENGTH_NEEDED:

        showinfo(
            title='Wrong length!',
            message=f'{WORD_LENGTH_NEEDED} letters needed!'
        )
        return False

    if wildcard_set != wildcard_set | pattern_set:
        showinfo(
            title='Wrong pattern',
            message='Only y,Y, g,G or b,B allowed !'
        )
        return False

    if abc_set != abc_set | word_set:
        showinfo(
            title='Wrong letters',
            message='Only ASCII a, b, c ... allowed'
        )
        return False

    if check_if_consistent(pattern.get(), user_word.get()) == False:
        showinfo(
            title='Logic !',
            message='Your input is not consistent'
        )
        return False

    return True


def init_lists():

    global player_try

    player_try = 0

    negativ_list.clear()     # letters not in word
    positiv_list.clear()     # letters in word
    letter_places.clear()    # letters on correct place
    letter_no_place.clear()  # letters not on this place
    two_letter.clear()       # two or more of letter XY in this word
    one_letter.clear()       # only one letter XY in this word

    for place in range(WORD_LENGTH_NEEDED):
        letter_no_place.append('')
        letter_places.append('')

    my_words.clear()
    my_patterns.clear()
    for index in range(MAXIMUM_TRIES):
        my_words.append('     ')
        my_patterns.append('bbbbb')

    show_user_words(my_words, my_patterns)

    filtered_words.clear()
    user_word.set('')
    pattern.set('')

def handle_user_input():

    global player_try

    if check_user_input():

        language_start_button['state'] = DISABLED

        global filtered_words

        update_letter_lists(pattern.get().lower(), user_word.get().upper())

        filtered_words = filter_list(filtered_words)

        list_items.set(filtered_words)

        my_words[player_try] = user_word.get()
        my_patterns[player_try] = pattern.get()

        player_try += 1

        # print(filtered_words)
        # print('try',player_try)
        # print(my_words)

        show_user_words(my_words, my_patterns)

        if player_try == MAXIMUM_TRIES or len(filtered_words) < 4:

            showinfo(
                title='End - New Game',
                message=f'Try {player_try}, rest {len(filtered_words)} words.'
            )

            word_pattern_button['state'] = DISABLED
            language_start_button['state'] = NORMAL

        user_word.set('')
        pattern.set('')


filter_frame = tk.Frame(root)


filter_frame.columnconfigure(1, weight=1)
# filter_frame.rowconfigure(2, weight=1)

world_label = ttk.Label(filter_frame, text='Your word :',
                        font=('Courier New', 12))
word_entry = ttk.Entry(filter_frame, width=6,
                       textvariable=user_word, font=('Courier New', 12))

world_label.grid(column=0, row=0, sticky=tk.W)
word_entry.grid(column=1, row=0, sticky=tk.E)
word_entry.focus()

pattern_label = ttk.Label(
    filter_frame, text='Pattern, use y, g, b:', font=('Courier New', 12))
pattern_entry = ttk.Entry(filter_frame, width=6,
                          textvariable=pattern, font=('Courier New', 12))

pattern_label.grid(column=0, row=1, sticky=tk.W)
pattern_entry.grid(column=1, row=1, sticky=tk.E)


word_pattern_button = ttk.Button(filter_frame, state=DISABLED,
                                 text='Try word and pattern ! ', command=handle_user_input)
word_pattern_button.grid(column=0, row=3, columnspan=2)

for widget in filter_frame.winfo_children():
    widget.grid(padx=3, pady=5)


filter_frame['relief'] = 'sunken'
filter_frame['background'] = 'red'
filter_frame.grid(column=0, row=1, columnspan=3, sticky=tk.EW, padx=5, pady=5)

###################################################################################
#
# GUI
# Show list of colored user words (Words/pattern)


# set the font.
fnt = font.Font(family='Times New Roman')


words_colored_frame = tk.Frame(root)
words_colored_frame.columnconfigure(WORD_LENGTH_NEEDED, weight=1)
words_colored_frame.rowconfigure(MAXIMUM_TRIES, weight=1)


words_colored_frame.grid(column=1, row=2, padx=5, pady=5, sticky=tk.N)

words_colored_frame['relief'] = 'sunken'
words_colored_frame['background'] = 'white'

#############################################################################################
#
# GUI Listbox and Scrollbar
# Show the filtered words


show_filtered_frame = tk.Frame(root)

list_items = tk.StringVar(value=filtered_words)

myListbox = tk.Listbox(show_filtered_frame, listvariable=list_items,
                       activestyle='none', selectmode = tk.SINGLE, height=19, width=7)

# myListbox : scrolling does not show the last word, if height = 20

myListbox.grid(row=0, column=0, sticky=tk.EW)
myListbox.config(font=("Arial", 16))

def item_selected(event):
    selected_indice = myListbox.curselection()
    selelected_word = myListbox.get(selected_indice)
    msg = f'You selected: {selelected_word}'
    showinfo(title= "Listbox - Info", message=msg)
    user_word.set(selelected_word)


myListbox.bind("<<ListboxSelect>>", item_selected)

# Bind a Scrollbar per command

scrollbar = ttk.Scrollbar(
    show_filtered_frame, orient='vertical',  command=myListbox.yview)
scrollbar.grid(row=0, column=1, sticky=tk.NS)

myListbox['yscrollcommand'] = scrollbar.set

show_filtered_frame.grid(column=0, row=2, padx=5, pady=5)
show_filtered_frame['relief'] = 'sunken'
show_filtered_frame['background'] = 'red'

root.mainloop()

import tkinter as tk
import tkinter.font as font
from tkinter import DISABLED, NORMAL, ANCHOR, ttk
from tkinter.messagebox import showinfo
import re

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
one_letter = []        # only one of letter xy in word

player_try = 0

filtered_words = []

my_words = []      # words, the user typed
my_patterns = []   # gamereaction , transscripted from user in a pattern like 'bbygb'




def update_letter_lists(pattern, word ):

    # update letter lists according to user input ( pattern, word) :
    #
    # positiv_list     : letters  in word
    # negativ_list     : letters not in the word
    # letter_places    : letters on correct places
    # letter_no_place  : letters not on correct places
    # two_letter       : two or more letters xy in the word
    # one_letter       : only one

    positiv_letter = []  # letters marked with yellow or green

    for index, letter in enumerate(word):

        if pattern[index] == "g":
            # green/orange Letter is correct on this place
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
            # two or more of this letter in the word
            two_letter.append(letter)

    for index, letter in enumerate(word):

        if pattern[index] == "b":
            # black/grey letter not on this place but could be positiv,if

            if letter not in positiv_list:
                negativ_list.append(letter)
            else:
                if positiv_letter.count(letter) == 1 :
                    one_letter.append(letter)
                    # we know now, only one of letter in the word
                letter_no_place[index] += letter

    #
    # print(" letter_places : ", letter_places)

    # print(" Negativ Liste : ", negativ_list)
    # print(" Positiv Liste : ", positiv_list)

    # print(" Letter not on this place ", letter_no_place)
    # print(" one letter ", one_letter)
    # print(" two letter ", two_letter)



def filter_list(prior_list):


    # we exploit the negativ_list and the positiv_list for reducing :
    our_list = list(filter( lambda word: set(word).isdisjoint(negativ_list), prior_list))
    our_list = list(filter( lambda word: set(positiv_list).issubset(set(word)), our_list))
 

    # we build a regex string with letter_places
    regex =''
    for c in letter_places:
        if c =='':
            regex += '.'
        else:
            regex += c
    
    reg_pattern = re.compile(regex)
    our_list = [word for word in our_list if reg_pattern.match(word)]

    # more reducing possibilities :
    def misc_filter(word):
        for index, letter in enumerate(word):
            if letter in letter_no_place[index]:
                return False
            if word.count(letter)<2 and letter in two_letter:
                return False
            if word.count(letter)>=2 and letter in one_letter:
                return False
        return True

    our_list = [word for word in our_list if misc_filter(word)]            

    
    return our_list



##############################################################################
#
#  GUI   select language frame

##############################################################################
#
# load the words


def load_selected_language():

    global filtered_words

    init_lists()

    if LanFr.language_selected.get() == "English":
        wordfile = ENG_WORD_FILE
    else:
        wordfile = GER_WORD_FILE

    try:
        f = open(wordfile, 'r')
    except FileNotFoundError:
        showinfo(
            title="Missing Word-File",
            message=f"File {wordfile}not found"
        )
        quit()

    for line in f:
        my_word = line[0:len(line) - 1]
        filtered_words.append(my_word.upper())

    f.close()

    # filtered_words = sorted(filtered_words)

    filtered_words.sort()
    ShowFiltFr.list_items.set(filtered_words)

    FiltFr.word_pattern_button['state'] = NORMAL

    showinfo(
        title='The Language',
        message=LanFr.language_selected.get()
    )


class LanguageFrame(tk.Frame):
    def __init__(self, container):
        super().__init__(container)
        self.language_selected = tk.StringVar()
        self.language_label = ttk.Label(self, text='What is your Language? ')
        self.language_label.grid(column=0, row=0)

        self.rb_english = ttk.Radiobutton(
            self,
            text='English',
            value='English',
            variable=self.language_selected)
        self.rb_english.grid(column=0, row=1, sticky="W")

        self.rb_german = ttk.Radiobutton(
            self,
            text='Deutsch',
            value='Deutsch',
            variable=self.language_selected)
        self.rb_german.grid(column=0, row=2, sticky="W")

        self.language_selected.set('English')

        self.language_start_button = ttk.Button(
            self,
            text='Start',
            command=load_selected_language
        )


        self.language_start_button.grid(column=0, row=3)

        for widget in self.winfo_children():
            widget.grid(padx=3, pady=5)

        self['relief'] = 'sunken'
        self['background'] = 'red'
        self.grid(column=0, row=0, padx=5, pady=5, sticky="W")




################################################################
#
# GUI user input and filter Frame (user_word and pattern)


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

    WordsColoredFrame.show_user_words(WordsColFr,my_words, my_patterns)

    filtered_words.clear()
    FiltFr.user_word.set('')
    FiltFr.pattern.set('')


def check_user_input(word, pattern):
    """ Validate user input """


    abc_set = {'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l',
               'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z'}
    wildcard_set = {'g', 'y', 'b', 'G', 'Y', 'B'}

    pattern_set = set(pattern)
    word_set = set(word.lower())


    if len(word) != WORD_LENGTH_NEEDED or len(pattern) != WORD_LENGTH_NEEDED:

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

    if check_if_consistent(pattern, word) == False:
        showinfo(
            title='Logic !',
            message='Your input is not consistent'
        )
        return False

    return True


def check_if_consistent(pattern, word):
    '''check if current inputs (pattern, word) contradicts earlier inputs '''

    positiv_letters = []  # letters marked with yellow (y) or green/orange (g)
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

def handle_user_input():
    ''' 
    callback from Button click (word_pattern_button in FilterFrame) 
    1) Check, if user input (word and pattern) is valid
    2) if so , reduce the word list (filtered_words)
    3) show reduced word list in a listbox and all user inputs (words/patterns)
    '''
    global player_try
    global filtered_words

    word_input = FiltFr.user_word.get()
    pattern_input = FiltFr.pattern.get()

    if check_user_input(word_input, pattern_input):

        LanFr.language_start_button['state'] = DISABLED
       

        update_letter_lists(pattern_input.lower(), word_input.upper())

        filtered_words = filter_list(filtered_words)

        ShowFiltFr.list_items.set(filtered_words)

        my_words[player_try] = word_input
        my_patterns[player_try] = pattern_input

        player_try += 1

        # print(filtered_words)
        # print('try',player_try)
        # print(my_words)

        WordsColoredFrame.show_user_words(WordsColFr, my_words, my_patterns)

        if player_try == MAXIMUM_TRIES or len(filtered_words) < 4:

            showinfo(
                title='End - New Game',
                message=f'Try {player_try}, rest {len(filtered_words)} words.'
            )

            FiltFr.word_pattern_button['state'] = DISABLED
            LanFr.language_start_button['state'] = NORMAL

        FiltFr.user_word.set('')
        FiltFr.pattern.set('')



class FilterFrame(tk.Frame):
    def __init__(self, container):
        super().__init__(container)

        self.columnconfigure(1, weight=1)


        # word Label
        self.word_label = ttk.Label(self, text='Your word :',
                        font=('Courier New', 12))
        self. word_label.grid(column=0, row=0, sticky=tk.W)

        # word entry
        self.user_word = tk.StringVar()
        self.word_entry = ttk.Entry(self, width=6,
                       textvariable=self.user_word, font=('Courier New', 12))
        self.word_entry.grid(column=1, row=0, sticky=tk.E)
        self.word_entry.focus()

        # pattern Label
        self.pattern_label = ttk.Label(self, text='Pattern,use y,g,b : e.g. ygbgb', 
                                        font=('Courier New', 12))
        self.pattern_label.grid(column=0, row=1, sticky=tk.W)

        # pattern entry
        self.pattern = tk.StringVar()
        self.pattern_entry = ttk.Entry(self, width=6,
                          textvariable=self.pattern, font=('Courier New', 12))
        self.pattern_entry.grid(column=1, row=1, sticky=tk.E)

        # button
        self.word_pattern_button = ttk.Button(self, state=DISABLED,
                                 text='Try word and pattern ! ', command=handle_user_input)
        self.word_pattern_button.grid(column=0, row=3, columnspan=2)


        for widget in self.winfo_children():
            widget.grid(padx=3, pady=5)
        self['relief'] = 'sunken'
        self['background'] = 'red'
        self.grid(column=0, row=1, columnspan=3, sticky=tk.EW, padx=5, pady=5)
        


###################################################################################
#
# GUI
# Show list of  user words with colored background  (Words/pattern as background color)

class WordsColoredFrame(tk.Frame):
    def __init__(self, container):
        super().__init__(container)

        self.columnconfigure(WORD_LENGTH_NEEDED, weight=1)
        self.rowconfigure(MAXIMUM_TRIES, weight=1)
        self.grid(column=1, row=2, padx=5, pady=5, sticky=tk.N)

        self['relief'] = 'sunken'
        self['background'] = 'white'


    def show_user_words(self, words, patterns):

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

                self.label = tk.Label(self, height=1, width=2, font=("Arial", 24), fg='white')
                self.label['background'] = my_color
                self.label['text'] = my_letter
                self.label.grid(column=grid_column, row=grid_row, stick=tk.W)
                self.label['relief'] = 'sunken'

        for widget in self.winfo_children():
            widget.grid(padx=1, pady=1)


#############################################################################################
#
# GUI Listbox and Scrollbar
# Show the filtered words

class ShowFilteredFrame(tk.Frame):
    def __init__(self, container):
        super().__init__(container)

        self.list_items = tk.StringVar(value=filtered_words)
        self.myListbox = tk.Listbox(self, listvariable=self.list_items,
                        height=19, width=7, exportselection = False)


        self.myListbox.grid(row=0, column=0, sticky=tk.EW)
        self.myListbox.config(font=("Arial", 16))

        self.myListbox.bind("<<ListboxSelect>>", self.item_selected)


        self.scrollbar = ttk.Scrollbar(self, orient='vertical',  command=self.myListbox.yview)
        self.scrollbar.grid(row=0, column=1, sticky=tk.NS)

        self.myListbox['yscrollcommand'] = self.scrollbar.set
        self.grid(column=0, row=2, padx=5, pady=5)
        self['relief'] = 'sunken'
        self['background'] = 'red'


    def item_selected(self, event):

        selected_indice = self.myListbox.curselection()
        selected_word = self.myListbox.get(selected_indice)

        # selected_word = self.myListbox.get(ANCHOR)
        msg = f'You selected: {selected_word}'
        showinfo(title= "Listbox - Info", message=msg)
        self.myListbox.select_clear(0, tk.END)

        FiltFr.user_word.set(selected_word)
        # word_entry.focus()

    

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry("400x735")
        self.resizable(False, False)
        self.title("Little Wordl-Helper")
        self.columnconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self['background'] = 'grey'
        for widget in self.winfo_children():
            widget.grid(padx=3, pady=5)

 

if __name__ == "__main__":

    app = App()


    LanFr = LanguageFrame(app)
    FiltFr = FilterFrame(app)
    ShowFiltFr = ShowFilteredFrame(app)
    WordsColFr = WordsColoredFrame(app)

    app.mainloop()

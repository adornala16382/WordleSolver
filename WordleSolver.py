import json
import random
import neat
import os
import tkinter as tk
from tkinter import *
from tkinter.ttk import *

f = open('wordList.json')
wordList = json.load(f)
f.close()
all_words = wordList['answers']['possibleAnswers']
board_width = 1200
board_height = 750
frequencyList = {}

def makeFrequencyList(filename):
    file = open(filename)
    lines = file.readlines()
    for line in lines:
        split = line.split('|')
        frequencyList[split[0]] = float(split[1])

makeFrequencyList('letterFrequency.txt')

class WordleSolver:

    allowedGuesses = all_words
    guess_count = 0
    answer = all_words[random.randint(0,len(all_words) - 1)]
    correctSpots = []
    wrongSpots = []

# initializes game
    def __init__(self, hardCodedAnswer, runStatistics):
        self.window = tk.Tk()
        self.window.title("Wordle Solver")
        self.canvas = Canvas(self.window, width=board_width, height=board_height, bg = '#222222')
        self.on = PhotoImage(file = "on.png")
        self.off = PhotoImage(file = "off.png")
        self.canvas.pack()
        self.hardCodedAnswer = hardCodedAnswer
        self.runStatistics = runStatistics
        if(self.runStatistics == True):
            self.statistics()
        else:
            self.restart()

# restarts game   
    def restart(self):
        self.allowedGuesses = all_words.copy()
        self.guess = ""
        self.guess_count = 0
        self.is_on = False
        self.victory = False
        if(self.hardCodedAnswer != None):
            self.answer = self.hardCodedAnswer
        else:
            self.answer = all_words[random.randint(0,len(all_words) - 1)]
        self.correctSpots = []
        self.wrongSpots = []
        self.deleteList = []
        self.currentWord = [[0,0],[0,0],[0,0],[0,0],[0,0]]
        self.canvas.delete("all")
        self.canvas.create_text(board_width / 2,  50, font="cmr 40 bold", fill='white', text="WORDLE")
        btn1 = Button(self.window, text = 'Make Computer Guess!', command = self.guessWord)
        self.canvas.create_window(board_width/2 -  400, board_height - 52.5, anchor='nw', window=btn1)
        btn2 = Button(self.window, text = 'New Game', command = self.restart)
        self.canvas.create_window(board_width/2 + 350, board_height - 52.5, anchor='nw', window=btn2)
        self.e1 = tk.Entry(self.window)
        self.canvas.create_window(board_width/2 - 170, board_height - 50, anchor='nw', window=self.e1)
        self.canvas.create_text(board_width/2 - 130, board_height - 60, font="cmr 10 bold", fill='white', text="TYPE GUESS")
        btn3 = Button(self.window, text = 'ENTER', command = self.typeInputWord)
        self.canvas.create_window(board_width/2 - 45, board_height - 52.5, anchor='nw', window=btn3)
        self.on_button = Button(self.window, image = self.off, command = self.switch)
        self.canvas.create_window(board_width/2 + 140, board_height - 65, anchor='nw', window=self.on_button)
        self.canvas.create_text(board_width/2 + 200, board_height - 95, font="cmr 10 bold", fill='white', text="Turn on in beginning\nof game to assist solving\nan external Wordle game")
        self.createGrid()
        if(self.runStatistics == False):
            print("answer: "+self.answer)

# Creates grid
    def createGrid(self):
        self.canvas.create_rectangle(board_width / 2 - 187.5, board_height / 12 + (75), board_width / 2 - 187.5 + (5*75), board_height / 12 + (7 *75),  fill="white")
        for i in range(7):
            self.canvas.create_line(board_width / 2 - 187.5, board_height / 12 + (75*(i+1)), board_width / 2 + 187.5, board_height / 12 + (75*(i+1)), fill='black', width=2)
        for i in range(6):
            self.canvas.create_line(board_width / 2 - 187.5 + (i*75), board_height / 12 + 75, board_width / 2 - 187.5 + (i*75), board_height / 12 + (75*7), fill='black', width=2)

# Determine if switch is on or off        
    def switch(self):   
        if(self.guess_count==0):
            if self.is_on:
                self.on_button.config(image = self.off)
                self.is_on = False
            else:
                self.on_button.config(image = self.on)
                self.is_on = True
                self.canvas.create_text(board_width/2, board_height / 12 + 60, font="cmr 10 bold", fill='white', text="Click on letters to change its color")
                self.answer = ""

# types input text on screen
    def typeInputWord(self):
        self.guess = self.e1.get()
        if(len(self.guess)==5):
            self.guess_count += 1
            self.computerMode()
            self.typeWord()
        self.e1.delete(0,tk.END)

# logic to guess the next word
    def guessWord(self):
        self.deleteList = []
        if(len(self.allowedGuesses) >= 1):
            if(self.guess_count <= 5 and self.victory==False):

                self.guess_count+= 1

                if(self.is_on == True):
                    self.assistMode()
                else:
                    self.computerMode()

                if(self.guess_count <= 6 and self.guess!= None):
                    self.typeWord()
                
                self.determineVictory()

# determines whether or not the computer won and displays victory/defeat screen
    def determineVictory(self):
        if(self.guess == self.answer):
            self.canvas.create_text(board_width / 2,  board_height / 12 + 35, font="cmr 20 bold", fill='green', text='VICTORY')
            self.canvas.create_text(board_width / 2,  board_height - 130, font="cmr 20 bold", fill='white', text=f'answer: {self.answer.upper()}')
            self.victory = True
        elif(self.guess_count == 6 and self.guess!=None):
            self.canvas.create_text(board_width / 2,  board_height - 130, font="cmr 20 bold", fill='white', text=f'answer: {self.answer.upper()}')
            self.canvas.create_text(board_width / 2,  board_height / 12 + 35, font="cmr 20 bold", fill='red', text='DEFEAT')
            self.victory = False
            self.guess_count = 7

# logic for assistMode to narrow down the possible word list
    def assistMode(self):
        for i, char in enumerate(self.guess):
            if(self.currentWord[i][1] %3 == 2):
                self.correctSpots.append((char,i))
                for k, word in enumerate(self.allowedGuesses):
                    if(word[i] != char):
                        self.deleteList.append(k)
            elif(self.currentWord[i][1] %3 == 1):
                self.wrongSpots.append((char,i))
                for j, word in enumerate(self.allowedGuesses):
                    if(char not in word or (char in word and word[i]==char)):
                        self.deleteList.append(j)
            else:
                for j, word in enumerate(self.allowedGuesses):
                    if(char in word):
                        self.deleteList.append(j)
        self.deleteWords()
        num = self.predict()
        self.guess = self.allowedGuesses[num]
        self.deleteList.append(num)

# logic for computerMode to narrow down the possible word list   
    def computerMode(self):
        num = self.predict()
        self.guess = self.allowedGuesses[num]
        self.deleteList.append(num)
        for i, char in enumerate(self.guess):
            if(char in self.answer):
                if(char == self.answer[i]):
                    self.correctSpots.append((char,i))
                    for k, word in enumerate(self.allowedGuesses):
                        if(word[i] != char):
                            self.deleteList.append(k)
                else:
                    self.wrongSpots.append((char,i))
                    for j, word in enumerate(self.allowedGuesses):
                        if(char not in word or (char in word and word[i]==char)):
                            self.deleteList.append(j)
            else:
                for j, word in enumerate(self.allowedGuesses):
                    if(char in word):
                        self.deleteList.append(j)
        self.deleteWords()

# changes the color of a tile when clicked on
    def change_color(self, *args):
        x = (args[0].x - 415) // 75
        y = ((args[0].y - 138) // 75) + 1
        if(y == self.guess_count and self.is_on == True):
            self.currentWord[x][1] += 1
            if(self.currentWord[x][1] % 3 == 0):
                self.canvas.itemconfig(self.currentWord[x][0], fill='gray')
            elif(self.currentWord[x][1] % 3 == 1):
                self.canvas.itemconfig(self.currentWord[x][0], fill='yellow')
            else:
                self.canvas.itemconfig(self.currentWord[x][0], fill='green')
# types out word on screen
    def typeWord(self):
        self.currentWord = []
        for i, char in enumerate(self.guess):
            if((char,i) in self.correctSpots):
                self.currentWord.append([self.canvas.create_rectangle(board_width / 2 - 187.5 + (i*75), board_height / 12 + (self.guess_count*75), board_width / 2 - 187.5 + (i*75)+75 - 1, board_height / 12 + (self.guess_count*75)+75 - 1,  fill="green", tags = f"curWord{i}"), 2])
            elif((char,i) in self.wrongSpots):
                self.currentWord.append([self.canvas.create_rectangle(board_width / 2 - 187.5 + (i*75), board_height / 12 + (self.guess_count*75), board_width / 2 - 187.5 + (i*75)+75 - 1, board_height / 12 + (self.guess_count*75)+75 - 1,  fill="yellow", tags = f"curWord{i}"), 1])
            else:
                self.currentWord.append([self.canvas.create_rectangle(board_width / 2 - 187.5 + (i*75), board_height / 12 + (self.guess_count*75), board_width / 2 - 187.5 + (i*75)+75 - 1, board_height / 12 + (self.guess_count*75)+75 - 1,  fill="gray", tags = f"curWord{i}"), 0]) 
            self.canvas.create_text(board_width / 2 - 150 + (i*75), board_height / 12 + 35 + (self.guess_count*75), font="cmr 30 bold", fill='black', text=char.upper(), tags = f"curWord{i}")
            self.canvas.tag_bind(f"curWord{i}","<Button-1>",self.change_color) 

# deletes words that can't be the answer from the list of possible guesses
    def deleteWords(self):
        self.deleteList = list(set(self.deleteList))
        self.deleteList.sort(reverse=True)
        for index in self.deleteList:
            del self.allowedGuesses[index]

# predicts the answer
    def predict(self):
        if(len(self.allowedGuesses)>= 2):
            max_len = -1
            max_index = 0
            for index, word in enumerate(self.allowedGuesses):
                map = set()
                length = 0
                for char in word:
                    if(char not in map):
                        map.add(char)
                        length += frequencyList[char.upper()]
                        if(length > max_len):
                            max_len = length
                            max_index = index
            return max_index

        else:
            num = random.randint(0,len(self.allowedGuesses)-1)
            return num

# runs statistics
    def statistics(self):
        scoreSum = 0
        for i in range(len(all_words)):      
            self.restart()
            self.answer = all_words[i]
            for j in range(6):
                self.guessWord()
            scoreSum += self.guess_count
            print(self.answer + ": " + str(self.guess_count))
        
        print("avg score: "+str(scoreSum/len(all_words)))

                
    def run(self):
        self.window.mainloop()

# Runs program
# Set hardCodedAnswer to a 5 letter word to set the word the computer has to guess
# Set runStatistics to True to see the average number of guesses the computer takes to get the answer
if __name__ == "__main__":
    game_instance = WordleSolver(hardCodedAnswer = None, runStatistics = False)
    game_instance.run()
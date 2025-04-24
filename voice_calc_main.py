import speech_recognition as sr
import pyttsx3
import time
import re

class VoiceCalculator:
    def __init__(self):
        self.r = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.engine.setProperty('voice', self.engine.getProperty('voices')[0].id)
        self.engine.setProperty('rate', self.engine.getProperty('rate') - 25)
        self.audio_text = ""
        self.recognize = ""
        self.result = 0
        self.exit = False

    def give_instruction(self):
        with sr.Microphone() as mike:
            self.engine.say("Podaj swoje działanie, gdy zobaczysz komunikat - Jesli chcesz zakonczyc, powiedz stop")
            self.engine.runAndWait()
            print("Mów!!!")
            self.r.adjust_for_ambient_noise(mike)
            self.audio_text = self.r.listen(mike, phrase_time_limit=15)
            self.engine.say("Dzieki!")
            self.engine.runAndWait()

    def calculate(self):
        try:
            self.recognize = self.r.recognize_google(self.audio_text, language='pl')
            print(self.recognize)
            if self.recognize == "stop":
                self.exit = True

            elements = self.recognize.split()
            if ( elements[0].isdigit() and elements[2].isdigit() and elements[1] in ('+', '-', 'x', '/') ):
                # print(elements)
                first, second = int(elements[0]), int(elements[2])
                if elements[1] == '+':
                    self.result = first + second
                elif elements[1] == '-':
                    self.result = first - second
                elif elements[1] == 'x':
                    self.result = first * second
                else:
                    self.result = first / second
                self.engine.say("Rezultat to {}".format(int(self.result)))
                self.engine.runAndWait()
            elif self.exit:
                self.engine.say("Dzieki za wspolprace, do widzenia!")
                self.engine.runAndWait()
            else:
                self.engine.say("To chyba nie jest dzialanie, podaj dzialanie na przyklad 2 plus 2")
                self.engine.runAndWait()
        except:
            self.engine.say("Przepraszam, nie rozumiem")
            self.engine.runAndWait()

    def loop(self):
        while(not self.exit):
            self.give_instruction()
            self.calculate()
        self.engine.stop()


if __name__ == '__main__':
    vc = VoiceCalculator()
    vc.loop()

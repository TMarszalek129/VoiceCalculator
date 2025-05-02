import speech_recognition as sr
import pyttsx3
import time
import re
import math
import winsound

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

        self.word_to_num = {
            "zero": "0", "jeden": "1", "dwa": "2", "trzy": "3", "cztery": "4",
            "pięć": "5", "sześć": "6", "siedem": "7", "osiem": "8", "dziewięć": "9",
            "dziesięć": "10"
        }

    def give_instruction(self):
        with sr.Microphone() as mike:
            self.engine.say("Podaj swoje działanie, po usłyszeniu dźwięku. Jeśli chcesz zakończyć, powiedz stop.")
            self.engine.runAndWait()
            duration = 200  # milliseconds
            freq = 440  # Hz
            winsound.Beep(freq, duration)
            self.r.adjust_for_ambient_noise(mike)
            self.audio_text = self.r.listen(mike, phrase_time_limit=5000, timeout=5000)
            self.engine.say("Dzięki!")
            self.engine.runAndWait()

    def preprocess_text(self, text):
        text = text.lower()
        text = text.replace("równa się", "")

        replacements = {
            "plus": "+",
            "dodać" : "+",
            "minus": "-",
            "razy": "*",
            "x" : "*",
            "podzielić przez": "/",
            "dzielone na" : "/",
            "podzielić": "/",
            "dzielone" : "/",
            # "na " : '/',
            "do potęgi": "**",
            "potęgi" : "**",
            "otwórz nawias": "(",
            "zamknij nawias": ")",
            "zamknij" : ")",
            "koniec" : ")",
            "otwórz" : "(",
            "√" : "pierwiastek "
        }
        for word, symbol in replacements.items():
            text = text.replace(word, symbol)

        for word, number in self.word_to_num.items():
            text = re.sub(r'\b{}\b'.format(word), number, text)

        return text

    def preprocess_sqrt_fact(self, elements):
        if "pierwiastek" in elements:
            idx = elements.index("pierwiastek")
            expression = "math.sqrt({})"
        if "silnia" in elements:
            idx = elements.index("silnia")
            expression = "math.factorial({})"
        number = None
        # if idx > 0 and elements[idx - 1] == "z" and idx > 1 and elements[idx - 2].isdigit():
        #     print("First condition")
        #     number = int(elements[idx - 2])
        #     elements.pop(idx)
        #     elements.pop(idx)
        #     elements[idx] = expression.format(number)
        #     print(elements)
        if idx < len(elements) - 1 and elements[idx + 1] == "z" and idx < len(elements) - 2 and elements[idx + 2].isdigit():
            number = int(elements[idx + 2])
            elements.pop(idx)
            elements.pop(idx)
            elements[idx] = expression.format(number)
        elif idx > 0 and elements[idx - 1].isdigit():
            number = int(elements[idx - 1])
            elements.pop(idx)
            elements[idx - 1] = expression.format(number)
        elif idx < len(elements) - 1 and elements[idx + 1].isdigit():
            number = int(elements[idx + 1])
            elements.pop(idx)
            elements[idx] = expression.format(number)
        else:
            raise Exception
        return elements

        # if number is not None:
        #     self.result = eval(expression.format(number))
        #     if math.fmod(self.result, 1.0) == 0:
        #         self.result = int(self.result)
        #     else:
        #         self.result = round(self.result, 2)
        #     # self.engine.say(f"Pierwiastek z {number} to {self.result}")
        #     # self.engine.runAndWait()
        #     # return
        #     self.engine.say(f"Rezultat to {self.result}")
        #     print("Rezultat to ", self.result)
        #     self.engine.runAndWait()


    # def preprocess_multi_digit(self, elements):
    #     # print("I am here")
    #     # IT DOES NOT WORK YET
    #     replacements = {
    #         "tysiące" : "*1000+",
    #         "tysięcy" : "*1000+",
    #         "tysiąc" : "*1000+"
    #     }
    #     for word, symbol in replacements.items():
    #         elements = elements.replace(word, symbol)
    #     return elements


    def calculate(self):
        try:
            self.recognize = self.r.recognize_google(self.audio_text, language='pl')
            print("Rozpoznane:", self.recognize)

            if self.recognize.lower() == "stop":
                self.exit = True
                self.engine.say("Dzięki za współpracę, do widzenia!")
                self.engine.runAndWait()
                return

            clean_text = self.preprocess_text(self.recognize)
            print("Po przetworzeniu:", clean_text)
            elements = clean_text.split()
            if "tysiące" in elements or "tysiąc" in elements or "tysięcy" in elements:
                elements = self.preprocess_multi_digit(elements)
            while "pierwiastek" in elements or "silnia" in elements:
                elements = self.preprocess_sqrt_fact(elements)

            expression = ''.join([e for e in elements if e != "z"])
            print("Wyrażenie do obliczenia:", expression)
            self.result = eval(expression)
            if math.fmod(self.result, 1.0) == 0:
                self.result = int(self.result)
            else:
                self.result = round(self.result, 2)
            self.engine.say(f"Rezultat to {self.result}")
            print("Rezultat to ", self.result)
            self.engine.runAndWait()

        except Exception as e:
            self.engine.say("Przepraszam, nie rozumiem działania. Spróbuj jeszcze raz")
            self.engine.runAndWait()

    def loop(self):
        while not self.exit:
            self.give_instruction()
            self.calculate()
        self.engine.stop()

if __name__ == '__main__':
    vc = VoiceCalculator()
    vc.loop()

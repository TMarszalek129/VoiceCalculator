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

        self.num_words = {
            "minus": "-",
            "zero": 0, "jeden": 1, "dwa": 2, "trzy": 3, "cztery": 4,
            "pięć": 5, "sześć": 6, "siedem": 7, "osiem": 8, "dziewięć": 9,
            "dziesięć": 10, "jedenaście": 11, "dwanaście": 12, "trzynaście": 13, "czternaście": 14,
            "piętnaście": 15, "szesnaście": 16, "siedemnaście": 17, "osiemnaście": 18, "dziewiętnaście": 19,
            "dwadzieścia": 20, "trzydzieści": 30, "czterdzieści": 40, "pięćdziesiąt": 50,
            "sześćdziesiąt": 60, "siedemdziesiąt": 70, "osiemdziesiąt": 80, "dziewięćdziesiąt": 90,
            "sto": 100, "dwieście": 200, "trzysta": 300, "czterysta": 400, "pięćset": 500,
            "sześćset": 600, "siedemset": 700, "osiemset": 800, "dziewięćset": 900,
            "tysiąc": 1000, "tysiące": 1000, "tysięcy": 1000
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

        text = self.replace_number_words(text)

        return text

    def replace_number_words(self, text):
        words = text.split()
        result = []
        buffer = []

        for word in words:
            if word in self.num_words or word == "minus":
                buffer.append(word)
            else:
                if buffer:
                    try:
                        number = self.parse_number_words(buffer)
                        result.append(str(number))
                    except:
                        result.extend(buffer)
                    buffer = []
                result.append(word)

        if buffer:
            try:
                number = self.parse_number_words(buffer)
                result.append(str(number))
            except:
                result.extend(buffer)

        return ' '.join(result)

    def parse_number_words(self, words):
        total = 0
        current = 0
        negative = False

        for word in words:
            if word == "minus":
                negative = True
            elif word in ["tysiąc", "tysiące", "tysięcy"]:
                if current == 0:
                    current = 1
                total += current * 1000
                current = 0
            elif word in self.num_words:
                current += self.num_words[word]
            else:
                break

        total += current
        return -total if negative else total

    def preprocess_sqrt_fact(self, elements):
        if "pierwiastek" in elements:
            idx = elements.index("pierwiastek")
            expression = "math.sqrt({})"
        elif "silnia" in elements:
            idx = elements.index("silnia")
            expression = "math.factorial({})"
        else:
            return elements

        number = None
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
            print("Błąd:", e)
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

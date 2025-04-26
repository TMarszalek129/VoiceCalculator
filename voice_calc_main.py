import speech_recognition as sr
import pyttsx3
import time
import re
import math

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

        # słownik słów na liczby
        self.word_to_num = {
            "zero": "0", "jeden": "1", "dwa": "2", "trzy": "3", "cztery": "4",
            "pięć": "5", "sześć": "6", "siedem": "7", "osiem": "8", "dziewięć": "9",
            "dziesięć": "10"
        }

    def give_instruction(self):
        with sr.Microphone() as mike:
            self.engine.say("Podaj swoje działanie. Jeśli chcesz zakończyć, powiedz stop.")
            self.engine.runAndWait()
            print("Mów!!!")
            self.r.adjust_for_ambient_noise(mike)
            self.audio_text = self.r.listen(mike, phrase_time_limit=15)
            self.engine.say("Dzięki!")
            self.engine.runAndWait()

    def preprocess_text(self, text):
        text = text.lower()

        # Usuwanie tylko niepotrzebnych fraz
        text = text.replace("równa się", "")

        # Zamiana słów na symbole
        replacements = {
            "plus": "+",
            "minus": "-",
            "razy": "*",  
            "x": "*",    
            "podzielić przez": "/",
            "podzielić": "/",
            "do potęgi": "**",
            "otwórz nawias": "(",
            "zamknij nawias": ")"
        }
        for word, symbol in replacements.items():
            text = text.replace(word, symbol)

        # Zamiana słownych liczb na cyfry
        for word, number in self.word_to_num.items():
            text = re.sub(r'\b{}\b'.format(word), number, text)

        return text

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

            # Obsługa "pierwiastek z liczby" albo "liczba pierwiastek"
            if "pierwiastek" in elements:
                idx = elements.index("pierwiastek")
                number = None
                if idx > 0 and elements[idx-1] == "z" and idx > 1 and elements[idx-2].isdigit():
                    number = int(elements[idx-2])
                elif idx < len(elements)-1 and elements[idx+1] == "z" and idx < len(elements)-2 and elements[idx+2].isdigit():
                    number = int(elements[idx+2])
                elif idx > 0 and elements[idx-1].isdigit():
                    number = int(elements[idx-1])
                elif idx < len(elements)-1 and elements[idx+1].isdigit():
                    number = int(elements[idx+1])

                if number is not None:
                    self.result = math.sqrt(number)
                    self.engine.say(f"Pierwiastek z {number} to {self.result}")
                    self.engine.runAndWait()
                    return

            # Obsługa "silnia z liczby" albo "liczba silnia"
            if "silnia" in elements:
                idx = elements.index("silnia")
                number = None
                if idx > 0 and elements[idx-1] == "z" and idx > 1 and elements[idx-2].isdigit():
                    number = int(elements[idx-2])
                elif idx < len(elements)-1 and elements[idx+1] == "z" and idx < len(elements)-2 and elements[idx+2].isdigit():
                    number = int(elements[idx+2])
                elif idx > 0 and elements[idx-1].isdigit():
                    number = int(elements[idx-1])
                elif idx < len(elements)-1 and elements[idx+1].isdigit():
                    number = int(elements[idx+1])

                if number is not None:
                    self.result = math.factorial(number)
                    self.engine.say(f"Silnia z {number} to {self.result}")
                    self.engine.runAndWait()
                    return

            # Jeśli nie ma jednoargumentowych funkcji, traktuj jako zwykłe działanie
            expression = ''.join([e for e in elements if e != "z"])  # usuwamy "z" tylko w działaniach
            print("Wyrażenie do obliczenia:", expression)
            self.result = eval(expression)
            self.engine.say(f"Rezultat to {self.result}")
            self.engine.runAndWait()

        except Exception as e:
            self.engine.say("Przepraszam, nie rozumiem działania.")
            self.engine.runAndWait()

    def loop(self):
        while not self.exit:
            self.give_instruction()
            self.calculate()
        self.engine.stop()

if __name__ == '__main__':
    vc = VoiceCalculator()
    vc.loop()

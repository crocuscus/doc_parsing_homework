from typing import List, Tuple
from fuzzywuzzy import fuzz, process
import re
import datetime
from datetime import date
class Solution:

    def __init__(self):
        authorities = ["правительство", "государственный совет", "кабинет министров", "cовет министров", "президент", "губернатор", "государственная дума", "глава", "дума"]
        _republics = ["адыгея", "алтай", "башкортостан", "бурятия", "дагестан", "ингушетия", "кабардино-балкария",
                    "калмыкия", "карачево-черкесия", "карелия", "коми", "крым", "марий эл", "мордовия", "саха (якутия)",
                    "северная осетия-алания", "татарстан", "тыва", "удмуртия", "хакасия", "чечня", "чувашия"]
        republics_ = ["чувашской", "удмуртской"]
        edges = ["алтайского", "забайкальского", "камчатского", "краснодарского", "красноярского",
                "пермского", "приморского", "ставропольского", "хабаровского"]
        areas = ["амурской", "архангельской", "астраханской", "белгородской", "брянской",
                 "владимирской", "волгоградской", "вологодской", "воронежской", "ивановской", "иркутской", 
                 "калининградской", "калужской", "кемеровской", "кировской", "костровской", "курганской",
                 "курской", "ленинградской", "липецкой", "магаданской", "московской", "мурманской",
                 "нижегородской", "новгородской", "новосибирской", "омской", "оренбургской", "орловской",
                 "пензенской", "псковской", "ростовской", "рязанской", "самарской", "саратовской",
                 "сахалинской", "свердловской", "смоленской", "тамбовской", "тверской", "томской",
                 "тульской", "тюменской", "ульяновской", "челябинской", "ярославской"]
        ao = ["ямало-ненецкого", "ненецкого", "ханты-мансийского", "чукотского"]
        subjects = ["федерального собрания российской федерации", "российской федерации", "еврейской автономной области"]
        subjects += [x + " республики" for x in republics_]
        subjects += ["республики " + x for x in _republics] 
        subjects += [x + " края" for x in edges]
        subjects += [x + " области" for x in areas]
        subjects += [x + " автономного округа" for x in ao]
        self.full_authorities = [x + " " + y for x in authorities for y in subjects] + [x[-2:] + "ая областная дума" for x in areas]
        print(len(self.full_authorities))
        

    def train(self, train: List[Tuple[str, dict]]) -> None:
        # fit your models here
        pass

    def predict_type(self, txt):
        possible_types = ["постановление", "федеральный закон", "распоряжение", "закон", "указ", "приказ"]
        p = [0] * len(possible_types)
        txt = " ".join(txt.split('\n')).lower()
        for i in range(len(possible_types)):
            p[i] = fuzz.partial_ratio(possible_types[i], txt)
        return possible_types[p.index(max(p))]

    def predict_number(self, text):
        txt = text.split('\n')
        possible_number_prefix = ["№", "N"]
        for line in txt:
            tokens = [i for i in line.split() if i]
            for i in range(len(tokens) - 1):
                if tokens[i] in possible_number_prefix:
                    return tokens[i + 1]
            for i in range(len(tokens)):
                for pre in possible_number_prefix:
                    if tokens[i].startswith(pre):
                        return tokens[i][len(pre):]

    def correct_date(self, day, month, year):
        try:
           date(year, month, day)
        except ValueError:
            return 0
        return 2013 <= year <= 2015


    def format_date(self, day, month, year):
        return date(year, month, day).strftime("%d.%m.%Y")

    def predict_date(self, text):
        magic = "от"
        months = ["январь", "февраль", "март", "апрель", "май", "июнь", "июль", "август", "сентябрь", "октябрь", "ноябрь", "декабрь"]
        txt = text.lower().split('\n')
        for line in txt:
            tokens = [i for i in line.split() if i]
            if len(tokens) > 9:
                continue
            if magic in tokens:
                i = tokens.index(magic) 
                if (i + 3) < len(tokens) and len(tokens[i + 1]) <= 2 and tokens[i + 1].isdigit() and len(tokens[i + 3]) == 4 and tokens[i + 3].isdigit():
                    day = int(tokens[i + 1])
                    year = int(tokens[i + 3])
                    if len(tokens[i + 2]) <= 2 and month.isdigit:
                        month = int(tokens[i + 2])
                        if self.correct_date(day, month, year):
                            return self.format_date(day, month, year)
                    elif process.extractOne(tokens[i + 2], months)[1] > 55  :
                        month = months.index(process.extractOne(tokens[i + 2], months)[0]) + 1
                        if self.correct_date(day, month, year):
                            return self.format_date(day, month, year)
         

                if (i + 1) < len(tokens) and len(tokens[i + 1]) == 10 and tokens[i + 1][:2].isdigit() and tokens[i + 1][3:5].isdigit() and tokens[i + 1][-4:].isdigit():
                    day = int(tokens[i + 1][:2])
                    month = int(tokens[i + 1][3:5])
                    year = int(tokens[i + 1][-4:])
                    if self.correct_date(day, month, year):
                        return self.format_date(day, month, year)
            
            for t in range(1, len(tokens) - 1):
                if len(tokens[t]) > 2 and process.extractOne(tokens[t], months)[1] > 55:
                    try:
                        month = months.index(process.extractOne(tokens[t], months)[0]) + 1
                        year = int(tokens[t + 1])
                        day = int(tokens[t - 1])
                        if self.correct_date(day, month, year):
                            return self.format_date(day, month, year)
                    except ValueError:
                        continue

            for t in range(len(tokens)):
                if len(tokens[t]) == 10:
                    try:
                        day = int(tokens[t][:2])
                        month = int(tokens[t][3:5])
                        year = int(tokens[t][-4:])
                        if self.correct_date(day, month, year):
                            return self.format_date(day, month, year)
                    except ValueError:
                        pass

        year = 2014
        month = 7
        day = 31
        return self.format_date(day, month, year)



    def predict_authority(self, txt):
        txt = txt.lower().split('\n')
        for line in txt:
            if len(line) > 10 and process.extractOne(line, self.full_authorities)[1] > 70:
                return process.extractOne(line, self.full_authorities)[0]
        return ""

    def remove_trash_symbols(self, line):
        trash =  '+\\&^*@®#$`›‘©=/([{%!;}]),'
        for c in trash:
            line = line.replace(c, '')
        line = line.replace('-№', '№')
        return line

    def semi_preprocess(self, txt):
        semitrash = '+\\&^*@®#$`›‘©/='
        for c in semitrash:
            txt = txt.replace(c, '')
        return txt


    def full_preprocess(self, txt):
        txt = txt.split('\n')
        result = []
        for line in txt:
            line = self.remove_trash_symbols(line)
            line = line.strip()
            tokens = [i for i in line.split() if i]
            for d in range(10):
                if str(d) in line:
                    result += [line]
                    break
            for t in tokens:
                if t.isdigit() or t.isalpha():
                    result += [line]
                    break
        return '\n'.join(result)

    def predict_name(self, txt):
        txt = txt.lower().split("\n")
        result = ""
        magic = ["о", "об", "o", "oб"]
        write_result = 0
        for line in txt:
            line = line.strip()
            if write_result and line:
                result += line + " "
            elif not write_result:
                tokens = [i for i in line.split() if i]
                if tokens and tokens[0] in magic:
                    result += line + " "
                    write_result = 1
            elif write_result and not line:
                return result[:-1]


    def predict(self, test: List[str]) -> List[dict]:
        # Do some predictions here and return results
        # Let's return empty result in proper format
        results = []
        for _ in test:
            name = self.predict_name(self.semi_preprocess(_))
            txt = self.full_preprocess(_)
            t = self.predict_type(txt)
            n = self.predict_number(txt)
            d = self.predict_date(txt)
            a = self.predict_authority(txt)
            prediction = {"type": t,
                          "date": d,
                          "number": n,
                          "authority": a,
                          "name": name}
            results.append(prediction)
        return results
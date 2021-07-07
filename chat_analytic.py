from datetime import date, datetime
import re
import emoji
import datefinder
import collections
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from numpy import negative
from textblob import TextBlob

class chatAnalytics :

    #initial for ios version
    is_android = False;
    is_ios = False;

    def __init__(self, text_file) :
        self.__file = text_file.read().decode()
        self.__pattern = re.compile('\d+:\d+\s+-\s+([a-zA-Z0-9]+\s?[a-zA-Z0-9]+\s?[a-zA-Z0-9]+\s?):\s+')
        self.__messengers = re.findall(self.__pattern, self.__file)

    def check_device(self) :
        if (self.__file[0] == '[') :
            self.is_ios = True

            return {
                "device_os": "iOS",
                "device_name": "iPhone",
                "status": self.is_ios
            }
        else :
            self.is_android = True
            
            return {
                "device_os": "Android",
                "device_name": "Android",
                "status": self.is_android
            }

    def detail_chat(self) :
        if (self.__file[0] == '[') :
            message_split = self.__pattern.split(self.__file)
            return message_split
        else :
            messengers = re.findall(self.__pattern, self.__file)

            count_messages = {}
            for each in messengers :
                if each in count_messages.keys() :
                    count_messages[each] += 1
                else :
                    count_messages[each] = 1

            add_space = "\n" + self.__file
            remove_space = " ".join(add_space.split())
            split_text = re.split('/, | - ', remove_space)
            slice_message = split_text[slice(1, len(split_text))]

            new_times = []
            new_texts = []
            self.__text_dates = []
            self.__text_times = []
            self.__text_authors = []
            self.__text_messages = []

            for new_format in range(len(slice_message) -1) :
                text = slice_message[new_format]
                cut_text = text[-15:]
                find_times = datefinder.find_dates(cut_text)
                
                for match in find_times :
                    date_format = match.strftime("%m/%d/%Y, %H:%M:%S")
                    new_times.append(date_format)

                new_texts.append(text[0:len(text)-15+1].strip())

            for time in new_times :
                split = time.split(", ")
                dates = split[0]
                times = split[1]

                self.__text_dates.append(dates)
                self.__text_times.append(times)

            last_message = slice_message[len(slice_message) -1]
            new_texts.append(last_message)

            remove_opening = new_texts[slice(1, len(new_texts))]

            for messages in remove_opening :
                split = messages.split(": ")
                names = split[0]
                texts = split[1]
                
                self.__text_authors.append(names)
                self.__text_messages.append(texts)

            data_table = []

            for data in range(len(self.__text_dates)) :
                data_object = {
                    "date": self.__text_dates[data],
                    "time": self.__text_times[data],
                    "author": self.__text_authors[data],
                    "message": self.__text_messages[data]
                }

                data_table.append(data_object)

            return data_table

    def total_chat(self) :
        if (self.__file[0] == '[') :
            return 'ios'
        else :
            # count day total
            first_date = datetime.strptime(self.__text_dates[0], '%m/%d/%Y')
            last_date = datetime.strptime(self.__text_dates[len(self.__text_dates) - 1], '%m/%d/%Y')
            total_days =  (last_date - first_date).days
            
            # messages total
            messages_total = len(self.__text_messages)
            
            # words total
            words_total = 0
            for word in self.__text_messages :
                split_word = word.split(" ")
                for split_words in split_word :
                    words_total += 1

            # letters total
            letters_total = 0
            for letter in self.__text_messages :
                letters = letter
                for split_letter in letters :
                    letters_total += 1

            data_total_chat = {
                "total_days": total_days,
                "messages_total": messages_total,
                "words_total": words_total,
                "letters_total": letters_total
            }

            return data_total_chat

    def content(self) :
        if (self.__file[0] == '[') :
            return 'ios'
        else :
            # media ommited total
            media_total = 0
            for media in self.__text_messages :
                if media == "<Media omitted>" :
                    media_total += 1

            # emoji total
            emoji_total = 0
            for emojis in self.__text_messages :
                if emojis in emoji.UNICODE_EMOJI['en'] :
                    emoji_total += 1

            # link total
            link_total = 0
            for link in self.__text_messages :
                detec_link = link.find("http")
                if detec_link != -1 :
                    link_total += 1
            
            # gps coordinate
            gps_total = 0
            for gps in self.__text_messages :
                detect_gps = gps.find("location")
                if detect_gps != -1 :
                    gps_total += 1

            content_total_chat = {
                "media_total": media_total,
                "emoji_total": emoji_total,
                "link_total": link_total,
                "gps_total": gps_total
            }

            return content_total_chat

    def timeline(self) :
        day_chat = []
        for day in self.__text_dates :
            day_name = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday','Sunday']
            day_number = datetime.strptime(day, '%m/%d/%Y').weekday()
            days = day_name[day_number]
            day_chat.append(days)

        timeline_chat = collections.Counter(day_chat)
        
        return timeline_chat

    def percentage(self, part, whole) :
        return 100 * float(part)/float(whole)

    def sentiment_analysis(self) :
        negative_list = []
        positive_list = []
        neutral_list = []
        negative = 0
        positive = 0
        neutral = 0

        total_message = len(self.__text_messages)

        for text in self.__text_messages :
            analysis = TextBlob(text)
            score = SentimentIntensityAnalyzer().polarity_scores(text)
            neg = score['neg']
            neu = score['neu']
            pos = score['pos']
            comp = score['compound']

            if neg > pos :
                negative_list.append(text)
                negative += 1
            elif pos > neg :
                positive_list.append(text)
                positive += 1
            elif pos == neg :
                neutral_list.append(text)
                neutral += 1

        positive = format(self.percentage(positive, total_message), '.1f')
        negative = format(self.percentage(negative, total_message), '.1f')
        neutral = format(self.percentage(neutral, total_message), '.1f')

        result_sentiment = {
            "message": {
                "negative": negative_list,
                "neutral": neutral_list,
                "positive": positive_list
            },
            "percentage": {
                "negative": negative,
                "neutral": neutral,
                "positive": positive
            },
        }
        
        return result_sentiment
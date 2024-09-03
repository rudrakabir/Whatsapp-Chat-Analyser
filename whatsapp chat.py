import re
from collections import Counter
from datetime import datetime, timedelta
import emoji

def parse_chat(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    pattern = r'(\[\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}:\d{2}\])\s(.+?):\s([\s\S]*?)(?=\n\[\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}:\d{2}\]|$)'
    matches = re.findall(pattern, content, re.DOTALL)
    
    parsed_messages = []
    for date_str, sender, message in matches:
        try:
            date = datetime.strptime(date_str, '[%d/%m/%y, %H:%M:%S]')
        except ValueError:
            try:
                date = datetime.strptime(date_str, '[%m/%d/%y, %H:%M:%S]')
            except ValueError:
                print(f"Skipping message with invalid date format: {date_str}")
                continue
        parsed_messages.append((date, sender, message.strip()))
    
    # Debug: Print all parsed messages
    for date, sender, message in parsed_messages:
        print(f"Parsed message:\nDate: {date}\nSender: {sender}\nMessage: {message}\n")
    
    return parsed_messages


def analyze_chat(messages):
    results = {}

    # Message count per user
    results['message_count'] = Counter(sender for _, sender, _ in messages)

    # Messages by day of the week
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    results['messages_by_day'] = Counter(days[date.weekday()] for date, _, _ in messages)

    # Top emojis used
    all_emojis = [char for _, _, msg in messages for char in msg if char in emoji.EMOJI_DATA]
    results['top_emojis'] = Counter(all_emojis).most_common(20)

    # Top words used
    all_words = [word.lower() for _, _, msg in messages for word in re.findall(r'\w+', msg)]
    results['top_words'] = Counter(all_words).most_common(20)

    # Time of day messaging
    results['morning_messaging'] = Counter(date.hour for date, _, _ in messages if 0 <= date.hour < 12)
    results['afternoon_evening_messaging'] = Counter(date.hour for date, _, _ in messages if 12 <= date.hour < 24)

    # Time spent messaging (assuming 1 minute per message)
    results['time_spent'] = {sender: timedelta(minutes=count) for sender, count in results['message_count'].items()}

    # Phrase frequency (updated)
    love_phrases = [
        r'\bi\s*love\s*you',  # English
        r'आई\s*लव\s*यू',      # Hindi (transliteration)
        r'मैं\s*तुमसे\s*प्यार\s*करता\s*हूं',  # Hindi
        r'मैं\s*तुमसे\s*प्यार\s*करती\s*हूं',  # Hindi (feminine)
    ]
    love_pattern = '|'.join(love_phrases)
    
    def count_love_phrases(msg):
        print(f"Analyzing message: {msg[:100]}...") # Debug print
        count = len(re.findall(love_pattern, msg, re.IGNORECASE | re.UNICODE))
        print(f"Direct matches found: {count}") # Debug print
        
        # Check for "I love you" in script-like content
        script_lines = re.findall(r'(?:^|\n).*?:.*?(?:\n|$)', msg, re.MULTILINE)
        for line in script_lines:
            print(f"Checking script line: {line.strip()}") # Debug print
            if re.search(love_pattern, line, re.IGNORECASE | re.UNICODE):
                count += 1
                print(f"Match found in script line, new count: {count}") # Debug print
        
        return count

    results['phrase_frequency'] = sum(count_love_phrases(msg) for _, _, msg in messages)
    print(f"Total phrase frequency: {results['phrase_frequency']}") # Debug print


    # First encounter
    results['first_encounter'] = messages[:2]

    # Laugh counter
    laugh_patterns = r'\b(haha|lol|lmao|rofl)\b|😂|🤣'
    results['laugh_counter'] = sum(len(re.findall(laugh_patterns, msg, re.IGNORECASE)) for _, _, msg in messages)

    # Date range
    results['date_range'] = (messages[0][0], messages[-1][0])

    return results

def format_results(results):
    output = "Chat Analysis Results\n\n"

    output += "Message count per user:\n"
    for user, count in results['message_count'].items():
        output += f"{user}: {count}\n"
    output += "\n"

    output += "Messages by day of the week:\n"
    for day, count in results['messages_by_day'].items():
        output += f"{day}: {count}\n"
    output += "\n"

    output += "Top emojis used:\n"
    for emoji, count in results['top_emojis']:
        output += f"{emoji}: {count}\n"
    output += "\n"

    output += "Top words used:\n"
    for word, count in results['top_words']:
        output += f"{word}: {count}\n"
    output += "\n"

    output += "Time of day messaging (morning):\n"
    for hour in range(12):
        output += f"{hour:02d}:00 - {hour:02d}:59: {results['morning_messaging'][hour]}\n"
    output += "\n"

    output += "Time of day messaging (afternoon/evening):\n"
    for hour in range(12, 24):
        output += f"{hour:02d}:00 - {hour:02d}:59: {results['afternoon_evening_messaging'][hour]}\n"
    output += "\n"

    output += "Time spent messaging:\n"
    for user, time in results['time_spent'].items():
        output += f"{user}: {time}\n"
    output += "\n"

    output += f"Phrase frequency ('I love you'): {results['phrase_frequency']}\n\n"

    output += "First encounter:\n"
    for date, sender, message in results['first_encounter']:
        output += f"[{date}] {sender}: {message}\n"
    output += "\n"

    output += f"Laugh counter: {results['laugh_counter']}\n\n"

    output += f"Date range: {results['date_range'][0]} to {results['date_range'][1]}\n"

    return output

# Main execution
file_path = 'samplechat.txt'  # Replace with the actual file path
messages = parse_chat(file_path)
results = analyze_chat(messages)
formatted_results = format_results(results)

print(formatted_results)

# Optionally, save the results to a file
with open('chat_analysis_results.txt', 'w', encoding='utf-8') as file:
    file.write(formatted_results)
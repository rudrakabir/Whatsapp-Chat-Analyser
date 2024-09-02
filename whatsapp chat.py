import re
from collections import Counter
from datetime import datetime
import emoji

def parse_chat(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Regular expression to match the date, time, sender, and message
    pattern = r'(\d{1,2}/\d{1,2}/\d{2,4}),\s(\d{1,2}:\d{2})\s-\s([^:]+):\s(.+)'
    messages = re.findall(pattern, content, re.MULTILINE)
    
    return [
        {
            'date': datetime.strptime(date + ' ' + time, '%d/%m/%Y %H:%M'),
            'sender': sender.strip(),
            'message': message.strip()
        }
        for date, time, sender, message in messages
    ]

def analyze_chat(messages):
    results = {
        'message_count': Counter(),
        'day_of_week': Counter(),
        'emojis': Counter(),
        'words': Counter(),
        'time_of_day_morning': Counter(),
        'time_of_day_afternoon': Counter(),
        'time_spent': Counter(),
        'phrase_frequency': 0,
        'first_encounter': None,
        'laugh_counter': 0,
        'date_range': {'start': None, 'end': None}
    }

    all_senders = set()
    for msg in messages:
        sender = msg['sender']
        all_senders.add(sender)
        date = msg['date']
        message = msg['message']

        # Message count
        results['message_count'][sender] += 1

        # Day of week
        results['day_of_week'][date.strftime('%A')] += 1

        # Emojis
        emojis = [c for c in message if c in emoji.EMOJI_DATA]
        results['emojis'].update(emojis)

        # Words
        words = message.lower().split()
        results['words'].update(words)

        # Time of day
        hour = date.hour
        if 0 <= hour < 12:
            results['time_of_day_morning'][hour] += 1
        else:
            results['time_of_day_afternoon'][hour] += 1

        # Phrase frequency
        if "i love you" in message.lower():
            results['phrase_frequency'] += 1

        # Laugh counter
        if re.search(r'\b(haha|lol|lmao|😂)\b', message.lower()):
            results['laugh_counter'] += 1

        # Date range
        if results['date_range']['start'] is None or date < results['date_range']['start']:
            results['date_range']['start'] = date
        if results['date_range']['end'] is None or date > results['date_range']['end']:
            results['date_range']['end'] = date

    # First encounter
    if len(all_senders) == 2:
        sender1, sender2 = list(all_senders)
        for msg in messages:
            if msg['sender'] in [sender1, sender2]:
                if results['first_encounter'] is None:
                    results['first_encounter'] = []
                results['first_encounter'].append(f"{msg['sender']}: {msg['message']}")
                if len(results['first_encounter']) == 2:
                    break

    return results

def format_results(results):
    output = []

    output.append("Message count per user:")
    for user, count in results['message_count'].items():
        output.append(f"{user}: {count}")

    output.append("\nMessages by day of the week:")
    for day, count in results['day_of_week'].items():
        output.append(f"{day}: {count}")

    output.append("\nTop emojis used:")
    for emoji, count in results['emojis'].most_common(5):
        output.append(f"{emoji}: {count}")

    output.append("\nTop words used:")
    for word, count in results['words'].most_common(10):
        output.append(f"{word}: {count}")

    output.append("\nTime of day messaging (morning):")
    for hour in range(12):
        output.append(f"{hour}:00 - {hour+1}:00: {results['time_of_day_morning'][hour]}")

    output.append("\nTime of day messaging (afternoon/evening):")
    for hour in range(12, 24):
        output.append(f"{hour}:00 - {(hour+1)%24}:00: {results['time_of_day_afternoon'][hour]}")

    output.append(f"\nPhrase frequency ('I love you'): {results['phrase_frequency']}")

    if results['first_encounter']:
        output.append("\nFirst encounter:")
        output.extend(results['first_encounter'])

    output.append(f"\nLaugh counter: {results['laugh_counter']}")

    output.append("\nDate range:")
    output.append(f"Start: {results['date_range']['start'].strftime('%Y-%m-%d %H:%M')}")
    output.append(f"End: {results['date_range']['end'].strftime('%Y-%m-%d %H:%M')}")

    return "\n".join(output)

def main(file_path):
    messages = parse_chat(file_path)
    results = analyze_chat(messages)
    output = format_results(results)
    print(output)

if __name__ == "__main__":
    file_path = "path_to_your_chat_file.txt"  # Replace with the actual file path
    main(file_path)
import json
import os

class LanguageManager:
    def __init__(self):
        # Erstelle den vollständigen Pfad zur JSON-Datei
        current_dir = os.path.dirname(os.path.abspath(__file__))  # Aktuelles Verzeichnis
        json_path = os.path.join(current_dir, 'language_texts.json')  # Pfad zur JSON-Datei

        # Lade die Texte aus der JSON-Datei
        with open(json_path, 'r', encoding='utf-8') as file:
            self.texts = json.load(file)

    def get_text(self, language, text_key):
        # Gib den entsprechenden Text basierend auf der Sprache zurück
        return self.texts.get(language, {}).get(text_key, self.texts['de'].get(text_key, 'Text not found'))


#aufrufbar
# preferred_language = UserSettings.objects.get(customer_user=user_new).preferred_language
 #       greeting_text = language_manager.get_text(preferred_language, 'greeting')
  #      print(greeting_text)
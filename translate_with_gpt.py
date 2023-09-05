import polib
import settings
import os, sys, getopt
import openai
import time
import settings
from get_languages import get_languages

def validate_settings():
    if not settings.OPENAI_KEY:
        print('OPENAI_KEY is not defined. Please fill this variable in settings file')
        sys.exit(2)

    if not settings.CONTEXT:
        print('CONTEXT is not defined. Please fill this variable in settings file')
        sys.exit(2)

    if not settings.LANGUAGES_TO_TRANSLATE:
        print('LANGUAGES_TO_TRANSLATE is not defined. Please fill this variable in settings file')
        sys.exit(2)

    if not settings.FILES_TO_TRANSLATE:
        print('FILES_TO_TRANSLATE is not defined. Please fill this variable in settings file')
        sys.exit(2)
    return True

def main(argv):

    validate_settings()
    languages = get_languages()
    openai.api_key = settings.OPENAI_KEY

    for file in settings.FILES_TO_TRANSLATE:
        for language in settings.LANGUAGES_TO_TRANSLATE:
            
            print('gerando a tradução do arquivo: {file} no idioma {language}'.format(file=file, language=languages[language]))
            pofile = polib.pofile(file)
            new_file = '/'.join(file.split('/')[:-1]) + '/' + language + '.po'

            for entry in pofile:
                found_error = False

                while found_error:
                    try:
                        response = openai.ChatCompletion.create(
                            model="gpt-3.5-turbo",
                            messages=[{"role": "user", "content": "Translate from english to {language}. Please do not explain the terms. Translate the following text: {msgid}".format(
                                language=languages[language],
                                context=settings.CONTEXT,
                                msgid=entry.msgid)}],
                            temperature=0,
                            max_tokens=256
                        )
                    except Exception as e:
                        print(e)
                    else:
                        found_error = False
                        time.sleep(0.1)
                        text = response
                        entry.msgstr = response.choices[0].get('message').get('content')
                        print(entry.msgid, entry.msgstr)
                        pofile.save(new_file)

if __name__ == "__main__":
   main(sys.argv[1:])
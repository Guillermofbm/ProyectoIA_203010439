import random


def handle_response(message) -> str:
    p_message = message.lower()
    if p_message == '$hola':
        return 'Buen dia como estas?!'

    if p_message == '$random':
        return str(random.randint(1, 6))

    if p_message == '$ayuda':
        return "`Prueba escribir $registro`"


    #  return 'Yeah, I don\'t know. Try typing "!help".'
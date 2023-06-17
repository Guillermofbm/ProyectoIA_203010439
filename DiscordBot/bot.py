import discord
import responses
import re
import datetime
import random
import asyncio
import json

# Send messages
async def send_message(message, user_message, is_private):
    try:
        response = responses.handle_response(user_message)
        await message.author.send(response) if is_private else await message.channel.send(response)

    except Exception as e:
        print(e)


def load_users():
    try:
        with open("users.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
def save_users(users):
    with open("users.json", "w") as file:
        json.dump(users, file)

def run_discord_bot():
    TOKEN = 'MTExNzU0NzUzMzQ1NjEyNTk5Mw.GHaFiQ.agU74eIMNqLwQV_EFlNgLciClwxYXSgggBmDFA'
    intents = discord.Intents.default()  # Create an instance of Intents
    intents.message_content = True
    intents.typing = False  # Disable typing events if you don't need them
    intents.presences = False  # Disable presence events if you don't need them
    intents.members = True

    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print(f'{client.user} is now running!')

    @client.event
    async def on_member_join(member):
        welcome_channel = discord.utils.get(member.guild.text_channels, name="bienvenidas")
        await welcome_channel.send(f'¡Bienvenido/a, {member.mention}! ¡Espero que te diviertas en este servidor!')

    @client.event
    async def on_message(message):
        # Make sure bot doesn't get stuck in an infinite loop

        server_name = client.get_guild(685574146737963038)
        if "$miembros" == message.content.lower():
           await message.channel.send(f"```py\n{server_name.member_count}```")
    #CALCULO
        if message.content.startswith("$calcular"):
            # Obtener la expresión matemática del mensaje
            expression = re.search(r"\$calcular\s(.+)", message.content)
            if expression:
                try:
                    result = eval(expression.group(1))
                    await message.channel.send(f"El resultado es: {result}")
                except Exception:
                    await message.channel.send("No se pudo calcular la expresión.")
            else:
                await message.channel.send("Debes proporcionar una expresión matemática.")
    #LISTA
        if "$actividad" == message.content.lower():
            online = 0
            idle = 0
            offline = 0

            for m in server_name.members:
                if str(m.status) == "online":
                    online += 1
                if str(m.status) == "offline":
                    offline += 1
                else:
                    idle += 1
            await message.channel.send(f"```Online: {online+1}.\nIdle/busy/dnd: {idle}.\nOffline: {offline}```")
    #TIEMPO
        if message.content.lower() == "$tiempo":
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            await message.channel.send(f"La hora actual es: {current_time}")

        if message.author == client.user:
            return

    #BANEO POR MENSAJE
        prohibido = ["alcohol", "+18", "spam"]
        if not message.author.bot:  # Evita que el bot responda a otros bots
            content = message.content.lower()
            for word in prohibido:
                if word in content:
                    # Banear al usuario que usó una palabra prohibida
                    await message.author.ban(reason="Uso de palabra prohibida")
                    # Enviar un mensaje al canal de registro o moderación
                    await message.channel.send(
                        f"Usuario {message.author.name} ha sido baneado por uso de palabra prohibida.")
                    break  # Detener la verificación después de encontrar una palabra prohibida
    #DESBANEO
        if message.content.startswith("$desbanear"):
            # Obtener el ID del usuario a desbanear del mensaje
            user_id = message.content.split("$desbanear ", 1)[1]
            # Intentar desbanear al usuario
            try:
                user = await client.fetch_user(user_id)
                await message.guild.unban(user)
                await message.channel.send(f"Usuario {user.name} ha sido desbaneado.")
            except discord.NotFound:
                await message.channel.send("No se pudo encontrar al usuario.")
            except discord.errors.Forbidden:
                await message.channel.send("No tengo los permisos para desbanear usuarios.")
    #MINIJUEGO
        if message.content.lower() == "$adivina":
            # Generar un número aleatorio entre 1 y 100
            secret_number = random.randint(1, 100)
            await message.channel.send(
                "¡Bienvenido/a a Adivina el número! Estoy pensando en un número del 1 al 100. ¡Adivina cuál es!")

            def check(guess):
                return guess.author == message.author and guess.channel == message.channel

            # Esperar la respuesta del jugador
            while True:
                try:
                    guess = await client.wait_for("message", check=check,
                                                  timeout=60)  # Esperar hasta 60 segundos por una respuesta
                    if guess.content.lower() == "salir":
                        await message.channel.send("¡Gracias por jugar! Hasta luego.")
                        break
                    elif not guess.content.isdigit():
                        await message.channel.send("Ingresa un número válido.")
                        continue
                    elif int(guess.content) < secret_number:
                        await message.channel.send("Es un número más alto.")
                    elif int(guess.content) > secret_number:
                        await message.channel.send("Es un número más bajo.")
                    else:
                        await message.channel.send(f"¡Felicidades! ¡Has adivinado el número {secret_number}!")
                        break
                except asyncio.TimeoutError:
                    await message.channel.send("Se agotó el tiempo. ¡El juego ha terminado!")
    #ALARMA
        if message.content.startswith("$alarma"):
            # Obtener el tiempo de espera y el mensaje de la alarma del mensaje
            args = message.content.split("$alarma ", 1)[1].split(",")
            try:
                # Convertir el tiempo de espera a segundos (puedes usar otros formatos de tiempo si lo deseas)
                time = int(args[0])
                # Obtener el mensaje de la alarma
                alarm_message = args[1]
                await message.channel.send(f"La alarma sonara en {time} segundos!!")
                # Esperar el tiempo especificado
                await asyncio.sleep(time)
                # Enviar el mensaje de la alarma al canal
                await message.channel.send(f"{message.author.mention}, ¡Alarma! {alarm_message}")
            except (ValueError, IndexError):
                await message.channel.send(
                    "Uso incorrecto. El formato correcto es: $alarma tiempo_en_segundos,mensaje_de_alarma")

    #ECONOMIA

    #SALDO
        if message.content.startswith("$saldo"):
            users = load_users()
            user_id = str(message.author.id)

            if user_id in users:
                balance = users[user_id]["balance"]
                await message.channel.send(f"Tu saldo es: {balance} monedas")
            else:
                await message.channel.send("No tienes una cuenta. ¡Regístrate usando $registro!")
    #REGISTRO
        if message.content.startswith("$registro"):
            users = load_users()
            user_id = str(message.author.id)

            if user_id not in users:
                users[user_id] = {
                    "balance": 10
                }
                save_users(users)
                await message.channel.send("¡Cuenta registrada con éxito!")
            else:
                await message.channel.send("Ya tienes una cuenta.")
    #APUESTA
        if message.content.startswith("$apuesta"):
            users = load_users()
            user_id = str(message.author.id)
            bet_amount = int(message.content.split("$apuesta ", 1)[1])

            if user_id in users:
                balance = users[user_id]["balance"]
                if balance >= bet_amount:
                    # Simular el resultado de la apuesta (50% de probabilidad de ganar)
                    if random.random() < 0.5:
                        users[user_id]["balance"] += bet_amount
                        save_users(users)
                        await message.channel.send(f"¡Has ganado {bet_amount} monedas!")
                    else:
                        users[user_id]["balance"] -= bet_amount
                        save_users(users)
                        await message.channel.send(f"Has perdido {bet_amount} monedas.")
                else:
                    await message.channel.send("No tienes suficientes monedas para hacer esa apuesta.")
            else:
                await message.channel.send("No tienes una cuenta. ¡Regístrate usando $registro!")
    #MODIFICAR MOD
        if message.content.startswith("$mod"):
            if message.author.guild_permissions.administrator:
                users = load_users()
                args = message.content.split("$mod ", 1)[1].split(",")

                if len(args) != 2:
                    await message.channel.send("El formato correcto es: $modificar_saldo NOMBRE_DE_USUARIO,NUEVO_SALDO")
                else:
                    username = args[0]
                    new_balance = int(args[1])

                    if username in users:
                        users[username]["balance"] = new_balance
                        save_users(users)
                        await message.channel.send("Saldo modificado con éxito.")
                    else:
                        await message.channel.send("El usuario no existe.")
            else:
                await message.channel.send("No tienes permisos para usar este comando.")

    #Usuarios Registrados
        if message.content.startswith("$usuarios"):
            if message.author.guild_permissions.administrator:
                users = load_users()

                if users:
                    user_list = ""
                    for user_id, user_data in users.items():
                        member = message.guild.get_member(int(user_id))
                        if member:
                            username = member.name
                            user_list += f"ID: {user_id} | Nombre: {username}\n"
                    if user_list:
                        await message.channel.send(f"Usuarios registrados:\n{user_list}")
                    else:
                        await message.channel.send("No se encontraron usuarios registrados.")
                else:
                    await message.channel.send("No hay usuarios registrados.")
            else:
                await message.channel.send("No tienes permisos para usar este comando.")

    #Eliminar Usuario
        if message.content.startswith("$eliminar"):
            if message.author.guild_permissions.administrator:
                users = load_users()
                user_id = message.content.split("$eliminar ", 1)[1]

                if user_id in users:
                    del users[user_id]
                    save_users(users)
                    await message.channel.send("Usuario eliminado con éxito.")
                else:
                    await message.channel.send("El usuario no existe.")
            else:
                await message.channel.send("No tienes permisos para usar este comando.")
    #Comprar LVL UP
        if message.content.startswith("$lvlup"):
            users = load_users()
            user_id = str(message.author.id)
            role_name = message.content.split("$lvlup ", 1)[1]

            # Verificar si el usuario tiene suficientes monedas
            if user_id in users:
                balance = users[user_id]["balance"]
                if balance >= 50:  # El costo para obtener el rol es de 200 monedas (ajusta el costo según tus necesidades)
                    # Buscar el rol por nombre
                    target_role = discord.utils.get(message.guild.roles, name=role_name)
                    if target_role:
                        # Añadir el rol al usuario
                        await message.author.add_roles(target_role)

                        # Restar el costo del saldo del usuario
                        users[user_id]["balance"] -= 50
                        save_users(users)

                        await message.channel.send(
                            f"{message.author.mention}, has obtenido el rol {role_name} pagando 50 monedas.")
                    else:
                        await message.channel.send(f"No se encontró el rol {role_name}.")
                else:
                    await message.channel.send(f"{message.author.mention}, no tienes suficientes monedas para obtener el rol.")
            else:
                await message.channel.send("No tienes una cuenta. ¡Regístrate usando $registro!")
    #TRANSFERENCIA
        if message.content.startswith("$transferir"):
            users = load_users()
            sender_id = str(message.author.id)
            receiver_id = message.content.split("$transferir ", 1)[1].split(" ")[0]
            amount = int(message.content.split(" ")[2])
            await message.channel.send(f"Transfiriendo {amount} monedas a {receiver_id}.")

            # Verificar si el remitente tiene suficientes monedas
            if sender_id in users:
                sender_balance = users[sender_id]["balance"]
                if sender_balance >= amount:
                    # Verificar si el receptor existe
                    if receiver_id in users:
                        # Transferir monedas del remitente al receptor
                        users[sender_id]["balance"] -= amount
                        users[receiver_id]["balance"] += amount
                        save_users(users)

                        sender_name = message.author.name
                        receiver_name = client.get_user(int(receiver_id)).name

                        await message.channel.send(f"{sender_name} ha transferido {amount} monedas a {receiver_name}.")
                    else:
                        await message.channel.send(f"El receptor {receiver_id} no está registrado.")
                else:
                    missing = amount-users[sender_id]["balance"]
                    await message.channel.send(f"No tienes suficientes monedas para realizar la transferencia. Te Faltan {missing} monedas.")
            else:
                await message.channel.send("No tienes una cuenta. ¡Regístrate usando $registro!")

        # Get data about the user
        username = str(message.author)
        user_message = str(message.content.strip())
        channel = str(message.channel)

        # Debug printing
        print(f"{username} said: '{user_message}' ({channel})")

        # If the user message contains a '?' in front of the text, it becomes a private message

        if user_message[0] == '?':
            user_message = user_message[1:]  # [1:] Removes the '?'
            await send_message(message, user_message, is_private=True)
        else:
            await send_message(message, user_message, is_private=False)

    # Remember to run your bot with your personal TOKEN
    client.run(TOKEN)
from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import join_room, leave_room, send, SocketIO
from cryptography.fernet import Fernet
import random
from string import ascii_uppercase

app = Flask(__name__)
app.config["SECRET_KEY"] = "secretKey"

socketio = SocketIO(app)

rooms = {}
encryption_key = Fernet.generate_key()
cipher_suite = Fernet(encryption_key)


def generate_unique_code(length):
    while True:
        code = "".join(random.choice(ascii_uppercase) for _ in range(length))
        if code not in rooms:
            break
    return code


def is_name_available(room, name):
    if room in rooms and "used_names" in rooms[room]:
        return name not in rooms[room]["used_names"]
    return True


def encrypt_message(message):
    return cipher_suite.encrypt(message.encode())


def decrypt_message(encrypted_message):
    return cipher_suite.decrypt(encrypted_message).decode()


@app.route("/", methods=["POST", "GET"])
def home():
    session.clear()
    if request.method == "POST":
        name = request.form.get("name")
        code = request.form.get("code")
        join = request.form.get("join", False)
        create = request.form.get("Create", False)

        if not name:
            return render_template("home.html", error="Please enter a name.", code=code, name=name)

        if not is_name_available(code, name):
            return render_template("home.html", error="Name already exists in the room. Please choose another name.", code=code, name=name)

        if join != False and not code:
            return render_template("home.html", error="Please enter a room code.", code=code, name=name)

        room = code
        if create != False:
            room = generate_unique_code(4)
            rooms[room] = {"members": 0, "messages": [], "used_names": set()}
        elif code not in rooms:
            return render_template("home.html", error="Room does not exist.", code=code, name=name)

        session["room"] = room
        session["name"] = name
        rooms[room]["used_names"].add(name)
        return redirect(url_for("room"))

    return render_template("home.html")

@app.route("/room")
def room():
    room = session.get("room")
    if room is None or session.get("name") is None or room not in rooms:
        return redirect(url_for("home"))
    return render_template("room.html", code=room, messages=rooms[room]["messages"])

@socketio.on("message")
def message(data):
    room = session.get("room")
    if room not in rooms:
        return

    original_message = data["data"]
    encrypted_message = encrypt_message(original_message)

    content = {
        "name": session.get("name"),
        "message": encrypted_message,
        "original_message": original_message,
    }

    send(content, to=room)
    rooms[room]["messages"].append(content)

    print(f"{session.get('name')} said (original): {original_message}")
    print(f"{session.get('name')} said (encrypted): {encrypted_message}")

@socketio.on("connect")
def connect(auth):
    room = session.get("room")
    name = session.get("name")
    if not room or not name:
        return
    if room not in rooms:
        leave_room(room)
        return
    join_room(room)
    
    # Instead of using send, emit the "message" event
    socketio.emit("message", {"name": name, "original_message": "has entered the room"}, room=room)

    rooms[room]["members"] += 1
    print(f"{name} joined room {room}")


@socketio.on("disconnect")
def disconnect():
    room = session.get("room")
    name = session.get("name")
    leave_room(room)

    if room in rooms:
        rooms[room]["members"] -= 1
        if rooms[room]["members"] <= 0:
            del rooms[room]

    # Instead of using send, emit the "message" event
    socketio.emit("message", {"name": name, "original_message": "has left the room"}, room=room)

    print(f"{name} has left the room {room}")

    
if __name__ == "__main__":
    socketio.run(app, debug=True, use_reloader=False, allow_unsafe_werkzeug=True)
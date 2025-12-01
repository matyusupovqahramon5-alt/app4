from flask import Flask, render_template_string
from flask_socketio import SocketIO, emit
import eventlet

# Eventlet monkey patch (muhim!)
eventlet.monkey_patch()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'render_chat_2025'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Xabarlar (server qayta ishga tushsa yo‘qoladi, lekin tezlik uchun shunday)
messages = []

HTML = """<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Render Chat 24/7</title>
    <script src="https://cdn.socket.io/4.7.5/socket.io.min.js"></script>
    <style>
        body{margin:0;background:#0d1117;color:#c9d1d9;font-family:system-ui,-apple-system,sans-serif;height:100vh;display:flex;flex-direction:column}
        #messages{flex:1;overflow-y:auto;padding:20px;background:#010409;}
        .msg{margin:8px 0;padding:12px 18px;border-radius:18px;max-width:75%;word-wrap:break-word;position:relative;}
        .mine{background:#238636;color:white;margin-left:auto;border-bottom-right-radius:4px;}
        .other{background:#30363d;color:#c9d1d9;border-bottom-left-radius:4px;}
        .name{font-size:13px;font-weight:600;margin-bottom:4px;opacity:0.9;}
        .time{font-size:11px;opacity:0.7;position:absolute;bottom:4px;right:12px;}
        form{padding:12px;background:#0d1117;border-top:1px solid #30363d;display:flex;gap:10px;position:sticky;bottom:0;}
        input{flex:1;background:#30363d;color:white;border:none;border-radius:25px;padding:14px 18px;font-size:16px;outline:none;}
        button{background:#238636;color:white;border:none;border-radius:50%;width:50px;height:50px;cursor:pointer;font-size:20px;}
        button:hover{background:#2ea043;}
        h1{text-align:center;padding:15px;color:#58a6ff;font-size:22px;margin:0;border-bottom:1px solid #30363d;}
    </style>
</head>
<body>
    <h1>⚡ Render Chat 24/7</h1>
    <div id="messages"></div>
    <form onsubmit="send();return false;">
        <input id="name" placeholder="Ismingizni yozing" value="" required>
        <input id="text" placeholder="Xabar yozing..." autocomplete="off" required autofocus>
        <button type="submit">➤</button>
    </form>

<script>
    const socket = io();
    let myName = localStorage.getItem("chat_name") || "";
    document.getElementById("name").value = myName;

    socket.on("new_message", data => {
        const div = document.createElement("div");
        div.className = "msg " + (data.name === myName ? "mine" : "other");
        div.innerHTML = `
            <div class="name">${data.name}</div>
            ${data.text}
            <div class="time">${data.time}</div>
        `;
        document.getElementById("messages").appendChild(div);
        div.scrollIntoView({behavior:"smooth"});
    });

    function send() {
        let name = document.getElementById("name").value.trim();
        let text = document.getElementById("text").value.trim();
        if (!name || !text) return;
        
        localStorage.setItem("chat_name", name);
        myName = name;
        
        socket.emit("message", {name: name, text: text});
        document.getElementById("text").value = "";
    }

    document.getElementById("text").addEventListener("keypress", e => {
        if (e.key === "Enter") send();
    });
</script>
</body>
</html>"""

@app.route("/")
def index():
    return render_template_string(HTML)

@socketio.on("message")
def handle_message(data):
    name = data["name"][:25]
    text = data["text"][:1000]
    time = eventlet.import_patched('datetime').datetime.now().strftime("%H:%M")
    
    msg = {"name": name, "text": text, "time": time}
    messages.append(msg)
    if len(messages) > 500:
        messages.pop(0)
    
    emit("new_message", msg, broadcast=True)

if __name__ == "__main__":
    socketio.run(app)
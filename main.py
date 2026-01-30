import tkinter as tk
from tkinter import ttk, messagebox
import discord
import asyncio
import threading
import json
import os
import time

BOT_TOKEN = "Your_Bot's_Token"

os.system("")
os.system("cls")

ASCII_ART = [
"██████╗██╗     ███████╗██╗   ██╗██╗  ██╗",
"██╔════╝██║     ██╔════╝╚██╗ ██╔╝╚██╗██╔╝",
"██║     ██║     █████╗   ╚████╔╝  ╚███╔╝ ",
"██║     ██║     ██╔══╝    ╚██╔╝   ██╔██╗ ",
"╚██████╗███████╗███████╗   ██║   ██╔╝ ██╗",
"╚═════╝╚══════╝╚══════╝   ╚═╝   ╚═╝  ╚═╝"
]

def gradient(i, total):
    r1, g1, b1 = 180, 30, 30
    r2, g2, b2 = 255, 200, 80
    t = i / (total - 1)
    r = int(r1 + (r2 - r1) * t)
    g = int(g1 + (g2 - g1) * t)
    b = int(b1 + (b2 - b1) * t)
    return f"\033[38;2;{r};{g};{b}m"

for i, line in enumerate(ASCII_ART):
    print(gradient(i, len(ASCII_ART)) + line + "\033[0m")
    time.sleep(0.25)

time.sleep(1)

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.messages = True
intents.dm_messages = True
intents.members = True

client = discord.Client(intents=intents)

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

guild_cache = {}
channel_cache = {}
message_cache = []

current_target = None

def run_async(coro):
    asyncio.run_coroutine_threadsafe(coro, loop)

@client.event
async def on_ready():
    guild_cache.clear()
    for g in client.guilds:
        guild_cache[g.name] = g.id
    root.after(0, lambda: guild_combo.config(values=list(guild_cache.keys())))
    status_label.config(text=f"Logged in as {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if current_target and message.guild:
        t, i = current_target
        if t == "channel" and message.channel.id == i:
            add_message(message)
    if current_target and not message.guild:
        t, i = current_target
        if t == "dm" and message.author.id == i:
            add_message(message)

def add_message(msg):
    ts = msg.created_at.strftime("%H:%M:%S")
    line = f"[{ts}] {msg.author.name}: {msg.content}\n"
    def ui():
        chat_box.insert(tk.END, line)
        if auto_scroll.get():
            chat_box.see(tk.END)
    root.after(0, ui)

async def start_bot():
    try:
        await client.start(BOT_TOKEN)
    except discord.LoginFailure:
        messagebox.showerror("Error", "Invalid bot token")

async def load_channels(guild_id):
    guild = client.get_guild(int(guild_id))
    if not guild:
        return
    channel_cache.clear()
    for ch in guild.text_channels:
        channel_cache[ch.name] = ch.id
    root.after(0, lambda: channel_combo.config(values=list(channel_cache.keys())))

async def load_history(target, limit):
    chat_box.delete("1.0", tk.END)
    t, i = target
    if t == "channel":
        ch = client.get_channel(i)
        async for msg in ch.history(limit=limit, oldest_first=True):
            add_message(msg)
    elif t == "dm":
        user = await client.fetch_user(i)
        ch = user.dm_channel or await user.create_dm()
        async for msg in ch.history(limit=limit, oldest_first=True):
            add_message(msg)

def build_embed(d):
    if not d["enabled"]:
        return None
    embed = discord.Embed(
        title=d["title"] or None,
        description=d["description"] or None,
        color=int(d["color"], 16) if d["color"] else 0x5865F2
    )
    if d["footer"]:
        embed.set_footer(text=d["footer"])
    if d["thumbnail"]:
        embed.set_thumbnail(url=d["thumbnail"])
    if d["image"]:
        embed.set_image(url=d["image"])
    return embed

async def send_message(content, embed_data):
    if not current_target:
        return
    embed = build_embed(embed_data)
    t, i = current_target
    if t == "channel":
        await client.get_channel(i).send(content=content or None, embed=embed)
    elif t == "dm":
        user = await client.fetch_user(i)
        ch = user.dm_channel or await user.create_dm()
        await ch.send(content=content or None, embed=embed)

def on_guild_select(e):
    run_async(load_channels(guild_cache[guild_combo.get()]))

def on_channel_select(e):
    global current_target
    cid = channel_cache[channel_combo.get()]
    current_target = ("channel", cid)
    run_async(load_history(current_target, int(history_combo.get())))

def on_dm_open():
    global current_target
    uid = int(dm_id_entry.get())
    current_target = ("dm", uid)
    run_async(load_history(current_target, int(history_combo.get())))

def on_send():
    content = input_entry.get().strip()
    input_entry.delete(0, tk.END)
    embed_data = {
        "enabled": embed_enabled.get(),
        "title": embed_title.get(),
        "description": embed_desc.get("1.0", tk.END).strip(),
        "color": embed_color.get().replace("#", ""),
        "footer": embed_footer.get(),
        "thumbnail": embed_thumb.get(),
        "image": embed_image.get()
    }
    run_async(send_message(content, embed_data))

root = tk.Tk()
root.title("Cleyx baba valla billa 10 numara?")
root.geometry("1200x900")

dark_mode = True

def apply_theme():
    bg = "#0d0f14" if dark_mode else "#f2f2f2"
    fg = "#e6e6e6" if dark_mode else "#111111"
    entry = "#1a1d24" if dark_mode else "#ffffff"
    btn = "#222633" if dark_mode else "#dddddd"
    root.configure(bg=bg)
    for w in root.winfo_children():
        recolor(w, bg, fg, entry, btn)

def recolor(w, bg, fg, entry, btn):
    try:
        if isinstance(w, tk.Frame):
            w.configure(bg=bg)
        elif isinstance(w, tk.Label):
            w.configure(bg=bg, fg=fg)
        elif isinstance(w, (tk.Entry, tk.Text)):
            w.configure(bg=entry, fg=fg, insertbackground=fg)
        elif isinstance(w, tk.Button):
            w.configure(bg=btn, fg=fg)
        elif isinstance(w, tk.Checkbutton):
            w.configure(bg=bg, fg=fg, selectcolor=bg)
    except:
        pass
    for c in w.winfo_children():
        recolor(c, bg, fg, entry, btn)

def toggle_theme():
    global dark_mode
    dark_mode = not dark_mode
    apply_theme()

auto_scroll = tk.BooleanVar(value=True)
embed_enabled = tk.BooleanVar()

status_label = tk.Label(root, text="Logging in...")
status_label.pack()

top = tk.Frame(root)
top.pack()

guild_combo = ttk.Combobox(top, width=30, state="readonly")
guild_combo.pack(side=tk.LEFT)
guild_combo.bind("<<ComboboxSelected>>", on_guild_select)

channel_combo = ttk.Combobox(top, width=30, state="readonly")
channel_combo.pack(side=tk.LEFT)
channel_combo.bind("<<ComboboxSelected>>", on_channel_select)

history_combo = ttk.Combobox(top, values=["50","100","500","1000"], width=10)
history_combo.set("50")
history_combo.pack(side=tk.LEFT)

tk.Checkbutton(top, text="Auto-scroll", variable=auto_scroll).pack(side=tk.LEFT)
tk.Button(top, text="🌙 / ☀️", command=toggle_theme).pack(side=tk.RIGHT)

main = tk.Frame(root)
main.pack(fill=tk.BOTH, expand=True)

left = tk.Frame(main)
left.pack(side=tk.LEFT, fill=tk.Y)

tk.Label(left, text="Manual DM Open").pack()
dm_id_entry = tk.Entry(left)
dm_id_entry.pack()
tk.Button(left, text="Open DM by ID", command=on_dm_open).pack()

chat_box = tk.Text(main)
chat_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

bottom = tk.Frame(root)
bottom.pack(fill=tk.X)

input_entry = tk.Entry(bottom)
input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
tk.Button(bottom, text="Send", command=on_send).pack(side=tk.LEFT)

emb = tk.Frame(root)
emb.pack(fill=tk.X)

tk.Checkbutton(emb, text="Enable Embed", variable=embed_enabled).pack()

tk.Label(emb, text="Embed Title").pack()
embed_title = tk.Entry(emb); embed_title.pack(fill=tk.X)

tk.Label(emb, text="Embed Description").pack()
embed_desc = tk.Text(emb, height=3); embed_desc.pack(fill=tk.X)

tk.Label(emb, text="Embed Color (hex, no #)").pack()
embed_color = tk.Entry(emb); embed_color.pack(fill=tk.X)

tk.Label(emb, text="Embed Footer").pack()
embed_footer = tk.Entry(emb); embed_footer.pack(fill=tk.X)

tk.Label(emb, text="Thumbnail URL").pack()
embed_thumb = tk.Entry(emb); embed_thumb.pack(fill=tk.X)

tk.Label(emb, text="Image URL").pack()
embed_image = tk.Entry(emb); embed_image.pack(fill=tk.X)

apply_theme()

threading.Thread(target=lambda: loop.run_forever(), daemon=True).start()
run_async(start_bot())

root.mainloop()

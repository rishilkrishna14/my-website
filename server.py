# server.py
import asyncio
import random
import string
import time
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import socketio

from syllabus_data import get_curriculum_tree, get_questions, get_chapter_pdf_data, get_subtopics, SYLLABUS

# Initialize Socket.IO and FastAPI
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
app = FastAPI(title="EduBattle Multiplayer API")
socket_app = socketio.ASGIApp(sio, other_asgi_app=app)

# In-memory storage for rooms and matchmaking
rooms: Dict[str, Dict[str, Any]] = {}
random_queue: List[Dict[str, Any]] = []

def generate_room_code(length=5) -> str:
    letters = string.ascii_uppercase + "23456789"
    while True:
        code = "".join(random.choice(letters) for _ in range(length))
        if code not in rooms:
            return code

# REST Endpoints
@app.get("/api/curriculum")
async def api_curriculum():
    return get_curriculum_tree()

@app.get("/api/subtopics")
async def api_subtopics(board: str = "State Board", grade: str = "6", subject: str = "Science", chapter: str = ""):
    return {"subtopics": get_subtopics(board, grade, subject, chapter)}

@app.get("/api/study-material")
@app.get("/api/chapter-pdf")
async def api_chapter_pdf(board: str = "State Board", grade: str = "6", subject: str = "Science", chapter: str = "", subtopic: str = ""):
    return get_chapter_pdf_data(board, grade, subject, chapter, subtopic if subtopic else None)

@app.get("/api/textbooks")
async def api_textbooks():
    return {
        "board": "Tamil Nadu State Board (Samacheer Kalvi)",
        "medium": "English Medium",
        "official_portal": "https://textbooksonline.tn.nic.in/",
        "grades": {
            "6": {
                "title": "Class 6 (Standard VI)",
                "terms_note": "Term 1, Term 2, and Term 3 Editions",
                "direct_portal": "https://www.tntextbooks.in/p/6th-books.html",
                "subjects": [
                    {"name": "Science", "topics": "Measurements, Force & Motion, Living World of Plants, Electricity, Magnetism", "url": "https://www.tntextbooks.in/p/6th-books.html"},
                    {"name": "Mathematics", "topics": "Numbers, Ratio & Proportion, Fractions, Integers, Perimeter & Area", "url": "https://www.tntextbooks.in/p/6th-books.html"},
                    {"name": "Social Science", "topics": "Indus Civilisation, Ancient Tamilagam, Sangam Age, Universe & Solar System", "url": "https://www.tntextbooks.in/p/6th-books.html"},
                    {"name": "English", "topics": "Prose, Poetry, Supplementary Reader & Grammar", "url": "https://www.tntextbooks.in/p/6th-books.html"}
                ]
            },
            "7": {
                "title": "Class 7 (Standard VII)",
                "terms_note": "Term 1, Term 2, and Term 3 Editions",
                "direct_portal": "https://www.tntextbooks.in/p/7th-books.html",
                "subjects": [
                    {"name": "Science", "topics": "Atomic Structure, Heat & Temp, Light, Cell Biology, Polymer Chemistry", "url": "https://www.tntextbooks.in/p/7th-books.html"},
                    {"name": "Mathematics", "topics": "Number System, Algebra, Direct/Inverse Proportion, Simple Interest", "url": "https://www.tntextbooks.in/p/7th-books.html"},
                    {"name": "Social Science", "topics": "Later Cholas & Pandyas, Vijayanagar Empire, Earth Interior, State Government", "url": "https://www.tntextbooks.in/p/7th-books.html"},
                    {"name": "English", "topics": "Literature, Phonics, Creative Writing & Communicative Grammar", "url": "https://www.tntextbooks.in/p/7th-books.html"}
                ]
            },
            "8": {
                "title": "Class 8 (Standard VIII)",
                "terms_note": "Full Comprehensive Annual Edition",
                "direct_portal": "https://www.tntextbooks.in/p/8th-standard.html",
                "subjects": [
                    {"name": "Science", "topics": "Forces & Pressure, Sound, Acids & Bases, Microorganisms, Space Science", "url": "https://www.tntextbooks.in/p/8th-standard.html"},
                    {"name": "Mathematics", "topics": "Rational Numbers, Algebra, Life Mathematics, Geometry & Graph Theory", "url": "https://www.tntextbooks.in/p/8th-standard.html"},
                    {"name": "Social Science", "topics": "Advent of Europeans, British Rule, Rocks & Soils, The Judiciary, Money & Savings", "url": "https://www.tntextbooks.in/p/8th-standard.html"},
                    {"name": "English", "topics": "Language Skills, Vocabulary, Comprehension & Literature", "url": "https://www.tntextbooks.in/p/8th-standard.html"}
                ]
            }
        }
    }

@app.get("/api/solo-questions")
async def api_solo_questions(
    board: str = "CBSE",
    grade: str = "5",
    subject: str = "Science",
    chapter: str = "",
    game_type: str = "all",
    difficulty: str = "all",
    limit: int = 5
):
    qs = get_questions(board, grade, subject, chapter if chapter else None, game_type, difficulty, limit)
    return {"questions": qs}

class AIGenerateRequest(BaseModel):
    topic: str
    grade: str = "5"
    count: int = 3

@app.post("/api/ai-generate-questions")
async def api_ai_generate(req: AIGenerateRequest):
    # Dynamic educational question generator
    topic = req.topic.strip()
    generated = [
        {
            "type": "quiz",
            "difficulty": "medium",
            "question": f"Key concept in {topic}: Which of the following is most accurate?",
            "options": [
                f"Fundamental principle of {topic}",
                f"Common misconception about {topic}",
                f"Unrelated physical quantity",
                f"Historical myth"
            ],
            "answer": f"Fundamental principle of {topic}",
            "explanation": f"Understanding the core fundamentals of {topic} is vital for Class {req.grade} mastery."
        },
        {
            "type": "fill_in",
            "difficulty": "easy",
            "question": f"In school studies, the basic unit or property associated with {topic} is ______.",
            "answer": "core",
            "explanation": f"This highlights key vocabulary used in Class {req.grade} syllabus."
        },
        {
            "type": "buzz",
            "difficulty": "hard",
            "question": f"Fast Finger: Does {topic} play a crucial role in real-world everyday technology?",
            "options": ["Yes", "No"],
            "answer": "Yes",
            "explanation": f"Nearly all concepts in {topic} find direct applications in daily life and science."
        }
    ]
    return {"questions": generated[:req.count]}


# Competitive Rank Tier System: Bronze 1,2,3 -> Silver 1,2,3 -> Gold 1,2,3 -> Diamond 1,2,3
def get_rank_tier(xp: int) -> Dict[str, str]:
    if xp >= 11000:
        return {"tier": "Diamond", "division": "1", "badge": "💎 Diamond 1", "badge_clean": "Diamond 1", "color": "text-cyan-300", "bg": "bg-cyan-500/20 border-cyan-500/40"}
    elif xp >= 9000:
        return {"tier": "Diamond", "division": "2", "badge": "💎 Diamond 2", "badge_clean": "Diamond 2", "color": "text-cyan-300", "bg": "bg-cyan-500/20 border-cyan-500/40"}
    elif xp >= 7500:
        return {"tier": "Diamond", "division": "3", "badge": "💎 Diamond 3", "badge_clean": "Diamond 3", "color": "text-cyan-300", "bg": "bg-cyan-500/20 border-cyan-500/40"}
    elif xp >= 6000:
        return {"tier": "Gold", "division": "1", "badge": "🥇 Gold 1", "badge_clean": "Gold 1", "color": "text-amber-300", "bg": "bg-amber-500/20 border-amber-500/40"}
    elif xp >= 4800:
        return {"tier": "Gold", "division": "2", "badge": "🥇 Gold 2", "badge_clean": "Gold 2", "color": "text-amber-300", "bg": "bg-amber-500/20 border-amber-500/40"}
    elif xp >= 3800:
        return {"tier": "Gold", "division": "3", "badge": "🥇 Gold 3", "badge_clean": "Gold 3", "color": "text-amber-300", "bg": "bg-amber-500/20 border-amber-500/40"}
    elif xp >= 2900:
        return {"tier": "Silver", "division": "1", "badge": "🥈 Silver 1", "badge_clean": "Silver 1", "color": "text-slate-200", "bg": "bg-slate-400/20 border-slate-400/40"}
    elif xp >= 2100:
        return {"tier": "Silver", "division": "2", "badge": "🥈 Silver 2", "badge_clean": "Silver 2", "color": "text-slate-200", "bg": "bg-slate-400/20 border-slate-400/40"}
    elif xp >= 1400:
        return {"tier": "Silver", "division": "3", "badge": "🥈 Silver 3", "badge_clean": "Silver 3", "color": "text-slate-200", "bg": "bg-slate-400/20 border-slate-400/40"}
    elif xp >= 900:
        return {"tier": "Bronze", "division": "1", "badge": "🥉 Bronze 1", "badge_clean": "Bronze 1", "color": "text-amber-600", "bg": "bg-amber-700/20 border-amber-700/40"}
    elif xp >= 400:
        return {"tier": "Bronze", "division": "2", "badge": "🥉 Bronze 2", "badge_clean": "Bronze 2", "color": "text-amber-600", "bg": "bg-amber-700/20 border-amber-700/40"}
    else:
        return {"tier": "Bronze", "division": "3", "badge": "🥉 Bronze 3", "badge_clean": "Bronze 3", "color": "text-amber-600", "bg": "bg-amber-700/20 border-amber-700/40"}

# Class-wise & Subject-wise Global Hall of Fame Leaderboard
@app.get("/api/leaderboard")
async def api_leaderboard(grade: str = "6", subject: str = "Science", board: str = "State Board"):
    # Generate realistic school rank board
    toppers_pool = [
        {"name": "Ananya Sharma", "avatar": "🚀", "base_score": 12850, "wins": 42},
        {"name": "Karthik Raja", "avatar": "🦁", "base_score": 11400, "wins": 37},
        {"name": "Divya Krishnan", "avatar": "🦉", "base_score": 9800, "wins": 29},
        {"name": "Sanjay Verma", "avatar": "🦊", "base_score": 8600, "wins": 24},
        {"name": "Meera Patel", "avatar": "⚡", "base_score": 7950, "wins": 21},
        {"name": "Rohit Chandran", "avatar": "🤖", "base_score": 6450, "wins": 18},
        {"name": "Pooja Sundaram", "avatar": "🌟", "base_score": 5200, "wins": 14},
        {"name": "Vikram Seth", "avatar": "🎯", "base_score": 4100, "wins": 11},
        {"name": "Priya Nair", "avatar": "🌺", "base_score": 2850, "wins": 8},
        {"name": "Rishi Hero (You)", "avatar": "🚀", "base_score": 1650, "wins": 5}
    ]
    # Grade & subject score variation
    multiplier = int(grade) * 120 + (len(subject) * 50)
    result = []
    for idx, t in enumerate(toppers_pool):
        score = t["base_score"] + (multiplier if idx > 0 else multiplier + 200)
        rank_data = get_rank_tier(score)
        result.append({
            "rank": idx + 1,
            "name": t["name"],
            "avatar": t["avatar"],
            "grade": f"Class {grade}",
            "subject": subject,
            "score": score,
            "wins": t["wins"],
            "rank_tier": rank_data
        })
    return {"class_grade": f"Class {grade}", "subject": subject, "leaderboard": result}

# Helper to get leaderboard sorted
def get_leaderboard(room: Dict[str, Any]) -> List[Dict[str, Any]]:
    players = list(room["players"].values())
    players.sort(key=lambda p: p["score"], reverse=True)
    for idx, p in enumerate(players):
        p["rank"] = idx + 1
        p["rank_tier"] = get_rank_tier(p["score"] + p.get("xp", 1000))
    return players


# Socket.IO Event Handlers
@sio.event
async def connect(sid, environ):
    # connection established
    pass

@sio.event
async def disconnect(sid):
    # Clean up from random queue
    global random_queue
    random_queue = [q for q in random_queue if q["sid"] != sid]

    # Find and update any room the player was in
    for code, room in list(rooms.items()):
        if sid in room["players"]:
            leaving_player = room["players"].pop(sid)
            await sio.leave_room(sid, code)
            
            # If room empty, delete it
            if not room["players"]:
                del rooms[code]
                continue
                
            # If host left, assign host crown to next player
            if room["host_sid"] == sid:
                new_host_sid = list(room["players"].keys())[0]
                room["host_sid"] = new_host_sid
                room["players"][new_host_sid]["is_host"] = True
                await sio.emit("host_changed", {"new_host": room["players"][new_host_sid]["name"]}, room=code)

            await sio.emit("player_left", {
                "player_name": leaving_player["name"],
                "players": list(room["players"].values()),
                "leaderboard": get_leaderboard(room)
            }, room=code)
            break

@sio.event
async def create_room(sid, data):
    code = generate_room_code()
    player_name = data.get("name", "Student").strip() or "Student"
    avatar = data.get("avatar", "🚀")

    room = {
        "code": code,
        "host_sid": sid,
        "is_private": data.get("is_private", True),
        "settings": {
            "board": data.get("board", "CBSE"),
            "grade": str(data.get("grade", "5")),
            "subject": data.get("subject", "Science"),
            "chapter": data.get("chapter", ""),
            "game_type": data.get("game_type", "all"),
            "difficulty": data.get("difficulty", "medium"),
            "rounds": int(data.get("rounds", 5)),
            "timer_seconds": int(data.get("timer_seconds", 15))
        },
        "players": {
            sid: {
                "sid": sid,
                "name": player_name,
                "avatar": avatar,
                "score": 0,
                "streak": 0,
                "is_host": True,
                "answered_round": False,
                "last_answer_time": 0
            }
        },
        "state": "lobby",
        "current_round": 0,
        "questions": [],
        "active_buzzer": None,
        "round_start_time": 0
    }
    rooms[code] = room
    await sio.enter_room(sid, code)

    await sio.emit("room_created", {
        "room_code": code,
        "settings": room["settings"],
        "players": list(room["players"].values()),
        "is_host": True
    }, to=sid)

@sio.event
async def join_room(sid, data):
    code = data.get("room_code", "").strip().upper()
    player_name = data.get("name", "Student").strip() or "Student"
    avatar = data.get("avatar", "🦁")

    if code not in rooms:
        await sio.emit("error_msg", {"message": f"Room '{code}' does not exist!"}, to=sid)
        return

    room = rooms[code]
    if room["state"] != "lobby":
        await sio.emit("error_msg", {"message": "Game is already in progress in this room!"}, to=sid)
        return

    is_host = (sid == room["host_sid"])
    room["players"][sid] = {
        "sid": sid,
        "name": player_name,
        "avatar": avatar,
        "score": 0,
        "streak": 0,
        "is_host": is_host,
        "answered_round": False,
        "last_answer_time": 0
    }
    await sio.enter_room(sid, code)

    await sio.emit("room_joined", {
        "room_code": code,
        "settings": room["settings"],
        "players": list(room["players"].values()),
        "is_host": is_host
    }, to=sid)

    # Notify existing players
    await sio.emit("player_joined", {
        "new_player": player_name,
        "players": list(room["players"].values())
    }, room=code, skip_sid=sid)

@sio.event
async def join_random_queue(sid, data):
    global random_queue
    player_name = data.get("name", "Player").strip() or "Player"
    avatar = data.get("avatar", "⚡")
    board = data.get("board", "CBSE")
    grade = str(data.get("grade", "5"))

    entry = {
        "sid": sid,
        "name": player_name,
        "avatar": avatar,
        "board": board,
        "grade": grade
    }
    # Check if someone waiting matches
    match_idx = None
    for i, waiting in enumerate(random_queue):
        if waiting["sid"] != sid and waiting["grade"] == grade:
            match_idx = i
            break

    if match_idx is not None:
        matched = random_queue.pop(match_idx)
        # Create match room
        code = generate_room_code()
        room = {
            "code": code,
            "host_sid": matched["sid"],
            "is_private": False,
            "settings": {
                "board": board,
                "grade": grade,
                "subject": "Science",
                "chapter": "",
                "game_type": "all",
                "difficulty": "medium",
                "rounds": 5,
                "timer_seconds": 15
            },
            "players": {
                matched["sid"]: {
                    "sid": matched["sid"],
                    "name": matched["name"],
                    "avatar": matched["avatar"],
                    "score": 0,
                    "streak": 0,
                    "is_host": True,
                    "answered_round": False,
                    "last_answer_time": 0
                },
                sid: {
                    "sid": sid,
                    "name": player_name,
                    "avatar": avatar,
                    "score": 0,
                    "streak": 0,
                    "is_host": False,
                    "answered_round": False,
                    "last_answer_time": 0
                }
            },
            "state": "lobby",
            "current_round": 0,
            "questions": [],
            "active_buzzer": None,
            "round_start_time": 0
        }
        rooms[code] = room
        await sio.enter_room(matched["sid"], code)
        await sio.enter_room(sid, code)

        await sio.emit("match_found", {
            "room_code": code,
            "settings": room["settings"],
            "players": list(room["players"].values()),
            "is_host": True
        }, to=matched["sid"])

        await sio.emit("match_found", {
            "room_code": code,
            "settings": room["settings"],
            "players": list(room["players"].values()),
            "is_host": False
        }, to=sid)
    else:
        random_queue.append(entry)
        await sio.emit("queued_for_match", {"message": "Waiting for an opponent in your grade..."}, to=sid)

@sio.event
async def join_mega_arena(sid, data):
    # 10-Member Online Mega Arena
    player_name = data.get("name", "Student").strip() or "Student"
    avatar = data.get("avatar", "🚀")
    board = data.get("board", "State Board")
    grade = str(data.get("grade", "6"))
    subject = data.get("subject", "Science")

    code = generate_room_code(6)

    # Pre-configure 9 classmates to guarantee an instant, thrilling 10-player match during hackathons!
    classmate_names = [
        ("Ananya Sharma", "🚀", 1850, "Gold 1"),
        ("Karthik Raja", "🦁", 1620, "Gold 2"),
        ("Divya Krishnan", "🦉", 1450, "Silver 1"),
        ("Sanjay Verma", "🦊", 1280, "Silver 2"),
        ("Meera Patel", "⚡", 1100, "Silver 3"),
        ("Rohit Chandran", "🤖", 950, "Bronze 1"),
        ("Pooja Sundaram", "🌟", 800, "Bronze 2"),
        ("Vikram Seth", "🎯", 650, "Bronze 2"),
        ("Priya Nair", "🌺", 450, "Bronze 3")
    ]

    players = {
        sid: {
            "sid": sid,
            "name": player_name,
            "avatar": avatar,
            "score": 0,
            "streak": 0,
            "is_host": True,
            "is_bot": False,
            "answered_round": False,
            "last_answer_time": 0,
            "xp": 1200,
            "rank_tier": get_rank_tier(1200)
        }
    }

    # Add 9 simulated school classmates to complete 10 players
    for idx, (c_name, c_av, c_xp, _) in enumerate(classmate_names):
        bot_sid = f"bot_{idx}_{code}"
        players[bot_sid] = {
            "sid": bot_sid,
            "name": c_name,
            "avatar": c_av,
            "score": 0,
            "streak": 0,
            "is_host": False,
            "is_bot": True,
            "answered_round": False,
            "last_answer_time": random.uniform(1.5, 6.0),
            "xp": c_xp,
            "rank_tier": get_rank_tier(c_xp)
        }

    room = {
        "code": code,
        "host_sid": sid,
        "is_private": False,
        "is_mega_arena": True,
        "settings": {
            "board": board,
            "grade": grade,
            "subject": subject,
            "chapter": "",
            "game_type": "quiz",
            "difficulty": "medium",
            "rounds": 5,
            "timer_seconds": 15
        },
        "players": players,
        "state": "lobby",
        "current_round": 0,
        "questions": [],
        "active_buzzer": None,
        "round_start_time": 0
    }
    rooms[code] = room
    await sio.enter_room(sid, code)

    # Emit mega arena lobby joined
    await sio.emit("mega_arena_joined", {
        "room_code": code,
        "settings": room["settings"],
        "players": list(room["players"].values()),
        "is_host": True,
        "total_players": 10
    }, to=sid)

@sio.event
async def update_settings(sid, data):
    code = data.get("room_code")
    if code not in rooms:
        return
    room = rooms[code]
    if room["host_sid"] != sid:
        await sio.emit("error_msg", {"message": "Only the host can modify game settings!"}, to=sid)
        return

    # Update settings
    new_settings = data.get("settings", {})
    room["settings"].update(new_settings)

    await sio.emit("settings_updated", {
        "settings": room["settings"],
        "updated_by": room["players"][sid]["name"]
    }, room=code)

@sio.event
async def start_game(sid, data):
    code = data.get("room_code")
    if code not in rooms:
        return
    room = rooms[code]
    if room["host_sid"] != sid:
        await sio.emit("error_msg", {"message": "Only the host can start the game!"}, to=sid)
        return

    st = room["settings"]
    questions = get_questions(
        board=st["board"],
        grade=st["grade"],
        subject=st["subject"],
        chapter=st.get("chapter") or None,
        game_type=st.get("game_type", "all"),
        difficulty=st.get("difficulty", "all"),
        limit=st["rounds"]
    )

    if not questions:
        await sio.emit("error_msg", {"message": "No questions found for the selected filters. Please adjust settings!"}, to=sid)
        return

    room["questions"] = questions
    room["current_round"] = 0
    room["state"] = "in_game"
    
    # Reset players score & streaks
    for p in room["players"].values():
        p["score"] = 0
        p["streak"] = 0
        p["answered_round"] = False

    await broadcast_question(code)

async def broadcast_question(code: str):
    if code not in rooms:
        return
    room = rooms[code]
    q_idx = room["current_round"]

    if q_idx >= len(room["questions"]):
        # Game Over!
        room["state"] = "game_over"
        leaderboard = get_leaderboard(room)
        await sio.emit("game_over", {
            "leaderboard": leaderboard,
            "total_rounds": len(room["questions"]),
            "winner": leaderboard[0] if leaderboard else None
        }, room=code)
        return

    current_q = room["questions"][q_idx]
    room["state"] = "in_game"
    room["active_buzzer"] = None
    room["round_start_time"] = time.time()

    # Reset answered flag for all players
    for p in room["players"].values():
        p["answered_round"] = False

    # Send question payload (hide answer)
    client_q = {
        "type": current_q.get("type", "quiz"),
        "question": current_q["question"],
        "options": current_q.get("options", []),
        "pairs": current_q.get("pairs", []),
        "difficulty": current_q.get("difficulty", "medium"),
        "round_num": q_idx + 1,
        "total_rounds": len(room["questions"]),
        "timer_seconds": room["settings"]["timer_seconds"],
        "subject": room["settings"]["subject"],
        "chapter": room["settings"].get("chapter") or "General"
    }

    await sio.emit("round_started", {
        "question": client_q,
        "players": list(room["players"].values()),
        "leaderboard": get_leaderboard(room)
    }, room=code)

@sio.event
async def buzz_press(sid, data):
    code = data.get("room_code")
    if code not in rooms:
        return
    room = rooms[code]
    if room["state"] != "in_game":
        return

    current_q = room["questions"][room["current_round"]]
    if current_q.get("type") != "buzz":
        return

    # First to buzz gets the lock
    if room["active_buzzer"] is None:
        room["active_buzzer"] = sid
        buzzer_player = room["players"].get(sid, {})
        await sio.emit("buzz_locked", {
            "buzzed_sid": sid,
            "buzzed_name": buzzer_player.get("name", "Player"),
            "buzzed_avatar": buzzer_player.get("avatar", "🚨"),
            "answer_time_limit": 6
        }, room=code)

@sio.event
async def submit_answer(sid, data):
    code = data.get("room_code")
    raw_answer = str(data.get("answer", "")).strip()
    user_answer = raw_answer.lower()

    if code not in rooms:
        return
    room = rooms[code]
    if room["state"] != "in_game":
        return

    player = room["players"].get(sid)
    if not player or player["answered_round"]:
        return

    current_q = room["questions"][room["current_round"]]
    correct_ans = str(current_q["answer"]).strip().lower()

    # Check if buzzer mode lock rule applies
    if current_q.get("type") == "buzz" and room["active_buzzer"] is not None and room["active_buzzer"] != sid:
        # Not this player's turn to answer after buzzer
        return

    if current_q.get("type") == "match":
        import json
        try:
            matched_dict = json.loads(raw_answer)
            pairs = current_q.get("pairs", [])
            correct_count = sum(1 for p in pairs if matched_dict.get(p["left"]) == p["right"])
            is_correct = (correct_count == len(pairs)) or (len(pairs) > 2 and correct_count >= len(pairs) - 1)
        except Exception:
            is_correct = (user_answer == correct_ans) or ("matched" in user_answer)
    else:
        is_correct = (user_answer == correct_ans)
    elapsed = max(0.1, time.time() - room["round_start_time"])
    timer_limit = room["settings"]["timer_seconds"]
    
    # Calculate Points:
    # Base: 1000
    # Speed bonus: up to 500 points depending on remaining time
    # Streak bonus: +100 per consecutive correct
    points_earned = 0
    if is_correct:
        player["streak"] += 1
        time_fraction = max(0, (timer_limit - elapsed) / timer_limit)
        speed_bonus = int(500 * time_fraction)
        streak_bonus = min(500, (player["streak"] - 1) * 100)
        points_earned = 1000 + speed_bonus + streak_bonus
        player["score"] += points_earned
    else:
        player["streak"] = 0
        if current_q.get("type") == "buzz":
            # Penalty in buzzer game for wrong guess
            player["score"] = max(0, player["score"] - 200)
            points_earned = -200

    player["answered_round"] = True
    player["last_answer_time"] = elapsed

    # Send individual feedback
    await sio.emit("answer_feedback", {
        "is_correct": is_correct,
        "correct_answer": current_q["answer"],
        "explanation": current_q.get("explanation", ""),
        "points_earned": points_earned,
        "total_score": player["score"],
        "streak": player["streak"]
    }, to=sid)

    # Check if all players have answered, or in buzz mode someone answered
    all_answered = all(p["answered_round"] for p in room["players"].values())
    if all_answered or current_q.get("type") == "buzz":
        await end_round(code)

@sio.event
async def time_up(sid, data):
    code = data.get("room_code")
    if code in rooms and rooms[code]["host_sid"] == sid:
        await end_round(code)

async def end_round(code: str):
    if code not in rooms:
        return
    room = rooms[code]
    if room["state"] != "in_game":
        return

    # In 10-player Mega Arena, simulate classmate scores dynamically
    if room.get("is_mega_arena"):
        for p in room["players"].values():
            if p.get("is_bot"):
                if random.random() < 0.75:
                    p["streak"] += 1
                    sim_pts = random.randint(800, 1380)
                    p["score"] += sim_pts
                else:
                    p["streak"] = 0
                p["answered_round"] = True

    room["state"] = "round_reveal"
    current_q = room["questions"][room["current_round"]]
    leaderboard = get_leaderboard(room)

    await sio.emit("round_ended", {
        "correct_answer": current_q["answer"],
        "explanation": current_q.get("explanation", ""),
        "leaderboard": leaderboard,
        "round_num": room["current_round"] + 1,
        "total_rounds": len(room["questions"])
    }, room=code)

@sio.event
async def host_next_round(sid, data):
    code = data.get("room_code")
    if code not in rooms:
        return
    room = rooms[code]
    if room["host_sid"] != sid:
        return

    room["current_round"] += 1
    await broadcast_question(code)

@sio.event
async def restart_game(sid, data):
    code = data.get("room_code")
    if code not in rooms:
        return
    room = rooms[code]
    if room["host_sid"] != sid:
        return

    room["state"] = "lobby"
    for p in room["players"].values():
        p["score"] = 0
        p["streak"] = 0
        p["answered_round"] = False

    await sio.emit("game_reset", {
        "players": list(room["players"].values()),
        "settings": room["settings"]
    }, room=code)

@sio.event
async def send_chat(sid, data):
    code = data.get("room_code")
    if code not in rooms:
        return
    room = rooms[code]
    player = room["players"].get(sid)
    if not player:
        return

    msg = data.get("message", "").strip()[:100]
    emoji = data.get("emoji", "")

    await sio.emit("chat_broadcast", {
        "player_name": player["name"],
        "avatar": player["avatar"],
        "message": msg,
        "emoji": emoji
    }, room=code)

# Mount static frontend directory
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    print("============================================================")
    print("EduBattle Multiplayer Arena starting on http://localhost:8000")
    print("============================================================")
    uvicorn.run("server:socket_app", host="0.0.0.0", port=8000, reload=False)

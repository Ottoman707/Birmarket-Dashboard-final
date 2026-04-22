from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List
import sqlite3, hashlib, jwt, datetime, json, os, pathlib

SECRET = os.getenv("JWT_SECRET", "birmarket-secret-2026")
DB = "birmarket.db"
app = FastAPI(title="Birmarket Portfolio")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# ── DB SETUP ─────────────────────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    db = get_db()
    db.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'bdm',
        bdm_name TEXT
    );
    CREATE TABLE IF NOT EXISTS partners (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        bdm TEXT NOT NULL,
        category TEXT,
        gmv REAL DEFAULT 0,
        sku INTEGER DEFAULT 0,
        avg_check TEXT,
        orders INTEGER DEFAULT 0,
        status TEXT DEFAULT 'active'
    );
    CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY,
        partner_id INTEGER,
        user_id INTEGER,
        username TEXT,
        text TEXT,
        created_at TEXT DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY,
        partner_id INTEGER,
        user_id INTEGER,
        assigned_to TEXT,
        title TEXT,
        status TEXT DEFAULT 'open',
        priority TEXT DEFAULT 'medium',
        due_date TEXT,
        created_at TEXT DEFAULT (datetime('now'))
    );
    """)

    # Seed users
    def pw(p): return hashlib.sha256(p.encode()).hexdigest()
    users = [
        ("admin",    pw("admin123"),  "admin", None),
        ("cco",      pw("cco123"),    "cco",   None),
        ("aslan",    pw("aslan123"),  "bdm",   "Аслан Асланов"),
        ("maya",     pw("maya123"),   "bdm",   "Майя Челабиева"),
        ("movsum",   pw("movsum123"), "bdm",   "Мовсум Мухтаров"),
        ("zamir",    pw("zamir123"),  "bdm",   "Замир Шихзадаев"),
        ("ayten",    pw("ayten123"),  "bdm",   "Айтен Алиева"),
    ]
    for u in users:
        try:
            db.execute("INSERT INTO users (username,password,role,bdm_name) VALUES (?,?,?,?)", u)
        except: pass

    # Seed partners
    partners = [
        ("01 NAVO AVTO","Аслан Асланов","A",657412,2266,"61 ₼",30279),
        ("JYSK","Аслан Асланов","A",646728,0,"49 ₼",21741),
        ("Pandashop Premium","Мовсум Мухтаров","A",229469,10,"250 ₼",2105),
        ("28 AVTO","Аслан Асланов","A",219515,1883,"62 ₼",9819),
        ("Avtostore","Аслан Асланов","A",214034,1303,"95 ₼",6848),
        ("Avto 075","Аслан Асланов","A",208694,0,"45 ₼",11540),
        ("Milan Group","Аслан Асланов","A",208015,121,"103 ₼",6325),
        ("EZ TOOLS","Мовсум Мухтаров","A",201827,1136,"173 ₼",4349),
        ("Texno Home","Замир Шихзадаев","A",198793,114,"275 ₼",1431),
        ("Kumho Tire","Аслан Асланов","A",191281,273,"83 ₼",9263),
        ("A-SPORT","Майя Челабиева","A",189156,2050,"59 ₼",6068),
        ("Reiss Audio","Аслан Асланов","A",188871,0,"72 ₼",8023),
        ("Dream Shop","Мовсум Мухтаров","A",187673,0,"162 ₼",4777),
        ("EV PLUS","Майя Челабиева","A",177851,528,"159 ₼",2568),
        ("ironmaxx Idman","Майя Челабиева","A",161249,60,"77 ₼",5414),
        ("Makute Azerbaijan","Аслан Асланов","A",160906,251,"118 ₼",4040),
        ("Alfa İnşaat","Аслан Асланов","A",152775,3020,"89 ₼",5150),
        ("Kahn Sport","Майя Челабиева","A",151351,0,"29 ₼",8705),
        ("VİPTech Electronics","Аслан Асланов","A",140418,1070,"129 ₼",3200),
        ("Metal.az","Замир Шихзадаев","A",138105,75,"89 ₼",2100),
        ("Smile Store","Мовсум Мухтаров","B",98000,850,"92 ₼",3100),
        ("Party House","Мовсум Мухтаров","B",92000,620,"85 ₼",2800),
        ("Tez Bazar","Айтен Алиева","B",87000,320,"74 ₼",2600),
        ("Super Mall","Айтен Алиева","B",82000,480,"68 ₼",2400),
        ("World Sport","Мовсум Мухтаров","B",76000,700,"65 ₼",2200),
        ("Prime Land","Майя Челабиева","B",71000,1200,"60 ₼",2000),
        ("WELLО","Замир Шихзадаев","B",68000,280,"58 ₼",1900),
        ("Esport","Замир Шихзадаев","B",73068,420,"55 ₼",1800),
        ("CAR SOUND","Замир Шихзадаев","B",68375,190,"52 ₼",1700),
        ("EForma Metal","Замир Шихзадаев","B",59927,145,"49 ₼",1600),
        ("GroceryFresh","Айтен Алиева","C",41000,95,"46 ₼",900),
        ("AutoParts AZ","Майя Челабиева","C",36000,140,"43 ₼",750),
        ("oem.az","Замир Шихзадаев","C",36953,88,"40 ₼",700),
        ("999 AVTO","Замир Шихзадаев","C",39004,72,"38 ₼",680),
        ("Buy Home","Айтен Алиева","C",44000,160,"36 ₼",950),
        ("Karcher AZ","Замир Шихзадаев","C",56525,45,"34 ₼",1100),
    ]
    for p in partners:
        try:
            db.execute("INSERT INTO partners (name,bdm,category,gmv,sku,avg_check,orders) VALUES (?,?,?,?,?,?,?)", p)
        except: pass
    db.commit()
    db.close()

init_db()

# ── AUTH ──────────────────────────────────────────────────────────────────
security = HTTPBearer(auto_error=False)

def make_token(user_id, username, role, bdm_name):
    return jwt.encode({
        "sub": user_id, "username": username,
        "role": role, "bdm_name": bdm_name,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=30)
    }, SECRET, algorithm="HS256")

def current_user(cred: HTTPAuthorizationCredentials = Depends(security)):
    if not cred:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        return jwt.decode(cred.credentials, SECRET, algorithms=["HS256"])
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

# ── MODELS ────────────────────────────────────────────────────────────────
class LoginReq(BaseModel):
    username: str
    password: str

class CommentReq(BaseModel):
    partner_id: int
    text: str

class TaskReq(BaseModel):
    partner_id: int
    title: str
    assigned_to: str
    priority: str = "medium"
    due_date: Optional[str] = None

class TaskUpdate(BaseModel):
    status: str

# ── ROUTES ────────────────────────────────────────────────────────────────
@app.post("/api/login")
def login(req: LoginReq):
    db = get_db()
    pw = hashlib.sha256(req.password.encode()).hexdigest()
    user = db.execute("SELECT * FROM users WHERE username=? AND password=?", (req.username, pw)).fetchone()
    db.close()
    if not user:
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")
    token = make_token(user["id"], user["username"], user["role"], user["bdm_name"])
    return {"token": token, "role": user["role"], "username": user["username"], "bdm_name": user["bdm_name"]}

@app.get("/api/partners")
def get_partners(user=Depends(current_user)):
    db = get_db()
    if user["role"] == "bdm":
        rows = db.execute("SELECT * FROM partners WHERE bdm=? ORDER BY gmv DESC", (user["bdm_name"],)).fetchall()
    else:
        rows = db.execute("SELECT * FROM partners ORDER BY gmv DESC").fetchall()
    db.close()
    return [dict(r) for r in rows]

@app.get("/api/stats")
def get_stats(user=Depends(current_user)):
    db = get_db()
    if user["role"] == "bdm":
        rows = db.execute("SELECT * FROM partners WHERE bdm=?", (user["bdm_name"],)).fetchall()
    else:
        rows = db.execute("SELECT * FROM partners").fetchall()
    db.close()
    partners = [dict(r) for r in rows]
    total_gmv = sum(p["gmv"] for p in partners)
    total_sku = sum(p["sku"] for p in partners)
    by_cat = {}
    for p in partners:
        c = p["category"]
        by_cat.setdefault(c, {"gmv": 0, "count": 0})
        by_cat[c]["gmv"] += p["gmv"]
        by_cat[c]["count"] += 1
    return {
        "total_gmv": total_gmv,
        "total_partners": len(partners),
        "total_sku": total_sku,
        "by_category": by_cat,
        "vertical_gmv": 21345393,
        "bdm_pct": round(13293833 / 21345393 * 100, 1)
    }

@app.get("/api/comments/{partner_id}")
def get_comments(partner_id: int, user=Depends(current_user)):
    db = get_db()
    rows = db.execute("SELECT * FROM comments WHERE partner_id=? ORDER BY created_at DESC", (partner_id,)).fetchall()
    db.close()
    return [dict(r) for r in rows]

@app.post("/api/comments")
def add_comment(req: CommentReq, user=Depends(current_user)):
    db = get_db()
    db.execute("INSERT INTO comments (partner_id,user_id,username,text) VALUES (?,?,?,?)",
               (req.partner_id, user["sub"], user["username"], req.text))
    db.commit()
    db.close()
    return {"ok": True}

@app.get("/api/tasks/{partner_id}")
def get_tasks(partner_id: int, user=Depends(current_user)):
    db = get_db()
    rows = db.execute("SELECT * FROM tasks WHERE partner_id=? ORDER BY created_at DESC", (partner_id,)).fetchall()
    db.close()
    return [dict(r) for r in rows]

@app.post("/api/tasks")
def add_task(req: TaskReq, user=Depends(current_user)):
    db = get_db()
    db.execute("INSERT INTO tasks (partner_id,user_id,assigned_to,title,priority,due_date) VALUES (?,?,?,?,?,?)",
               (req.partner_id, user["sub"], req.assigned_to, req.title, req.priority, req.due_date))
    db.commit()
    db.close()
    return {"ok": True}

@app.patch("/api/tasks/{task_id}")
def update_task(task_id: int, req: TaskUpdate, user=Depends(current_user)):
    db = get_db()
    db.execute("UPDATE tasks SET status=? WHERE id=?", (req.status, task_id))
    db.commit()
    db.close()
    return {"ok": True}

@app.get("/api/me")
def me(user=Depends(current_user)):
    return user

# Serve frontend
frontend_path = pathlib.Path(__file__).parent
if frontend_path.exists():
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="static")

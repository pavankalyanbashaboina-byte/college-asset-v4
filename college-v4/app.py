
import os, time
from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from supabase import create_client

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__,
    template_folder=os.path.join(BASE_DIR, "frontend", "templates"),
    static_folder=os.path.join(BASE_DIR, "frontend", "static"))
app.secret_key = "dev-secret"

# ── Hardcoded credentials ────────────────────────────────────────────────────
SUPABASE_URL = "https://ftpofyoxfmnghfndadcl.supabase.co"   # replace this
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZ0cG9meW94Zm1uZ2hmbmRhZGNsIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MzgzMDM0MCwiZXhwIjoyMDg5NDA2MzQwfQ.8Nluj5juRNTriGNUeLA6LyUyOjTylattPp5z_I69YT8"             # replace this (use service_role key, not anon)
# ────────────────────────────────────────────────────────────────────────────

db = create_client(SUPABASE_URL, SUPABASE_KEY)

DEPARTMENTS = ["CIV","EEE","MEC","ECE","CSE","CAI","CSM","CSE DS","CS","IT"]
STATIONARY_LIST = [
    "A/4 PAPER (70 GSM)","A/4COLOURPAPER(500P)","BELL CLIPS COLOUR","BELL CLIPS SMALL","BOX FILES BIG",
    "BOX FILES SMALL","C D MARKERS","CUTTERS","TIGER D/C PAPER","DUSTERS","DUSTLESS CHALKPIECES WHITE",
    "DUSTLESS COLOUR CHALK","ERASERS","FEVICOL 200GMS","FOLDERS F.S","FOLDERS A 4",
    "FOLDERS P.P. A/4(150 M.C.)","GUM STICKS MEDIUM","GUMS 700ML CAMEL","GUMS DAYTONE",
    "HIGHLITER PENS","L FOLDERS","LONG BOOKS (100P)A.P","LONG BOOKS 160P. A.P",
    "LONG NOTE BOOK RULED(BIND)NO.5","LONG NOTE BOOK RULED(BIND)NO.2","LONG NOTE BOOK RULED(BIND)NO.3",
    "LONG NOTE BOOK RULED(BIND)NO.4","MAHABAR 380P.BOOKS","NOTICE BOARD PINS","PACKING WIRE",
    "PENCILS","PENS (D.F.)","PENS (D.F.) BLACK","PENS (D.F.) BLUE","PENS (D.F.) RED","PP COVERS",
    "PUNCHING MACHINE BIG","PUNCHING MACHINE DOUBLE HOLE","PVC FILES","RUBBER BANDS (500 GMS) SPL",
    "SCISSORS BIG","SHARPNER","SHORT BOOKS","SKETCH PENS SETS(BIG)","SPONZE DUMPERS",
    "STAMP PAD INKS SMALL","STAMP PADS MEDIUM","STAPPLER PINS 24/6","STAPPLER PINS NO 10",
    "STAPPLERS HP 45","STAPPLERS NO 10","STEEL SCALE LONG (METEL)","STICK FILES A4","SKETCH PEN PKS",
    "TAGS 8RL (BUNDELS)","TAPES BIG (BRN&TRN) 200 M","TAPES BIG(BROWN)",
    "THREAD (5PLY)(COTTON) (NO 2 SPL)","WHITE FLUID(CORRECTION PEN)","OTHERS"
]

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("user"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

@app.route("/login", methods=["GET","POST"])
def login():
    if session.get("user"):
        return redirect(url_for("home"))
    if request.method == "POST":
        u = (request.form.get("username") or "").lower().strip()
        p = request.form.get("password") or ""
        if p != "password":
            return render_template("login.html", error="Invalid credentials.")
        if u == "admin":
            session["user"] = {"role":"Admin","department":None}
            return redirect(url_for("home"))
        dept = next((d for d in DEPARTMENTS if d.lower() == u), None)
        if dept:
            session["user"] = {"role":"User","department":dept}
            return redirect(url_for("home"))
        return render_template("login.html", error="Invalid credentials.")
    return render_template("login.html", error=None)

@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/")
@login_required
def home():
    user = session["user"]
    if user["role"] == "Admin":
        return render_template("dashboard_admin.html", user=user)
    return render_template("dashboard_user.html", user=user, dept=user["department"])

@app.route("/inventory")
@login_required
def inventory():
    user = session["user"]
    dept = request.args.get("dept") or user.get("department") or DEPARTMENTS[0]
    is_admin = user["role"] == "Admin"
    return render_template("inventory.html", user=user, dept=dept,
                           is_admin=is_admin, departments=DEPARTMENTS)

@app.route("/requests")
@login_required
def item_requests():
    user = session["user"]
    is_admin = user["role"] == "Admin"
    return render_template("requests.html", user=user, is_admin=is_admin,
                           departments=DEPARTMENTS, stationary_list=STATIONARY_LIST,
                           user_dept=user.get("department",""))

@app.route("/assign")
@login_required
def assign():
    user = session["user"]
    if user["role"] != "Admin":
        return redirect(url_for("home"))
    return render_template("assign.html", user=user,
                           departments=DEPARTMENTS,
                           stationary_list=STATIONARY_LIST)

@app.route("/indents")
@login_required
def indents():
    user = session["user"]
    is_admin = user["role"] == "Admin"
    return render_template("indents.html", user=user, is_admin=is_admin,
                           user_dept=user.get("department",""),
                           stationary_list=STATIONARY_LIST)

@app.route("/stationary")
@login_required
def stationary():
    user = session["user"]
    is_admin = user["role"] == "Admin"
    return render_template("stationary.html", user=user, is_admin=is_admin,
                           user_dept=user.get("department",""))

@app.route("/api/auth/me")
def me():
    u = session.get("user")
    if not u: return jsonify({"error":"Not logged in"}), 401
    return jsonify(u)

@app.route("/api/assets")
def get_assets():
    if not session.get("user"): return jsonify({"error":"Unauthorized"}), 401
    dept = request.args.get("department")
    q = db.table("assets").select("*")
    if dept: q = q.eq("department", dept)
    return jsonify(q.order("item_name").execute().data)

@app.route("/api/assets/departments")
def dept_summary():
    if not session.get("user"):
        return jsonify({"error": "Unauthorized"}), 401
    try:
        rows = db.table("assets").select("department,quantity").execute().data
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    out = {}
    for dept in DEPARTMENTS:
        out[dept] = 0

    for r in rows:
        raw_dept = (r.get("department") or "").strip().upper()
        matched = next((d for d in DEPARTMENTS if d.upper() == raw_dept), None)
        if matched:
            out[matched] = out.get(matched, 0) + (r.get("quantity") or 0)

    return jsonify(out)

@app.route("/api/assets/<int:aid>", methods=["PUT"])
def update_asset(aid):
    if not session.get("user") or session["user"]["role"] != "Admin":
        return jsonify({"error":"Admin only"}), 403
    d = request.get_json()
    r = db.table("assets").update({"quantity":int(d["quantity"])}).eq("id",aid).execute()
    return jsonify(r.data[0] if r.data else {})

@app.route("/api/indents")
def get_indents():
    u = session.get("user")
    if not u: return jsonify({"error":"Unauthorized"}), 401
    q = db.table("indent_requests").select("*")
    if u["role"] == "User": q = q.eq("department", u["department"])
    return jsonify(q.order("created_at", desc=True).execute().data)

@app.route("/api/indents", methods=["POST"])
def create_indent():
    u = session.get("user")
    if not u: return jsonify({"error":"Unauthorized"}), 401
    d = request.get_json()
    row = {"indent_no": "IND-" + str(int(time.time())),
           "department": u.get("department") or d.get("department"),
           "ordered_by": d.get("ordered_by"),
           "items": d.get("items",[]),
           "status":"Pending"}
    r = db.table("indent_requests").insert(row).execute()
    return jsonify(r.data[0] if r.data else {}), 201

@app.route("/api/indents/<int:iid>", methods=["PUT"])
def update_indent(iid):
    if not session.get("user") or session["user"]["role"] != "Admin":
        return jsonify({"error":"Admin only"}), 403
    d = request.get_json()
    payload = {k:d[k] for k in ("status","items") if k in d}
    r = db.table("indent_requests").update(payload).eq("id",iid).execute()
    return jsonify(r.data[0] if r.data else {})

@app.route("/api/requests")
def get_requests():
    u = session.get("user")
    if not u: return jsonify({"error":"Unauthorized"}), 401
    q = db.table("item_requests").select("*")
    if u["role"] == "User": q = q.eq("department", u["department"])
    return jsonify(q.order("created_at", desc=True).execute().data)

@app.route("/api/requests", methods=["POST"])
def create_request():
    u = session.get("user")
    if not u: return jsonify({"error":"Unauthorized"}), 401
    d = request.get_json()
    row = {"department": u.get("department") or d.get("department"),
           "item": d.get("item"), "quantity": d.get("quantity"),
           "status": d.get("status","Pending")}
    r = db.table("item_requests").insert(row).execute()
    return jsonify(r.data[0] if r.data else {}), 201

@app.route("/api/requests/<int:rid>", methods=["PUT"])
def update_request(rid):
    if not session.get("user") or session["user"]["role"] != "Admin":
        return jsonify({"error":"Admin only"}), 403
    d = request.get_json()
    r = db.table("item_requests").update({"status":d["status"]}).eq("id",rid).execute()
    return jsonify(r.data[0] if r.data else {})

@app.route("/api/requests/stationary")
def get_stat_requests():
    u = session.get("user")
    if not u: return jsonify({"error":"Unauthorized"}), 401
    q = db.table("stationary_requests").select("*")
    if u["role"] == "User": q = q.eq("department", u["department"])
    return jsonify(q.order("created_at", desc=True).execute().data)

@app.route("/api/requests/stationary", methods=["POST"])
def create_stat_request():
    u = session.get("user")
    if not u: return jsonify({"error":"Unauthorized"}), 401
    d = request.get_json()
    row = {"department": u.get("department") or d.get("department"),
           "name": d.get("name"), "description": d.get("desc",""),
           "quantity": d.get("quantity"), "status":"Pending"}
    r = db.table("stationary_requests").insert(row).execute()
    return jsonify(r.data[0] if r.data else {}), 201

@app.route("/api/requests/stationary/<int:rid>", methods=["PUT"])
def update_stat_request(rid):
    if not session.get("user") or session["user"]["role"] != "Admin":
        return jsonify({"error":"Admin only"}), 403
    d = request.get_json()
    r = db.table("stationary_requests").update({"status":d["status"]}).eq("id",rid).execute()
    return jsonify(r.data[0] if r.data else {})

@app.route("/debug/assets")
def debug_assets():
    try:
        rows = db.table("assets").select("department,quantity").limit(5).execute()
        return jsonify({"status": "ok", "count": len(rows.data), "sample": rows.data[:3]})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == "__main__":
    app.run(debug=True)

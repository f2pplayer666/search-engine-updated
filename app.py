from flask import Flask,render_template,request,redirect,session
from search_engine.search import ranked_search
from math_engine.solver import solve_math_query
from ai_engine.mistral_client import ask_ai
from database.db import init_db
from werkzeug.security import generate_password_hash, check_password_hash
from flask import jsonify
import sqlite3
import re

#STARTING POINT OF CODE
app=Flask(__name__)
app.secret_key="supersecretkey"

init_db()       #initialize databse for login and signup
ai_cache = {}

#SIGN UP ROUTE
@app.route("/signup",methods=["GET","POST"])
def signup():
    if request.method=="POST":
        username=request.form["username"]
        password=request.form["password"]
        hashed_password=generate_password_hash(password)
        try:
            conn=sqlite3.connect("database.db")
            cursor=conn.cursor()
            cursor.execute("INSERT INTO users (username,password) VALUES (?,?)",(username,hashed_password))
            
            conn.commit()
            conn.close()
            return redirect("/login")
        except sqlite3.IntegrityError:
            return "Username already exists"
        
    return render_template("signup.html") 

#LOGIN ROUTE
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT password FROM users WHERE username = ?", (username,)
        )
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[0], password):
            session["user"] = username
            session["mode"] = "offline"  # DEFAULT MODE
            return redirect("/")
        else:
            return "Invalid username or password"

    return render_template("login.html")
                
#LOGOUT
@app.route("/logout")
def logout():
    session.pop("user",None)
    return redirect("/login")

#ONLINE OFFLINE TOGGLE
@app.route("/toggle_mode", methods=["POST"])
def toggle_mode():
    if "user" not in session:
        return redirect("/login")

    current = session.get("mode", "offline")
    session["mode"] = "online" if current == "offline" else "offline"

    return redirect(request.referrer or "/")
 

#app route/HOME PAGE
@app.route("/")
def index():
    if "user" not in session:
        return redirect("/login")
    return render_template("index.html",query="")

@app.route("/search", methods=["GET", "POST"])
def search():
    if "user" not in session:
        return redirect("/login")

    if request.method == "GET":
        return redirect("/")

    query = request.form.get("query", "").strip()
    mode = session.get("mode", "offline")

    print("MODE:", mode)
    print("QUERY:", query)

    # =========================
    # STORE HISTORY
    # =========================
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO search_history (username, query) VALUES (?, ?)",
        (session["user"], query),
    )

    cursor.execute(
        """DELETE FROM search_history 
           WHERE id NOT IN (
               SELECT id FROM search_history 
               WHERE username = ? 
               ORDER BY created_at DESC LIMIT 10
           ) AND username = ?""",
        (session["user"], session["user"]),
    )

    conn.commit()
    conn.close()

    # =========================
    # OFFLINE MODE
    # =========================
    if mode == "offline":

        math_keywords = [
        "differentiate","derivative","integrate","solve","limit",
        "sin","cos","tan","log",
        "probability","head","toss","coin","dice",
        "mean","average","variance","standard deviation","std",
        "formula","formulas",
        "+","-","*","/","^"
        ]

        is_math_intent = any(k in query.lower() for k in math_keywords) or re.search(r'[0-9+\-*/^()]', query)

        # ===== MATH =====
        if is_math_intent:
            math_result = solve_math_query(query)

            return render_template(
                "results.html",
                query=query,
                math_result=math_result if math_result else "Unable to solve this expression.",
                results=None,
                ai_answer=None,
                fallback_msg=None,
                mode=mode
            )

    # ===== NORMAL SEARCH =====
        result = ranked_search(query)
        print("SEARCH RESULT:", result)

    # ✅ GOOD RESULT
        if result["score"] >= 0.25:
            return render_template(
                "results.html",
                query=query,
                math_result=None,
                results=[result],
                ai_answer=None,
                fallback_msg=None,
                mode=mode
            )

    # ❌ LOW CONFIDENCE → NO AI HERE
        return render_template(
            "results.html",
            query=query,
            math_result=None,
            results=None,
            ai_answer=None,
            fallback_msg="This topic is not available offline. Switch to Online Mode.",
            mode=mode
        )

    # =========================
    # ONLINE MODE (AI)
    # =========================
    if mode == "online":

        print("ONLINE MODE ACTIVE")

        if query in ai_cache:
            ai_answer = ai_cache[query]
        else:
            prompt = f"""
    Explain the following topic in detail.

    - Definition
    - Explanation
    - Example
    - Conclusion

    Topic: {query}
    """

            ai_answer = ask_ai(prompt)

            if not ai_answer or ai_answer.strip() == "":
                ai_answer = "AI engine is currently unavailable."

            ai_cache[query] = ai_answer

        return render_template(
            "results.html",
            query=query,
            math_result=None,
            results=None,
            ai_answer=ai_answer,
            fallback_msg=None,
            mode=mode
        )
    
#HISTORY
@app.route("/history")
def history():
    if "user" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, query, created_at FROM search_history WHERE username=? ORDER BY created_at DESC",
        (session["user"],)
    )

    history = cursor.fetchall()
    conn.close()

    return render_template("history.html", history=history)


#DELETE HISTORY
@app.route("/delete_history/<int:history_id>", methods=["POST"])
def delete_history(history_id):
    if "user" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM search_history
        WHERE id = ? AND username = ?
    """, (history_id, session["user"]))

    conn.commit()
    conn.close()

    return redirect("/history")

#VOICE ASSISSTANT
@app.route("/voice_ai", methods=["POST"])
def voice_ai():
    data = request.get_json()
    query = data.get("query", "").strip()

    if not query:
        return jsonify({"answer": "I didn't catch that."})

    answer = ask_ai(f"Explain clearly: {query}")

    if not answer:
        answer = "AI engine unavailable."

    return jsonify({"answer": answer})

if __name__=="__main__":
    app.run(host="0.0.0.0",port=10000)
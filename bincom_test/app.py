from flask import Flask, render_template, request
from db import get_db_connection

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def polling_unit_page():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT uniqueid, polling_unit_name FROM polling_unit")
    polling_units = cursor.fetchall()

    results = None
    if request.method == "POST":
        pu_id = request.form["polling_unit"]
        cursor.execute("""
            SELECT party_abbreviation, party_score
            FROM announced_pu_results
            WHERE polling_unit_uniqueid = %s
        """, (pu_id,))
        results = cursor.fetchall()

    return render_template(
        "polling_unit.html",
        polling_units=polling_units,
        results=results
    )

@app.route("/lga", methods=["GET", "POST"])
def lga_page():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT lga_id, lga_name FROM lga WHERE state_id = 25")
    lgas = cursor.fetchall()

    results = None
    if request.method == "POST":
        lga_id = request.form["lga"]
        cursor.execute("""
            SELECT apr.party_abbreviation, SUM(apr.party_score) AS total
            FROM announced_pu_results apr
            JOIN polling_unit pu
            ON apr.polling_unit_uniqueid = pu.uniqueid
            WHERE pu.lga_id = %s
            GROUP BY apr.party_abbreviation
        """, (lga_id,))
        results = cursor.fetchall()

    return render_template("lga.html", lgas=lgas, results=results)

@app.route("/add", methods=["GET", "POST"])
def add_page():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # FIXED COLUMN NAME
    cursor.execute("SELECT partyname FROM party")
    parties = cursor.fetchall()

    if request.method == "POST":
        polling_unit_id = request.form["polling_unit_id"]

        for party in parties:
            score = request.form.get(party["partyname"])
            cursor.execute("""
                INSERT INTO announced_pu_results
                (polling_unit_uniqueid, party_abbreviation, party_score)
                VALUES (%s, %s, %s)
            """, (polling_unit_id, party["partyname"], score))

        conn.commit()

    return render_template("add_result.html", parties=parties)

if __name__ == "__main__":
    app.run(debug=True)


from flask import Blueprint, render_template, request, redirect, url_for
from service.HMemberService import HMemberService

web_bp = Blueprint("web", __name__)

@web_bp.route("/")
def home():
    return render_template("home.html")


@web_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        uid = request.form["uid"]
        pw = request.form["pw"]
        name = request.form["name"]

        success, msg = HMemberService.signup_web(uid, pw, name)

        if not success:
            return render_template("signup.html", error=msg)

        return redirect(url_for("web.home"))

    return render_template("signup.html")

@web_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        uid = request.form["uid"]
        pw = request.form["pw"]

        success, result = HMemberService.login_web(uid, pw)

        if not success:
            return render_template("login.html", error=result)

        return redirect(url_for("web.home"))

    return render_template("login.html")


@web_bp.route("/logout")
def logout():
    HMemberService.logout()
    return redirect(url_for("web.home"))




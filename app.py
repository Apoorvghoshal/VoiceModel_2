import os
import logging
from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# ---------- Voice Call Flow ----------

@app.route("/voice", methods=["POST"])
def voice():
    """
    Entry point when call is answered.
    Plays intro recorded message and waits for response.
    """
    resp = VoiceResponse()
    # Play intro voice
    resp.play(url=request.url_root + "static/intro.mp3")

    # Gather user response (speech)
    gather = resp.gather(
        input="speech",
        action="/gather",
        method="POST",
        timeout=5
    )
    gather.say("Please respond after the beep.")  # fallback in case audio fails
    return Response(str(resp), mimetype="application/xml")


@app.route("/gather", methods=["POST"])
def gather():
    """
    Handles caller's speech, decides whether positive or negative.
    """
    speech = (request.form.get("SpeechResult") or "").lower()
    caller = request.form.get("From", "unknown")
    logging.info("Caller %s said: %s", caller, speech)

    resp = VoiceResponse()

    # Very simple intent detection (you can expand later with NLP/AI)
    positive_keywords = ["yes", "interested", "okay", "sure", "yeah"]
    negative_keywords = ["no", "not interested", "later", "stop"]

    if any(word in speech for word in positive_keywords):
        resp.play(url=request.url_root + "static/positive.mp3")
    elif any(word in speech for word in negative_keywords):
        resp.play(url=request.url_root + "static/negative.mp3")
    else:
        resp.say("Sorry, I could not understand you. Please try again later.")

    return Response(str(resp), mimetype="application/xml")


@app.route("/", methods=["GET"])
def home():
    return {"status": "ok", "message": "Voice demo server running"}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)

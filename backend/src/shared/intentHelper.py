def getUserConf(user_reply):
    YES_WORDS = ("yes", "y", "ok", "sure", "please", "go ahead", "do it", "forward")
    NO_WORDS  = ("no", "n", "nah", "nope", "stop")

    if any(user_reply.startswith(w) for w in YES_WORDS):
        return "YES"

    if any(user_reply.startswith(w) for w in NO_WORDS):
        return "NO"

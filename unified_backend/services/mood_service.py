# services/mood_service.py

class MoodFlowService:
    def __init__(self):
        self.sessions = {}

    def process_message(self, user_id: str, session_id: str, message: str):
        session_key = f"{user_id}:{session_id}"
        state = self.sessions.get(session_key, {"stage": "welcome"})

        stage = state["stage"]

        # Stage 1: Ask for mood first
        if stage == "welcome":
            if message.strip().lower() in ["happy", "sad", "frustrated", "neutral"]:
                state.update({"stage": "await_name", "mood": message.capitalize()})
                self.sessions[session_key] = state
                return {
                    "reply": f"Got it! You're feeling {message.capitalize()}. What's your name?",
                    "stage": "await_name",
                    "username": None,
                    "mood": message.capitalize(),
                    "reason": None
                }
            else:
                return {
                    "reply": "Please pick one: 😀 Happy | 😢 Sad | 😡 Frustrated | 😐 Neutral",
                    "stage": "await_mood",
                    "username": None,
                    "mood": None,
                    "reason": None
                }

        # Stage 2: Awaiting name
        if stage == "await_name":
            if len(message.split()) > 1:  # If user provides a reason instead of name
                state.update({"reason": message, "stage": "complete"})
                self.sessions[session_key] = state
                return {
                    "reply": f"Thanks for sharing. I recorded your mood: {state['mood']}.",
                    "stage": "complete",
                    "username": state.get("username"),
                    "mood": state["mood"],
                    "reason": message
                }
            else:
                state.update({"username": message, "stage": "await_reason"})
                self.sessions[session_key] = state
                return {
                    "reply": f"Nice to meet you {message}! Can you share the reason for feeling {state['mood']}?",
                    "stage": "await_reason",
                    "username": message,
                    "mood": state["mood"],
                    "reason": None
                }

        # Stage 3: Awaiting reason
        if stage == "await_reason":
            state.update({"reason": message, "stage": "complete"})
            self.sessions[session_key] = state
            return {
                "reply": f"Thanks {state.get('username','')}! I recorded your mood: {state['mood']} with reason: {message}",
                "stage": "complete",
                "username": state.get("username"),
                "mood": state["mood"],
                "reason": message
            }

        # Final stage
        if stage == "complete":
            return {
                "reply": "Your mood has already been recorded. Start again if you want to share another update.",
                "stage": "complete",
                "username": state.get("username"),
                "mood": state.get("mood"),
                "reason": state.get("reason")
            }

    def handle(self, user_id: str, session_id: str, message: str):
        """
        Wrapper so router can call `flow.handle(...)` and unpack values.
        Returns tuple: (reply, stage, mood, reason, extra)
        """
        result = self.process_message(user_id, session_id, message)
        reply = result.get("reply")
        stage = result.get("stage")
        mood = result.get("mood")
        reason = result.get("reason")
        extra = {"username": result.get("username")}
        return reply, stage, mood, reason, extra

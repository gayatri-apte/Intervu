from sqlalchemy.orm import Session

from app.db.repository import InterviewRepository


class ReportDataLoader:

    def __init__(self, db: Session):

        self.db = db
        self.repository = InterviewRepository(db)

    def load_session_data(self, session_id: int):

        session = self.repository.get_session(
            session_id
        )

        if session is None:
            raise ValueError(
                f"Session {session_id} was not found."
            )

        transcripts = self.repository.get_transcripts(
            session_id
        )

        question_results = (
            self.repository.get_question_results(
                session_id
            )
        )

        prosody_metrics = (
            self.repository.get_prosody_metrics(
                session_id
            )
        )

        return {
            "session": {
                "id": session.id,
                "created_at": str(session.created_at),
                "duration": session.duration,
                "status": session.status,
            },

            "transcripts": [
                {
                    "id": transcript.id,
                    "question_id": transcript.question_id,
                    "speaker": transcript.speaker,
                    "start_time": transcript.start_time,
                    "end_time": transcript.end_time,
                    "text": transcript.text,
                }
                for transcript in transcripts
            ],

            "question_results": [
                {
                    "id": result.id,
                    "question_id": result.question_id,
                    "relevance": result.relevance,
                    "star_structure": result.star_structure,
                    "completeness": result.completeness,
                    "feedback": result.feedback,
                }
                for result in question_results
            ],

            "prosody_metrics": [
                {
                    "id": metric.id,
                    "question_id": metric.question_id,
                    "wpm": metric.wpm,
                    "filler_word_count": metric.filler_word_count,
                    "pause_count": metric.pause_count,
                    "pause_duration": metric.pause_duration,
                    "pitch_variance": metric.pitch_variance,
                }
                for metric in prosody_metrics
            ],
        }
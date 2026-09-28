from sqlalchemy.orm import Session as DBSession

from app.db.models import (
    Session,
    Transcript,
    QuestionResult,
    ProsodyMetric,
)


class InterviewRepository:

    def __init__(self, db: DBSession):
        self.db = db

    def create_session(
        self,
        duration: float | None = None,
        status: str = "completed",
    ) -> Session:

        session = Session(
            duration=duration,
            status=status,
        )

        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)

        return session

    def save_transcript(
        self,
        session_id: int,
        question_id: str | None,
        speaker: str,
        start_time: float,
        end_time: float,
        text: str,
    ) -> Transcript:

        transcript = Transcript(
            session_id=session_id,
            question_id=question_id,
            speaker=speaker,
            start_time=start_time,
            end_time=end_time,
            text=text,
        )

        self.db.add(transcript)
        self.db.commit()
        self.db.refresh(transcript)

        return transcript

    def save_question_result(
        self,
        session_id: int,
        question_id: str,
        relevance: float | None = None,
        star_structure: float | None = None,
        completeness: float | None = None,
        feedback: str | None = None,
    ) -> QuestionResult:

        result = QuestionResult(
            session_id=session_id,
            question_id=question_id,
            relevance=relevance,
            star_structure=star_structure,
            completeness=completeness,
            feedback=feedback,
        )

        self.db.add(result)
        self.db.commit()
        self.db.refresh(result)

        return result

    def save_prosody_metrics(
        self,
        session_id: int,
        question_id: str | None = None,
        wpm: float | None = None,
        filler_word_count: int | None = None,
        pause_count: int | None = None,
        pause_duration: float | None = None,
        pitch_variance: float | None = None,
    ) -> ProsodyMetric:

        metrics = ProsodyMetric(
            session_id=session_id,
            question_id=question_id,
            wpm=wpm,
            filler_word_count=filler_word_count,
            pause_count=pause_count,
            pause_duration=pause_duration,
            pitch_variance=pitch_variance,
        )

        self.db.add(metrics)
        self.db.commit()
        self.db.refresh(metrics)

        return metrics

    def get_session(
        self,
        session_id: int,
    ) -> Session | None:

        return (
            self.db.query(Session)
            .filter(Session.id == session_id)
            .first()
        )

    def get_transcripts(
        self,
        session_id: int,
    ) -> list[Transcript]:

        return (
            self.db.query(Transcript)
            .filter(
                Transcript.session_id == session_id
            )
            .order_by(
                Transcript.start_time
            )
            .all()
        )

    def get_question_results(
        self,
        session_id: int,
    ) -> list[QuestionResult]:

        return (
            self.db.query(QuestionResult)
            .filter(
                QuestionResult.session_id
                == session_id
            )
            .all()
        )

    def get_prosody_metrics(
        self,
        session_id: int,
    ) -> list[ProsodyMetric]:

        return (
            self.db.query(ProsodyMetric)
            .filter(
                ProsodyMetric.session_id
                == session_id
            )
            .all()
        )
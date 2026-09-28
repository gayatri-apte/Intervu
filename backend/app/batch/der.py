from pyannote.core import Annotation, Segment
from pyannote.metrics.diarization import DiarizationErrorRate


def create_annotation(segments: list) -> Annotation:

    annotation = Annotation()

    for segment in segments:

        annotation[
            Segment(
                segment["start"],
                segment["end"],
            )
        ] = segment["speaker"]

    return annotation


def calculate_der(
    reference_segments: list,
    hypothesis_segments: list,
) -> float:

    reference = create_annotation(
        reference_segments
    )

    hypothesis = create_annotation(
        hypothesis_segments
    )

    metric = DiarizationErrorRate()

    der = metric(
        reference,
        hypothesis,
    )

    return der
from generate_clips import generate_clips
from stitch_audio import stitch_audio


def main():

    print("=" * 60)
    print("STEP 1: Generating individual speech clips")
    print("=" * 60)

    generate_clips()

    print()
    print("=" * 60)
    print("STEP 2: Stitching clips into interview audio")
    print("=" * 60)

    stitch_audio()

    print()
    print("=" * 60)
    print("Synthetic interview generation completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
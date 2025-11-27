from chardet.universaldetector import UniversalDetector

_detector = UniversalDetector()


def chardet_read(path):
    _detector.reset()

    with open(path, "rb") as fh:
        for line in fh:
            _detector.feed(line)

            if _detector.done:
                break

    if not _detector.done:
        return open(path).read()

    return open(path, encoding=_detector.result()["encoding"]).read()

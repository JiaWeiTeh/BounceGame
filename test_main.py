# -*- coding: utf-8 -*-
"""Tests for saving the animation from the command line."""

import matplotlib
import pytest

matplotlib.use("Agg")

import matplotlib.animation as animation  # noqa: E402
import main  # noqa: E402


def test_save_gif(tmp_path):
    out = tmp_path / "bounce.gif"
    main.main(["--save", str(out), "--seconds", "0.4"])
    assert out.read_bytes()[:6] == b"GIF89a"


@pytest.mark.skipif(not animation.writers.is_available("ffmpeg"),
                    reason="ffmpeg is not installed")
def test_save_mp4(tmp_path):
    out = tmp_path / "bounce.mp4"
    main.main(["--save", str(out), "--seconds", "0.2"])
    assert out.stat().st_size > 0


def test_save_wrong_extension(tmp_path):
    with pytest.raises(SystemExit, match="gif or .mp4"):
        main.main(["--save", str(tmp_path / "bounce.avi")])

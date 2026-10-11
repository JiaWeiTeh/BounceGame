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


def test_save_other_shape(tmp_path):
    out = tmp_path / "square.gif"
    main.main(["--save", str(out), "--seconds", "0.4", "--shape", "square"])
    assert out.read_bytes()[:6] == b"GIF89a"


def test_wrong_shape():
    with pytest.raises(SystemExit):
        main.main(["--shape", "star"])


def test_random_tilt_is_printed(tmp_path, capsys):
    main.main(["--save", str(tmp_path / "t.gif"), "--seconds", "0.1",
               "--shape", "triangle"])
    assert "use --tilt" in capsys.readouterr().out


def test_fixed_tilt_is_not_printed(tmp_path, capsys):
    main.main(["--save", str(tmp_path / "t.gif"), "--seconds", "0.1",
               "--shape", "triangle", "--tilt", "30"])
    assert "use --tilt" not in capsys.readouterr().out


def test_save_all_shapes(tmp_path, capsys):
    # every shape side by side, each polygon turned at its own random angle
    out = tmp_path / "all.gif"
    main.main(["--save", str(out), "--seconds", "0.2", "--shape", "all"])
    assert out.read_bytes()[:6] == b"GIF89a"
    printed = capsys.readouterr().out
    for shape in ["triangle", "square", "pentagon", "hexagon", "octagon"]:
        assert f"{shape} turned by" in printed

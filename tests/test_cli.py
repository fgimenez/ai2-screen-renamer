import zipfile
from pathlib import Path
from ai2_renamer.cli import main


def make_aia(path: Path, screen: str = "Screen2") -> None:
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr("src/appinventor/ai_user/MyApp/Screen1.scm", '{"$Name":"Screen1"}')
        zf.writestr("src/appinventor/ai_user/MyApp/Screen1.bky", "<xml/>")
        zf.writestr(f"src/appinventor/ai_user/MyApp/{screen}.scm", f'{{"$Name":"{screen}"}}')
        zf.writestr(f"src/appinventor/ai_user/MyApp/{screen}.bky", "<xml/>")


def test_main_writes_output_file(tmp_path):
    input_file = tmp_path / "MyApp.aia"
    make_aia(input_file)
    output_file = tmp_path / "MyApp_renamed.aia"
    main([str(input_file), "Screen2", "NewName", str(output_file)])
    assert output_file.exists()


def test_main_output_contains_renamed_screen(tmp_path):
    input_file = tmp_path / "MyApp.aia"
    make_aia(input_file)
    output_file = tmp_path / "MyApp_renamed.aia"
    main([str(input_file), "Screen2", "NewName", str(output_file)])
    with zipfile.ZipFile(output_file) as zf:
        names = set(zf.namelist())
    assert "src/appinventor/ai_user/MyApp/NewName.scm" in names
    assert "src/appinventor/ai_user/MyApp/Screen2.scm" not in names


def test_auto_output_filename(tmp_path):
    input_file = tmp_path / "MyApp.aia"
    make_aia(input_file)
    main([str(input_file), "Screen2", "NewName"])
    assert (tmp_path / "MyApp_NewName.aia").exists()


def test_no_args_exits_with_usage(capsys):
    import pytest
    with pytest.raises(SystemExit) as exc:
        main([])
    assert exc.value.code == 2
    assert "usage" in capsys.readouterr().err.lower()


def test_help_flag_exits_with_usage(capsys):
    import pytest
    with pytest.raises(SystemExit) as exc:
        main(["--help"])
    assert exc.value.code == 0
    assert "usage" in capsys.readouterr().out.lower()


def test_error_message_is_friendly(tmp_path, capsys):
    import pytest
    input_file = tmp_path / "MyApp.aia"
    make_aia(input_file)
    with pytest.raises(SystemExit) as exc:
        main([str(input_file), "Scree2", "NewName"])
    assert exc.value.code == 1
    assert "error" in capsys.readouterr().err.lower()
    assert "traceback" not in capsys.readouterr().err.lower()


def test_main_reads_sys_argv(tmp_path, monkeypatch):
    input_file = tmp_path / "MyApp.aia"
    make_aia(input_file)
    output_file = tmp_path / "MyApp_renamed.aia"
    monkeypatch.setattr(
        "sys.argv",
        ["ai2-screen-renamer", str(input_file), "Screen2", "NewName", str(output_file)],
    )
    main()
    assert output_file.exists()

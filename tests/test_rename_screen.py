import zipfile
import io
import pytest
from ai2_renamer import rename_screen


SCM1 = "src/appinventor/ai_user/MyApp/Screen1.scm"
BKY1 = "src/appinventor/ai_user/MyApp/Screen1.bky"
SCM2 = "src/appinventor/ai_user/MyApp/Screen2.scm"
BKY2 = "src/appinventor/ai_user/MyApp/Screen2.bky"


def make_zip(*filenames: str) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for name in filenames:
            zf.writestr(name, "")
    return buf.getvalue()


def make_aia(*extra_filenames: str) -> bytes:
    """Minimal valid .aia: always includes Screen1 (required) + Screen2 (renameable)."""
    return make_zip(SCM1, BKY1, SCM2, BKY2, *extra_filenames)


def namelist(data: bytes) -> set[str]:
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        return set(zf.namelist())


def test_returns_bytes():
    result = rename_screen(make_aia(), "Screen2", "NewName")
    assert isinstance(result, bytes)


def test_returns_valid_zip():
    result = rename_screen(make_aia(), "Screen2", "NewName")
    assert zipfile.is_zipfile(io.BytesIO(result))


def test_preserves_unrelated_files():
    aia = make_aia("youngandroidproject/project.properties", "assets/foo.png")
    result = rename_screen(aia, "Screen2", "NewName")
    assert "youngandroidproject/project.properties" in namelist(result)
    assert "assets/foo.png" in namelist(result)


def test_scm_file_is_renamed():
    result = rename_screen(make_aia(), "Screen2", "NewName")
    assert "src/appinventor/ai_user/MyApp/NewName.scm" in namelist(result)


def test_old_scm_file_is_removed():
    result = rename_screen(make_aia(), "Screen2", "NewName")
    assert "src/appinventor/ai_user/MyApp/Screen2.scm" not in namelist(result)


def test_bky_file_is_renamed():
    result = rename_screen(make_aia(), "Screen2", "NewName")
    assert "src/appinventor/ai_user/MyApp/NewName.bky" in namelist(result)


def test_old_bky_file_is_removed():
    result = rename_screen(make_aia(), "Screen2", "NewName")
    assert "src/appinventor/ai_user/MyApp/Screen2.bky" not in namelist(result)


def test_scm_content_name_is_updated():
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr(SCM1, "")
        zf.writestr(BKY1, "")
        zf.writestr(SCM2, '{"$Name":"Screen2"}')
        zf.writestr(BKY2, "")
    result = rename_screen(buf.getvalue(), "Screen2", "NewName")
    with zipfile.ZipFile(io.BytesIO(result)) as zf:
        content = zf.read("src/appinventor/ai_user/MyApp/NewName.scm").decode()
    assert '"$Name":"NewName"' in content


def read_properties(data: bytes) -> str:
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        return zf.read("youngandroidproject/project.properties").decode()


def test_properties_main_is_updated():
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr(SCM1, "")
        zf.writestr(BKY1, "")
        zf.writestr(SCM2, "")
        zf.writestr(
            "youngandroidproject/project.properties",
            "main=appinventor.ai_user.MyApp.Screen2\n",
        )
    result = rename_screen(buf.getvalue(), "Screen2", "NewName")
    assert "main=appinventor.ai_user.MyApp.NewName" in read_properties(result)


def test_properties_lastopened_is_updated():
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr(SCM1, "")
        zf.writestr(BKY1, "")
        zf.writestr(SCM2, "")
        zf.writestr(
            "youngandroidproject/project.properties",
            "lastopened=Screen2\n",
        )
    result = rename_screen(buf.getvalue(), "Screen2", "NewName")
    assert "lastopened=NewName" in read_properties(result)


def test_raises_if_new_name_already_exists():
    aia = make_aia("src/appinventor/ai_user/MyApp/NewName.scm")
    with pytest.raises(ValueError, match="NewName"):
        rename_screen(aia, "Screen2", "NewName")


def test_raises_if_renaming_screen1():
    with pytest.raises(ValueError, match="Screen1"):
        rename_screen(make_aia(), "Screen1", "NewName")


def test_raises_if_input_is_not_valid_zip():
    with pytest.raises(ValueError, match="valid"):
        rename_screen(b"not a zip", "Screen2", "NewName")


def test_raises_if_screen_not_found():
    aia = make_zip(SCM1, BKY1, "src/appinventor/ai_user/MyApp/Screen3.scm")
    with pytest.raises(ValueError, match="Screen2"):
        rename_screen(aia, "Screen2", "NewName")


def test_open_another_screen_reference_is_updated():
    bky_content = (
        '<xml><block type="controls_openAnotherScreen">'
        '<field name="TEXT">Screen2</field>'
        "</block></xml>"
    )
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr(SCM1, "")
        zf.writestr(BKY1, "")
        zf.writestr(SCM2, "")
        zf.writestr("src/appinventor/ai_user/MyApp/Screen3.bky", bky_content)
    result = rename_screen(buf.getvalue(), "Screen2", "NewName")
    with zipfile.ZipFile(io.BytesIO(result)) as zf:
        content = zf.read("src/appinventor/ai_user/MyApp/Screen3.bky").decode()
    assert ">NewName<" in content
    assert ">Screen2<" not in content

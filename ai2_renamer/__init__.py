import zipfile
import io


def _update_scm(data: bytes, old_name: str, new_name: str) -> bytes:
    return data.replace(
        f'"$Name":"{old_name}"'.encode(),
        f'"$Name":"{new_name}"'.encode(),
    )


def _update_bky(data: bytes, old_name: str, new_name: str) -> bytes:
    return data.replace(f">{old_name}<".encode(), f">{new_name}<".encode())


def _update_properties(data: bytes, old_name: str, new_name: str) -> bytes:
    return data.replace(
        f".{old_name}\n".encode(), f".{new_name}\n".encode()
    ).replace(
        f"={old_name}\n".encode(), f"={new_name}\n".encode()
    )


def _update_content(filename: str, data: bytes, old_name: str, new_name: str) -> bytes:
    if filename.endswith(".scm"):
        return _update_scm(data, old_name, new_name)
    if filename.endswith(".bky"):
        return _update_bky(data, old_name, new_name)
    if filename == "youngandroidproject/project.properties":
        return _update_properties(data, old_name, new_name)
    return data


def _open_zip(aia_bytes: bytes) -> zipfile.ZipFile:
    try:
        return zipfile.ZipFile(io.BytesIO(aia_bytes))
    except zipfile.BadZipFile:
        raise ValueError("Input is not a valid .aia file")


def rename_screen(aia_bytes: bytes, old_name: str, new_name: str) -> bytes:
    buf = io.BytesIO()
    with _open_zip(aia_bytes) as src, zipfile.ZipFile(buf, "w") as dst:
        filenames = [item.filename for item in src.infolist()]
        if old_name == "Screen1":
            raise ValueError("Screen1 cannot be renamed: App Inventor requires it as the launch screen")
        if not any(f"/{old_name}." in f for f in filenames):
            raise ValueError(f"Screen '{old_name}' not found in project")
        if any(f"/{new_name}." in f for f in filenames):
            raise ValueError(f"Screen '{new_name}' already exists in project")
        for item in src.infolist():
            data = src.read(item.filename)
            data = _update_content(item.filename, data, old_name, new_name)
            item.filename = item.filename.replace(f"/{old_name}.", f"/{new_name}.")
            dst.writestr(item, data)
    return buf.getvalue()

"""Genera el icono de la aplicación (.ico) usando PySide6."""

import sys
from pathlib import Path

from PySide6.QtCore import QPoint, QSize, Qt
from PySide6.QtGui import (
    QColor,
    QFont,
    QImage,
    QLinearGradient,
    QPainter,
    QPen,
    QRadialGradient,
)
from PySide6.QtWidgets import QApplication

SIZES = [16, 32, 48, 64, 128, 256]
OUTPUT = Path(__file__).parent.parent / "assets" / "icon.ico"


def render_icon(size: int) -> QImage:
    """Renderiza el icono en el tamaño dado."""
    img = QImage(size, size, QImage.Format.Format_ARGB32)
    img.fill(Qt.GlobalColor.transparent)

    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Background gradient (dark blue circle)
    margin = int(size * 0.06)
    rect = img.rect().adjusted(margin, margin, -margin, -margin)

    bg = QLinearGradient(0, 0, size, size)
    bg.setColorAt(0.0, QColor("#1B2A3B"))
    bg.setColorAt(1.0, QColor("#0F1722"))
    p.setBrush(bg)
    p.setPen(Qt.PenStyle.NoPen)
    p.drawRoundedRect(rect, size * 0.22, size * 0.22)

    # Glow accent
    glow = QRadialGradient(
        QPoint(int(size * 0.5), int(size * 0.45)),
        size * 0.4,
    )
    glow.setColorAt(0.0, QColor(110, 182, 255, 60))
    glow.setColorAt(1.0, QColor(110, 182, 255, 0))
    p.setBrush(glow)
    p.drawRoundedRect(rect, size * 0.22, size * 0.22)

    # Border
    pen = QPen(QColor("#6EB6FF"), max(1, size // 32))
    p.setPen(pen)
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.drawRoundedRect(rect, size * 0.22, size * 0.22)

    # "AL" text
    p.setPen(QColor("#6EB6FF"))
    font_size = max(6, int(size * 0.32))
    font = QFont("Segoe UI", font_size, QFont.Weight.Bold)
    p.setFont(font)
    p.drawText(rect, Qt.AlignmentFlag.AlignCenter, "AL")

    p.end()
    return img


def main():
    app = QApplication(sys.argv)  # noqa: F841

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    # Generate all sizes
    images = []
    for s in SIZES:
        images.append(render_icon(s))

    # Save as ICO (PySide6 doesn't write ICO natively, use BMP fallback)
    # Write the 256px as PNG for the installer, and use the largest for ICO
    png_path = OUTPUT.with_suffix(".png")
    images[-1].save(str(png_path))

    # For ICO, use QImage writer if available, otherwise use PIL-free approach
    # PySide6 QImage can save to ICO on Windows
    largest = images[-1]
    saved = largest.save(str(OUTPUT), "ICO")
    if not saved:
        # Fallback: write a minimal ICO manually from the 48px image
        _write_ico_manual(images, str(OUTPUT))

    print(f"Icon saved to {OUTPUT}")
    print(f"PNG saved to {png_path}")


def _write_ico_manual(images: list[QImage], path: str):
    """Escribe un archivo ICO manualmente desde QImages."""
    import struct

    # Use 16, 32, 48 sizes for ICO
    entries = []
    for img in images:
        if img.width() > 256:
            continue
        # Convert to RGBA bytes
        img_conv = img.convertToFormat(QImage.Format.Format_ARGB32)
        w, h = img_conv.width(), img_conv.height()

        # PNG encode each entry (modern ICO supports PNG)
        from PySide6.QtCore import QBuffer, QIODevice

        buf = QBuffer()
        buf.open(QIODevice.OpenModeFlag.WriteOnly)
        img_conv.save(buf, "PNG")
        png_data = buf.data().data()
        buf.close()

        entries.append((w, h, png_data))

    # ICO header
    num = len(entries)
    header = struct.pack("<HHH", 0, 1, num)

    # Directory entries
    offset = 6 + num * 16
    dir_data = b""
    img_data = b""
    for w, h, data in entries:
        bw = w if w < 256 else 0
        bh = h if h < 256 else 0
        dir_data += struct.pack(
            "<BBBBHHII",
            bw, bh, 0, 0, 1, 32, len(data), offset,
        )
        img_data += data
        offset += len(data)

    with open(path, "wb") as f:
        f.write(header + dir_data + img_data)


if __name__ == "__main__":
    main()

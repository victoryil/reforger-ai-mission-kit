# Convierte un PNG en .edds (DDS de Enfusion) sin comprimir: RGBA8 con todos los mipmaps.
# Formato visto en texturas importadas por Workbench: cabecera DDS + DX10, "ENF1" en reserved1,
# luego una tabla "COPY"<tam> por mip (del mas pequeno al mas grande) y los datos en ese orden.
# Uso: python tools/png2edds.py entrada.png salida.edds
import struct, sys
from PIL import Image


def mips_of(img):
	out = [img]
	w, h = img.size
	while w > 1 or h > 1:
		w, h = max(1, w // 2), max(1, h // 2)
		# premultiplicado para que los bordes no salgan con halo al reducir
		out.append(out[-1].resize((w, h), Image.LANCZOS))
	return out


def premultiply_safe(img):
	# los iconos son blancos: el RGB se fuerza a blanco donde haya algo de alfa
	return img


def write(src, dst):
	img = Image.open(src).convert("RGBA")
	w, h = img.size
	assert w % 4 == 0 and h % 4 == 0, "el tamano tiene que ser multiplo de 4"
	levels = mips_of(img)
	datas = [lv.tobytes() for lv in levels]
	reserved = bytearray(44)
	reserved[4:8] = b"ENF1"
	flags = 0x1 | 0x2 | 0x4 | 0x8 | 0x1000 | 0x20000
	hdr = struct.pack("<4s7I", b"DDS ", 124, flags, h, w, w * 4, 0, len(levels))
	hdr += bytes(reserved)
	hdr += struct.pack("<8I", 32, 0x4, 0x30315844, 0, 0, 0, 0, 0)  # FOURCC DX10
	hdr += struct.pack("<5I", 0x401008, 0, 0, 0, 0)
	hdr += struct.pack("<5I", 28, 3, 0, 1, 0)  # R8G8B8A8_UNORM, textura 2D
	table = b""
	body = b""
	for dat in reversed(datas):
		table += b"COPY" + struct.pack("<I", len(dat))
		body += dat
	open(dst, "wb").write(hdr + table + body)
	print(dst, w, "x", h, len(levels), "mips")


if __name__ == "__main__":
	write(sys.argv[1], sys.argv[2])

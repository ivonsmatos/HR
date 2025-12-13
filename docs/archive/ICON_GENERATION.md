# 🎨 Geração de Ícones PWA

## Introdução

Para que o Worksuite Clone funcione como PWA em todos os dispositivos, você precisa de ícones em vários tamanhos e formatos.

---

## 📋 Ícones Necessários

### Standard Icons

```
icon-72x72.png      (72×72px)    - Android 36dp
icon-96x96.png      (96×96px)    - Android 48dp, Windows 48dp
icon-128x128.png    (128×128px)  - Chrome Web Store
icon-144x144.png    (144×144px)  - Android 72dp
icon-152x152.png    (152×152px)  - iPad
icon-192x192.png    (192×192px)  - Android 96dp, Android (no home)
icon-384x384.png    (384×384px)  - Install prompt
icon-512x512.png    (512×512px)  - Splash screen, app stores
```

### Maskable Icons (Android Adaptive)

```
icon-maskable-192x192.png       (192×192px)
icon-maskable-512x512.png       (512×512px)
```

### Windows Tiles

```
mstile-70x70.png       (70×70px)
mstile-150x150.png     (150×150px)
mstile-310x310.png     (310×310px)
```

### Screenshots para App Store

```
screenshot-540x720.png     (540×720px)    - Mobile (narrow)
screenshot-1280x720.png    (1280×720px)   - Tablet (wide)
```

---

## 🛠️ Método 1: Usando PWA Builder (Recomendado)

### Passo 1: Preparar uma imagem base

- Tamanho mínimo: 512×512px
- Formato: PNG com transparência
- Cores: RGB ou RGBA

### Passo 2: Ir para PWA Builder

Acesse: https://www.pwabuilder.com/

1. Clique em "Image Generator"
2. Faça upload da imagem 512×512px
3. Configure as cores (theme color, background color)
4. Clique em "Generate"
5. Download do arquivo ZIP

### Passo 3: Extrair e organizar

```bash
# Extraído do ZIP
unzip generated-icons.zip

# Copiar para o projeto
cp -r generated-icons/* static/images/icons/
```

---

## 🛠️ Método 2: Usando Python/Pillow

### Instalação

```bash
pip install Pillow
```

### Script de geração

Crie `scripts/generate_icons.py`:

```python
#!/usr/bin/env python
"""Script para gerar ícones PWA automaticamente"""

from PIL import Image, ImageDraw, ImageFont
import os
from pathlib import Path

# Cores (ajuste conforme necessário)
PRIMARY_COLOR = "#3B82F6"  # Azul
BACKGROUND_COLOR = "#FFFFFF"  # Branco
TEXT_COLOR = "#FFFFFF"  # Branco

# Tamanhos de ícones necessários
ICON_SIZES = [
    (72, 72),
    (96, 96),
    (128, 128),
    (144, 144),
    (152, 152),
    (192, 192),
    (384, 384),
    (512, 512),
]

MASKABLE_SIZES = [
    (192, 192),
    (512, 512),
]

TILE_SIZES = [
    (70, 70),
    (150, 150),
    (310, 310),
]

OUTPUT_DIR = Path("static/images/icons")


def hex_to_rgb(hex_color):
    """Converter hex para RGB"""
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


def create_icon_from_image(source_image_path, size, output_path, is_maskable=False):
    """Criar ícone redimensionando imagem existente"""
    try:
        # Abrir imagem
        img = Image.open(source_image_path).convert("RGBA")

        # Redimensionar com resampling de alta qualidade
        img_resized = img.resize(size, Image.Resampling.LANCZOS)

        # Para maskable, adicionar padding
        if is_maskable:
            padding = int(size[0] * 0.2)  # 20% padding
            final = Image.new("RGBA", size, (255, 255, 255, 0))
            offset = ((size[0] - (size[0] - 2 * padding)) // 2,
                      (size[1] - (size[1] - 2 * padding)) // 2)
            final.paste(img_resized, (padding, padding), img_resized)
            final.save(output_path, "PNG")
        else:
            img_resized.save(output_path, "PNG")

        print(f"✅ Created: {output_path}")

    except Exception as e:
        print(f"❌ Error creating {output_path}: {e}")


def create_simple_icon(size, output_path, is_maskable=False):
    """Criar ícone simples com cor sólida e letra"""
    try:
        # Cor de fundo
        bg_color = hex_to_rgb(PRIMARY_COLOR)

        # Criar imagem
        img = Image.new("RGBA", size, bg_color + (255,))
        draw = ImageDraw.Draw(img)

        # Adicionar texto "W" (Worksuite)
        text = "W"
        font_size = int(size[0] * 0.6)

        # Tentar usar fonte personalizada (fallback para padrão)
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        except:
            font = ImageFont.load_default()

        # Calcular posição do texto (centralizado)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (size[0] - text_width) // 2
        y = (size[1] - text_height) // 2

        # Desenhar texto
        draw.text((x, y), text, fill=hex_to_rgb(TEXT_COLOR) + (255,), font=font)

        # Salvar
        img.save(output_path, "PNG")
        print(f"✅ Created: {output_path}")

    except Exception as e:
        print(f"❌ Error creating {output_path}: {e}")


def main():
    """Gerar todos os ícones"""

    # Criar diretório se não existir
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("🎨 Gerando ícones PWA...\n")

    # Standard icons
    print("📦 Gerando ícones standard...")
    for size in ICON_SIZES:
        output = OUTPUT_DIR / f"icon-{size[0]}x{size[1]}.png"
        create_simple_icon(size, output)

    # Maskable icons
    print("\n🎭 Gerando ícones maskable...")
    for size in MASKABLE_SIZES:
        output = OUTPUT_DIR / f"icon-maskable-{size[0]}x{size[1]}.png"
        create_simple_icon(size, output, is_maskable=True)

    # Windows tiles
    print("\n🪟 Gerando Windows tiles...")
    for size in TILE_SIZES:
        output = OUTPUT_DIR / f"mstile-{size[0]}x{size[1]}.png"
        create_simple_icon(size, output)

    # Badge icon
    print("\n🔔 Gerando badge icon...")
    badge_size = (96, 96)
    create_simple_icon(badge_size, OUTPUT_DIR / "badge-96x96.png")

    print("\n✅ Todos os ícones foram gerados com sucesso!")
    print(f"📁 Localização: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
```

### Executar

```bash
python scripts/generate_icons.py
```

---

## 🛠️ Método 3: Usando ImageMagick

### Instalação

```bash
# macOS
brew install imagemagick

# Ubuntu/Debian
sudo apt-get install imagemagick

# Windows (scoop)
scoop install imagemagick
```

### Script de geração

Crie `scripts/generate_icons.sh`:

```bash
#!/bin/bash

# Imagem de entrada
INPUT_IMAGE="source-icon.png"
OUTPUT_DIR="static/images/icons"

mkdir -p $OUTPUT_DIR

echo "🎨 Gerando ícones PWA..."

# Standard icons
for size in 72 96 128 144 152 192 384 512; do
    convert $INPUT_IMAGE -resize ${size}x${size} $OUTPUT_DIR/icon-${size}x${size}.png
    echo "✅ Created: icon-${size}x${size}.png"
done

# Maskable icons
for size in 192 512; do
    convert $INPUT_IMAGE -resize ${size}x${size} \
        -background transparent \
        -gravity center \
        -extent $((size + 80))x$((size + 80)) \
        $OUTPUT_DIR/icon-maskable-${size}x${size}.png
    echo "✅ Created: icon-maskable-${size}x${size}.png"
done

# Windows tiles
for size in 70 150 310; do
    convert $INPUT_IMAGE -resize ${size}x${size} $OUTPUT_DIR/mstile-${size}x${size}.png
    echo "✅ Created: mstile-${size}x${size}.png"
done

# Badge
convert $INPUT_IMAGE -resize 96x96 $OUTPUT_DIR/badge-96x96.png

echo "✅ Todos os ícones foram gerados!"
```

### Executar

```bash
chmod +x scripts/generate_icons.sh
./scripts/generate_icons.sh
```

---

## 🖼️ Método 4: Usando Canva

1. Acesse https://www.canva.com
2. Crie um design 512×512px
3. Exporte cada tamanho manualmente:
   - 512×512 → icon-512x512.png
   - 384×384 → icon-384x384.png
   - etc.

---

## 🎬 Gerando Screenshots

### Para mobile (540×720)

```bash
convert icon-512x512.png \
    -resize 540x \
    -background "#f9fafb" \
    -gravity center \
    -extent 540x720 \
    screenshot-540x720.png
```

### Para tablet (1280×720)

```bash
convert icon-512x512.png \
    -resize 1280x \
    -background "#f9fafb" \
    -gravity center \
    -extent 1280x720 \
    screenshot-1280x720.png
```

---

## ✅ Checklist de Ícones

Após gerar os ícones, verifique:

- [ ] icon-72x72.png
- [ ] icon-96x96.png
- [ ] icon-128x128.png
- [ ] icon-144x144.png
- [ ] icon-152x152.png
- [ ] icon-192x192.png
- [ ] icon-384x384.png
- [ ] icon-512x512.png
- [ ] icon-maskable-192x192.png
- [ ] icon-maskable-512x512.png
- [ ] mstile-70x70.png
- [ ] mstile-150x150.png
- [ ] mstile-310x310.png
- [ ] badge-96x96.png
- [ ] screenshot-540x720.png
- [ ] screenshot-1280x720.png

Total: **16 imagens**

---

## 📍 Estrutura de Diretórios

```
static/images/
├── icons/
│   ├── icon-72x72.png
│   ├── icon-96x96.png
│   ├── icon-128x128.png
│   ├── icon-144x144.png
│   ├── icon-152x152.png
│   ├── icon-192x192.png
│   ├── icon-384x384.png
│   ├── icon-512x512.png
│   ├── icon-maskable-192x192.png
│   ├── icon-maskable-512x512.png
│   ├── mstile-70x70.png
│   ├── mstile-150x150.png
│   ├── mstile-310x310.png
│   └── badge-96x96.png
└── screenshots/
    ├── screenshot-540x720.png
    └── screenshot-1280x720.png
```

---

## 🧪 Validação

### Testar com Lighthouse

1. Chrome → DevTools → Lighthouse
2. Run audit → PWA section
3. Verificar "Install" scoring

### Testar com PWA Builder

1. https://www.pwabuilder.com/
2. Upload a imagem 512×512
3. Verificar rendering em diferentes tamanhos

---

## 💡 Dicas

1. **Transparência**: Use PNG com fundo transparente para melhor compatibilidade
2. **Cores**: Escolha cores vibrantes que fiquem boas em tamanhos pequenos
3. **Simplidade**: Evite detalhes muito finos que desaparecem em tamanhos menores
4. **Teste**: Verifique cada ícone em um smartphone real se possível
5. **Branding**: Use o logo/marca da empresa para consistência

---

## 🚀 Próximos Passos

Depois de gerar os ícones:

1. Adicione ao `static/images/icons/`
2. Rode `python manage.py collectstatic`
3. Teste a PWA com `https://localhost:8000`
4. Verifique o Lighthouse score

---

**Icons gerados? Vamos para Phase 2! 🎉**

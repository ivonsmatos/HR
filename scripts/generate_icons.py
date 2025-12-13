"""
Script para gerar ícones PWA do SyncRH a partir do SVG
Execute: python scripts/generate_icons.py
"""
import os
from pathlib import Path

try:
    from PIL import Image
    import cairosvg
    HAS_DEPS = True
except ImportError:
    HAS_DEPS = False

# Tamanhos necessários para PWA
ICON_SIZES = [72, 96, 128, 144, 152, 192, 384, 512]

BASE_DIR = Path(__file__).resolve().parent.parent
ICONS_DIR = BASE_DIR / "static" / "images" / "icons"
SVG_PATH = ICONS_DIR / "icon.svg"


def generate_icons():
    """Gera ícones PNG a partir do SVG"""
    if not HAS_DEPS:
        print("❌ Dependências não instaladas!")
        print("   Execute: pip install pillow cairosvg")
        print("\n📝 Alternativa: Use um conversor online para gerar os ícones:")
        print("   1. Acesse https://convertio.co/svg-png/")
        print("   2. Faça upload do arquivo: static/images/icons/icon.svg")
        print("   3. Gere PNGs nos tamanhos: 72, 96, 128, 144, 152, 192, 384, 512")
        print("   4. Renomeie como: icon-72x72.png, icon-96x96.png, etc.")
        return False
    
    if not SVG_PATH.exists():
        print(f"❌ Arquivo SVG não encontrado: {SVG_PATH}")
        return False
    
    print(f"📁 Gerando ícones em: {ICONS_DIR}")
    ICONS_DIR.mkdir(parents=True, exist_ok=True)
    
    for size in ICON_SIZES:
        output_path = ICONS_DIR / f"icon-{size}x{size}.png"
        print(f"   Gerando {size}x{size}...", end=" ")
        
        try:
            # Converter SVG para PNG
            cairosvg.svg2png(
                url=str(SVG_PATH),
                write_to=str(output_path),
                output_width=size,
                output_height=size
            )
            print("✓")
        except Exception as e:
            print(f"✗ Erro: {e}")
    
    print("\n✅ Ícones gerados com sucesso!")
    return True


def create_placeholder_icons():
    """Cria ícones placeholder simples usando PIL"""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("❌ PIL não disponível. Instale: pip install pillow")
        return False
    
    print(f"📁 Criando ícones placeholder em: {ICONS_DIR}")
    ICONS_DIR.mkdir(parents=True, exist_ok=True)
    
    for size in ICON_SIZES:
        output_path = ICONS_DIR / f"icon-{size}x{size}.png"
        print(f"   Criando {size}x{size}...", end=" ")
        
        try:
            # Criar imagem com gradiente
            img = Image.new('RGB', (size, size), color=(18, 46, 64))  # #122E40
            draw = ImageDraw.Draw(img)
            
            # Desenhar borda arredondada (simplificada)
            border_color = (39, 75, 89)  # #274B59
            draw.rectangle([0, 0, size-1, size-1], outline=border_color, width=max(2, size//32))
            
            # Desenhar "S" no centro
            font_size = int(size * 0.6)
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                font = ImageFont.load_default()
            
            text = "S"
            text_color = (208, 229, 242)  # #D0E5F2
            
            # Centralizar texto
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (size - text_width) // 2
            y = (size - text_height) // 2 - bbox[1]
            
            draw.text((x, y), text, fill=text_color, font=font)
            
            img.save(output_path, 'PNG')
            print("✓")
        except Exception as e:
            print(f"✗ Erro: {e}")
    
    print("\n✅ Ícones placeholder criados!")
    return True


if __name__ == "__main__":
    print("🎨 Gerador de Ícones PWA - SyncRH")
    print("=" * 40)
    
    if HAS_DEPS:
        success = generate_icons()
    else:
        print("⚠️  cairosvg não disponível, usando placeholders...")
        success = create_placeholder_icons()
    
    if success:
        print("\n📋 Próximos passos:")
        print("   1. Verifique os ícones em static/images/icons/")
        print("   2. Reinicie o servidor Django")
        print("   3. Acesse o sistema e verifique o PWA")

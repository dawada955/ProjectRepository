from PyQt5.QtGui import QFontDatabase, QFont


class FontManager:
    _font_families = {}

    @staticmethod
    def load_font(alias, font_path):
        """
        alias: 自定义别名，如 'PingFang-Regular'
        font_path: 字体文件路径
        """
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id == -1:
            print(f"Failed to load font from {font_path}")
            return None
        families = QFontDatabase.applicationFontFamilies(font_id)
        if families:
            FontManager._font_families[alias] = families[0]
            print(f"Loaded font '{alias}' as '{families[0]}'")
            return families[0]
        return None

    @staticmethod
    def get_font(alias, size=12, weight=QFont.Normal):
        """
        alias: 加载时指定的别名
        """
        family = FontManager._font_families.get(alias)
        if family:
            font = QFont(family, size, weight)
            return font
        else:
            print(f"Font alias '{alias}' not found. Did you load it?")
            return QFont()

# 用法 初始化字体
# FontManager.load_font("NotoSerifCJKsc-ExtraLight", "fonts/NotoSerifCJKsc-ExtraLight.otf")
# FontManager.load_font("NotoSerifCJKsc-SemiBold", "fonts/NotoSerifCJKsc-SemiBold.otf")
# FontManager.load_font("NotoSansCJKsc-VF", "fonts/NotoSansCJKsc-VF.otf")

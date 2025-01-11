TRANSLATIONS = {
    'zh_CN': {
        'settings': '设置',
        'scan_directories': '图片扫描目录：',
        'add_directory': '添加目录',
        'remove_directory': '删除目录',
        'ok': '确定',
        'cancel': '取消',
        'language': '语言：',
        'file_menu': '文件(&F)',
        'new': '新建',
        'exit': '退出',
        'edit_menu': '编辑(&E)',
        'cut': '剪切',
        'copy': '复制',
        'paste': '粘贴',
        'tools_menu': '工具(&T)',
        'help_menu': '帮助(&H)',
        'help': '帮助',
        'about': '关于',
        'select_directory': '选择扫描目录',
        'file_types': '支持的文件类型：'
    },
    'en_US': {
        'settings': 'Settings',
        'scan_directories': 'Scan Directories:',
        'add_directory': 'Add Directory',
        'remove_directory': 'Remove Directory',
        'ok': 'OK',
        'cancel': 'Cancel',
        'language': 'Language:',
        'file_menu': '&File',
        'new': 'New',
        'exit': 'Exit',
        'edit_menu': '&Edit',
        'cut': 'Cut',
        'copy': 'Copy',
        'paste': 'Paste',
        'tools_menu': '&Tools',
        'help_menu': '&Help',
        'help': 'Help',
        'about': 'About',
        'select_directory': 'Select Directory',
        'file_types': 'Supported File Types:'
    }
}

def get_text(key: str, language: str) -> str:
    """获取指定语言的文本"""
    return TRANSLATIONS.get(language, TRANSLATIONS['en_US']).get(key, key) 
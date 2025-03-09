import os

def fix_imports(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 替换导入语句
                content = content.replace('from app.agent.base', 'from backend.agent.agent.base')
                content = content.replace('from app.agent.', 'from backend.agent.')
                content = content.replace('import app.agent.', 'import backend.agent.')
                content = content.replace('from app.', 'from backend.')
                content = content.replace('import app.', 'import backend.')
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)

if __name__ == "__main__":
    # 修复app目录下的所有Python文件
    fix_imports('app')
    # 修复backend目录下的所有Python文件
    fix_imports('backend') 
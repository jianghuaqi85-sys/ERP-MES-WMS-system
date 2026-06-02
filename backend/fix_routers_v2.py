import os

def fix_routers_v2():
    base_dir = os.path.join(os.path.dirname(__file__), "app", "apps")
    for root, dirs, files in os.walk(base_dir):
        if "router.py" in files:
            file_path = os.path.join(root, "router.py")
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            old_line2 = 'result = {"total": total, "items": items}'
            new_line2 = 'result = {"total": total, "items": [{k: v for k, v in item.__dict__.items() if not k.startswith(\'_\')} for item in items]}'
            
            if old_line2 in content:
                content = content.replace(old_line2, new_line2)
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"Fixed result= {file_path}")

if __name__ == "__main__":
    fix_routers_v2()

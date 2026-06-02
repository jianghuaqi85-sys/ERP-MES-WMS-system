import os

def fix_routers():
    base_dir = os.path.join(os.path.dirname(__file__), "app", "apps")
    for root, dirs, files in os.walk(base_dir):
        if "router.py" in files:
            file_path = os.path.join(root, "router.py")
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Replace the items line
            old_line = 'return {"total": total, "items": items}'
            new_line = 'return {"total": total, "items": [{k: v for k, v in item.__dict__.items() if not k.startswith(\'_\')} for item in items]}'
            
            if old_line in content:
                content = content.replace(old_line, new_line)
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"Fixed {file_path}")
            else:
                print(f"Skipped {file_path} (no match)")

if __name__ == "__main__":
    fix_routers()

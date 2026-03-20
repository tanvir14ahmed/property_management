import os
import re

def replace_currency(root_dir):
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".html"):
                path = os.path.join(root, file)
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Replace $ with ৳ only when it looks like a price (optional, but let's do all $)
                # The user asked to change $ to ৳
                new_content = content.replace("$", "৳")
                
                if new_content != content:
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(new_content)
                    print(f"Updated {path}")

if __name__ == "__main__":
    replace_currency(r"d:\Joy\Projects\property_management\templates")

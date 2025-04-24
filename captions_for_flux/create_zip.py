#!/usr/bin/env python
import os
import argparse
import zipfile

def create_zip_archive(folder_path, output_path=None):
    if output_path is None:
        folder_name = os.path.basename(os.path.normpath(folder_path))
        output_path = os.path.join(os.path.dirname(folder_path), folder_name + ".zip")
    print(f"Creating zip archive from: {folder_path}")
    print(f"Archive will be saved as: {output_path}")

    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                # Используем относительный путь для сохранения структуры каталогов
                arcname = os.path.relpath(file_path, start=folder_path)
                zipf.write(file_path, arcname)
    print("Zip archive created successfully.")

def main():
    parser = argparse.ArgumentParser(description="Create a zip archive from a folder.")
    parser.add_argument("folder", help="Path to the folder to be zipped.")
    parser.add_argument("-o", "--output", help="Output zip file path (default: folder.zip in folder's parent).")
    args = parser.parse_args()

    if not os.path.isdir(args.folder):
        print(f"Error: The folder '{args.folder}' does not exist or is not a directory.")
        exit(1)
    
    create_zip_archive(args.folder, args.output)

if __name__ == '__main__':
    main()

import os
import re
import shutil
import tempfile
import zipfile

print("#################### ETS2 mp_mod_optional converter ####################\n")
print("#################### use at your own risk ##############################\n")
dir_path = input(r"Input mod path(ex:D:\SteamLibrary\steamapps\workshop\content\227300)：")
is_modify_all = int(input("\nIs it necessary to force the conversion of the 'mp_mod_optional' to false in the mod ? ("
                          "input 1 or 0)： \n"))
modify_name = 'manifest.sii'
modify_flag = 'mp_mod_optional: true'
if is_modify_all == 1:
    is_modify_all = True
elif is_modify_all == 0:
    is_modify_all = False
else:
    print("input error！")
    quit()
optional_false_flag = 'mp_mod_optional: false'
temp_dir = tempfile.mkdtemp()


def update_content(content):
    pattern = r'}(?=\s*})'
    return re.sub(pattern, f'{modify_flag}\n}}', content, count=1)


def write_file(updated_content, file_path, zip_info=None, new_zip=None, mode=None):
    if mode == 'zip':
        new_zip.writestr(zip_info, updated_content.encode('utf-8'))
    else:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(updated_content)
    print(f"Modified {file_path}")


def process_manifest_file(file_path, content, zip_info=None, new_zip=None, mode=None):
    if modify_flag not in content and optional_false_flag not in content:
        updated_content = update_content(content)
    elif is_modify_all and optional_false_flag in content:
        updated_content = content.replace(optional_false_flag, modify_flag)
    else:
        updated_content = content

    if mode == 'zip':
        write_file(updated_content, file_path, zip_info, new_zip, mode='zip')
    else:
        write_file(updated_content, file_path)


def main():
    for folder_name, sub_folders, filenames in os.walk(dir_path):
        if modify_name in filenames:
            manifest_path = os.path.join(folder_name, modify_name)
            with open(manifest_path, 'r', encoding='utf-8') as file:
                content = file.read()
                process_manifest_file(manifest_path, content)

        for filename in filenames:
            if filename.endswith(".zip"):
                zip_path = os.path.join(folder_name, filename)
                try:
                    temp_zip_path = os.path.join(temp_dir, filename)
                    with zipfile.ZipFile(zip_path, 'r') as original_zip, zipfile.ZipFile(temp_zip_path, 'w') as new_zip:
                        for file_info in original_zip.infolist():
                            if file_info.filename == modify_name:
                                with original_zip.open(file_info) as manifest_file:
                                    content = manifest_file.read().decode('utf-8')
                                    process_manifest_file(zip_path, content, file_info, new_zip, mode='zip')
                            else:
                                new_zip.writestr(file_info, original_zip.read(file_info.filename))

                    shutil.move(temp_zip_path, zip_path)
                except RuntimeError:
                    print(f"skip encrypt zipfile: {zip_path}")
                    continue
    print("\nComplete！\n")
    os.system("pause")


if __name__ == '__main__':
    main()

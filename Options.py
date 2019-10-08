import json


def get_list_sub():
    my_list = []
    with open("Options.json", "r+") as my_file:
        json_data = json.load(my_file)
        for lang in json_data['Subtitle']:
            my_list.append((lang, json_data['Subtitle'][lang]['Checked']))
    return my_list


def update_list_sub(my_list={}):
    with open("Options.json", "r+") as my_file:
        json_data = json.load(my_file)
        sub_code_list = json_data['List Subtitle']
        for key, value in my_list.items():
            json_data['Subtitle'][key]['Checked'] = value
            vl = json_data['Subtitle'][key]['Code']
            if value and vl not in sub_code_list:
                sub_code_list.append(vl)
            elif vl in sub_code_list and not value:
                sub_code_list.remove(vl)
        json_data['List Subtitle'] = sub_code_list
        my_file.seek(0)
        json.dump(json_data, my_file, indent=4)
        my_file.truncate()


def get_list_sub_codes():
    with open("Options.json", "r+") as my_file:
        json_data = json.load(my_file)
        return json_data['List Subtitle']


def get_directory():
    with open("Options.json", "r+") as my_file:
        json_data = json.load(my_file)
        return json_data['Directory']


def update_directory(new_dir):
    with open("Options.json", "r+") as my_file:
        json_data = json.load(my_file)
        json_data['Directory'] = new_dir
        my_file.seek(0)
        json.dump(json_data, my_file, indent=4)
        my_file.truncate()

import json
import re


def xml_to_json(xml_str):
    def parse_element(xml):
        result = {}
        tag_pattern = re.compile(r'<(?P<tag>\w+)>(?P<content>.*?)</(?P=tag)>', re.DOTALL)

        for match in tag_pattern.finditer(xml):
            tag = match.group('tag')
            content = match.group('content').strip()

            if re.search(r'<\w+>', content):
                nested_value = parse_element(content)
                if tag in result:
                    if not isinstance(result[tag], list):
                        result[tag] = [result[tag]]
                    result[tag].append(nested_value)
                else:
                    result[tag] = nested_value
            else:
                if tag in result:
                    if not isinstance(result[tag], list):
                        result[tag] = [result[tag]]
                    result[tag].append(content)
                else:
                    result[tag] = content

        return result

    json_data = parse_element(xml_str)

    if 'root' in json_data:
        json_data = json_data['root']

    return json_data


with open("schedule.xml", "r", encoding="utf-8") as file:
    xml_data = file.read()

json_data = xml_to_json(xml_data)

with open("schedule_d2.json", "w", encoding="utf-8") as file:
    json.dump(json_data, file, ensure_ascii=False, indent=2)

print("Конвертировано в schedule_d2.json.")


import json
import xml.etree.ElementTree as ET


def xml_to_dict(element):
    result = {}
    if element.attrib:
        result.update(element.attrib)
    if element.text and element.text.strip():
        result['text'] = element.text.strip()
    for child in element:
        child_result = xml_to_dict(child)
        if child.tag not in result:
            result[child.tag] = child_result
        else:
            if not isinstance(result[child.tag], list):
                result[child.tag] = [result[child.tag]]
            result[child.tag].append(child_result)
    return result


with open("schedule.xml", "r", encoding="utf-8") as file:
    xml_data = file.read()

root = ET.fromstring(xml_data)

json_data = xml_to_dict(root)

with open("schedule_d1.json", "w", encoding="utf-8") as file:
    json.dump(json_data, file, ensure_ascii=False, indent=2)

print("Конвертировано в schedule_d1.json.")


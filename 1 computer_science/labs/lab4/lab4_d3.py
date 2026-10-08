import json

def xml_to_json(xml_str):
    def parse_element(xml, start_pos=0):
        result = {}
        while start_pos < len(xml):
            start_tag_pos = xml.find('<', start_pos)
            if start_tag_pos == -1:
                break

            end_tag_pos = xml.find('>', start_tag_pos)
            if end_tag_pos == -1:
                break

            tag = xml[start_tag_pos + 1:end_tag_pos]
            content_start_pos = end_tag_pos + 1

            close_tag_pos = xml.find(f"</{tag}>", content_start_pos)
            if close_tag_pos == -1:
                break

            content = xml[content_start_pos:close_tag_pos].strip()

            if content.startswith("<"):
                nested_value, new_pos = parse_element(content)
                result[tag] = nested_value
                start_pos = close_tag_pos + len(f"</{tag}>")
            else:
                result[tag] = content
                start_pos = close_tag_pos + len(f"</{tag}>")

        return result, start_pos

    json_data, _ = parse_element(xml_str)

    if 'root' in json_data:
        json_data = json_data['root']

    return json_data


with open("ch.xml", "r", encoding="utf-8") as file:
    xml_data = file.read()

json_data = xml_to_json(xml_data)

with open("ch_d3.json", "w", encoding="utf-8") as file:
    json.dump(json_data, file, ensure_ascii=False, indent=2)

print("Конвертировано в ch_d3.json.")



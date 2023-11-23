import json
from collections import deque

class LimitedQueue:
    def __init__(self, max_size):
        self.queue = deque(maxlen=max_size)

    def enqueue(self, item):
        self.queue.append(item)

    def dequeue(self):
        if self.is_empty():
            return None
        return self.queue.popright()

    def is_empty(self):
        return len(self.queue) == 0

    def size(self):
        return len(self.queue)


def exclude_key(dictionary, key_to_exclude):
    return {key: value for key, value in dictionary.items() if key != key_to_exclude}

def find_item_by_id(nested_dict, target_id):
    for key, value in nested_dict.items():
        if isinstance(value, dict):
            if 'id' in value and value['id'] == target_id:
                return key
            else:
                result = find_item_by_id(value, target_id)
                if result:
                    return result
    return None

def makeJsonList(data_str):
    json_strings = data_str.split('}{')
    json_list = []
    for s in json_strings:
        s = s.replace("{", "")
        s = s.replace("}", "")
        s = "{" + s + "}"
        json_tmp = json.loads(s)
        json_list.append(json_tmp)
    return json_list

def find_item(dictionary, identifier):
    for key, values in dictionary.items():
        if values[0] == identifier:
            return key
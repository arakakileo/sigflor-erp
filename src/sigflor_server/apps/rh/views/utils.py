from rest_framework import parsers

class NestedMultipartParser(parsers.MultiPartParser):
    def parse(self, stream, media_type=None, parser_context=None):
        result = super().parse(stream, media_type=media_type, parser_context=parser_context)
        data = {}
        # Mescla dados e arquivos
        for key, value in result.data.items():
            self._expand_dict(data, key, value)
        for key, value in result.files.items():
            self._expand_dict(data, key, value)
        return parsers.DataAndFiles(data, result.files)

    def _expand_dict(self, data, key, value):
        keys = key.replace(']', '').split('[')
        current = data
        for i, k in enumerate(keys[:-1]):
            if k not in current:
                next_key_is_int = keys[i+1].isdigit()
                current[k] = [] if next_key_is_int else {}
            if isinstance(current, list):
                idx = int(k)
                while len(current) <= idx: current.append({})
                current = current[idx]
            else:
                current = current[k]
        last_key = keys[-1]
        if isinstance(current, list):
            idx = int(last_key)
            while len(current) <= idx: current.append({})
            current[idx] = value
        else:
            current[last_key] = value
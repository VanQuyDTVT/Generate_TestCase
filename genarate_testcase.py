import os
import ast
import time
import json
import configs
import templates as templates
import itertools


class TestCaseGenerator:
    def __init__(self) -> None:
        self.load_configs()


    @staticmethod
    def pre_process_host_port():
        host = configs.HOST.split('://')[1]
        if ':' in host:
            port = host.split(':')[1]
            host = host.split(':')[0].split('.')
        else:
            port = '80'
            host = host.split('.')
        return host, port


    @staticmethod
    def get_start_end_step(value:tuple):
        if len(value) == 3:
            start, end, step = value
        else:
            start, end = value
            step = 1
        end += 1
        return start, end, step

    @staticmethod
    def find_dynamic_index(name:str):
        start, end, step, new_name = None, None, None, None
        if '(' in name and ')' in name:
            start_idx = name.index('(')
            end_idx = name.index(')') + 1
            dynamic_index = ast.literal_eval(name[start_idx:end_idx])
            try:
                value = ast.literal_eval(dynamic_index)
                start, end, step = TestCaseGenerator.get_start_end_step(value)
                new_name = name[0:start_idx] + '{}' + name[end_idx:]
            except Exception:
                print(f'WARN: Dynamic index is invalid format! \n"{name}"')
        return start, end, step, new_name


    def pre_process_params(self):
        param_source = {
            0: self.request_body,
            1: self.request_params
            }
        for check, param in param_source.items():
            print(check, param)
            for key, values in param.items():
                if check and key in configs.BODY.keys():
                    raise KeyError(f'Duplicated param "{key}" at both request param and request body!')
                for value in values:
                    start = None
                    if isinstance(value, tuple):
                        start, end, step = TestCaseGenerator.get_start_end_step(value)
                        new_value = None
                        print('is tuple:',start, end, step)
                    elif isinstance(value, str):
                        start, end, step, new_value = TestCaseGenerator.find_dynamic_index(value)

                    if start is not None:
                        values.pop(values.index(value))
                        for idx in range(start, end, step):
                            value = idx if new_value is None else new_value.format(idx)
                            values.append(value)
                        print(param)

        all_params = {**self.request_body, **self.request_params}

        keys = all_params.keys()
        values = all_params.values()

        return keys, values


    @staticmethod
    def mapper(template:str, data:dict) -> str:
        output = template
        for key, value in data.items():
            output = output.replace(key, value)

        return output


    def load_configs(self):
        self.api = configs.API
        self.api_key = configs.API_KEY
        self.method = configs.METHOD
        self.folder_name = configs.METHOD + ' ' + configs.API.split('/')[-1]
        self.protocol = configs.HOST.split('://')[0]
        self.host, self.port = TestCaseGenerator.pre_process_host_port()
        self.path = configs.API.strip('/').split('/')
        self.request_params = configs.PARAMS
        self.request_body = configs.BODY
        self.params, self.param_values = self.pre_process_params()


    @staticmethod
    def generate_query(query_params):
        case=[]
        for key, value in query_params:
            mapping_data = dict(
                __KEY = key,
                __VALUE = value
            )
            case.append(TestCaseGenerator.mapper(templates.case, mapping_data))
        return TestCaseGenerator.mapper(templates.query, 
                                        dict(__QUERY_DATA=','.join(case)))


    def generate_header(self):
        mapping_data = dict(
            __API_KEY = self.api_key,
        )
        return TestCaseGenerator.mapper(templates.header, mapping_data)


    def generate_url(self, query_params):
        if query_params:
            __raw_url = f"{self.host}{self.api}?{'&'.join(f'{key}={value}' for key, value in query_params)}"
            __query = self.generate_query(query_params)
        else:
            __raw_url = f"{self.host}{self.api}"
            __query = ''

        mapping_data = dict(
            __RAW_URL = __raw_url,
            __HOST = f'''"{'","'.join(self.host)}"''',
            __PORT = self.port,
            __PATH = f'''"{'","'.join(self.path)}"''',
            __QUERY = __query
        )
        return TestCaseGenerator.mapper(templates.url, mapping_data)


    def generate_body(self, query_body):
        if not query_body:
            return ''
        __body = dict()
        for key,value in query_body:
            __body[key] = value
        mapping_data = dict(
            __BODY_RAW = str(__body).replace('"','\\\\\\"').replace("'", '\\"')
        )
        return TestCaseGenerator.mapper(templates.body, mapping_data)


    def generate_item(self, query_params, query_body):
        mapping_data = dict(
            __NAME = (','.join(f'{key}={value}' for key, value in query_params+query_body)).replace('"', ''),
            __METHOD = self.method,
            __HEADER = self.generate_header(),
            __URL = self.generate_url(query_params),
            __BODY = self.generate_body(query_body)
        )
        return TestCaseGenerator.mapper(templates.item, mapping_data)


    def generate_info(self, items:list):
        mapping_data = dict(
            __NAME = self.folder_name,
            __ITEM = items
        )
        return TestCaseGenerator.mapper(templates.info, mapping_data)


    def create_items(self):
        items = []
        for combination in itertools.product(*self.param_values):
            query_params= []
            query_body= []
            for key, value in zip(self.params, combination):
                if value is None:
                    continue

                if key in self.request_params.keys():
                    query_params.append((key, str(value)))
                else:
                    query_body.append((key, str(value)))

            item = self.generate_item(query_params, query_body)
            items.append(item)

        return ','.join(items)


    def generate_testcase(self):
        items = self.create_items()
        data = self.generate_info(items)
        path_file = f'output/{self.folder_name}.json'

        with open(path_file, 'w+') as file:
            # file.write(data)
            json.dump(json.loads(data), file, indent=4)


def main():
    os.makedirs('output', exist_ok=True)
    _start_time = time.time()
    print('Generating...')
    try:
        worker = TestCaseGenerator()
        worker.generate_testcase()
        print('Done!! Generate time: ', time.time()-_start_time)
    except Exception as e:
        print('Error!!')
        raise KeyError(e)


if __name__ == '__main__':
    main()
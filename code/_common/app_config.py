import json


class ConfigManager():
    _instance = None
    
    CONFIG_FILE = '.aegis_config'
    
        # {
        #     'id': 'HOME',
        #     'name': 'Home',
        #     'type': 'connection',
        #     'query': 'from=Chavornay&to=Renens',
        #     'min_delay': 2,
        #     'checks': 5,
        #     'display': True,
        #     'notify_start': None,
        #     'notify_end': None,
        #     # 'check_frequency': 60
        # },
        # {
        #     'id': 'HOME2',
        #     'name': 'Home2',
        #     'type': 'connection',
        #     'query': 'from=Renens&to=Chavornay',
        #     'min_delay': 2,
        #     'checks': 5,
        #     'display': True,
        #     'notify_start': None,
        #     'notify_end': None,
        #     # 'check_frequency': 60
        # },
    check_list = []
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            
            conf = None
            try:
                with open(cls._instance.CONFIG_FILE, "r") as infile:
                    conf = json.load(infile)
            except Exception as e:
                print("ERROR LOADING CONF", cls._instance.CONFIG_FILE, e)
                pass
            
            try:
                cls._instance.check_list = conf["checks"]
            except:
                pass

        return cls._instance
    
    def save(self):
        json_object = json.dumps({
            'checks': self.check_list,
        }, indent=4)
            
        with open(self.CONFIG_FILE, 'w') as outfile:
            outfile.write(json_object)


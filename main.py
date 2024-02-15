import os
import sys
import requests

from homeassistant_api import Client

with Client(
    'http://homeassistant.local:8123/api',
    # secret from env
    f'{os.environ["HOME_ASSISTANT_SECRET"]}',
) as client:
    while True:
        prompt = input('Enter your request: ')

        print(f'User Request: {prompt}')

        entites = {
            'light.lamp_light': 'living room lamp',
            'switch.heater_switch': 'living room heater',
            'switch.living_room_radiator': 'living room radiator',
            'switch.wax_melter': 'Bedroom wax melter',
            'switch.dehumidifier': 'Dehumidifier',
            'switch.bed_warmer_switch': 'Bed warmer',
            'light.bedroom_lamps': 'Bedroom lamps',
        } 

        entites_str = '\n'.join([f'entity:{entity} friendly_name:{action}' for entity, action in entites.items()])

        system_message = f"""
            As a home assistant, your role is to interpret user requests to control home devices. Users might request actions like turning devices on or off.\n\n

            Available devices and their commands are as follows:\n
            {entites_str}\n\n

            Format your response as 'entity:action', where 'entity' is the device identifier and 'action' is either 'on', 'off', or 'toggle'. \n\n

            Examples:\n
            - To turn off the living room lamp: entity:light.lamp_light action:off\n
            - To turn on the living room heater: entity:switch.heater_switch action:on\n\n

            For multiple actions in a single request, separate each command by a new line.\n\n

            Remember to use only the provided entity identifiers and actions. If the request refers to a device in a general term, use your judgment based on the available entities. For instance, if asked to 'turn off the living room light' with no specific entity for a light, assume the user means the 'living room lamp'.\n\n

            Example of good response:\n
            User Request: I am going to bed in half an hour can you prepeare the bedroom\n\n

            Response:\n\n
            entity:light.bedroom_lamps action:on\n
            entity:switch.bed_warmer_switch action:on\n
            entity:switch.wax_melter action:on\n\n

            Example of bad response:\n
            User Request: I am going to bed in half an hour can you prepeare the bedroom\n
            Actions:\n
            entity:bedroom_lamps action:on\n
            entity:bed_warmer_switch action:off\n
            entity:wax_melter action:off\n\n

            The user will want the lights on to see, the bed warmer on to warm the bed, and the wax melter on to create a nice smell. This will create a nice atmosphere for the user to go to bed.
        """

        def main():

            response = requests.post('http://localhost:11434/api/generate', json={
                'prompt': f'Your instructions: {system_message} \n\n User Request: {prompt}',
                'model': 'llama2:7b-chat',
                'stream': False,
            })

            data = response.json()

            if data['done']:
                print(data['response'])

                actions = data['response'].split('\n')
                
                print(f'Actions: {actions}')

                for action in actions:
                    entity = action.split(' ')[0].split(':')[1].strip()
                    action = action.split(' ')[1].split(':')[1].strip()
                
                    print(f'entity:{entity} action:{action}')
        #
                    supported_domains = ['automation', 'input_boolean', 'remote', 'script', 'binary_sensor', 'climate', 'cover', 'device_tracker', 'fan', 'light', 'lock', 'media_player', 'sensor', 'switch']
                    
                    domain = entity.split('.')[0]

                    if domain in supported_domains:
                        device = client.get_domain(domain)

                        if action == 'on':
                            device.turn_on(entity_id=entity)
                        if action == 'off':
                            device.turn_off(entity_id=entity)
                        if action == 'toggle':
                            device.toggle(entity_id=entity)

                    else:
                        print('Error: Entity type not supported.')

            else:
                print('Error: ', data['error'])

        if __name__ == '__main__':
            main()

import os
import sys
import requests

from homeassistant_api import Client
from system_message import get_message

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
        
        system_message = get_message(entites_str)

        def main():

            response = requests.post('http://localhost:11434/api/generate', json={
                'prompt': f'Your instructions: {system_message} \n\n User Request: {prompt}',
                'model': 'llama2:7b-chat',
                'stream': False,
            })

            data = response.json()

            if data['done']:
                try:
                    actions = data['response'].split('\n')
                    
                    print(f'Actions: {actions}')

                    for action in actions:
                        try:
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
                        except:
                            print('Error: Invalid action format.')
                except:
                    print('Error: Invalid response format.')
            else:
                print('Error: ', data['error'])

        if __name__ == '__main__':
            main()

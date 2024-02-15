import os
import sys
import requests

from homeassistant_api import Client
from system_message import get_action_message, get_user_message

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

        action_system_message = get_action_message(entites_str)

        def main():

            action_response = requests.post('http://localhost:11434/api/generate', json={
                'prompt': f'Your instructions: {action_system_message} \n\n User Request: {prompt}',
                'model': 'llama2:7b-chat',
                'stream': False,
            })

            data = action_response.json()

            if data['done']:
                actions = data['response'].split('\n')

                user_system_message = get_user_message(', '.join(actions), prompt)

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

                human_response = requests.post('http://localhost:11434/api/generate', json={
                    'prompt': user_system_message,
                    'model': 'llama2:7b-chat',
                    'stream': False,
                })

                human_data = human_response.json()

                if human_data['done']:
                    print(human_data['response'])
                else:
                    print('Error: Invalid response format.')                    
            else:
                print('Error: ', data['error'])

        if __name__ == '__main__':
            main()

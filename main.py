import os
import sys
import requests

from homeassistant_api import Client

with Client(
    'http://homeassistant.local:8123/api',
    # secret from env
    f'{os.environ["HOME_ASSISTANT_SECRET"]}',
) as client:

    prompt = sys.argv[1]

    print(f'User Request: {prompt}')

    entites = {
        'light.lamp_light': 'living room lamp',
        'switch.heater_switch': 'living room heater',
        'switch.living_room_radiator': 'living room radiator',
        'switch.wax_melter': 'Bedroom wax melter',
        'switch.dehumidifier': 'Dehumidifier',
    } 

    system_message = f"""
        You are a home assistant. You can control the home devices depending on the user's request.
        The user can say "Turn off living room lamp" to turn off the living room lamp.
        Here are the entities {str(entites)}. 
        \nFor example you should repond with: 
        \n\nentity:light.lamp_light action:off
        \n\nStrictly follow the format and the entities provided.
        \n\nDo not refer to any other entities. So you can make assumptions about the entities. For example if the user says "Turn off the living room light", and there is no other entitiy referring light, you can assume that the user is referring to the living room lamp.
        \nThe user can request multiple actions in a single request. For example "Turn off the living room lamp and turn on the living room heater".
        \nThis can be done by putting each entity and action in a new line.
        \n\nFor example you should repond with:
        \n\nentity:light.lamp_light action:off
        \nentity:switch.heater_switch action:on
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

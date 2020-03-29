""" Overmind - Top level Object """
from defs import *
from glo import *
import director.overseer

__pragma__('noalias', 'name')
__pragma__('noalias', 'undefined')
__pragma__('noalias', 'Infinity')
__pragma__('noalias', 'keys')
__pragma__('noalias', 'get')
__pragma__('noalias', 'set')
__pragma__('noalias', 'type')
__pragma__('noalias', 'update')

def run():
    """ Run the Overmind """

    #quick way to determine where the hives are
    hives = []
    tendrils = []
    rooms = [Game.rooms[n] for n in Object.keys(Game.rooms)]
    for room in rooms:
        spawns = room.find(FIND_MY_SPAWNS)
        if spawns != undefined:
            hives.append(room)
        else:
            tendrils.append(room)

    #quick way to group the tendrils with to their hives
    #TO DO

    #Run each hive
    for hive in hives:
        director.overseer.run(hive)

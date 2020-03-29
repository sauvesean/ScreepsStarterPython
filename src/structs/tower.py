""" tower structure """
from defs import *
from glo import *

__pragma__('noalias', 'name')
__pragma__('noalias', 'undefined')
__pragma__('noalias', 'Infinity')
__pragma__('noalias', 'keys')
__pragma__('noalias', 'get')
__pragma__('noalias', 'set')
__pragma__('noalias', 'type')
__pragma__('noalias', 'update')


def run(structure):
    """
    Runs a tower structure.
    :param structure: The tower to run
    """

    #pre-checks
    if not structure.isActive or structure.energy <= 0:
        return

    enemies = structure.room.find(FIND_HOSTILE_CREEPS)
    #attack enemies
    if len(enemies) > 0:
        structure.attack(structure.pos.findClosestByRange(enemies))
        #console.log('attacking enemy')
        return

    creeps = structure.room.find(FIND_MY_CREEPS)
    damaged_creeps = [c for c in creeps if c.hits < c.hitsMax]
    #heal damaged creeps
    if len(damaged_creeps) > 0:
        structure.heal(structure.pos.findClosestByRange(damaged_creeps))
        #console.log('healing creep')
        return

    structures = structure.room.find(FIND_STRUCTURES)
    damaged_structures = [s for s in structures if \
        ((s.hits < s.hitsMax * 0.95) and \
        (s.structureType != STRUCTURE_WALL) and (s.structureType != STRUCTURE_RAMPART))]
    #repair structures (other than walls and ramparts)
    if len(damaged_structures) > 0:
        structure.repair(structure.pos.findClosestByRange(damaged_structures))
        #console.log('repairing structure')
        return

    #damaged_walls = [s for s in structures if \
    #    ((s.hits < s.hitsMax * 0.80) and \
    #    ((s.structureType == STRUCTURE_WALL) or (s.structureType == STRUCTURE_RAMPART)))]
    ##repair walls and ramparts
    #if len(damaged_walls) > 0:
    #    lowest_wall = None
    #    lowest_hits = 0
    #    for wall in damaged_walls:
    #        if wall.hits < lowest_hits or lowest_hits == 0:
    #            lowest_wall = wall
    #            lowest_hits = wall.hits
    #    structure.repair(lowest_wall)
    #    console.log('repairing wall/rampart')
    #    return

    #console.log('nothing for tower to do')

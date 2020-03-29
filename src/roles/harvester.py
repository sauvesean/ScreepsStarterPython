""" harvester role """
from defs import *
from glo import *
import util

__pragma__('noalias', 'name')
__pragma__('noalias', 'undefined')
__pragma__('noalias', 'Infinity')
__pragma__('noalias', 'keys')
__pragma__('noalias', 'get')
__pragma__('noalias', 'set')
__pragma__('noalias', 'type')
__pragma__('noalias', 'update')


def run(creep):
    """
    Runs a creep as a generic harvester.
    :param creep: The creep to run
    """

    if creep.carryCapacity == 0:
        creep.suicide()

    # If we're full, stop filling up and remove the saved source
    if creep.memory.filling and _.sum(creep.carry) >= creep.carryCapacity:
        creep.memory.filling = False
    # If we're empty, start filling again and remove the saved target
    elif not creep.memory.filling and creep.carry.energy <= 0:
        creep.memory.filling = True
        del creep.memory.target
        source = get_best_source(creep)
        if len(source) > 0:
            creep.memory.source = source.id


    if creep.memory.filling:
        # If we have a saved source, use it
        if creep.memory.source:
            source = Game.getObjectById(creep.memory.source)
        else:
            # Get a random new source and save it
            source = creep.pos.findClosestByPath(util.get_available_sources(creep.room))
            if len(source) > 0:
                creep.memory.source = source.id
            else:
                #creep.memory.role = ROLE_BUILDER
                #del creep.memory.target
                #del creep.memory.source
                return


        # If we're near the source, harvest it - otherwise, move to it.
        if creep.pos.isNearTo(source.pos):
            result = creep.harvest(source)
            if result != OK:
                console.log("[{}] Unknown result from creep.harvest({}): {}".format(creep.name, source, result))
                del creep.memory.source
        else:
            creep.moveTo(source)
    else:
        # If we have a saved target, use it
        if creep.memory.target:
            target = Game.getObjectById(creep.memory.target)
        else:
            # Get a random new target.
            storage_types_energy_base = [STRUCTURE_SPAWN, STRUCTURE_EXTENSION]
            storage_types_generic_temporary = [STRUCTURE_CONTAINER, STRUCTURE_STORAGE]

            #only transfer to containers and storage if there are haulers here
            haulers = [c for c in creep.room.find(FIND_MY_CREEPS) \
                if (c.memory.role == ROLE_HAULER and c.memory.assisting_role == ROLE_HARVESTER)]
            if len(haulers) > 0:
                target = creep.pos.findClosestByPath( \
                    [ \
                        s for s in creep.room.find(FIND_STRUCTURES) \
                        if ([t for t in storage_types_energy_base if t == s.structureType] and \
                        s.energy < s.energyCapacity) or \
                        ([t for t in storage_types_generic_temporary if t == s.structureType] and \
                        _.sum(s.store) < s.storeCapacity) \
                    ])
            else:
                target = creep.pos.findClosestByPath( \
                    [ \
                        s for s in creep.room.find(FIND_STRUCTURES) \
                        if ([t for t in storage_types_energy_base if t == s.structureType] and \
                        s.energy < s.energyCapacity) \
                    ])

            if len(target) == 0:
                console.log('cant find path for creep {}'.format(creep.name))
                return
            creep.memory.target = target.id

        if creep.pos.isNearTo(target):
            result = creep.transfer(target, RESOURCE_ENERGY)
            if result == OK or result == ERR_FULL:
                del creep.memory.target
            else:
                console.log("[{}] Unknown result from creep.transfer({}, {}): {}".format(
                    creep.name, target, RESOURCE_ENERGY, result))


        else:
            creep.moveTo(target)

def get_best_source(creep):
    sources = [s for s in creep.room.find(FIND_SOURCES) if s.energy > 0]
    best_score = 10000.000000
    for source in sources:

        hostile_creeps = source.pos.findInRange(FIND_HOSTILE_CREEPS, 10)
        hostile_spawns = source.pos.findInRange(FIND_HOSTILE_STRUCTURES, 10)
        used_work = get_source_used_work(creep, source)
        if len(hostile_creeps) == 0 and len(hostile_spawns) == 0 and used_work < 8:
            score = get_source_score(creep, source)
            if score <= best_score:
                best_score = score
                best = source

    if not best:
        for source in sources:
            score = get_source_score(creep, source)
            if score <= best_score:
                best_score = score
                best = source
    return best

def get_source_score(creep, source):
    score = get_source_used_spots(creep, source) / util.get_source_spots(source)
    return score


def get_source_used_spots(creep, source):
    creeps = [c for c in creep.room.find(FIND_MY_CREEPS) if \
        c.memory.role == ROLE_HARVESTER and c.memory.source == source.id and c.id != creep.id]
    return len(creeps)


def get_source_used_work(creep, source):
    total_work = 0
    creeps = [c for c in creep.room.find(FIND_MY_CREEPS) if \
        c.memory.role == ROLE_HARVESTER and c.memory.source == source.id and c.id != creep.id]
    for creep in creeps:
        body = creep.body
        for part in body:
            total_work += 1 if part.type == WORK else 0
    return total_work

""" builder role """
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
    Runs a creep as a generic builder.
    :param creep: The creep to run
    """

    if creep.carryCapacity == 0:
        creep.suicide()

    if creep.memory.filling and _.sum(creep.carry) >= creep.carryCapacity:
        creep.memory.filling = False
        del creep.memory.source
    elif not creep.memory.filling and creep.carry.energy == 0:
        creep.memory.filling = True
        del creep.memory.target

    if Game.time > creep.memory.target_expires:
        del creep.memory.target

    #console.log('builder filling status: {} energy: {}'.format(creep.memory.filling, creep.carry.energy))
    if creep.memory.filling:
        # If we have a saved source, use it
        source = Game.getObjectById(creep.memory.source)
        if not source:
            source = Game.getObjectById(get_new_source(creep))
        elif source.structureType == STRUCTURE_SPAWN or source.structureType == STRUCTURE_EXTENSION:
            if source.energy == 0:
                source = Game.getObjectById(get_new_source(creep))
        elif source.structureType == STRUCTURE_CONTAINER or source.structureType == STRUCTURE_STORAGE:
            if source.store[RESOURCE_ENERGY] == 0:
                source = Game.getObjectById(get_new_source(creep))

        if not source:
            console.log('no available sources for builder')
            #creep.memory.role = ROLE_HARVESTER
            return

        # If we're near the source, harvest it - otherwise, move to it.
        if creep.pos.isNearTo(source.pos):
            result = creep.withdraw(source, RESOURCE_ENERGY)
            if result != OK:
                console.log("[{}] Unknown result from creep.harvest({}): {}".format(creep.name, source, result))
        else:
            creep.moveTo(source)
    else:
        # If we have a saved target, use it
        target = Game.getObjectById(creep.memory.target)
        if not target:
            #console.log('no saved targets, finding')
            target = Game.getObjectById(get_new_target(creep))
            if not target:
                console.log('no available targets for builder')
                return

        if not isinstance(target, ConstructionSite):
            if target.structureType != STRUCTURE_CONTROLLER and target.hits >= target.hitMax:
                target = Game.getObjectById(get_new_target(creep))
            if not target:
                console.log('no available targets for builder')
                return


        is_close = creep.pos.inRangeTo(target, 3)

        if is_close:
            if isinstance(target, ConstructionSite):
                result = creep.build(target)
                if result == ERR_INVALID_TARGET:
                    del creep.memory.target
                    return

                if result != OK:
                    console.log("[{}] Unknown result from creep.build({}): {}".format(
                        creep.name, target, result))
                # Let the creeps get a little bit closer than required to the controller, to make room for other creeps.
                if not creep.pos.inRangeTo(target, 2):
                    creep.moveTo(target)
            elif target.structureType == STRUCTURE_CONTROLLER:
                #console.log('attempting upgrade controller, progress: {}/{}'.format(target.progress, target.progressTotal))
                result = creep.upgradeController(target)
                if result != OK:
                    console.log("[{}] Unknown result from creep.upgradeController({}): {}".format(
                        creep.name, target, result))
                # Let the creeps get a little bit closer than required to the controller, to make room for other creeps.
                if not creep.pos.inRangeTo(target, 2):
                    creep.moveTo(target)
            else:
                result = creep.repair(target)
                if result != OK:
                    console.log("[{}] Unknown result from creep.repair({}): {}".format(
                        creep.name, target, result))
                # Let the creeps get a little bit closer than required to the controller, to make room for other creeps.
                if not creep.pos.inRangeTo(target, 2):
                    creep.moveTo(target)
        else:
            creep.moveTo(target)

def get_new_source(creep):

    #container or storage
    structures = creep.room.find(FIND_STRUCTURES)
    containers = [s for s in structures if \
        ((s.structureType == STRUCTURE_CONTAINER) or (s.structureType == STRUCTURE_STORAGE))]

    if len(containers) > 0:
        useable_containers = [s for s in containers if s.store[RESOURCE_ENERGY] > 0]
        if len(useable_containers) > 0:
            source = creep.pos.findClosestByPath(useable_containers)
    else:
        #spawn or extension if there are no containers or storages
        cores = [s for s in structures if \
            (((s.structureType == STRUCTURE_SPAWN) or (s.structureType == STRUCTURE_EXTENSION)) and \
            (s.energy > 0))]
        if len(cores) > 0:
            source = creep.pos.findClosestByPath(cores)

    if source:
        creep.memory.source = source.id
        source_id = source.id
    else:
        source_id = ''
    return source_id

def get_new_target(creep):
    build_target = creep.pos.findClosestByPath(creep.room.find(FIND_CONSTRUCTION_SITES))

    #repair_targets2 = [s for s in creep.room.find(FIND_STRUCTURES)]
    #repair_targets2 = [s for s in repair_targets2 if s.structureType \
    # != STRUCTURE_WALL and s.structureType != STRUCTURE_RAMPART and s.hits / s.hitMax <= 0.4]

    #console.log('len of repair_targets2 is {}'.format(len(repair_targets2)))
    #console.log('first target id is {} of type {}'.format(repair_targets2[0].id, repair_targets2[0].structureType))
    structures = creep.room.find(FIND_STRUCTURES)
    repair_target1 = creep.pos.findClosestByPath([s for s in structures if \
        ((s.hits < s.hitsMax / 3) and \
        (s.structureType != STRUCTURE_WALL) and (s.structureType != STRUCTURE_RAMPART))])

    repair_target2 = creep.pos.findClosestByPath([s for s in structures if \
        ((s.hits < s.hitsMax * 0.75) and \
        (s.structureType != STRUCTURE_WALL) and (s.structureType != STRUCTURE_RAMPART))])

    controller_target = _(creep.room.find(FIND_STRUCTURES)) \
        .filter(lambda s: (s.structureType == STRUCTURE_CONTROLLER)) \
        .sample()

    energy_in_storage = _.sum([s.store[RESOURCE_ENERGY] for s in structures if s.structureType == STRUCTURE_STORAGE])

    wall_target_hits = util.get_wall_target_hits(creep.room)
    console.log('wall_target_hits: {}'.format(wall_target_hits))
    wall_targets = [s for s in structures if \
        ((s.hits < wall_target_hits) and \
        ((s.structureType == STRUCTURE_WALL) or (s.structureType == STRUCTURE_RAMPART)))]

    if controller_target.ticksToDowngrade <= 4000 and controller_target:
        creep.memory.target = controller_target.id
        target_id = controller_target.id
    elif repair_target1:
        creep.memory.target = repair_target1.id
        target_id = repair_target1.id
    elif build_target:
        creep.memory.target = build_target.id
        target_id = build_target.id
    elif repair_target2:
        creep.memory.target = repair_target2.id
        target_id = repair_target2.id
    elif len(wall_targets) > 0 and energy_in_storage >= 50000:
        lowest_wall = None
        lowest_hits = 0
        for wall in wall_targets:
            if wall.hits < lowest_hits or lowest_hits == 0:
                lowest_wall = wall
                lowest_hits = wall.hits
        creep.memory.target = lowest_wall.id
        target_id = lowest_wall.id
    elif controller_target:
        creep.memory.target = controller_target.id
        target_id = controller_target.id
    else:
        target_id = ''
    if target_id != '':
        console.log('builder found new target {}'.format(target_id))
        creep.memory.target_expires = Game.time + 50
    return target_id

""" hauler role """
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


def run(creep):
    """
    Runs a creep as a generic hauler.
    :param creep: The creep to run

    creep.memory.assisting = id of creep that hauler is helping
    creep.memory.assisting_role = role of crepe that hauler is helping
    creep.memory.storageInput = if hauler is taking from a container (when assisting a builder, or
        assisting a harvester with a nearby container)
    creep.memory.storageOutput = if hauler is sending to a spawn, extension, or storage

    Basic logic:
        - Target a worker creep that no other hauler has targeted
        - If target creep's role is harvester, the hauler will take energy from the harvester and bring back to base
            - take from any containers within 3 spaces of the harvester first
            - take from harvester next
            - if not next to either, but next to another harvester, take from that other harvester
            - if not next to container or harvester, move towards the closest of the two
        - Send to spawn or extension first
        - Next, send to storage
        - If no valid storage, spawn, or extensions, fill up first, then move back within 3 spaces of spawn
        - If no valid assisting target, but there is a valid
             container or storage (input) and a valid storage, spawn, or extension (output),
             then haul from the container or storage to the storage, spawn, or extension
    """


    if creep.carryCapacity == 0:
        creep.suicide()

    if creep.memory.filling and _.sum(creep.carry) >= creep.carryCapacity:
        creep.memory.filling = False
        assisting_id = get_new_assisting(creep)
    elif (not creep.memory.filling) and (creep.carry[RESOURCE_ENERGY]) <= 0:
        creep.memory.filling = True
        assisting_id = get_new_assisting(creep)
    else:
        assisting_id = check_assisting(creep)

    assisting = Game.getObjectById(assisting_id)
    if len(assisting) == 0:
        console.log('hauler {} is not assisting a valid target'.format(creep.name))
        return
    assisting_role = assisting.memory.role


    if creep.memory.filling:
        storage_input = get_storage_input(creep, assisting, assisting_role)
        if len(storage_input) > 0:
            transfer(creep, storage_input, True)
        else:
            console.log('hauler {} cant fill up.  retargeting a harvester'.format(creep.name))
            assisting_id = get_new_assisting(creep, [ROLE_HARVESTER])
            return
    elif not creep.memory.filling:
        storage_output = get_storage_output(creep, assisting, assisting_role)
        if len(storage_output) > 0:
            transfer(creep, storage_output, False)
        else:
            console.log('hauler {} cant empty.  retargeting a builder'.format(creep.name))
            assisting_id = get_new_assisting(creep, [ROLE_BUILDER])
            return

def check_assisting(creep):
    assisting = Game.getObjectById(creep.memory.assisting)
    if len(assisting) == 0:
        return get_new_assisting(creep)
    else:
        return creep.memory.assisting

def get_new_assisting(creep, roles=''):
    roles = [ROLE_BUILDER, ROLE_HARVESTER] if roles == '' else roles

    creeps = creep.room.find(FIND_MY_CREEPS)
    workers = [w for w in creeps if len([r for r in roles if w.memory.role == r]) > 0]
    haulers = [h for h in creeps if (h.memory.role == ROLE_HAULER and h.id != creep.id)]
    free_workers = [w for w in workers if len([h for h in haulers if h.memory.assisting == w.id]) == 0]

    if len(free_workers) > 0:
        assisting = creep.pos.findClosestByPath(free_workers)
        if len(assisting) > 0:
            creep.memory.assisting = assisting.id
            creep.memory.assisting_role = assisting.memory.role
            return assisting.id

    builders = [b for b in creeps if b.role == ROLE_BUILDER]
    if len(builders) > 0:
        assisting = creep.pos.findClosestByPath(builders)
        if len(assisting) > 0:
            creep.memory.assisting = assisting.id
            creep.memory.assisting_role = assisting.memory.role
            return assisting.id

    console.log('no valid worker to assist')
    del creep.memory.assisting
    return False

def get_storage_input(creep, assisting, assisting_role):
    if assisting_role == ROLE_HARVESTER:
        #container within 3 squares of assisting
        structures = assisting.pos.findInRange(FIND_STRUCTURES, 5)
        #console.log('structures found: {}'.format([s.structureType for s in structures]))
        containers = [s for s in structures if \
            ((s.structureType == STRUCTURE_CONTAINER) and (s.store[RESOURCE_ENERGY] > 0))]
        #console.log('hauler {} assisting {} at pos {}, {}'.format(creep.name, assisting.name, assisting.pos.x, assisting.pos.y))
        if len(containers) > 0:
            #console.log('found container to use')
            return creep.pos.findClosestByPath(containers)


        #assisting if in 1 square
        distance_from_assisting = creep.pos.getRangeTo(assisting.pos)
        if distance_from_assisting <= 1:
            return assisting

        #any other harvester if in 1 square
        other_harvesters = [c for c in creep.room.find(FIND_MY_CREEPS) if \
            ((c.memory.role == ROLE_HARVESTER) and (c.energy > 0) and (c.pos.inRangeTo(creep.pos, 1)))]
        if len(other_harvesters) > 0:
            return creep.pos.findClosestByPath(other_harvesters)

        #fall back to taking from assisting
        return assisting

    elif assisting_role == ROLE_BUILDER:
        #any harvester within 1 square
        harvesters = [c for c in creep.room.find(FIND_MY_CREEPS) if \
            ((c.memory.role == ROLE_HARVESTER) and (c.energy > 0))]
        harvesters_within_1 = [c for c in harvesters if c.pos.inRangeTo(creep.pos, 1)]
        if len(harvesters_within_1) > 0:
            return creep.pos.findClosestByPath(harvesters_within_1)

        #any haulers with assisting_role of ROLE_HARVESTER within 1 square
        haulers = [c for c in creep.room.find(FIND_MY_CREEPS) if \
            ((c.memory.role == ROLE_HAULER) and (c.memory.assisting_role == ROLE_HARVESTER) and (c.energy > 0))]
        haulers_within_1 = [c for c in haulers if c.pos.inRangeTo(creep.pos, 1)]
        if len(haulers_within_1) > 0:
            return creep.pos.findClosestByPath(haulers_within_1)

        #container or storage
        structures = creep.room.find(FIND_STRUCTURES)
        containers = [s for s in structures if \
            ((s.structureType == STRUCTURE_CONTAINER) or (s.structureType == STRUCTURE_STORAGE))]

        if len(containers) > 0:
            useable_containers = [s for s in containers if s.store[RESOURCE_ENERGY] > 0]
            if len(useable_containers) > 0:
                return creep.pos.findClosestByPath(useable_containers)
        else:
            #spawn or extension if there are no containers or storages
            cores = [s for s in structures if \
                (((s.structureType == STRUCTURE_SPAWN) or (s.structureType == STRUCTURE_EXTENSION)) and \
                (s.energy > 0))]
            if len(cores) > 0:
                return creep.pos.findClosestByPath(cores)

        #any hauler with assisting_role of ROLE_HARVESTER
        if len(haulers) > 0:
            return creep.pos.findClosestByPath(haulers)

        #any harvester
        if len(harvesters) > 0:
            return creep.pos.findClosestByPath(harvesters)

def get_storage_output(creep, assisting, assisting_role):
    if assisting_role == ROLE_HARVESTER:
        #spawn or extension
        cores = [s for s in creep.room.find(FIND_MY_STRUCTURES) if \
            (((s.structureType == STRUCTURE_SPAWN) or (s.structureType == STRUCTURE_EXTENSION)) and \
            (s.energy < s.energyCapacity))]
        if len(cores) > 0:
            return creep.pos.findClosestByPath(cores)

        #towers
        towers = [s for s in creep.room.find(FIND_MY_STRUCTURES) if \
            ((s.structureType == STRUCTURE_TOWER) and \
            (s.energy < s.energyCapacity))]
        if len(towers) > 0:
            return creep.pos.findClosestByPath(towers)

        #storage
        storages = [s for s in creep.room.find(FIND_MY_STRUCTURES) if \
            ((s.structureType == STRUCTURE_STORAGE) and \
            (_.sum(s.store) < s.storeCapacity))]
        if len(storages) > 0:
            return creep.pos.findClosestByPath(storages)

        #any hauler with assisting_role of ROLE_BUILDER
        haulers = [c for c in creep.room.find(FIND_MY_CREEPS) if \
            ((c.memory.role == ROLE_HAULER) and (c.memory.assisting_role == ROLE_BUILDER) and (_.sum(c.carry) < c.carryCapacity))]
        if len(haulers) > 0:
            return creep.pos.findClosestByPath(haulers)

    elif assisting_role == ROLE_BUILDER:
        return assisting



def transfer(creep, target, filling):

    if filling:
        input_from = target
        output_to = creep
        input_from_is_creep = True if (len(input_from.body) > 0) else False
        output_to_is_creep = True
    else:
        input_from = creep
        output_to = target
        input_from_is_creep = True
        output_to_is_creep = True if (len(output_to.body) > 0) else False

    if input_from_is_creep:
        result = input_from.transfer(output_to, RESOURCE_ENERGY)
    elif output_to_is_creep:
        result = output_to.withdraw(input_from, RESOURCE_ENERGY)
    else:
        del creep.memory.assisting
        del creep.memory.assisting_role
        return

    if result == ERR_NOT_IN_RANGE:
        creep.moveTo(target)
    elif result == ERR_FULL or result == ERR_NOT_ENOUGH_RESOURCES:
        del creep.memory.assisting
        del creep.memory.assisting_role
    elif not result == OK:
        console.log("[{}] Unknown result from creep transfer or withdraw {}, {}): {}".format(input_from, output_to, RESOURCE_ENERGY, result))

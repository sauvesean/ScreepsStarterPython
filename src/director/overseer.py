from structs import tower
from roles import harvester
from roles import hauler
from roles import builder
import util
from glo import *
from defs import *

__pragma__('noalias', 'name')
__pragma__('noalias', 'undefined')
__pragma__('noalias', 'Infinity')
__pragma__('noalias', 'keys')
__pragma__('noalias', 'get')
__pragma__('noalias', 'set')
__pragma__('noalias', 'type')
__pragma__('noalias', 'update')

#class hive():
#
#    def __init__(self)

#passes in a room right now.  Will eventually be passed in a custom 'hive' object
def run(hive):
    #console.log('running hive {}'.format(hive))

    run_spawners(hive)

    run_structures(hive)

    run_creeps(hive)

    controller_target = _(hive.find(FIND_STRUCTURES)) \
        .filter(lambda s: (s.structureType == STRUCTURE_CONTROLLER)) \
        .sample()

    if controller_target.ticksToDowngrade <= 4000:
        console.log('ticks to downgrade: ' + controller_target.ticksToDowngrade)

def run_structures(hive):
    structures = [s for s in hive.find(FIND_MY_STRUCTURES)]

    for structure in structures:
        if structure.structureType == STRUCTURE_TOWER:
            tower.run(structure)

def run_spawners(hive):
    # Run each spawn
    spawns = [s for s in hive.find(FIND_MY_SPAWNS) if not s.spawning]
    for spawn in spawns:
        #assign role to newly created creep
        if spawn.memory.newCreepWaiting:
            creep = Game.creeps[spawn.memory.newCreepName]
            creep.memory.role = spawn.memory.newCreepRole
            spawn.memory.newCreepWaiting = False
            spawn.memory.newCreepName = ''
            spawn.memory.newCreepRole = ''

        role = get_best_role(spawn)
        if role != '':
            spawn_new_creep(spawn, role)

def get_best_role(spawn):
    role = ''
    # Get the number of harvester creeps in the room.
    creeps = spawn.room.find(FIND_MY_CREEPS)
    #Standard collections aren't implemented in transcrypt, so we can't use Counter
    #num_creeps = Counter([c.memory.role for c in creeps])
    num_creeps = {
        ROLE_HARVESTER: len([c for c in creeps if c.memory.role == ROLE_HARVESTER]),
        ROLE_HAULER: len([c for c in creeps if c.memory.role == ROLE_HAULER]),
        ROLE_BUILDER: len([c for c in creeps if c.memory.role == ROLE_BUILDER])
    }
    #console.log('num_creep harvester: {}'.format(num_creeps[ROLE_HARVESTER]))

    # If there are no harvesters spawn a creep once energy is at 250 or more
    if num_creeps[ROLE_HARVESTER] <= 0 and spawn.room.energyAvailable >= 250:
        role = ROLE_HARVESTER

    # If there are less than enough harvesters but at least one,
    # wait until all spawns and extensions are full before
    # spawning.
    elif spawn.room.energyAvailable >= spawn.room.energyCapacityAvailable:
        source_spots = _.sum([util.get_source_spots(s) for s in spawn.room.find(FIND_SOURCES)])
        maxed_sources = (num_creeps[ROLE_HARVESTER] >= source_spots or \
            (spawn.room.controller.level >= 4 and num_creeps[ROLE_HARVESTER] >= len(spawn.room.find(FIND_SOURCES))))
        if num_creeps[ROLE_HARVESTER] == 0 and num_creeps[ROLE_BUILDER] > 0:
            #change a builder into a harvester
            builder = [c for c in spawn.room.find(FIND_MY_CREEPS) if c.memory.role == ROLE_BUILDER]
            
        if not maxed_sources and num_creeps[ROLE_HAULER] >= num_creeps[ROLE_HARVESTER]:
            role = ROLE_HARVESTER
        elif num_creeps[ROLE_HAULER] < (num_creeps[ROLE_HARVESTER] + num_creeps[ROLE_BUILDER]):
            role = ROLE_HAULER
        elif num_creeps[ROLE_BUILDER] < 2:
            role = ROLE_BUILDER
            #console.log('out of creeps to spawn')
            #num_haulers = _.sum(Game.creeps, lambda c: c.pos.roomName == spawn.pos.roomName and c.memory.role == ROLE_HAULER)

    return role


def spawn_new_creep(spawn, role):
    name = '{}{}{}'.format(role, Game.time, spawn.name)
    result = spawn.spawnCreep(util.get_best_body(spawn.room, role), name)
    if result == OK:
        spawn.memory.newCreepWaiting = True
        spawn.memory.newCreepName = name
        spawn.memory.newCreepRole = role

def run_creeps(hive):
    # Run each creep
    #console.log('running all creeps in hive {}'.format(hive))
    creeps = [c for c in hive.find(FIND_MY_CREEPS) if c.memory.role != undefined]
    #this doesn't seem to work even when modules are imported using 'import roles.rolename'
    #this is because of the way transcrypt handles the namespace
    #so I'll do it the hard way
    #getattr(roles, creep.memory.role).run(creep)
    #run_functions = {
    #    ROLE_HARVESTER: harvester.run,
    #    ROLE_HAULER: hauler.run
    #}
    for creep in creeps:
        #run_functions[creep.memory.role](creep)
        if creep.memory.role == ROLE_HARVESTER:
            harvester.run(creep)
        elif creep.memory.role == ROLE_HAULER:
            hauler.run(creep)
        elif creep.memory.role == ROLE_BUILDER:
            builder.run(creep)
        else:
            console.log('creep run not implemented')

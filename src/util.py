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

def get_available_sources(room):
    sources = [s for s in room.find(FIND_SOURCES) if s.energy > 0]

    #creeps = room.find(FIND_MY_CREEPS)
    valid_sources = []
    for source in sources:

        hostile_creeps = source.pos.findInRange(FIND_HOSTILE_CREEPS, 10)
        hostile_spawns = source.pos.findInRange(FIND_HOSTILE_STRUCTURES, 10)
        used_work = get_source_used_work(source, room)
        if len(hostile_creeps) == 0 and len(hostile_spawns) == 0 and used_work < 8:
            source_spots = get_source_spots(source)
            source_used_spots = get_source_used_spots(source, room)

            if source_spots > source_used_spots:
                valid_sources.append(source)

    if valid_sources == []:
        for source in sources:
            source_spots = get_source_spots(source)
            source_used_spots = get_source_used_spots(source, room)
            #source_used_work = get_source_used_work(source, room)
            if source_spots > source_used_spots:
                valid_sources.append(source)

    return valid_sources

def get_best_source(room):
    sources = [s for s in room.find(FIND_SOURCES) if s.energy > 0]
    best_score = 10000.000000
    for source in sources:

        hostile_creeps = source.pos.findInRange(FIND_HOSTILE_CREEPS, 10)
        hostile_spawns = source.pos.findInRange(FIND_HOSTILE_STRUCTURES, 10)
        used_work = get_source_used_work(source, room)
        if len(hostile_creeps) == 0 and len(hostile_spawns) == 0 and used_work < 8:
            score = get_source_score(source)
            if score <= best_score:
                best_score = score
                best = source

    if not best:
        for source in sources:
            score = get_source_score(source)
            if score <= best_score:
                best_score = score
                best = source
    return best

def get_best_source_score(room):
    sources = [s for s in room.find(FIND_SOURCES) if s.energy > 0]
    best_score = 10000.000000
    for source in sources:

        hostile_creeps = source.pos.findInRange(FIND_HOSTILE_CREEPS, 10)
        hostile_spawns = source.pos.findInRange(FIND_HOSTILE_STRUCTURES, 10)
        used_work = get_source_used_work(source, room)
        if len(hostile_creeps) == 0 and len(hostile_spawns) == 0 and used_work < 8:
            score = get_source_score(source)
            if score <= best_score:
                best_score = score

    if best_score == 10000.0:
        for source in sources:
            score = get_source_score(source)
            if score <= best_score:
                best_score = score

    return best_score

def get_source_score(source):
    score = get_source_used_spots(source, source.room) / get_source_spots(source)
    return score


def get_source_used_spots(source, room):
    creeps = [c for c in room.find(FIND_MY_CREEPS) if c.memory.role == ROLE_HARVESTER and c.memory.source == source.id]
    return len(creeps)


def get_source_used_work(source, room):
    total_work = 0
    creeps = [c for c in room.find(FIND_MY_CREEPS) if c.memory.role == ROLE_HARVESTER and c.memory.source == source.id]
    for creep in creeps:
        body = creep.body
        for part in body:
            total_work += 1 if part.type == WORK else 0
    return total_work


def get_source_spots(source):
    source_spots = 0
    for mod_x in range(3):
        for mod_y in range(3):
            if not (mod_x == 1 and mod_y == 1):
                new_x = source.pos.x + mod_x - 1
                new_y = source.pos.y + mod_y - 1
                new_room = source.pos.roomName
                if Game.map.getTerrainAt(new_x, new_y, new_room) != 'wall':
                    source_spots += 1
    return source_spots

def get_total_source_spots(room):
    sources = [s for s in room.find(FIND_SOURCES) if s.energy > 0]
    source_spots = 0
    for source in sources:

        hostile_creeps = source.pos.findInRange(FIND_HOSTILE_CREEPS, 5)
        hostile_spawns = source.pos.findInRange(FIND_HOSTILE_STRUCTURES, 5)
        if len(hostile_creeps) == 0 and len(hostile_spawns) == 0:
            source_spots += get_source_spots(source)

    return source_spots

def get_body(role):
    #dictionary 'get' function wasn't working in transcrypt, so failing back to if..elif..
    #1 = 300
    #2 = 300 + 250 = 550
    #3 = 300 + 500 = 800
    #4 = 300 + 1000 = 1300
    #5 = 300 + 1500 = 1800
    #6 = 300 + 2000 = 2300
    #7 = 300 + 5000 = 5300
    #8 = 300 + 12000 = 12300
    if role == ROLE_HARVESTER:
        result = [
            [WORK, CARRY, MOVE, MOVE],
            [WORK, WORK, WORK, CARRY, CARRY, MOVE, MOVE],
            [WORK, WORK, WORK, WORK, WORK, CARRY, CARRY, MOVE, MOVE],
            [WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK, CARRY, CARRY, CARRY, MOVE, MOVE, MOVE, MOVE, MOVE],
            [WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK, CARRY, CARRY, CARRY, MOVE, MOVE, MOVE, MOVE, MOVE],
            [WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK, CARRY, CARRY, CARRY, CARRY, MOVE, MOVE, MOVE, MOVE, MOVE, MOVE]
        ]
    elif role == ROLE_HAULER:
        result = [
            [CARRY, MOVE, CARRY, MOVE, CARRY, MOVE],
            [CARRY, MOVE, CARRY, MOVE, CARRY, MOVE, \
                CARRY, MOVE, CARRY, MOVE],
            [CARRY, MOVE, CARRY, MOVE, CARRY, MOVE, \
                CARRY, MOVE, CARRY, MOVE, CARRY, MOVE, CARRY, MOVE, CARRY, MOVE],
            [CARRY, MOVE, CARRY, MOVE, CARRY, MOVE, \
                CARRY, MOVE, CARRY, MOVE, CARRY, MOVE, CARRY, MOVE, CARRY, MOVE, \
                CARRY, MOVE, CARRY, MOVE, CARRY, MOVE, CARRY, MOVE, CARRY, MOVE],
            [CARRY, MOVE, CARRY, MOVE, CARRY, MOVE, \
                CARRY, MOVE, CARRY, MOVE, CARRY, MOVE, CARRY, MOVE, CARRY, MOVE, \
                CARRY, MOVE, CARRY, MOVE, CARRY, MOVE, CARRY, MOVE, CARRY, MOVE, \
                CARRY, MOVE, CARRY, MOVE, CARRY, MOVE, CARRY, MOVE, CARRY, MOVE],
            [CARRY, MOVE, CARRY, MOVE, CARRY, MOVE, \
                CARRY, MOVE, CARRY, MOVE, CARRY, MOVE, CARRY, MOVE, CARRY, MOVE, \
                CARRY, MOVE, CARRY, MOVE, CARRY, MOVE, CARRY, MOVE, CARRY, MOVE, \
                CARRY, MOVE, CARRY, MOVE, CARRY, MOVE, CARRY, MOVE, CARRY, MOVE, \
                CARRY, MOVE, CARRY, MOVE, CARRY, MOVE, CARRY, MOVE, CARRY, MOVE],
            [CARRY, MOVE, CARRY, MOVE, CARRY, MOVE, \
                CARRY, MOVE, CARRY, MOVE, CARRY, MOVE, CARRY, MOVE, CARRY, MOVE, \
                CARRY, MOVE, CARRY, MOVE, CARRY, MOVE, CARRY, MOVE, CARRY, MOVE, \
                CARRY, MOVE, CARRY, MOVE, CARRY, MOVE, CARRY, MOVE, CARRY, MOVE, \
                CARRY, MOVE, CARRY, MOVE, CARRY, MOVE, CARRY, MOVE, CARRY, MOVE],
            [CARRY, MOVE, CARRY, MOVE, CARRY, MOVE, \
                CARRY, MOVE, CARRY, MOVE, CARRY, MOVE, CARRY, MOVE, CARRY, MOVE, \
                CARRY, MOVE, CARRY, MOVE, CARRY, MOVE, CARRY, MOVE, CARRY, MOVE, \
                CARRY, MOVE, CARRY, MOVE, CARRY, MOVE, CARRY, MOVE, CARRY, MOVE, \
                CARRY, MOVE, CARRY, MOVE, CARRY, MOVE, CARRY, MOVE, CARRY, MOVE]
        ]
    elif role == ROLE_BUILDER:
        result = [
            [WORK, CARRY, MOVE, MOVE],
            [WORK, WORK, WORK, CARRY, CARRY, MOVE, MOVE],
            [WORK, WORK, WORK, WORK, WORK, CARRY, CARRY, MOVE, MOVE],
            [WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK, CARRY, CARRY, CARRY, MOVE, MOVE, MOVE, MOVE, MOVE],
            [WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK, \
                CARRY, CARRY, CARRY, CARRY, CARRY, CARRY, MOVE, MOVE, MOVE, MOVE, MOVE, MOVE, MOVE, MOVE]
        ]
    else:
        result = [
            [WORK, CARRY, MOVE, MOVE],
            [WORK, WORK, WORK, CARRY, CARRY, MOVE, MOVE],
            [WORK, WORK, WORK, WORK, WORK, CARRY, CARRY, MOVE, MOVE],
            [WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK, CARRY, CARRY, CARRY, MOVE, MOVE, MOVE, MOVE, MOVE],
            [WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK, CARRY, CARRY, CARRY, MOVE, MOVE, MOVE, MOVE, MOVE]
        ]
    return result


def get_best_body(room, role):
    energy = room.energyAvailable
    bodies = get_body(role)
    level = 0
    max_level = room.controller.level
    best_body = []
    for body in bodies:
        cost = 0
        level += 1
        if level <= max_level:
            for part in body:
                cost += BODYPART_COST[part]
            if cost <= energy:
                best_body = body

    return best_body

def get_wall_target_hits(room):
    controller_level = room.controller.level
    target_hits = [0, 10000, 20000, 50000, 150000, 500000, 1000000, 2000000, 2900000]
    return target_hits[controller_level]

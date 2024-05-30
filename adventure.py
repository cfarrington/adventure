#!/usr/bin/env python3
program_description='''
An adventure game.
'''

class Object:
    lookup = {}
    def __init__(self,name,actions):
        self.lookup[name] = self
        self.name = name
        self.location = None
        self.actions = set(actions)

# XXX some temporary nonsense
# XXX eventually list all the objects in the game, and the list of actions
# XXX the object performs
Object('bell',['ring'])
Object('book',['read'])
Object('candle',['light'])

class Position:
    '''Define a room within a map.'''
    def __init__(self,x,y):
        self.x = x
        self.y = y
    def __eq__(self,rhs):
        return isinstance(rhs,Position) and self.x == rhs.x and self.y == rhs.y
    def __str__(self):
        return f'({self.x},{self.y})'

class Map:
    def __init__(self,w,h):
        self.w = w
        self.h = h
    def starting_position(self):
        return Position(0,0)
    def move(self,pos,direction):
        dx = dict(E=1,W=-1)
        dy = dict(N=-1,S=1)
        new_pos = Position(
                pos.x+dx.get(direction,0),
                pos.y+dy.get(direction,0),
                )
        if 0 <= new_pos.x < self.w and 0 <= new_pos.y < self.h:
            return new_pos
        return None # out of bounds

class Player:
    backpack_capacity = 3
    permanent_actions = [
            'move',
            'dump',
            ]
    def __init__(self):
        self.backpack = set()
    def turn(self,a):
        words = self.get_action()
        self.perform_action(a,words)
    def get_action(self):
        cmd = input('What do you want to do? ')
        return cmd.split()
    def perform_action(self,a,words):
        if not words:
            return
        # assemble all valid action names
        valid_actions = set(self.permanent_actions)
        if self.backpack:
            valid_actions.add('drop')
        room_objects = a.room_objects(self.position)
        if len(self.backpack) < self.backpack_capacity and room_objects:
            valid_actions.add('grab')
        for obj in room_objects|self.backpack:
            valid_actions |= set(obj.actions)
        # validate entered action
        if words[0] not in valid_actions:
            print(f"'{words[0]}' is not a valid action")
            return
        # call function to perform action, passing player and arguments
        action = getattr(a,'do_'+words[0])
        action(self,words[1:])

class Adventure:
    def setup(self):
        self.player = Player()
        self.map = Map(3,1)
        self.player.position = self.map.starting_position()
        # XXX for testing
        Object.lookup['bell'].location = Position(0,0)
        Object.lookup['book'].location = Position(1,0)
        Object.lookup['candle'].location = Position(2,0)
    def play(self):
        self.setup()
        while (True):
            self.player.turn(self)
    def room_objects(self,pos):
        return set(x for x in Object.lookup.values() if x.location == pos)
    def do_dump(self,player,args):
        print('Player at',player.position)
        print('Backpack:',','.join(x.name for x in player.backpack))
        room_objs = self.room_objects(player.position)
        print('Room contents:',','.join(x.name for x in room_objs))
    def do_move(self,player,args):
        # XXX eventually handle missing arg here, maybe in a reusable way
        new_pos = self.map.move(player.position,args[0])
        if not new_pos:
            print("There's nothing in that direction")
        else:
            print("Entering a new room")
            self.player.position = new_pos
    def do_grab(self,player,args):
        obj = Object.lookup.get(args[0])
        if not obj:
            print(f"'{args[0]}' is not an object")
            return
        if obj.location != player.position:
            print(f"'{args[0]}' is not in this room")
            return
        obj.location = None
        player.backpack.add(obj)
    def do_drop(self,player,args):
        obj = Object.lookup.get(args[0])
        if not obj:
            print(f"'{args[0]}' is not an object")
            return
        if obj not in player.backpack:
            print(f"'{args[0]}' is not in the backpack")
            return
        obj.location = player.position
        player.backpack.remove(obj)
    # XXX implement object-specific actions
    # XXX - note that if multiple objects support the same action, we need to
    # XXX   detect and disambiguate this case

if __name__ == '__main__':
    p1 = Position(0,0)
    p2 = Position(0,0)
    assert p1 == p2
    import argparse
    parser = argparse.ArgumentParser(
            description=program_description,
            formatter_class=argparse.RawDescriptionHelpFormatter,
            )
    args = parser.parse_args()
    a = Adventure()
    a.play()
    

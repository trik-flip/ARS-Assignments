from src.robby.robot import Robot

class fitness:
    @staticmethod
    def fitfunc(robby: Robot):
        travelled = 0
        been_here = [robby.history[0]]
        for pos in robby.history:
            if min([fitness._moved(*pos,*p) for p in been_here]) > robby.size:
                been_here.append(pos)
                travelled += 1

        max_distance = max([fitness._moved(*robby.history[0], *pos) for pos in robby.history])
        return -max_distance*3 - travelled*1 + robby.collision_count*100

    @staticmethod
    def _moved(x,y,x2,y2):
        return( (x2-x)**2+(y2-y)**2)**1/2

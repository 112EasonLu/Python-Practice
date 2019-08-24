import random
# show the maze or the path
def show_maze(maze):
    for i in maze:
        for j in i:
            if j==0:
                print('\033[36m',j,sep='',end=' \033[0m')
            elif j=='+':
                print('\033[31m',j,sep='',end=' \033[0m')
            elif j=='O':
                print('\033[33m',j,sep='',end=' \033[0m')
            else:
                print(j,end=' ')
        print()
# build a maze which the size of maze is [n]
def build_maze(n):
    maze=[]
    # outer wall
    for i in range(n+2):
        if i==0:
            maze.append(['O']+[0]*(n+1))
        elif i==n+1:
            maze.append([0]*(n+1)+['O'])
        else:
            maze.append([0]+[' ']*n+[0])
    # random inner wall
    for i in range(1,n+1):
        if i==1:
            for j in range(n//4):
                maze[i][random.randint(2,n-1)]=0
        elif i==n:
            for j in range(n//4):
                maze[i][random.randint(1,n-2)]=0
        else:
            for j in range(n//4):
                maze[i][random.randint(1,n-1)]=0
    show_maze(maze)
    return maze
# find the exit of the maze
def route():
    maze=build_maze(9)
    # the way out of maze
    path=[(1,1)]
    # never again
    footprint=[]
    # right down left up
    steps=((0,1),(1,0),(0,-1),(-1,0))
    # entrance
    x=y=1
    while x!=9 or y!=9:
        # horizontal vertical
        for h,v in steps:
            if maze[x+h][y+v]==' ' and (x+h,y+v) not in footprint:
                path.append((x+h,y+v))
                footprint.append((x+h,y+v))
                break
        else:
            path.pop()
        # location
        x,y=path[-1]
    # show the maze and the path
    for x,y in path:
        maze[x][y]='+'
    show_maze(maze)
# play
route()
#wip

empty_board1 = ' 1 | 2 | 3 '
empty_board2 = ' 4 | 5 | 6 '
empty_board3 = ' 7 | 8 | 9 '
line = '-----------'
new_line1 = ' 1 | 2 | 3 '
new_line2 = ' 4 | 5 | 6 '
new_line3 = ' 7 | 8 | 9 '
turn = 0
play = 0
 
 
def print_empty_board(s1, s2, s3, l):
    print(s1)
    print(l)
    print(s2)
    print(l)
    print(s3)
 
 
def get_position():
    global turn
    x = prompt_user_input()
    if validate_if_not_yet_played(x, new_line1, new_line2, new_line3):
        replace_position(x)
    else:
        turn -= 1
        get_position()
 
 
def prompt_user_input():
    global turn
    position = raw_input('Where do you wish to play ?\n')
    turn += 1
    return position
 
 
def validate_if_not_yet_played(num, s1, s2, s3):
    full_board = s1+s2+s3
    if num not in full_board:
        print ('Error: Position already played')
        return False
 
    return True
 
 
def replace_position(num):
    if num in new_line1:
        print('in line 1')
        change_line1(num)
    elif num in new_line2:
        new_line2.replace(num, 'x')
    elif num in new_line3:
        new_line3.replace(num, 'o')
 
 
def change_line1(num):
    global new_line1
    global new_line2
    global new_line3
    global turn
    player = find_player(turn)
 
    print('in change line')
    print (num)
 
    if num == 1:
        print('is one')
        new_line1 = new_line1[:1] + player + new_line1[2:]
        print(new_line1)
 
   
    # show_updated_board()
 
 
def find_player(x):
    if x % 2 == 0:
        player = 'O'
    else:
        player = 'X'
    return player
 
 
def show_updated_board():
    global new_line1
    global new_line2
    global new_line3
    print(new_line1)
    print(line)
    print(new_line2)
    print(line)
    print(new_line3)
 
 
def return_board_to_original_state():
    global empty_board1
    global empty_board3
    global empty_board3
    global new_line1
    global new_line2
    global new_line3
    new_line1 = empty_board1
    new_line2 = empty_board2
    new_line3 = empty_board3
 
return_board_to_original_state()
 
print_empty_board(empty_board1, empty_board2, empty_board3, line)
 
get_position()

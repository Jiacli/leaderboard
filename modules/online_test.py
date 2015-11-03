# -*- coding: utf-8 -*-
import math


def evaluate(infile, golden):

    test_in = open(infile, 'r')
    error = False
    err_msg = 'No error.'
    RMSE = 0.0
    ACC = 0.0
    size = len(golden)

    for star in golden:

        line = test_in.readline()
        if len(line) == 0:
            err_msg = 'Error: answer incomplete!'
            error = True
            break

        try:
            line = line.strip().split(' ')
            star_hard, star_soft = int(line[0]), float(line[1])
        except:
            err_msg = "Error: couldn't parse rating line in test file, \
                please check your submitted file."
            error = True
            break

        if star == star_hard:
            ACC += 1.0
        RMSE += (star - star_soft) ** 2

    test_in.close()

    if not error:
        return True, (ACC / size, math.sqrt(RMSE / size))
    else:
        return False, err_msg



def evaluate_rmse(infile, golden):
    test_in = open(infile, 'r')
    golden_in = open(golden, 'r')
    
    error = False
    err_msg = 'No error.'

    RMSE = 0.0
    num_ratings = 0

    while True:
        g_line = golden_in.readline()
        t_line = test_in.readline()
    
        if len(g_line) == 0 and len(t_line) == 0:
            # normally got to the end of each file at the same time
            break
        elif len(g_line) == 0 and len(t_line) > 0:
            err_msg = 'Error: prematurely reached the end of the test file'
            error = True
            break
        elif len(g_line) > 0 and len(t_line) == 0:
            err_msg = 'Error: answer incomplete!'
            error = True
            break
    
        # this is a rating line
        rating = -1
        rating_t = -1
        try:
            rating = float(g_line.strip())
        except:
            err_msg = 'Error: couldn\'t parse rating line in golden file, please report to TA'
            error = True
            break

        try:
            rating_t = float(t_line.strip())
        except:
            err_msg = 'Error: couldn\'t parse rating line in test file, please check your submitted file.'
            error = True
            break

        delta = rating_t - rating
        RMSE += delta * delta
        num_ratings = num_ratings + 1

    test_in.close()
    golden_in.close()

    if not error:
        return True, (math.sqrt(RMSE / num_ratings))
    else:
        return False, err_msg

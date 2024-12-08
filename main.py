# !/usr/bin/python3
# -*- coding: utf-8 -*-

import argparse
from browse import Readoor

parser = argparse.ArgumentParser(prog="Readoor automation")
parser.add_argument("-r", "--redo", action="store_true",
                    help="Redo the finished chapters with the correct answer")
parser.add_argument("-d", "--do", action="store_true",
                    help="Finish the unfinished with ai generated answers")
parser.add_argument("-t", "--time", type=int, default=900,
                    help="Set a time limit for how fast every chapter is finished")
parser.add_argument("-v", "--visible", action="store_false",
                    help="If the windows of the browser is visible")
parser.add_argument("-s", "--secbysec", action="store_true",
                    help="If the the program stops and let you decide on every chapter")
parser.add_argument("-p", "--path", type=str, default="",
                    help="If the the program stops and let you decide on every chapter")

args = parser.parse_args()

if args.do:
    driver = Readoor()
    driver.start(args.visible,args.time,args.secbysec,path_to_browser=args.path)
    driver.finish_unfinished()
    driver.stop()
    
if args.redo:
    driver = Readoor()
    driver.start(args.visible,args.time,args.secbysec,path_to_browser=args.path)
    driver.redo_finished()
    driver.stop()

    
    
    
    
    